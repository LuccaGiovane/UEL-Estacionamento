# Variáveis do compilador
CXX = g++
CXXFLAGS = -std=c++11 -Wall -g

# Nome do executável
TARGET = estacionamento

# Lista de arquivos fonte
SRCS = main.cpp centralcontrol.cpp middleware.cpp car.cpp base.cpp

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

# Regra para limpar os arquivos compilados
clean:
	rm -f $(OBJS) $(TARGET)

# Regra para executar o programa
run: all
	./$(TARGET)

