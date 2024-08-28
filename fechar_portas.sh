#!/bin/bash

# Fechar portas 8881 até 8889
for port in {8881..8889}
do
sudo iptables -D INPUT -p tcp --dport $port -j ACCEPT
echo "Porta $port fechada."
done

# Salvar as regras para persistência após reinicialização
sudo iptables-save | sudo tee /etc/iptables/rules.v4

echo "Todas as portas entre 8881 e 8889 foram fechadas com sucesso."
