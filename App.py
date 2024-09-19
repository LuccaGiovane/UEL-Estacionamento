import socket

class App:
    def __init__(self, middleware_ports=None):
        print("Iniciando App...")
        self.middleware_ip = "127.0.0.1"
        self.middleware_ports = middleware_ports if middleware_ports else {}
        self.car_id_counter = 1

    def activate_station(self, station_number):
        if station_number not in self.middleware_ports:
            print(f"Erro: Estação {station_number} não existe.")
            return

        try:
            port = self.middleware_ports[station_number]
            with socket.create_connection((self.middleware_ip, port), timeout=5) as sock:
                message = "AE"
                sock.sendall(message.encode())
                response = sock.recv(1024).decode()
                print(f"Estação {station_number} ativada: {response}")
        except (ConnectionRefusedError, socket.timeout, socket.error) as e:
            print(f"Erro ao ativar estação {station_number}: {e}")

    def desligar_estacao(self, station_number):
        if station_number not in self.middleware_ports:
            print(f"Erro: Estação {station_number} não existe.")
            return

        try:
            port = self.middleware_ports[station_number]
            with socket.create_connection((self.middleware_ip, port), timeout=5) as sock:
                message = "DE"
                sock.sendall(message.encode())
                response = sock.recv(1024).decode()
                print(f"Estação {station_number} desligada: {response}")
        except (ConnectionRefusedError, socket.timeout, socket.error) as e:
            print(f"Erro ao desligar estação {station_number}: {e}")

    def request_vaga(self, car_id, station_number):
        if station_number not in self.middleware_ports:
            print(f"Erro: Estação {station_number} não existe.")
            return

        try:
            port = self.middleware_ports[station_number]
            with socket.create_connection((self.middleware_ip, port), timeout=5) as sock:
                message = f"RV, {car_id}"
                sock.sendall(message.encode())
                response = sock.recv(1024).decode()
                print(f"Resposta da estação {station_number} para o carro {car_id}: {response}")
        except (ConnectionRefusedError, socket.timeout, socket.error) as e:
            print(f"Erro ao requisitar vaga na estação {station_number}: {e}")

    def liberar_vaga(self, car_id, station_number):
        if station_number not in self.middleware_ports:
            print(f"Erro: Estação {station_number} não existe.")
            return

        try:
            port = self.middleware_ports[station_number]
            with socket.create_connection((self.middleware_ip, port), timeout=5) as sock:
                message = f"LV, {car_id}"
                sock.sendall(message.encode())
                response = sock.recv(1024).decode()
                print(f"Resposta da estação {station_number} para o carro {car_id}: {response}")
        except (ConnectionRefusedError, socket.timeout, socket.error) as e:
            print(f"Erro ao liberar vaga na estação {station_number}: {e}")

    def mostrar_vagas(self, station_number):
        if station_number not in self.middleware_ports:
            print(f"Erro: Estação {station_number} não existe.")
            return

        try:
            port = self.middleware_ports[station_number]
            with socket.create_connection((self.middleware_ip, port), timeout=5) as sock:
                message = "V"
                sock.sendall(message.encode())
                response = sock.recv(1024).decode()
                print(f"Vagas na estação {station_number}: {response}")
        except (ConnectionRefusedError, socket.timeout, socket.error) as e:
            print(f"Erro ao obter vagas na estação {station_number}: {e}")

    def handle_input(self):
        while True:
            command = input(
                "Digite um comando (AE <número> ou DE <número> ou RV <carro_id> <número> ou LV <carro_id> <número> ou V <número>): ").strip()
            parts = command.split()

            if len(parts) == 2 and parts[0] == "AE":
                station_number = int(parts[1])
                self.activate_station(station_number)
            elif len(parts) == 2 and parts[0] == "DE":
                station_number = int(parts[1])
                self.desligar_estacao(station_number)
            elif len(parts) == 3 and parts[0] == "RV":
                car_id = parts[1]
                station_number = int(parts[2])
                self.request_vaga(car_id, station_number)
            elif len(parts) == 3 and parts[0] == "LV":
                car_id = parts[1]
                station_number = int(parts[2])
                self.liberar_vaga(car_id, station_number)
            elif len(parts) == 2 and parts[0] == "V":
                station_number = int(parts[1])
                self.mostrar_vagas(station_number)
            else:
                print(
                    "Comando inválido. Tente AE <número_da_estação>, DE <número_da_estação>, RV <carro_id> <número_da_estação>, LV <carro_id> <número_da_estação> ou V <número_da_estação>.")


if __name__ == "__main__":
    print("App iniciado. Aguardando comandos...")
    # Configurações de portas para as estações
    middleware_ports = {
        1: 8880,
        2: 8881,
        3: 8882,
        4: 8883,
        5: 8884,
        6: 8885,
        7: 8886,
        8: 8887,
        9: 8888,
        10: 8889
    }

    app = App(middleware_ports)
    app.handle_input()
