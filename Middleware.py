class Middleware:
    def __init__(self, id_middleware, ip, port):
        self.id_middleware = id_middleware
        self.ip = ip
        self.port = port
        self.vagas = {}  # Vagas gerenciadas localmente
        self.outras_estacoes = []  # Lista de outros middlewares conectados
        self.lider = None  # ID do middleware líder

    def solicitar_ocupacao_vaga(self, vaga_id):
        if vaga_id in self.vagas:
            if self.vagas[vaga_id] == 'livre':
                self.vagas[vaga_id] = 'ocupada'
                self.notificar_mudanca(vaga_id, 'ocupada')
            else:
                # Se não houver vagas locais disponíveis, solicitar de outra estação
                vaga = self.solicitar_vaga_de_outra_estacao()
                if vaga:
                    self.vagas[vaga_id] = 'ocupada'
                    self.notificar_mudanca(vaga_id, 'ocupada')
        else:
            # Se a vaga não for local, solicitar ao middleware apropriado
            self.redirecionar_solicitacao(vaga_id, 'ocupacao')

    def solicitar_liberacao_vaga(self, vaga_id):
        if vaga_id in self.vagas:
            self.vagas[vaga_id] = 'livre'
            self.notificar_mudanca(vaga_id, 'livre')
        else:
            self.redirecionar_solicitacao(vaga_id, 'liberacao')

    def solicitar_status_vagas(self):
        return self.vagas

    def notificar_mudanca(self, vaga_id, status):
        # Notifica outros middlewares sobre a mudança de status
        mensagem = f"MUDANCA:{vaga_id}:{status}"
        self.enviar_para_todos(mensagem)

    def redirecionar_solicitacao(self, vaga_id, tipo_solicitacao):
        # Encaminha a solicitação para o middleware que controla a vaga
        for estacao in self.outras_estacoes:
            if estacao.gerencia_vaga(vaga_id):
                if tipo_solicitacao == 'ocupacao':
                    estacao.ocupar_vaga(vaga_id)
                elif tipo_solicitacao == 'liberacao':
                    estacao.liberar_vaga(vaga_id)
                break