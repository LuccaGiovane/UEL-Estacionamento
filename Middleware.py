import socket
import threading


class Middleware:
    total_vagas_global = 100  # O total de vagas do estacionamento

    def __init__(self, station_port, neighbors):
        self.station_ip = "127.0.0.1"
        self.station_port = station_port
        self.neighbors = neighbors
        self.active_stations = {neighbor: False for neighbor in neighbors}
        self.total_vagas = 0  # Inicialmente, a estação não controla vagas
        self.vagas_controladas = []  # Lista para controlar as vagas alocadas a esta estação
        self.carros = {}
        self.is_active = False  # Estado inicial da estação (inativa)

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.station_ip, self.station_port))
            self.server_socket.listen(2)
            print(f"Estação iniciada na porta {station_port}, aguardando conexões...")
        except socket.error as e:
            print(f"Erro ao iniciar o socket na porta {station_port}: {e}")
            return

        threading.Thread(target=self.run_server, daemon=True).start()

    def run_server(self):
        while True:
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
            while True:
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
        parts = message.split(", ")
        code = parts[0]

        if code == "RV":  # Requisitar vaga
            car_id = parts[1]
            return self.allocate_vaga(car_id)
        elif code == "LV":  # Liberar vaga
            car_id = parts[1]
            return self.release_vaga(car_id)
        elif code == "AE":  # Ativar estação
            print(f"Ativando estação {self.station_port}...")
            return self.activate_station()
        elif code == "STATUS":
            if self.is_active:
                return f"ATIVA, {self.total_vagas}, {self.get_vagas_livres()}"
            else:
                return "INATIVA"
        elif code == "V":  # Mostrar vagas disponíveis
            return self.mostrar_vagas()
        elif code == "UPDATE_VAGAS":
            vagas = int(parts[1])
            new_station_port = int(parts[2])
            print(f"Debug: Atualizando vagas da estação {self.station_port} para {vagas} vagas.")
            # Mantém apenas as vagas ocupadas dentro do novo limite
            occupied_vagas = [vaga for vaga in self.vagas_controladas if vaga is not None]
            if len(occupied_vagas) > vagas:
                # Existem carros excedentes
                excess_cars = occupied_vagas[vagas:]
                occupied_vagas = occupied_vagas[:vagas]
            else:
                excess_cars = []
            # Atualiza vagas_controladas
            self.vagas_controladas = occupied_vagas + [None] * (vagas - len(occupied_vagas))
            self.total_vagas = vagas
            # Reconstrói self.carros
            self.carros = {car_id: idx for idx, car_id in enumerate(self.vagas_controladas) if car_id is not None}
            # Lida com os carros excedentes
            if excess_cars:
                print(f"Estação {self.station_port} tem {len(excess_cars)} carros excedentes após a redução de vagas.")
                for car_id in excess_cars:
                    print(f"Transferindo carro {car_id} para estação {new_station_port}.")
                    # Envia mensagem para a nova estação alocar o carro
                    try:
                        with socket.create_connection((self.station_ip, new_station_port), timeout=5) as sock:
                            mensagem = f"ALLOCATE_CAR, {car_id}"
                            sock.sendall(mensagem.encode())
                            print(f"Enviando carro {car_id} para alocação na estação {new_station_port}.")
                    except (ConnectionRefusedError, socket.timeout, socket.error):
                        print(f"Erro ao conectar com a estação {new_station_port} para transferir o carro {car_id}.")
            else:
                print(f"Estação {self.station_port} não possui carros excedentes após a redução de vagas.")
        elif code == "ALLOCATE_CAR":
            car_id = parts[1]
            response = self.allocate_vaga(car_id)
            print(f"Carro {car_id} transferido para estação {self.station_port}.")
            return response
        elif code == "CHECK_CAR":
            car_id = parts[1]
            if car_id in self.carros:
                return "ENCONTRADO"
            else:
                return "NAO_ENCONTRADO"

    def mostrar_vagas(self):
        vagas_ocupadas = len([vaga for vaga in self.vagas_controladas if vaga is not None])
        vagas_livres = self.get_vagas_livres()
        response = f"Estação {self.station_port}: Total de vagas: {self.total_vagas}, Ocupadas: {vagas_ocupadas}, Livres: {vagas_livres}"
        print(f"Debug: Estação {self.station_port} tem {self.total_vagas} vagas.")
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
        estacoes_ativas = self.pingar_estacoes_vizinhas()
        if len(estacoes_ativas) == 0:
            # Primeira estação a ser ativada controla todas as vagas
            self.total_vagas = Middleware.total_vagas_global
            self.vagas_controladas = [None] * self.total_vagas
            print(f"Estação {self.station_port} recebeu todas as {self.total_vagas} vagas.")
        else:
            # Redistribuir vagas
            print(f"Redistribuindo vagas entre {len(estacoes_ativas)} estações ativas.")
            self.redistribuir_vagas(estacoes_ativas)
        self.is_active = True  # Marca a estação como ativa
        return "Estação ativada."

    def redistribuir_vagas(self, estacoes_ativas):
        """Redistribui as vagas corretamente."""
        estacao_com_mais_vagas = max(estacoes_ativas, key=lambda estacao: self.get_vagas_estacao(estacao))
        print(f"Estação com mais vagas: {estacao_com_mais_vagas}")
        total_vagas_estacao = self.get_vagas_estacao(estacao_com_mais_vagas)
        vagas_livres_estacao = self.get_vagas_livres_estacao(estacao_com_mais_vagas)
        vagas_ocupadas_estacao = total_vagas_estacao - vagas_livres_estacao
        vagas_a_serem_doadas = total_vagas_estacao // 2
        print(f"Vagas a serem doadas pela estação {estacao_com_mais_vagas}: {vagas_a_serem_doadas}")

        # Atualiza a estação que vai doar as vagas
        self.update_vagas(estacao_com_mais_vagas, total_vagas_estacao - vagas_a_serem_doadas, self.station_port)

        # Atualiza a estação que está herdando as vagas
        self.total_vagas = vagas_a_serem_doadas
        self.vagas_controladas = [None] * self.total_vagas
        print(f"Estação {self.station_port} recebeu {self.total_vagas} vagas.")

    def update_vagas(self, estacao, vagas_restantes, new_station_port):
        """Atualiza a quantidade de vagas da estação que doou as vagas."""
        try:
            # Envia uma mensagem para a estação doadora com o número de vagas restantes e a porta da nova estação
            with socket.create_connection((self.station_ip, estacao), timeout=5) as sock:
                mensagem = f"UPDATE_VAGAS, {vagas_restantes}, {new_station_port}"
                sock.sendall(mensagem.encode())
                print(f"Atualizando a estação {estacao} para {vagas_restantes} vagas restantes.")
        except (ConnectionRefusedError, socket.timeout):
            pass

    def pingar_estacoes_vizinhas(self):
        estacoes_ativas = []
        for neighbor in self.neighbors:
            resposta = self.ping_estacao(neighbor)
            if resposta:
                status, total_vagas, vagas_livres = resposta
                if status == "ATIVA":
                    estacoes_ativas.append(neighbor)
        return estacoes_ativas

    def ping_estacao(self, porta):
        try:
            with socket.create_connection((self.station_ip, porta), timeout=5) as sock:
                sock.sendall("STATUS".encode())
                resposta = sock.recv(1024).decode()
            if resposta.startswith("ATIVA"):
                partes = resposta.split(", ")
                status = partes[0]
                total_vagas = partes[1]
                vagas_livres = partes[2]
                return (status, int(total_vagas), int(vagas_livres))
            else:
                return None
        except (ConnectionRefusedError, socket.timeout, socket.error):
            return None

    def get_vagas_estacao(self, estacao):
        """Consulta a quantidade de vagas de uma estação vizinha."""
        try:
            with socket.create_connection((self.station_ip, estacao), timeout=5) as sock:
                sock.sendall("STATUS".encode())
                resposta = sock.recv(1024).decode()
                if resposta.startswith("ATIVA"):
                    partes = resposta.split(", ")
                    return int(partes[1])  # Total de vagas
        except (ConnectionRefusedError, socket.timeout, socket.error):
            pass
        return 0

    def get_vagas_livres_estacao(self, estacao):
        """Consulta o número de vagas livres de uma estação vizinha."""
        try:
            with socket.create_connection((self.station_ip, estacao), timeout=5) as sock:
                sock.sendall("STATUS".encode())
                resposta = sock.recv(1024).decode()
                if resposta.startswith("ATIVA"):
                    partes = resposta.split(", ")
                    vagas_livres = int(partes[2])
                    return vagas_livres
        except (ConnectionRefusedError, socket.timeout, socket.error):
            pass
        return 0

    def get_vagas_livres(self):
        """Calcula o número de vagas livres."""
        return len([vaga for vaga in self.vagas_controladas if vaga is None])

    def consulta_carro_vizinha(self, car_id, estacao):
        """Consulta se um carro está estacionado em uma estação vizinha."""
        try:
            with socket.create_connection((self.station_ip, estacao), timeout=5) as sock:
                mensagem = f"CHECK_CAR, {car_id}"
                sock.sendall(mensagem.encode())
                resposta = sock.recv(1024).decode()
                return resposta
        except (ConnectionRefusedError, socket.timeout, socket.error):
            pass
        return "NAO_ENCONTRADO"


if __name__ == "__main__":
    try:
        station_port = int(input("Digite a porta para esta estação: "))
    except ValueError:
        print("Erro: Por favor, digite um número válido para a porta.")
        exit(1)

    neighbors = [port for port in range(8880, 8891) if port != station_port]
    middleware = Middleware(station_port, neighbors)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Encerrando middleware...")
