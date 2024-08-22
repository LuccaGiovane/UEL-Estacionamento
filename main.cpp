#include <thread>
#include "centralcontrol.h"
#include "middleware.h"
#include "station.h"

int main() {
    // Inicializar Estações
    Station station1("Station1", "127.0.0.1", 8881, 'A');
    Station station2("Station2", "127.0.0.1", 8882, 'A');

    // Inicializar o Middleware para as estações
    Middleware middleware1(station1.getName(), station1.getIpAddress(), station1.getPort());
    Middleware middleware2(station2.getName(), station2.getIpAddress(), station2.getPort());

    // Criar threads para as estações
    std::thread t1(&Middleware::startListening, &middleware1);
    std::thread t2(&Middleware::startListening, &middleware2);

    // Central Control
    CentralControl MainControl;
    MainControl.readfile("file.txt");
    MainControl.printParkingTickets();
    MainControl.readCommandFromFile("commands.txt");

    // Esperar as threads terminarem
    t1.join();
    t2.join();

    return 0;
}
