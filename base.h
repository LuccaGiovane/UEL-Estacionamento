#include <string>
#include <array>
using namespace std;


class Communication {
    public:
    string sendMessage(const std::string& server_ip, int server_port, const std::string& request_msg);
    string actFunction( string dest_IP, int dest_Port, string cmd);
};


