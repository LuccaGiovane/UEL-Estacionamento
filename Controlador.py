import time
import random
import threading
from App import App  # Certifique-se de que o App está no mesmo diretório ou adicione a importação correta


class CentralControle:
    def __init__(self, app):
        self.app = app

    def simular_carro(self, car_id, station_number):
        """Simula um carro entrando e saindo do estacionamento."""
        print(f"Simulando entrada do carro {car_id} na estação {station_number}...")
        self.app.request_vaga(car_id, station_number)

        # Simula o tempo que o carro fica estacionado
        time.sleep(random.randint(5, 15))  # 5 a 15 segundos

        print(f"Simulando saída do carro {car_id} da estação {station_number}...")
        self.app.liberar_vaga(car_id, station_number)

    def start(self):
        """Inicia a simulação de carros entrando e saindo."""
        for i in range(1, 6):  # Simula 5 carros
            car_id = f"CAR_{i}"
            station_number = random.randint(1, 10)  # Escolhe uma estação aleatória
            threading.Thread(target=self.simular_carro, args=(car_id, station_number)).start()
            time.sleep(random.randint(1, 3))  # Intervalo entre carros


if __name__ == "__main__":
    app = App({
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
    })
    central = CentralControle(app)
    central.start()
