# Lista de portas a serem fechadas
$portas = 8881..8890

foreach ($porta in $portas) {
    # Remove a regra de entrada para cada porta
    Get-NetFirewallRule | Where-Object { $_.DisplayName -eq "Abrir Porta $porta" } | Remove-NetFirewallRule
}

Write-Host "Portas fechadas com sucesso!"

#colabora pycharm