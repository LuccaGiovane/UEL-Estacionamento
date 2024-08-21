#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <cstdlib>
#include "middleware.h"

Middleware::Middleware(std::string stationName, std::string ipAddress, int port)
        : stationName(stationName), ipAddress(ipAddress), port(port), freeSpots(10) {
    std::cout << "[INFO] Middleware criado para " << stationName << " no IP " << ipAddress << " e porta " << port << std::endl;
}

void Middleware::startListening() {
    std::cout << "[DEBUG] " << stationName << " iniciando o escutador..." << std::endl;
    // Código de escuta de mensagens
    while (true) {
        std::string message = receiveMessage();
        std::cout << "[DEBUG] " << stationName << " recebeu a mensagem: " << message << std::endl;
        // Processar mensagem
        processMessage(message);
    }
}

void Middleware::processMessage(const std::string& message) {
    std::cout << "[INFO] " << stationName << " processando mensagem: " << message << std::endl;
    if (message == "RV") {
        allocateSpot();
        sendMessage("OK");
    }
}

void Middleware::allocateSpot() {
    std::cout << "[INFO] " << stationName << " alocando vaga. Vagas livres antes: " << freeSpots << std::endl;
    if (freeSpots > 0) {
        freeSpots--;
        std::cout << "[INFO] Vaga alocada. Vagas livres agora: " << freeSpots << std::endl;
    } else {
        std::cout << "[WARNING] Não há vagas disponíveis." << std::endl;
    }
}

std::string Middleware::receiveMessage() {
    // Simular recebimento de mensagem
    std::cout << "[DEBUG] Simulando recebimento de mensagem em " << stationName << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return "RV";
}

void Middleware::sendMessage(const std::string& message) {
    std::cout << "[DEBUG] " << stationName << " enviando mensagem: " << message << std::endl;
    // Simular envio de mensagem
}
