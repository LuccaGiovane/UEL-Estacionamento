import socket
import threading

class Monitor:
    def __init__(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", int(port)))
        self.server_socket.listen(5)
        print(f"Monitor ouvindo na porta {port}...")

        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            client_socket, _ = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        while True:
            try:
                mensagem = client_socket.recv(1024).decode()
                if not mensagem:
                    break
                self.exibir_status_estacao(mensagem)
            except (ConnectionResetError, socket.error):
                break
        client_socket.close()

    def exibir_status_estacao(self, mensagem):
        partes = mensagem.split(", ")
        if len(partes) == 4:
            port, status, vagas_totais, vagas_livres = partes
            print(f"Estação na porta {port}: Status: {status}, Vagas Totais: {vagas_totais}, Vagas Disponíveis: {vagas_livres}")

if __name__ == "__main__":
    port = int(input("Digite a porta para o monitor: "))
    monitor = Monitor(port)
