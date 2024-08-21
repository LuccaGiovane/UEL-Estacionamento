#include <string>
#include <iostream>
#include <fstream>
#include <random>      // For random number generation
#include <chrono>      // For time functions
#include "car.h"
//#include "base.h"
//using namespace std;
using namespace std;

Car::Car(){
    outResultFile.open ("output.txt");
}

Car::~Car(){
    outResultFile.close ();
}

void Car::carThread(string dest_IP, int dest_Port, string exit_IP, int exit_Port) {
    auto start = std::chrono::high_resolution_clock::now();
    std::cout << "[LOG] Dest_IP: " << dest_IP << " Dest_port: " << dest_Port << std::endl;
    Communication::sendMessage(dest_IP, dest_Port, "RV");

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(5, 10);

    int sleepTime = dist(gen);
    std::cout << "[LOG] Car waiting for: " << sleepTime << " microseconds." << std::endl;
    std::this_thread::sleep_for(std::chrono::microseconds(sleepTime));

    std::cout << "[LOG] Sending LV to exit IP: " << exit_IP << " Port: " << exit_Port << std::endl;
    Communication::sendMessage(exit_IP, exit_Port, "LV");

    auto end = std::chrono::high_resolution_clock::now();
    auto elapsedTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

    std::cout << "[LOG] Car operation completed in: " << elapsedTime << " microseconds." << std::endl;
    writeToFile(std::to_string(elapsedTime));
}


void Car::writeToFile(string text){
    outResultFile << text << "\n";
}

