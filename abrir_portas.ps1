# Lista de portas a serem abertas
$portas = 8881..8890

foreach ($porta in $portas) {
    # Cria uma regra de entrada para cada porta
    New-NetFirewallRule -DisplayName "Abrir Porta $porta" -Direction Inbound -LocalPort $porta -Protocol TCP -Action Allow
    New-NetFirewallRule -DisplayName "Abrir Porta $porta" -Direction Outbound -LocalPort $porta -Protocol TCP -Action Allow
}

Write-Host "Portas abertas com sucesso!"
