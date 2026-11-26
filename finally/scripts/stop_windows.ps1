$ErrorActionPreference = "Stop"

$ContainerName = "finally-app"

$running = docker ps -q --filter "name=^/$ContainerName$"
if ($running) { docker stop $ContainerName | Out-Null }

$existing = docker ps -aq --filter "name=^/$ContainerName$"
if ($existing) { docker rm $ContainerName | Out-Null }

Write-Host "FinAlly container stopped. Volume finally-data is preserved."