#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "station.h"

// Construtor
Station::Station(std::string name, std::string ip, int port, char status)
        : name(name), ip(ip), port(port), status(status) {}

// Métodos Getters
std::string Station::getIpAddress() const { return ip; }
int Station::getPort() const { return port; }
char Station::getStatus() const { return status; }

// Simula a resposta da estação (exemplo simples)
bool Station::ping() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return false;
    }

    struct sockaddr_in station_addr;
    station_addr.sin_family = AF_INET;
    station_addr.sin_port = htons(port);  // Porta da estação
    inet_pton(AF_INET, ip.c_str(), &station_addr.sin_addr);  // IP da estação

    int result = connect(sock, (struct sockaddr*)&station_addr, sizeof(station_addr));
    close(sock);

    return result == 0;  // Retorna true se a conexão foi bem-sucedida
}

// Verifica se a estação está ativa
bool Station::isActive() const { return status == 'A'; }

// Retorna o número de vagas ocupadas (exemplo simplificado)
int Station::getOcupiedVagas() const { return vagas.size(); }

// Retorna a lista de vagas (exemplo simplificado)
std::vector<int> Station::getVagas() const { return vagas; }

// Adiciona uma vaga (exemplo simplificado)
void Station::addVaga(int vaga) { vagas.push_back(vaga); }

// Limpa as vagas da estação (exemplo simplificado)
void Station::clearVagas() { vagas.clear(); }
