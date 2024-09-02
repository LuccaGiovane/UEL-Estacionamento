#include <iomanip>
#include <iostream>
#include <thread>
#include <random>
#include <chrono>
#include <vector>
#include <climits>
#include "centralcontrol.h"

using namespace std;

void CentralControl::detectAndHandleFailure() {
    for (Station& station : stations) {
        if (!isStationResponsive(station)) {
            std::cout << "[LOG] Detected failure at station: " << station.getName() << std::endl;
            redistributeVagas(station);
        }
    }
}

bool CentralControl::isStationResponsive(Station& station) {
    return station.ping();
}

void CentralControl::redistributeVagas(Station& failedStation) {
    Station* newStation = electNewStation();
    if (newStation != nullptr) {
        std::cout << "[LOG] Redistributing vagas from " << failedStation.getName() << " to " << newStation->getName() << std::endl;
        transferVagas(failedStation, newStation);
    } else {
        std::cout << "[ERROR] No station available to take over vagas!" << std::endl;
    }
}

Station* CentralControl::electNewStation() {
    Station* selectedStation = nullptr;
    int minVagas = INT_MAX;
    for (auto& station : stations) {
        if (station.isActive() && station.getOcupiedVagas() < minVagas) {
            selectedStation = &station;
            minVagas = station.getOcupiedVagas();
        }
    }
    return selectedStation;
}

void CentralControl::transferVagas(Station& from, Station* to) {
    for (int vaga : from.getVagas()) {
        to->addVaga(vaga);
    }
    from.clearVagas();
}

void CentralControl::reconfigureTree() {
    std::cout << "[LOG] Tree reconfigured after station failure." << std::endl;
}

void CentralControl::readCommandFromFile(string cmdFile) {
    string command;
    int destination;
    ifstream inCommandFile(cmdFile, ios::in);
    if (!inCommandFile) {
        cerr << "Command File could not be opened" << endl;
        exit(EXIT_FAILURE);
    }
    while (inCommandFile >> command >> destination) {
        std::cout << "[LOG] Processing command: " << command << " station: " << destination << std::endl;
        this->handleCommand(command, getIpAddress(destination), getPort(destination));
    }

    for (auto& thread : newThread) {
        if (thread.joinable()) {
            thread.join();
        }
    }
}

void CentralControl::handleCommand(string cmd, string dest_IP, int dest_Port) {
    string response;
    std::cout << "[LOG] Handling command: " << cmd << " for station IP: " << dest_IP << " Port: " << dest_Port << std::endl;
    if (cmd == "RV") {
        carNumber++;
        std::string carID = setCarID(6);  // Gera um ID único para o carro
        std::cout << "[LOG] Starting the car: " << carID << std::endl;
        string exit_name;
        string exit_ipaddr;
        int exit_port;
        selectExit(exit_name, exit_ipaddr, &exit_port);
        std::cout << "[LOG] Exit selected: " << exit_name << " IP: " << exit_ipaddr << " Port: " << exit_port << std::endl;
        newThread.emplace_back(&Car::carThread, this, dest_IP, dest_Port, exit_ipaddr, exit_port, carID);

    } else if ((cmd == "AE") || (cmd == "FE") || (cmd == "VD") || (cmd == "ST")) {
        actNumber++;
        response = Communication::actFunction(dest_IP, dest_Port, cmd);
        std::cout << "[LOG] Response from command " << cmd << ": " << response << std::endl;
        if (cmd == "VD") {
            writeToFile(response);
        }
        std::cout << "[LOG] Resuming the process..." << std::endl;
    } else {
        std::cout << "[LOG] Unknown command!" << std::endl;
    }
}

void CentralControl::selectExit(string& station, string& addr, int* p) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(1, 9);
    int ind = dist(gen);
    while (status[ind] == 0) {
        ind = dist(gen);
    }
    station = name[ind];
    addr = ipaddress[ind];
    *p = port[ind];
    std::cout << "[LOG] Selected exit: " << station << " IP: " << addr << " Port: " << *p << std::endl;
}

CentralControl::CentralControl() {
    actNumber = 0;
    carNumber = 0;
}

CentralControl::~CentralControl() {
}

void CentralControl::readfile(string filename) {
    ifstream inClientFile(filename, ios::in);
    if (!inClientFile) {
        cerr << "File could not be opened" << endl;
        exit(EXIT_FAILURE);
    }
    int i = 0;
    while (inClientFile >> name[i] >> ipaddress[i] >> port[i]) {
        status[i] = '0';
        i++;
    }
    inClientFile.close();
}

void CentralControl::printParkingTickets() {
    for (int i = 0; i < 10; i++) {
        cout << left << setw(10) << name[i] << setw(13) << ipaddress[i]
             << setw(7) << port[i] << " Status: " << status[i] << endl;
    }
}

string CentralControl::getName(int ind) {
    return name[ind - 1];
}

string CentralControl::getIpAddress(int ind) {
    return ipaddress[ind - 1];
}

int CentralControl::getPort(int ind) {
    return port[ind - 1];
}

char CentralControl::getStatus(int ind) {
    return status[ind - 1];
}

// Função para gerar IDs únicos de carros
string CentralControl::setCarID(int length) {
    string res = "";
    for (int i = 0; i < length; i++)
        res += alphabet[rand() % 36];
    return res;
}
