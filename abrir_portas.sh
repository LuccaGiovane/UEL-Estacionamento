#!/bin/bash

# Forçar o uso do iptables-legacy
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy

# Abrir portas 8881 até 8889
for port in {8881..8889}
do
  sudo iptables -I INPUT -p tcp --dport $port -j ACCEPT
  echo "Porta $port aberta."
done

# Salvar as regras para persistência após reinicialização
sudo iptables-save | sudo tee /etc/iptables/rules.v4

echo "Todas as portas entre 8881 e 8889 foram abertas com sucesso."
