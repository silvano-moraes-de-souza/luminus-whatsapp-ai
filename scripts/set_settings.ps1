$body = @{
    rejectCall = $true
    msgCall = "Desculpe, não posso atender ligações. Por favor, envie uma mensagem."
    groupsIgnore = $true
    alwaysOnline = $false
    readMessages = $true
    readStatus = $false
    syncFullHistory = $false
} | ConvertTo-Json -Compress

$envContent = Get-Content "luminus\.env" -Raw
$evoKey   = if ($envContent -match 'EVOLUTION_API_KEY=(.+)') { $Matches[1].Trim() } else { Read-Host "Digite a EVOLUTION_API_KEY" }
$instance = if ($envContent -match 'INSTANCE_NAME=(.+)')      { $Matches[1].Trim() } else { "meu_agente" }

$response = Invoke-RestMethod -Uri "http://localhost:8085/settings/set/$instance" -Method Post -Headers @{apikey=$evoKey;'Content-Type'='application/json'} -Body $body

$response | ConvertTo-Json -Depth 10