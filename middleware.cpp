// middleware.cpp
#include "middleware.h"
#include <iostream>

Middleware::Middleware(const std::string& name, const std::string& ip, int port)
        : stationName(name), stationIP(ip), stationPort(port) {
    // Inicializar as vagas como todas disponíveis
    for (int i = 1; i <= 100; ++i) {  // Supondo 100 vagas como exemplo
        spots[i] = true;
    }
}

void Middleware::connectToManager(const std::string& managerIP, int managerPort) {
    // Conectar ao gerente para iniciar a comunicação
    sendMessage("Connect", managerIP, managerPort);
}

void Middleware::connectToStation(const std::string& stationIP, int stationPort) {
    // Conectar a outra estação e atualizar a árvore de encaminhamento
    connectedStations[stationIP] = stationPort;
    sendMessage("Connect", stationIP, stationPort);
}

void Middleware::receiveMessage(const std::string& message) {
    // Lógica para processar as mensagens recebidas de outras estações
    std::cout << "Received message: " << message << std::endl;
}

void Middleware::sendMessage(const std::string& message, const std::string& destIP, int destPort) {
    // Lógica para enviar mensagens a outras estações
    std::cout << "Sending message: " << message << " to " << destIP << ":" << destPort << std::endl;
}

void Middleware::allocateSpot(int spotNumber) {
    if (spots[spotNumber]) {
        spots[spotNumber] = false;
        std::cout << "Spot " << spotNumber << " allocated." << std::endl;
    } else {
        std::cout << "Spot " << spotNumber << " is already occupied." << std::endl;
    }
}

void Middleware::freeSpot(int spotNumber) {
    if (!spots[spotNumber]) {
        spots[spotNumber] = true;
        std::cout << "Spot " << spotNumber << " freed." << std::endl;
    } else {
        std::cout << "Spot " << spotNumber << " is already free." << std::endl;
    }
}

int Middleware::findFreeSpot() {
    for (const auto& spot : spots) {
        if (spot.second) {
            return spot.first;
        }
    }
    return -1;  // Nenhuma vaga disponível
}

void Middleware::transferSpots(const std::vector<int>& spots, const std::string& newStationIP) {
    // Transferir a responsabilidade das vagas para outra estação
    for (int spot : spots) {
        freeSpot(spot);
    }
    // Enviar mensagem para a nova estação com as vagas transferidas
    std::string message = "Transfer spots to " + newStationIP;
    sendMessage(message, newStationIP, connectedStations[newStationIP]);
}
