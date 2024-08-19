#include <sys/socket.h>

#include <string>
#include <array>
#include <unistd.h>
#include <arpa/inet.h>

#include "car.h"

using namespace std;


class CentralControl:  public Car{
public:
    void readCommandFromFile(string cmdFile);
    void handleCommand(string cmd, string dest_IP, int dest_Port);

    CentralControl();
    ~CentralControl();
    void readfile(string);
    void printParkingTickets();
    void selectExit(string& station, string&  addr, int * p);
    string getName(int ind);
    string getIpAddress (int ind);
    int getPort(int ind);
    char getStatus(int ind);

private:
    
    vector<thread> newThread;
    int carNumber;
    int actNumber;


    array <string,10> name;
    array <string,10> ipaddress;
    array <int,10> port;
    array <char,10> status; // 0=offline   1=online
};
