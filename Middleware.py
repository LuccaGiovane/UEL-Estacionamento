
import socket
import threading
import time
import argparse

from collections import deque


class Middleware:
    total_vagas_global = 100  # O total de vagas do estacionamento

    def __init__(self, station_number, neighbors):
        '''Inicializa a instância da classe Middleware com o número da estação e seus vizinhos.'''
        self.station_number = station_number
        self.station_port = 8880 + (station_number - 1)  # Define a porta da estação com base no número
        self.station_ip = "127.0.0.1"  # IP local
        self.rv_queue = deque()
        self.lv_queue = deque()
        self.neighbors = neighbors  # Lista de estações vizinhas
        self.neighbor_ports = {neighbor: 8880 + (neighbor - 1) for neighbor in neighbors}  # Portas das estações vizinhas
        self.active_stations = {}  # Dicionário para armazenar estações ativas
        self.total_vagas = 0  # Inicialmente, a estação não controla vagas
        self.vagas_controladas = []  # Lista para controlar as vagas alocadas a esta estação
        self.carros = {}  # Dicionário para mapear carros às vagas
        self.is_active = False  # Estado inicial da estação (inativa)
        self.running = True  # Controla se a estação está rodando
        self.processed_failed_stations = set()  # Para evitar processar falhas múltiplas vezes

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.station_ip, self.station_port))
            self.server_socket.listen(5)  # Define a fila de conexões
            print(f"Estação {self.station_number} iniciada na porta {self.station_port}, aguardando conexões...")
        except socket.error as e:
            print(f"Erro ao iniciar o socket na porta {self.station_port}: {e}")
            return

        # Inicia a thread do servidor
        threading.Thread(target=self.run_server, daemon=True).start()
        # Inicia a thread para monitorar as estações
        threading.Thread(target=self.monitor_stations, daemon=True).start()
        # Inicia a thread que processa as requisições de vaga
        threading.Thread(target=self.processar_requisicoes_vaga, daemon=True).start()

    def run_server(self):
        '''Executa o servidor que aceita conexões de clientes e trata cada conexão em uma nova thread.'''
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()

                # Aceitar apenas conexões de localhost
                if addr[0] != "127.0.0.1":
                    client_socket.close()
                    continue

                client_socket.settimeout(5)  # Define timeout para a conexão
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except socket.error as e:
                pass  # Ignora erros de socket temporários

    def handle_client(self, client_socket):
        """Lida com a comunicação com um cliente conectado, processando mensagens recebidas."""
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
                    break  # Sai do loop se o socket der timeout
        finally:
            client_socket.close()  # Fecha a conexão com o cliente

    def processar_requisicoes_vaga(self):
        '''Thread responsável por processar as requisições de vaga da fila.'''
        while self.running:
            try:
                if self.rv_queue:
                    car_id = self.rv_queue.popleft()  # Pega a próxima requisição (timeout de 1 segundo)
                    vaga_alocada = self.allocate_vaga(car_id)
                    if vaga_alocada:
                        print(f"Carro {car_id} alocado na vaga {vaga_alocada} pela estação {self.station_number}.")
                    else:
                        print(f"Estação {self.station_number}: Nenhuma vaga disponível para o carro {car_id}.")
                        self.rv_queue.appendleft(car_id)
                else:
                    continue
            except Exception as e:
                print(f"Erro ao processar requisição de vaga: {e}")
            continue

    def process_message(self, message):
        '''Processa uma mensagem recebida e executa a ação correspondente.'''
        parts = message.strip().split(".")
        code = parts[0]

        if code == "RV":  # Requisitar vaga
            car_id = parts[1]
            print(f"Requisição de vaga recebida para o carro {car_id}. Adicionando à fila.")
            self.rv_queue.append(car_id)
            return "Carro Adicionado a fila"
            #return self.allocate_vaga(car_id)
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
            response = self.allocate_vaga(car_id, force=True)
            print(f"Carro {car_id} transferido para estação {self.station_number}.")
            return response
        elif code == "ALLOCATE_CARS":
            carros_str = parts[1]
            carros = carros_str.split(";")
            for car_id in carros:
                self.allocate_vaga(car_id, force=True)
            print(f"Carros {carros} transferidos para estação {self.station_number}.")
            return "Carros alocados."
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
            carros_estacao_falha = []
            if len(parts) > 2:
                carros_str = parts[2]
                if carros_str:
                    carros_estacao_falha = carros_str.split(";")
            print(f"Estação {estacao_desligada} desligou. Iniciando eleição para redistribuição de vagas.")
            if estacao_desligada not in self.processed_failed_stations:
                self.processed_failed_stations.add(estacao_desligada)
                # Remover a estação falha antes de criar estacoes_ativas
                if estacao_desligada in self.active_stations:
                    del self.active_stations[estacao_desligada]

                estacoes_ativas = list(self.active_stations.keys())
                estacoes_ativas.append(self.station_number)
                coordenador = min(estacoes_ativas)
                if self.station_number == coordenador:
                    # Apenas o coordenador processa a redistribuição
                    self.eleicao_estacao_falha(estacao_desligada, carros_estacao_falha)
                else:
                    # Outras estações apenas atualizam suas vagas
                    self.redistribuir_vagas(estacoes_ativas)
        elif code == "GET_CARROS":
            carros_list = list(self.carros.keys())
            response = ", ".join(carros_list)
            return response
        else:
            return "Comando desconhecido"

    def mostrar_vagas(self):
        '''Exibe o número total de vagas, vagas ocupadas e vagas livres da estação.'''
        vagas_ocupadas = len([vaga for vaga in self.vagas_controladas if vaga is not None])
        vagas_livres = self.get_vagas_livres()
        response = f"Estação {self.station_number}: Total de vagas: {self.total_vagas}, Ocupadas: {vagas_ocupadas}, Livres: {vagas_livres}"
        #print(f"Debug: Estação {self.station_number} tem {self.total_vagas} vagas.")
        return response

    def allocate_vaga(self, car_id, force=False):
        '''Aloca uma vaga para um carro específico, podendo forçar a alocação se necessário.'''
        if not force and car_id in self.carros:
            return f"Carro {car_id} já está alocado em uma vaga."

        for i, vaga in enumerate(self.vagas_controladas):
            if vaga is None:
                self.vagas_controladas[i] = car_id
                self.carros[car_id] = i
                response = f"Vaga {i + 1} alocada para carro {car_id}."
                return response

        return "Sem vagas disponíveis"

    def release_vaga(self, car_id):
        '''Libera a vaga ocupada por um carro específico, verificando em vizinhos se necessário.'''
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
                    self.enviar_mensagem_vizinha_liberar_vaga(car_id, neighbor)
                    return f"Carro {car_id} liberado na estação {neighbor}"
            return f"Carro {car_id} não foi encontrado."

    def enviar_mensagem_vizinha_liberar_vaga(self, car_id, neighbor):
        '''Envia uma mensagem à estação vizinha para liberar a vaga do carro.'''
        # Envia uma mensagem para a estação vizinha liberar a vaga
        # A mensagem enviada será do tipo "LV,<car_id>"
        neighbor_port = self.neighbor_ports[neighbor]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.station_ip, neighbor_port))
            s.sendall(f"LV.{car_id}".encode())
            # A estação vizinha receberá a mensagem e atualizará suas vagas
            resposta = s.recv(1024).decode()
            print(f"Resposta da estação vizinha {self.station_number}:{neighbor_port} : {resposta}")

    def activate_station(self):
        '''Ativa a estação, pinge as estações vizinhas e redistribui as vagas entre as ativas.'''
        self.is_active = True  # Marca a estação como ativa
        estacoes_ativas = self.pingar_estacoes_vizinhas()
        estacoes_ativas.append(self.station_number)
        self.redistribuir_vagas(estacoes_ativas)
        return "Estação ativada."

    def redistribuir_vagas(self, estacoes_ativas):
        '''Redistribui as vagas corretamente entre as estações ativas.'''
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
                # Ajusta vagas_controladas mantendo os carros alocados
                occupied_vagas = [vaga for vaga in self.vagas_controladas if vaga is not None]
                self.vagas_controladas = occupied_vagas + [None] * (self.total_vagas - len(occupied_vagas))
                # Atualiza self.carros
                self.carros = {car_id: idx for idx, car_id in enumerate(self.vagas_controladas) if car_id is not None}
                print(f"Estação {self.station_number} recebeu {self.total_vagas} vagas.")
            else:
                # Atualiza a estação remota
                self.update_vagas(estacao, vagas)

    def update_vagas(self, estacao, vagas_novas):
        '''Atualiza a quantidade de vagas da estação especificada.'''
        estacao_port = 8880 + (estacao - 1)
        try:
            with socket.create_connection((self.station_ip, estacao_port), timeout=1) as sock:
                mensagem = f"UPDATE_VAGAS.{vagas_novas}"
                sock.sendall(mensagem.encode())
                print(f"Atualizando a estação {estacao} para {vagas_novas} vagas.")
        except (ConnectionRefusedError, socket.timeout, socket.error):
            pass  # Ignora erros de conexão

    def pingar_estacoes_vizinhas(self):
        '''Pinge as estações vizinhas para verificar quais estão ativas.'''
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
        '''Envia uma mensagem de status para uma estação específica e retorna sua resposta.'''
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
        '''Consulta o número de vagas livres de uma estação vizinha.'''
        if estacao in self.active_stations:
            return self.active_stations[estacao]['vagas_livres']
        else:
            return 0

    def get_vagas_livres(self):
        '''Calcula o número de vagas livres na estação atual.'''
        return len([vaga for vaga in self.vagas_controladas if vaga is None])

    def consulta_carro_vizinha(self, car_id, estacao):
        '''Consulta se um carro está estacionado em uma estação vizinha.'''
        estacao_port = 8880 + (estacao - 1)
        try:
            with socket.create_connection((self.station_ip, estacao_port), timeout=1) as sock:
                mensagem = f"CHECK_CAR.{car_id}"
                sock.sendall(mensagem.encode())
                resposta = sock.recv(1024).decode()
                return resposta
        except (ConnectionRefusedError, socket.timeout, socket.error):
            pass
        return "NAO_ENCONTRADO"

    def monitor_stations(self):
        '''Monitora as estações vizinhas periodicamente para detectar falhas e redistribuir vagas.'''
        while self.running:
            time.sleep(5)  # Intervalo de monitoramento
            estacoes_ativas_anteriores = set(self.active_stations.keys())
            estacoes_ativas = self.pingar_estacoes_vizinhas()
            estacoes_falhas = estacoes_ativas_anteriores - set(estacoes_ativas)
            if estacoes_falhas:
                for estacao_falha in estacoes_falhas:
                    if estacao_falha not in self.processed_failed_stations:
                        print(f"Estação {estacao_falha} falhou. Iniciando eleição para redistribuição de vagas.")
                        self.processed_failed_stations.add(estacao_falha)
                        # Remover a estação falha antes de criar estacoes_ativas
                        if estacao_falha in self.active_stations:
                            del self.active_stations[estacao_falha]

                        estacoes_ativas = list(self.active_stations.keys())
                        estacoes_ativas.append(self.station_number)
                        coordenador = min(estacoes_ativas)
                        if self.station_number == coordenador:
                            # Coordenador processa a redistribuição
                            self.eleicao_estacao_falha(estacao_falha, [])
                        else:
                            # Outras estações apenas atualizam suas vagas
                            self.redistribuir_vagas(estacoes_ativas)

    def eleicao_estacao_falha(self, estacao_falha, carros_estacao_falha):
        '''Realiza a eleição para redistribuir as vagas da estação falha.'''
        print(f"Carros na estação {estacao_falha}: {carros_estacao_falha}")

        # Remove a estação falha das estações ativas
        # Já foi removida antes de chamar este método

        # Obter a lista atualizada de estações ativas (incluindo self)
        estacoes_ativas = list(self.active_stations.keys())
        estacoes_ativas.append(self.station_number)

        self.redistribuir_vagas(estacoes_ativas)

        # Apenas o coordenador redistribui os carros
        self.redistribuir_carros(carros_estacao_falha, estacoes_ativas)

    def redistribuir_carros(self, carros, estacoes_ativas):
        '''Redistribui os carros para uma única estação ativa.'''
        if not carros:
            return

        # Escolhe uma estação para receber todos os carros (por exemplo, a de menor número)
        estacao_destino = min(estacoes_ativas)

        if estacao_destino == self.station_number:
            # A estação atual é a escolhida
            for car_id in carros:
                response = self.allocate_vaga(car_id, force=True)
                if response != "Sem vagas disponíveis":
                    print(f"Carro {car_id} realocado para estação {self.station_number}.")
                else:
                    print(f"Não foi possível realocar o carro {car_id} na estação {self.station_number}.")
        else:
            # Envia todos os carros para a estação destino
            self.alocar_carros_vizinha(carros, estacao_destino)

    def alocar_carros_vizinha(self, carros, estacao):
        '''Aloca carros em uma estação vizinha especificada.'''
        estacao_port = 8880 + (estacao - 1)
        carros_str = ";".join(carros)
        try:
            with socket.create_connection((self.station_ip, estacao_port), timeout=5) as sock:
                mensagem = f"ALLOCATE_CARS.{carros_str}"
                sock.sendall(mensagem.encode())
                resposta = sock.recv(1024).decode()
                if "Carros alocados" in resposta:
                    print(f"Carros {carros} realocados para estação {estacao}.")
                else:
                    print(f"Não foi possível realocar os carros {carros} na estação {estacao}.")
        except (ConnectionRefusedError, socket.timeout, socket.error):
            print(f"Erro ao conectar com a estação {estacao} para realocar carros.")

    def desligar_estacao(self):
        '''Desliga a estação, informando os vizinhos e fechando o socket.'''
        # Informa as outras estações sobre o desligamento
        self.informar_desligamento()
        self.is_active = False
        self.running = False
        self.server_socket.close()
        print(f"Estação {self.station_number} foi desligada.")

    def informar_desligamento(self):
        '''Informa as estações vizinhas sobre o desligamento da estação atual.'''
        carros_list = list(self.carros.keys())
        carros_str = ";".join(carros_list)
        for neighbor in self.neighbors:
            neighbor_port = self.neighbor_ports[neighbor]
            try:
                with socket.create_connection((self.station_ip, neighbor_port), timeout=1) as sock:
                    mensagem = f"STATION_DOWN.{self.station_number}.{carros_str}"
                    sock.sendall(mensagem.encode())
            except (ConnectionRefusedError, socket.timeout, socket.error):
                pass  # Ignora erros de conexão

    def __del__(self):
        '''Desliga a estação ao deletar a instância, se ainda estiver rodando.'''
        if self.running:
            self.desligar_estacao()






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Middleware para estações.')
    parser.add_argument('--station', type=int, help='Número da estação (1-10)', default=None)

    args = parser.parse_args()
    if args.station is not None:
        station_number = args.station
        if not (1 <= station_number <= 10):
            print("Erro: O número da estação deve ser entre 1 e 10.")
            exit(1)
    else:
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
        middleware.desligar_estacao()
