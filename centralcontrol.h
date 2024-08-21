#ifndef CENTRALCONTROL_H
#define CENTRALCONTROL_H

#include <string>
#include <array>
#include <vector>
#include <thread>
#include "car.h"

class CentralControl : public Car {
public:
    void readCommandFromFile(std::string cmdFile);
    void handleCommand(std::string cmd, std::string dest_IP, int dest_Port);

    CentralControl();
    ~CentralControl();
    void readfile(std::string filename);
    void printParkingTickets();
    void selectExit(std::string& station, std::string& addr, int* p);
    std::string getName(int ind);
    std::string getIpAddress(int ind);
    int getPort(int ind);
    char getStatus(int ind);

private:
    std::vector<std::thread> newThread;
    int actNumber;
    int carNumber;
    std::array<std::string, 10> name;
    std::array<std::string, 10> ipaddress;
    std::array<int, 10> port;
    std::array<char, 10> status;
};

#endif
