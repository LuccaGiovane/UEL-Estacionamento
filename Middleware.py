import socket
import threading

class Middleware:
    def __init__(self, station_port, neighbors):
        self.station_ip = "127.0.0.1"
        self.station_port = station_port
        self.neighbors = neighbors
        self.total_vagas = 10  # Cada estação tem 10 vagas fixas
        self.vagas_controladas = [None] * self.total_vagas  # Inicializa todas as vagas como livres (None)
        self.carros = {}  # Armazena os carros alocados em suas respectivas vagas

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.station_ip, self.station_port))
            self.server_socket.listen(2)  # Limitar a 2 conexões simultâneas
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

                client_socket.settimeout(5)  # Timeout para encerrar conexões inativas após 5 segundos
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
            return self.activate_station()
        elif code == "STATUS":
            return f"ATIVA, {self.total_vagas}, {self.get_vagas_livres()}"
        elif code == "V":  # Mostrar vagas disponíveis
            return self.mostrar_vagas()
        elif code == "CONSULTA_CARRO":  # Verificar se o carro está nesta estação
            car_id = parts[1]
            return self.consulta_carro(car_id)

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
            # Se o carro não está nesta estação, consultar vizinhos
            for neighbor in self.neighbors:
                resposta = self.consulta_carro_vizinha(car_id, neighbor)
                if resposta == "ENCONTRADO":
                    return f"Carro {car_id} liberado na estação {neighbor}"
            return f"Carro {car_id} não foi encontrado."

    def consulta_carro(self, car_id):
        """Verifica se o carro está nesta estação."""
        if car_id in self.carros:
            return "ENCONTRADO"
        return "NAO_ENCONTRADO"

    def consulta_carro_vizinha(self, car_id, neighbor_port):
        """Consulta uma estação vizinha para verificar se o carro está alocado lá."""
        try:
            with socket.create_connection((self.station_ip, neighbor_port), timeout=5) as sock:
                mensagem = f"CONSULTA_CARRO, {car_id}"
                sock.sendall(mensagem.encode())
                resposta = sock.recv(1024).decode()
                return resposta
        except (ConnectionRefusedError, socket.timeout):
            return "NAO_ENCONTRADO"

    def activate_station(self):
        return "Estação ativada."

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
