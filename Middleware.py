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
        threading.Thread(target=self.pingar_estacoes_vizinhas, daemon=True).start()

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

        if code == "RV":
            car_id = parts[1]
            return self.allocate_vaga(car_id)
        elif code == "LV":
            car_id = parts[1]
            return self.release_vaga(car_id)
        elif code == "AE":
            return self.activate_station()
        elif code == "STATUS":
            return f"ATIVA, {self.total_vagas}, {self.get_vagas_livres()}"
        elif code == "V":
            return self.mostrar_vagas()

    def mostrar_vagas(self):
        """Retorna o número total de vagas, vagas ocupadas e vagas livres na estação."""
        vagas_ocupadas = len([vaga for vaga in self.vagas_controladas if vaga is not None])
        vagas_livres = self.get_vagas_livres()
        response = f"Estação {self.station_port}: Total de vagas: {self.total_vagas}, Ocupadas: {vagas_ocupadas}, Livres: {vagas_livres}"
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
        estacoes_ativas.append(self.station_port)  # Adiciona a própria estação como ativa
        self.redistribuir_vagas(estacoes_ativas)

        return "Estação ativada."

    def redistribuir_vagas(self, estacoes_ativas):
        """Redistribui as vagas entre todas as estações ativas."""
        total_estacoes_ativas = len(estacoes_ativas)
        vagas_por_estacao = Middleware.total_vagas_global // total_estacoes_ativas
        restante = Middleware.total_vagas_global % total_estacoes_ativas

        for i, estacao in enumerate(estacoes_ativas):
            if estacao == self.station_port:
                self.total_vagas = vagas_por_estacao + (1 if i < restante else 0)
                self.vagas_controladas = [None] * self.total_vagas
            else:
                self.comunicar_vizinho_redistribuicao(estacao, vagas_por_estacao + (1 if i < restante else 0))

    def comunicar_vizinho_redistribuicao(self, neighbor, vagas_redistribuidas):
        """Envia uma mensagem para as estações vizinhas redistribuírem suas vagas."""
        try:
            with socket.create_connection((self.station_ip, neighbor), timeout=5) as sock:
                mensagem = f"REDISTRIBUIR, {vagas_redistribuidas}"
                sock.sendall(mensagem.encode())
        except (ConnectionRefusedError, socket.timeout):
            pass

    def pingar_estacoes_vizinhas(self):
        """Verifica regularmente quais estações vizinhas estão ativas e retorna as ativas."""
        estacoes_ativas = []
        for neighbor in self.neighbors:
            resposta = self.ping_estacao(neighbor)
            if resposta:
                status, total_vagas, vagas_livres = resposta
                if status == "ATIVA":
                    estacoes_ativas.append(neighbor)
        return estacoes_ativas

    def ping_estacao(self, porta):
        """Tenta conectar-se a uma estação vizinha e verifica seu status."""
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
