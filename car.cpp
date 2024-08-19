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

void Car::carThread(string dest_IP, int dest_Port, string exit_IP, int exit_Port){
    //send RV
    auto start = std::chrono::high_resolution_clock::now();
    std::cout << "Dest_IP: " << dest_IP << " Dest_port: "<<dest_Port<< std::endl;
    Communication::sendMessage(dest_IP, dest_Port, "RV");
    // wait
    // Create a random number generator
    std::random_device rd;  // Seed for the random number engine
    std::mt19937 gen(rd()); // Mersenne Twister engine
    std::uniform_int_distribution<> dist(5, 10); // Range from 5 to 10 microseconds

    // Generate a random sleep duration
    int sleepTime = dist(gen);

    // Sleep for the generated duration
    std::this_thread::sleep_for(std::chrono::microseconds(sleepTime));

    // select a station to leave
    Communication::sendMessage (exit_IP, exit_Port, "LV");
    auto end = std::chrono::high_resolution_clock::now();
    auto elapsedTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

    writeToFile(std::to_string(elapsedTime));
    outResultFile << std::to_string(elapsedTime) << "\n";
}

void Car::writeToFile(string text){
    outResultFile << text << "\n";
}

