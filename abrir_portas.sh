#!/bin/bash

# Abrir portas de 8880 até 8890 no firewall (Linux)
for port in {8880..8890}
do
    echo "Abrindo porta $port no firewall..."
    sudo ufw allow $port/tcp
done

echo "Portas de 8880 a 8890 abertas com sucesso."
