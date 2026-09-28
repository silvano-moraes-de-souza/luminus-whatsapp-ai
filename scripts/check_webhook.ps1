$body = @{
    instanceName = "meu_agente"
} | ConvertTo-Json -Compress

$envContent = Get-Content "luminus\.env" -Raw
$webhookSecret = if ($envContent -match 'WEBHOOK_SECRET=(.+)') { $Matches[1].Trim() } else { Read-Host "Digite o WEBHOOK_SECRET" }
$evoKey      = if ($envContent -match 'EVOLUTION_API_KEY=(.+)') { $Matches[1].Trim() } else { Read-Host "Digite a EVOLUTION_API_KEY" }
$instance    = if ($envContent -match 'INSTANCE_NAME=(.+)')      { $Matches[1].Trim() } else { "meu_agente" }

$body = @{
    webhook = @{
        enabled = $true
        url = "http://192.168.15.30:3000/webhook"
        webhookByEvents = $false
        webhookBase64 = $false
        events = @("QRCODE_UPDATED", "MESSAGES_UPSERT", "MESSAGES_UPDATE", "MESSAGES_DELETE")
        headers = @{
            Authorization = "Bearer $webhookSecret"
        }
    }
} | ConvertTo-Json -Compress

$response = Invoke-RestMethod -Uri "http://localhost:8085/webhook/set/$instance" -Method Post -Headers @{apikey=$evoKey;'Content-Type'='application/json'} -Body $body

$response | ConvertTo-Json -Depth 10