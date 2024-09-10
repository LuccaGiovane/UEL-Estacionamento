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
            return f"ATIVA, {self.total_vagas}, {self.get_vagas_livres()}"
        elif code == "V":  # Mostrar vagas disponíveis
            return self.mostrar_vagas()

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
                response = f"Vaga {i+1} alocada para carro {car_id}."
                return response

        return "Sem vagas disponíveis"

    def release_vaga(self, car_id):
        if car_id in self.carros:
            vaga_index = self.carros[car_id]
            self.vagas_controladas[vaga_index] = None
            del self.carros[car_id]
            response = f"Carro {car_id} liberou a vaga {vaga_index+1}"
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
        return "Estação ativada."

    def redistribuir_vagas(self, estacoes_ativas):
        """Redistribui as vagas corretamente."""
        estacao_com_mais_vagas = max(estacoes_ativas, key=lambda estacao: self.get_vagas_estacao(estacao))
        print(f"Estação com mais vagas: {estacao_com_mais_vagas}")
        vagas_a_serem_doadas = self.get_vagas_estacao(estacao_com_mais_vagas) // 2

        # Atualiza a estação que vai doar as vagas
        self.atualizar_estacao_vagas(estacao_com_mais_vagas, vagas_a_serem_doadas)

        # Atualiza a estação que está herdando as vagas
        self.total_vagas = vagas_a_serem_doadas
        self.vagas_controladas = [None] * self.total_vagas
        print(f"Estação {self.station_port} recebeu {self.total_vagas} vagas.")

    def atualizar_estacao_vagas(self, estacao, vagas_a_serem_doadas):
        """Atualiza a quantidade de vagas da estação que doou as vagas."""
        try:
            with socket.create_connection((self.station_ip, estacao), timeout=5) as sock:
                mensagem = f"ATUALIZAR_VAGAS, {vagas_a_serem_doadas}"
                sock.sendall(mensagem.encode())
                print(f"Atualizando estação {estacao} para {vagas_a_serem_doadas} vagas doadas.")
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
                return (status, total_vagas, vagas_livres)
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

    def get_vagas_livres(self):
        """Calcula o número de vagas livres."""
        return len([vaga for vaga in self.vagas_controladas if vaga is None])

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
