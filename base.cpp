
#include <string>
#include <fstream> // file stream
#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <random>      // For random number generation
#include <chrono>      // For time functions
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "base.h"
using namespace std;

string Communication::sendMessage(const std::string& server_ip, int server_port, const std::string& request_msg) {
    int sock = 0;
    struct sockaddr_in serv_addr;
    char buffer[1024] = {0};

    // Creating socket file descriptor
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cerr << "Socket creation error" << std::endl;
        return " ";
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(server_port);

    // Convert IPv4 and IPv6 addresses from text to binary form
    if (inet_pton(AF_INET, server_ip.c_str(), &serv_addr.sin_addr) <= 0) {
        std::cerr << "Invalid address/ Address not supported" << std::endl;
        return " ";
    }

    // Connect to the server
    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "Connection failed" << std::endl;
        return " ";
    }

    // Send the request message
    send(sock, request_msg.c_str(), request_msg.length(), 0);
    std::cout << "Request sent: " << request_msg << std::endl;

    // Receive the response message
    int valread = read(sock, buffer, 1024);
    std::cout << "Response received: " << std::string(buffer, valread) << std::endl;

    // Close the socket
    close(sock);

    return (std::string(buffer, valread));
}

string Communication::actFunction( string dest_IP, int dest_Port, string cmd){
    string response;
    response = Communication::sendMessage(dest_IP, dest_Port, cmd);
    return (response);
}
