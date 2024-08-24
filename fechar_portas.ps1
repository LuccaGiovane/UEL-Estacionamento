# Lista de portas a serem fechadas
$portas = 8881..8890

foreach ($porta in $portas) {
    # Remove as regras de entrada e saída para cada porta
    Remove-NetFirewallRule -DisplayName "Abrir Porta $porta" -Direction Inbound -LocalPort $porta -Protocol TCP -Action Allow -Profile Any
    Remove-NetFirewallRule -DisplayName "Abrir Porta $porta" -Direction Outbound -LocalPort $porta -Protocol TCP -Action Allow -Profile Any
}

Write-Host "Portas fechadas com sucesso!"
