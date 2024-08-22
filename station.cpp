#include "station.h"

// Construtor
Station::Station(std::string name, std::string ip, int port, char status)
        : name(name), ip(ip), port(port), status(status) {}

// Métodos Getters
std::string Station::getIpAddress() const { return ip; }
int Station::getPort() const { return port; }
char Station::getStatus() const { return status; }

// Simula a resposta da estação (exemplo simples)
bool Station::ping() { return status == 'A'; }  // Considera ativa se status for 'A'

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
