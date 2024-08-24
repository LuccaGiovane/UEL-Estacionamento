#include <iostream>
#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "middleware.h"

using namespace std;

void Middleware::startListening() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        std::cerr << "[LOG] Falha ao criar o socket" << std::endl;
        exit(EXIT_FAILURE);//
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        std::cerr << "[LOG] Erro nas opções do socket" << std::endl;
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    inet_pton(AF_INET, stationIP.c_str(), &address.sin_addr);
    address.sin_port = htons(stationPort);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        std::cerr << "[LOG] Erro ao ligar o socket" << std::endl;
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        std::cerr << "[LOG] Erro ao ouvir conexões" << std::endl;
        exit(EXIT_FAILURE);
    }

    std::cout << "[LOG] Middleware está ouvindo em " << stationIP << ":" << stationPort << std::endl;

    while (true) {
        if ((new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen)) < 0) {
            std::cerr << "[LOG] Erro ao aceitar conexão" << std::endl;
            continue;
        }



        char buffer[1024] = {0};
        int valread = read(new_socket, buffer, 1024);
        std::string message(buffer, valread);

        std::cout << "[LOG] Mensagem recebida: " << message << std::endl;

        receiveMessage(message);

        std::string response = "OK";
        send(new_socket, response.c_str(), response.length(), 0);
        close(new_socket);
    }
}

bool Middleware::connectToManager(const std::string& manager_ip, int manager_port) {
    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cerr << "[LOG] Erro na criação do socket" << std::endl;
        return false;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(manager_port);

    if (inet_pton(AF_INET, manager_ip.c_str(), &serv_addr.sin_addr) <= 0) {
        std::cerr << "[LOG] Endereço inválido/ não suportado" << std::endl;
        return false;
    }

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "[LOG] Conexão com o gerente falhou" << std::endl;
        return false;
    }

    std::cout << "[LOG] Conectado ao gerente com sucesso!" << std::endl;

    manager_socket = sock;
    return true;
}

void Middleware::receiveMessage(const std::string& message) {
    std::cout << "[LOG] Processing received message: " << message << std::endl;
    // Implement your logic here
}

void Middleware::sendMessage(const std::string& message, const std::string& destIP, int destPort) {
    std::cout << "[LOG] Sending message: " << message << " to " << destIP << ":" << destPort << std::endl;
}

void Middleware::allocateSpot(int spotNumber) {
    if (spots[spotNumber]) {
        spots[spotNumber] = false;
        std::cout << "[LOG] Spot " << spotNumber << " allocated." << std::endl;
    } else {
        std::cout << "[LOG] Spot " << spotNumber << " is already occupied." << std::endl;
    }
}

void Middleware::freeSpot(int spotNumber) {
    if (!spots[spotNumber]) {
        spots[spotNumber] = true;
        std::cout << "[LOG] Spot " << spotNumber << " freed." << std::endl;
    } else {
        std::cout << "[LOG] Spot " << spotNumber << " is already free." << std::endl;
    }
}


Middleware::Middleware(const std::string& name, const std::string& ip, int port)
        : stationName(name), stationIP(ip), stationPort(port), manager_ip("127.0.0.1"), manager_port(8880) {
    for (int i = 1; i <= 100; ++i) {
        spots[i] = true;
    }
}



void Middleware::activateStation() {
    if (connectToManager(manager_ip, manager_port)) {
        std::string activation_msg = "AE";
        send(manager_socket, activation_msg.c_str(), activation_msg.length(), 0);
        std::cout << "Mensagem de ativação enviada ao gerente" << std::endl;
    }
}

void Middleware::connectToStation(const std::string& stationIP, int stationPort) {
    connectedStations[stationIP] = stationPort;
    sendMessage("Connect", stationIP, stationPort);
}

