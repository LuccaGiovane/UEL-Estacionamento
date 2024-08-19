#include "centralcontrol.h"
#include "middleware.h"

int main() {
    // Inicializar o Middleware
    Middleware middleware("Station1", "127.0.0.1", 8881);

    // Conectar ao gerente (IP e porta fictícios)
    if (middleware.connectToManager("127.0.0.1", 8880)) {
       // middleware.activateStation();
    }

    // Central Control
    CentralControl MainControl;
    MainControl.readfile("file.txt");
    MainControl.printParkingTickets();
    MainControl.readCommandFromFile("commands.txt");

    return 0;
}

