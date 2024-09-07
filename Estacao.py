import socket
import threading

class Estacao:
    max_vagas = 10
    def __init__(self, ip, port, portas_vizinhas):
        self.ip = ip
        self.port = port
        self.monitorIp = "127.0.0.1"
        self.monitorPort = 8000
        self.valor_predefinido_vagas = 10
        self.vagas = [False] * Estacao.max_vagas
        self.vagas_totais = 0
        self.vagas_livres = 0
        self.vizinhas_ativas = 0
        self.ativa = False  # Estado inicial dormente
        self.portas_vizinhas = portas_vizinhas  # Portas das estações vizinhas
        self.status_vizinhas = {porta: "Inativa" for porta in portas_vizinhas}

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)

        threading.Thread(target=self.run_server, daemon=True).start()
        threading.Thread(target=self.pingar_estacoes_vizinhas, daemon=True).start()
        threading.Thread(target=self.enviar_status_para_monitor, daemon=True).start()

        self.exibir_status_console()

    def run_server(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                if data == "STATUS":
                    if self.ativa:
                        total_vagas = len(self.vagas)
                        vagas_livres = self.vagas.count(False)
                        resposta = f"ATIVA, {total_vagas}, {vagas_livres}"
                        client_socket.send(resposta.encode())
                    else:
                        client_socket.send("DORMENTE".encode())
                elif data.startswith("UPDATE_VAGAS"):
                    _, vagas_totais = data.split(", ")
                    self.vagas_totais = int(vagas_totais)
                    self.vagas_livres = self.vagas_totais - sum(1 for vaga in self.vagas if vaga)
                    self.exibir_status_console()
                elif self.ativa:
                    if data == "RV":  # Requisição de Vaga
                        self.processar_requisicao_vaga(client_socket)
                elif data == "AE":
                    self.ativar_estacao()
        finally:
            client_socket.close()

    def enviar_status_para_monitor(self):
        while True:
            try:
                with socket.create_connection((self.monitorIp, self.monitorPort), timeout=5) as sock:
                    status = "Ativa" if self.ativa else "Dormente"
                    mensagem = f"Porta: {self.port}, Status: {status}, Vagas Totais: {self.vagas_totais}, Vagas Livres: {self.vagas_livres}"
                    sock.sendall(mensagem.encode())
            except (ConnectionRefusedError, socket.timeout, socket.error):
                pass
            threading.Event().wait(5)

    def processar_requisicao_vaga(self, client_socket):
        vaga_alocada = False
        for i in range(len(self.vagas)):
            if not self.vagas[i]:
                self.vagas[i] = True
                vaga_alocada = True
                self.exibir_status_console()
                client_socket.send(f"Vaga {i+1} alocada".encode())
                break
        if not vaga_alocada:
            client_socket.send("Sem vagas disponíveis".encode())

    def pingar_estacoes_vizinhas(self):
        while True:
            for porta in self.portas_vizinhas:
                resposta = self.ping_estacao(porta)
                if resposta:
                    status, total_vagas, vagas_livres = resposta
                    self.status_vizinhas[porta] = (status, total_vagas, vagas_livres)
                    self.vizinhas_ativas += 1
                else:
                    self.status_vizinhas[porta] = ("Inativa", "N/A", "N/A")
            self.exibir_status_console()
            threading.Event().wait(2)

    def ping_estacao(self, porta):
        try:
            with socket.create_connection((self.ip, porta), timeout=5) as sock:
                sock.sendall("STATUS".encode())
                resposta = sock.recv(1024).decode()
            if resposta.startswith("ATIVA"):
                partes = resposta.split(", ")
                status = "Ativa"
                total_vagas = partes[1]
                vagas_livres = partes[2]
                return (status, total_vagas, vagas_livres)
            else:
                return ("Inativa", "N/A", "N/A")
        except (ConnectionRefusedError, socket.timeout, socket.error):
            return ("Inativa", "N/A", "N/A")

    def ativar_estacao(self):
        self.ativa = not self.ativa
        if self.ativa:
            self.redistribuir_vagas()
        else:
            self.vagas_totais = 0
            self.vagas_livres = 0
        estado = "ativada" if self.ativa else "desativada"
        print(f"Estação {estado}")
        self.exibir_status_console()

    def redistribuir_vagas(self):
        estacoes_ativas = [porta for porta, (status, _, _) in self.status_vizinhas.items() if status == "Ativa"]

        if estacoes_ativas:
            total_vagas_disponiveis = sum(int(status[1]) for status in self.status_vizinhas.values() if status[0] == "Ativa")
            num_estacoes_ativas = len(estacoes_ativas)
            vagas_por_estacao = total_vagas_disponiveis // num_estacoes_ativas
            vagas_resto = total_vagas_disponiveis % num_estacoes_ativas

            for porta in estacoes_ativas:
                total_vagas = vagas_por_estacao
                if vagas_resto > 0:
                    total_vagas += 1
                    vagas_resto -= 1
                self.atualizar_vagas_estacao(porta, total_vagas)

            self.vagas_totais = vagas_por_estacao + (1 if vagas_resto > 0 else 0)
            self.vagas_livres = self.vagas_totais - sum(1 for vaga in self.vagas if vaga)
        else:
            self.vagas_totais = self.valor_predefinido_vagas
            self.vagas_livres = self.valor_predefinido_vagas

        self.exibir_status_console()

    def atualizar_vagas_estacao(self, porta, vagas_totais):
        try:
            with socket.create_connection((self.ip, porta), timeout=5) as sock:
                mensagem = f"UPDATE_VAGAS, {vagas_totais}"
                sock.sendall(mensagem.encode())
        except (ConnectionRefusedError, socket.timeout, socket.error):
            print(f"Falha ao atualizar a estação na porta {porta}")

    def exibir_status_console(self):
        print(f"\nStatus da Estação (Porta: {self.port})")
        print(f"Ativa: {self.ativa}")
        print(f"Vagas Totais: {self.vagas_totais}")
        print(f"Vagas Livres: {self.vagas_livres}")
        print(f"Vizinhas Ativas: {self.vizinhas_ativas}")
        for port, status in self.status_vizinhas.items():
            print(f"Estação {port}: {status[0]}, Vagas Totais: {status[1]}, Vagas Livres: {status[2]}")

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = int(input("Digite a porta para esta estação: "))
    portas_vizinhas = list(map(int, input("Digite as portas das estações vizinhas (separadas por espaço): ").split()))
    estacao = Estacao(ip, port, portas_vizinhas)
