#ifndef CENTRALCONTROL_H
#define CENTRALCONTROL_H

#include <string>
#include <array>
#include <vector>
#include <thread>
#include "car.h"
#include "station.h"

class CentralControl : public Car {
public:
    CentralControl();
    ~CentralControl();

    // Funções existentes
    void readCommandFromFile(std::string cmdFile);
    void handleCommand(std::string cmd, std::string dest_IP, int dest_Port);
    void readfile(std::string filename);
    void printParkingTickets();
    void selectExit(std::string& station, std::string& addr, int* p);
    std::string getName(int ind);
    std::string getIpAddress(int ind);
    int getPort(int ind);
    char getStatus(int ind);

    // Funções para tolerância a falhas
    void detectAndHandleFailure();
    bool isStationResponsive(Station& station);
    void redistributeVagas(Station& failedStation);
    Station* electNewStation();
    void transferVagas(Station& from, Station* to);
    void reconfigureTree();

    // Nova função para gerar IDs dos carros
    std::string setCarID(int length); // Gera um ID único para cada carro

private:
    std::vector<std::thread> newThread;
    int actNumber;
    int carNumber;
    std::array<std::string, 10> name;
    std::array<std::string, 10> ipaddress;
    std::array<int, 10> port;
    std::array<char, 10> status;

    // Outros membros para tolerância a falhas
    std::vector<Station> stations;

    // Adicionado o alfabeto para geração de IDs
    const std::string alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
};

#endif
