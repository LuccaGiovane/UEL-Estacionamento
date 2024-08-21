#include <thread>  // Para usar std::thread
#include "centralcontrol.h"
#include "middleware.h"

int main() {
    // Inicializar o Middleware para as estações
    Middleware middleware1("Station1", "127.0.0.1", 8881);
    Middleware middleware2("Station2", "127.0.0.1", 8882);

    // Criar threads para as estações
    std::thread t1(&Middleware::startListening, &middleware1);
    std::thread t2(&Middleware::startListening, &middleware2);

    // Central Control
    CentralControl MainControl;
    MainControl.readfile("file.txt");
    MainControl.printParkingTickets();
    MainControl.readCommandFromFile("commands.txt");

    // Esperar as threads terminarem //
    t1.join();
    t2.join();

    return 0;
}
