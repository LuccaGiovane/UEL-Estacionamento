// middleware.h
#ifndef MIDDLEWARE_H
#define MIDDLEWARE_H

#include <string>
#include <vector>
#include <map>

class Middleware {
public:
    Middleware(const std::string& name, const std::string& ip, int port);
    void connectToManager(const std::string& managerIP, int managerPort);
    void connectToStation(const std::string& stationIP, int stationPort);
    void receiveMessage(const std::string& message);
    void sendMessage(const std::string& message, const std::string& destIP, int destPort);
    void handleFailure(const std::string& failedStation);

    // Gerenciamento de vagas
    void allocateSpot(int spotNumber);
    void freeSpot(int spotNumber);
    int findFreeSpot();
    void transferSpots(const std::vector<int>& spots, const std::string& newStationIP);

private:
    std::string stationName;
    std::string stationIP;
    int stationPort;
    std::map<int, bool> spots;  // Mapeamento de número da vaga para disponibilidade
    std::map<std::string, int> connectedStations;  // IP da estação conectada para sua porta
};

#endif