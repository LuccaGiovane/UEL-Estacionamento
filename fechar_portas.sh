#!/bin/bash

# Fechar portas de 8880 até 8890 no firewall (Linux)
for port in {8880..8890}
do
    echo "Fechando porta $port no firewall..."
    sudo ufw deny $port/tcp
done

echo "Portas de 8880 a 8890 foram fechadas com sucesso."
