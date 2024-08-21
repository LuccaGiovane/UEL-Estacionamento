#include <iostream>
#include <thread>
#include "centralcontrol.h"
#include "middleware.h"

int main() {
    std::cout << "[INFO] Iniciando o programa..." << std::endl;

    CentralControl MainControl;
    MainControl.readfile("file.txt");
    MainControl.printParkingTickets();

    Middleware middleware1("Station1", "127.0.0.1", 8881);
    Middleware middleware2("Station2", "127.0.0.1", 8882);

    std::thread t1(&Middleware::startListening, &middleware1);
    std::thread t2(&Middleware::startListening, &middleware2);

    MainControl.readCommandFromFile("commands.txt");

    t1.join();
    t2.join();

    std::cout << "[INFO] Programa finalizado." << std::endl;

    return 0;
}
