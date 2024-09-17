import socket
import threading
import time


class Middleware:
    total_vagas_global = 100  # O total de vagas do estacionamento

    def __init__(self, station_number, neighbors):
        self.station_number = station_number
        self.station_port = 8880 + (station_number - 1)
        self.station_ip = "127.0.0.1"
        self.neighbors = neighbors
        self.neighbor_ports = {neighbor: 8880 + (neighbor - 1) for neighbor in neighbors}
        self.active_stations = {}
        self.total_vagas = 0  # Inicialmente, a estação não controla vagas
        self.vagas_controladas = []  # Lista para controlar as vagas alocadas a esta estação
        self.carros = {}
        self.is_active = False  # Estado inicial da estação (inativa)
        self.running = True  # Controla se a estação está rodando
        self.processed_failed_stations = set()  # Para evitar processar falhas múltiplas vezes

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.station_ip, self.station_port))
            self.server_socket.listen(5)
            print(f"Estação {self.station_number} iniciada na porta {self.station_port}, aguardando conexões...")
        except socket.error as e:
            print(f"Erro ao iniciar o socket na porta {self.station_port}: {e}")
            return

        threading.Thread(target=self.run_server, daemon=True).start()
        threading.Thread(target=self.monitor_stations, daemon=True).start()

    def run_server(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()

                # Aceitar apenas conexões de localhost
                if addr[0] != "127.0.0.1":
                    client_socket.close()
                    continue

                client_socket.settimeout(5)
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except socket.error as e:
                pass

    def handle_client(self, client_socket):
        try:
            while self.running:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    response = self.process_message(data)
                    if response:
                        client_socket.send(response.encode())
                except socket.timeout:
                    break
        finally:
            client_socket.close()

    def process_message(self, message):
        parts = message.strip().split(", ")
        code = parts[0]

        if code == "RV":  # Requisitar vaga
            car_id = parts[1]
            return self.allocate_vaga(car_id)
        elif code == "LV":  # Liberar vaga
            car_id = parts[1]
            return self.release_vaga(car_id)
        elif code == "AE":  # Ativar estação
            print(f"Ativando estação {self.station_number}...")
            return self.activate_station()
        elif code == "STATUS":
            if self.is_active:
                return f"ATIVA, {self.total_vagas}, {self.get_vagas_livres()}, {self.station_number}"
            else:
                return "INATIVA"
        elif code == "V":  # Mostrar vagas disponíveis
            return self.mostrar_vagas()
        elif code == "UPDATE_VAGAS":
            vagas = int(parts[1])
            print(f"Debug: Atualizando vagas da estação {self.station_number} para {vagas} vagas.")
            # Atualiza vagas_controladas
            occupied_vagas = [vaga for vaga in self.vagas_controladas if vaga is not None]
            self.vagas_controladas = occupied_vagas + [None] * (vagas - len(occupied_vagas))
            self.total_vagas = vagas
            # Reconstrói self.carros
            self.carros = {car_id: idx for idx, car_id in enumerate(self.vagas_controladas) if car_id is not None}
            print(f"Estação {self.station_number} agora tem {self.total_vagas} vagas.")
        elif code == "ALLOCATE_CAR":
            car_id = parts[1]
            response = self.allocate_vaga(car_id)
            print(f"Carro {car_id} transferido para estação {self.station_number}.")
            return response
        elif code == "CHECK_CAR":
            car_id = parts[1]
            if car_id in self.carros:
                return "ENCONTRADO"
            else:
                return "NAO_ENCONTRADO"
        elif code == "DE":  # Desligar estação
            print(f"Desligando estação {self.station_number}...")
            self.desligar_estacao()
            return "Estação desligada."
        elif code == "PING":
            return "PONG"
        elif code == "STATION_DOWN":
            estacao_desligada = int(parts[1])
            print(f"Estação {estacao_desligada} desligou. Iniciando eleição para redistribuição de vagas.")
            if estacao_desligada not in self.processed_failed_stations:
                self.processed_failed_stations.add(estacao_desligada)
                self.eleicao_estacao_falha(estacao_desligada)
        else:
            return "Comando desconhecido"

    def mostrar_vagas(self):
        vagas_ocupadas = len([vaga for vaga in self.vagas_controladas if vaga is not None])
        vagas_livres = self.get_vagas_livres()
        response = f"Estação {self.station_number}: Total de vagas: {self.total_vagas}, Ocupadas: {vagas_ocupadas}, Livres: {vagas_livres}"
        print(f"Debug: Estação {self.station_number} tem {self.total_vagas} vagas.")
        return response

    def allocate_vaga(self, car_id):
        if car_id in self.carros:
            return f"Carro {car_id} já está alocado em uma vaga."

        for i, vaga in enumerate(self.vagas_controladas):
            if vaga is None:
                self.vagas_controladas[i] = car_id
                self.carros[car_id] = i
                response = f"Vaga {i + 1} alocada para carro {car_id}."
                return response

        return "Sem vagas disponíveis"

    def release_vaga(self, car_id):
        if car_id in self.carros:
            vaga_index = self.carros[car_id]
            self.vagas_controladas[vaga_index] = None
            del self.carros[car_id]
            response = f"Carro {car_id} liberou a vaga {vaga_index + 1}"
            return response
        else:
            for neighbor in self.neighbors:
                resposta = self.consulta_carro_vizinha(car_id, neighbor)
                if resposta == "ENCONTRADO":
                    return f"Carro {car_id} liberado na estação {neighbor}"
            return f"Carro {car_id} não foi encontrado."

    def activate_station(self):
        self.is_active = True  # Marca a estação como ativa
        estacoes_ativas = self.pingar_estacoes_vizinhas()
        estacoes_ativas.append(self.station_number)
        self.redistribuir_vagas(estacoes_ativas)
        return "Estação ativada."

    def redistribuir_vagas(self, estacoes_ativas):
        """Redistribui as vagas corretamente entre as estações ativas."""
        total_estacoes = len(estacoes_ativas)
        vagas_por_estacao = Middleware.total_vagas_global // total_estacoes
        vagas_restantes = Middleware.total_vagas_global % total_estacoes

        # Ordena as estações para distribuir vagas restantes de forma consistente
        estacoes_ordenadas = sorted(estacoes_ativas)
        vagas_por_estacao_dict = {}

        for estacao in estacoes_ordenadas:
            vagas = vagas_por_estacao
            if vagas_restantes > 0:
                vagas += 1
                vagas_restantes -= 1
            vagas_por_estacao_dict[estacao] = vagas

        # Atualiza as estações com o novo número de vagas
        for estacao in estacoes_ordenadas:
            vagas = vagas_por_estacao_dict[estacao]
            if estacao == self.station_number:
                # Atualiza a estação atual
                self.total_vagas = vagas
                self.vagas_controladas = [None] * self.total_vagas
                print(f"Estação {self.station_number} recebeu {self.total_vagas} vagas.")
            else:
                # Atualiza a estação remota
                self.update_vagas(estacao, vagas)

    def update_vagas(self, estacao, vagas_novas):
        """Atualiza a quantidade de vagas da estação."""
        estacao_port = 8880 + (estacao - 1)
        try:
            with socket.create_connection((self.station_ip, estacao_port), timeout=1) as sock:
                mensagem = f"UPDATE_VAGAS, {vagas_novas}"
                sock.sendall(mensagem.encode())
                print(f"Atualizando a estação {estacao} para {vagas_novas} vagas.")
        except (ConnectionRefusedError, socket.timeout, socket.error):
            pass

    def pingar_estacoes_vizinhas(self):
        estacoes_ativas = []
        for neighbor in self.neighbors:
            neighbor_port = self.neighbor_ports[neighbor]
            resposta = self.ping_estacao(neighbor_port)
            if resposta:
                status, total_vagas, vagas_livres, station_number = resposta
                if status == "ATIVA":
                    self.active_stations[neighbor] = {
                        'total_vagas': total_vagas,
                        'vagas_livres': vagas_livres
                    }
                    estacoes_ativas.append(neighbor)
            else:
                if neighbor in self.active_stations:
                    del self.active_stations[neighbor]
        return estacoes_ativas

    def ping_estacao(self, porta):
        try:
            with socket.create_connection((self.station_ip, porta), timeout=1) as sock:
                sock.sendall("STATUS".encode())
                resposta = sock.recv(1024).decode()
            if resposta.startswith("ATIVA"):
                partes = resposta.split(", ")
                status = partes[0]
                total_vagas = int(partes[1])
                vagas_livres = int(partes[2])
                station_number = int(partes[3])
                return (status, total_vagas, vagas_livres, station_number)
            else:
                return None
        except (ConnectionRefusedError, socket.timeout, socket.error):
            return None

    def get_vagas_livres_estacao(self, estacao):
        """Consulta o número de vagas livres de uma estação vizinha."""
        if estacao in self.active_stations:
            return self.active_stations[estacao]['vagas_livres']
        else:
            return 0

    def get_vagas_livres(self):
        """Calcula o número de vagas livres."""
        return len([vaga for vaga in self.vagas_controladas if vaga is None])

    def consulta_carro_vizinha(self, car_id, estacao):
        """Consulta se um carro está estacionado em uma estação vizinha."""
        estacao_port = 8880 + (estacao - 1)
        try:
            with socket.create_connection((self.station_ip, estacao_port), timeout=1) as sock:
                mensagem = f"CHECK_CAR, {car_id}"
                sock.sendall(mensagem.encode())
                resposta = sock.recv(1024).decode()
                return resposta
        except (ConnectionRefusedError, socket.timeout, socket.error):
            pass
        return "NAO_ENCONTRADO"

    def monitor_stations(self):
        """Monitora as estações vizinhas periodicamente."""
        while self.running:
            time.sleep(5)
            estacoes_ativas_anteriores = set(self.active_stations.keys())
            estacoes_ativas = self.pingar_estacoes_vizinhas()
            estacoes_falhas = estacoes_ativas_anteriores - set(estacoes_ativas)
            if estacoes_falhas:
                for estacao_falha in estacoes_falhas:
                    if estacao_falha not in self.processed_failed_stations:
                        print(f"Estação {estacao_falha} falhou. Iniciando eleição para redistribuição de vagas.")
                        self.processed_failed_stations.add(estacao_falha)
                        self.eleicao_estacao_falha(estacao_falha)

    def eleicao_estacao_falha(self, estacao_falha):
        """Realiza a eleição para redistribuir as vagas da estação falha."""
        # Remove a estação falha das estações ativas
        if estacao_falha in self.active_stations:
            del self.active_stations[estacao_falha]
        else:
            return

        # Obter a lista atualizada de estações ativas (incluindo self)
        estacoes_ativas = list(self.active_stations.keys())
        estacoes_ativas.append(self.station_number)

        self.redistribuir_vagas(estacoes_ativas)

    def desligar_estacao(self):
        """Desliga a estação."""
        self.is_active = False
        self.running = False
        # Informa as outras estações sobre o desligamento
        self.informar_desligamento()
        self.server_socket.close()
        print(f"Estação {self.station_number} foi desligada.")

    def informar_desligamento(self):
        """Informa as estações vizinhas sobre o desligamento."""
        for neighbor in self.neighbors:
            neighbor_port = self.neighbor_ports[neighbor]
            try:
                with socket.create_connection((self.station_ip, neighbor_port), timeout=1) as sock:
                    mensagem = f"STATION_DOWN, {self.station_number}"
                    sock.sendall(mensagem.encode())
            except (ConnectionRefusedError, socket.timeout, socket.error):
                pass

    def __del__(self):
        if self.running:
            self.desligar_estacao()


if __name__ == "__main__":
    try:
        station_number = int(input("Digite o número da estação (1-10): "))
        if not (1 <= station_number <= 10):
            print("Erro: O número da estação deve ser entre 1 e 10.")
            exit(1)
    except ValueError:
        print("Erro: Por favor, digite um número válido para a estação.")
        exit(1)

    neighbors = [n for n in range(1, 11) if n != station_number]
    middleware = Middleware(station_number, neighbors)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando middleware...")
