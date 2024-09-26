#include "centralcontrol.h"



int main() {


    CentralControl MainControl;
    MainControl.readfile("file.txt");
    MainControl.printParkingTickets();
    MainControl.readCommandFromFile("commands.txt");

    return 0;
}
