#include <thread>
#include "centralcontrol.h"
#include "middleware.h"
#include "station.h"

//int main() {
//    // Inicializar Estações
//    Station station1("Station1", "127.0.0.1", 8881, 'A');
//    Station station2("Station2", "127.0.0.1", 8882, 'A');
//
//    // Inicializar o Middleware para as estações
//    Middleware middleware1(station1.getName(), station1.getIpAddress(), station1.getPort());
//    Middleware middleware2(station2.getName(), station2.getIpAddress(), station2.getPort());
//
//    // Criar threads para as estações
//    std::thread t1(&Middleware::startListening, &middleware1);
//    std::thread t2(&Middleware::startListening, &middleware2);
//
//    // Central Control
//    CentralControl MainControl;
//    MainControl.readfile("file.txt");
//    MainControl.printParkingTickets();
//    MainControl.readCommandFromFile("commands.txt");
//
//    // Esperar as threads terminarem
//    t1.join();
//    t2.join();
//
//    return 0;
//}

int main() {
    // Cria instâncias das estações conforme o arquivo file.txt
    Station station1("Station1", "127.0.0.1", 8881, 'A');
    Station station2("Station2", "127.0.0.1", 8882, 'A');
    // Adicione todas as outras estações conforme necessário
    Station station10("Station10", "127.0.0.1", 8890, 'A');

    // Inicializa o Middleware para as estações
    Middleware middleware1(station1.getName(), station1.getIpAddress(), station1.getPort());
    Middleware middleware2(station2.getName(), station2.getIpAddress(), station2.getPort());
    // Inicializa o Middleware para a última estação
    Middleware middleware10(station10.getName(), station10.getIpAddress(), station10.getPort());

    // Cria threads para as estações, iniciando o método startListening
    std::thread t1(&Middleware::startListening, &middleware1);
    std::thread t2(&Middleware::startListening, &middleware2);
    // Adicione threads para outras estações
    std::thread t10(&Middleware::startListening, &middleware10);

    // Executa o código original de leitura dos arquivos e execução dos comandos
    CentralControl MainControl;
    MainControl.readfile("file.txt");
    MainControl.printParkingTickets();
    MainControl.readCommandFromFile("commands.txt");

    // Faz o join das threads para garantir que elas terminem corretamente
    t1.join();
    t2.join();
    t10.join();

    return 0;
}
