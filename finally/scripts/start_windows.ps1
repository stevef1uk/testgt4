$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

$ImageName = "finally"
$ContainerName = "finally-app"
$VolumeName = "finally-data"
$Port = if ($env:APP_PORT) { $env:APP_PORT } else { "8010" }

docker version *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker is not available. Start Docker and retry." }

$running = docker ps -q --filter "name=^/$ContainerName$"
if ($running) {
    Write-Host "FinAlly is already running."
} else {
    $existing = docker ps -aq --filter "name=^/$ContainerName$"
    if ($existing) {
        docker start $ContainerName | Out-Null
    } else {
        docker image inspect $ImageName *> $null
        if ($LASTEXITCODE -ne 0) { docker build -t $ImageName $Root }
        $envArgs = @()
        if (Test-Path ".env") { $envArgs = @("--env-file", ".env") }
        docker run -d --name $ContainerName -v "$($VolumeName):/app/db" -p "$($Port):8010" @envArgs $ImageName | Out-Null
    }
}

Write-Host "FinAlly is running at http://localhost:$Port"