#ifndef STATION_H
#define STATION_H

#include <string>
#include <vector>

class Station {
public:
    // Construtor
    Station(std::string name, std::string ip, int port, char status);


    // Métodos Getters
    std::string getName() const { return name; }
    std::string getIpAddress() const;
    int getPort() const;
    char getStatus() const;

    // Métodos de controle
    bool ping();  // Simula a resposta da estação
    bool isActive() const;  // Verifica se a estação está ativa
    int getOcupiedVagas() const;  // Obtém o número de vagas ocupadas
    std::vector<int> getVagas() const;  // Obtém as vagas da estação
    void addVaga(int vaga);  // Adiciona uma vaga à estação
    void clearVagas();  // Limpa as vagas da estação

private:
    std::string name;
    std::string ip;
    int port;
    char status;
    std::vector<int> vagas;  // Exemplo de como armazenar vagas
};

#endif