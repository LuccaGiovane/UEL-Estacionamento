// middleware.cpp
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

    // Criando socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        std::cerr << "Falha ao criar o socket" << std::endl;
        exit(EXIT_FAILURE);
    }

    // Configurando opções do socket
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        std::cerr << "Erro nas opções do socket" << std::endl;
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(stationPort);

    // Ligando o socket a porta definida
    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        std::cerr << "Erro ao ligar o socket" << std::endl;
        exit(EXIT_FAILURE);
    }

    // Ouvindo conexões
    if (listen(server_fd, 3) < 0) {
        std::cerr << "Erro ao ouvir conexões" << std::endl;
        exit(EXIT_FAILURE);
    }

    std::cout << "Middleware está ouvindo em " << stationIP << ":" << stationPort << std::endl;

    while (true) {
        if ((new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen)) < 0) {
            std::cerr << "Erro ao aceitar conexão" << std::endl;
            exit(EXIT_FAILURE);
        }

        char buffer[1024] = {0};
        int valread = read(new_socket, buffer, 1024);
        std::string message(buffer, valread);

        std::cout << "Mensagem recebida: " << message << std::endl;

        // Processar a mensagem recebida
        receiveMessage(message);

        // Responder a estação
        std::string response = "OK";
        send(new_socket, response.c_str(), response.length(), 0);

        // Fechar o socket de conexão
        close(new_socket);
    }
}

Middleware::Middleware(const std::string& name, const std::string& ip, int port)
        : stationName(name), stationIP(ip), stationPort(port) {
    // Inicializar as vagas como todas disponíveis
    for (int i = 1; i <= 100; ++i) {  // Supondo 100 vagas como exemplo
        spots[i] = true;
    }
}

bool Middleware::connectToManager(const std::string& manager_ip, int manager_port) {
    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cerr << "Erro na criação do socket" << std::endl;
        return false;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(manager_port);

    if (inet_pton(AF_INET, manager_ip.c_str(), &serv_addr.sin_addr) <= 0) {
        std::cerr << "Endereço inválido/ não suportado" << std::endl;
        return false;
    }

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "Conexão com o gerente falhou" << std::endl;
        return false;
    }

    std::cout << "Conectado ao gerente com sucesso!" << std::endl;

    manager_socket = sock;
    return true;  // Retorna true se a conexão foi bem-sucedida
}

void Middleware::activateStation() {
    if (connectToManager(manager_ip, manager_port)) {
        std::string activation_msg = "AE";
        send(manager_socket, activation_msg.c_str(), activation_msg.length(), 0);
        std::cout << "Mensagem de ativação enviada ao gerente" << std::endl;
    }
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
