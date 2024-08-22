# Defina as portas que você deseja abrir
$ports = @(8881, 8882, 8883, 8884, 8885, 8886, 8887, 8888, 8889, 8890)

# Nome da regra no firewall
$ruleName = "WSL_Allow_Ports"

# Adicionar regra de entrada para as portas definidas
foreach ($port in $ports) {
    New-NetFirewallRule -DisplayName "$ruleName_$port" -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow
}

# Adicionar regra de saída para as portas definidas
foreach ($port in $ports) {
    New-NetFirewallRule -DisplayName "$ruleName_$port" -Direction Outbound -LocalPort $port -Protocol TCP -Action Allow
}

Write-Host "Regras de firewall adicionadas com sucesso!"
