# Variáveis do compilador
CXX = g++
CXXFLAGS = -std=c++11 -Wall -g

# Nome do executável
TARGET = estacionamento

# Lista de arquivos fonte
SRCS = main.cpp centralcontrol.cpp middleware.cpp car.cpp base.cpp station.cpp

# Geração da lista de arquivos objeto
OBJS = $(SRCS:.cpp=.o)

# Regra padrão: compilar tudo e gerar o executável
all: $(TARGET)

# Regra para gerar o executável
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Regras para compilar os arquivos objeto
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Regras para liberar as portas e executar o programa
run: all
	@echo "Liberando portas no Firewall..."
	@powershell.exe -Command "Start-Process -NoNewWindow -Wait powershell.exe -ArgumentList '-Command \"& {$(foreach port,8881 8882 8883 8884 8885 8886 8887 8888 8889 8890, netsh advfirewall firewall add rule name=Port$(port) dir=in action=allow protocol=TCP localport=$(port); )}\"'"
	@echo "Portas liberadas. Executando o programa..."
	./$(TARGET)

# Regra para limpar os arquivos compilados
clean:
	rm -f $(OBJS) $(TARGET)
