#include <string>
#include <fstream> // file stream
#include <iostream>
#include <thread>
#include <vector>

#include <iostream>
#include <cstdlib>
using namespace std;
#ifndef Car_H
#define Car_H

#include "base.h"

class Car : public Communication {
public:
    Car();
    ~Car();
    void carThread(string dest_IP, int dest_Port, string exit_IP, int exit_Port, string carID);
    void writeToFile(string text);
private:
    ofstream outResultFile;
    
};

#endif
