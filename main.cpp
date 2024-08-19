//#include "base.h"
#include "centralcontrol.h"
//#include "car.h"


int main() {


    CentralControl MainControl;
    MainControl.readfile("file.txt");
    MainControl.printParkingTickets();
    MainControl.readCommandFromFile("commands.txt");

    return 0;
}
