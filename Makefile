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
	@echo "Abrindo portas no Firewall..."
	@bash ./abrir_portas.sh
	@echo "Portas abertas. Executando o programa..."
	./$(TARGET)
	@echo "Fechando portas no Firewall..."
	@powershell.exe -Command "Start-Process -NoNewWindow -Wait powershell.exe -File fechar_portas.ps1"
	@echo "Portas fechadas."

# Regra para limpar os arquivos compilados
clean:
	rm -f $(OBJS) $(TARGET)
