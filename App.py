class App:
    def __init__(self, middleware):
        self.middleware = middleware  # Referência ao middleware associado

    def ocupar_vaga(self, vaga_id):
        # Solicita ao middleware que ocupe a vaga
        self.middleware.solicitar_ocupacao_vaga(vaga_id)

    def liberar_vaga(self, vaga_id):
        # Solicita ao middleware que libere a vaga
        self.middleware.solicitar_liberacao_vaga(vaga_id)

    def status_vagas(self):
        return self.middleware.solicitar_status_vagas()