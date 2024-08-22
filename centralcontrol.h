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

    // Novas funções para tolerância a falhas
    void detectAndHandleFailure();  // Detecta falhas e lida com redistribuição de vagas
    bool isStationResponsive(Station &station);  // Verifica se a estação está respondendo
    void redistributeVagas(Station &failedStation);  // Redistribui vagas da estação falhada
    Station* electNewStation();  // Escolhe nova estação para receber vagas
    void transferVagas(Station &from, Station *to);  // Transfere vagas de uma estação para outra
    void reconfigureTree();  // Reconfigura a árvore de encaminhamento

private:
    std::vector<std::thread> newThread;
    int actNumber;
    int carNumber;
    std::array<std::string, 10> name;
    std::array<std::string, 10> ipaddress;
    std::array<int, 10> port;
    std::array<char, 10> status;

    // Outros membros privados necessários para a lógica de falhas
    std::vector<Station> stations;  // Lista de estações gerenciadas
};

#endif
