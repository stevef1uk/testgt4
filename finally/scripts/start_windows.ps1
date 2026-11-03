$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | Where-Object { $_ -match "^\s*[^#][^=]*=" } | ForEach-Object {
        $name, $value = $_ -split "=", 2
        [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim())
    }
}

New-Item -ItemType Directory -Force -Path (Join-Path $root "db") | Out-Null
$logFile = Join-Path $root "db\polecat.log"
$pidFile = Join-Path $env:TEMP "polecat.pid"
$hostName = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }
$port = if ($env:PORT) { $env:PORT } else { "8000" }

$process = Start-Process -FilePath "python" `
    -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", $hostName, "--port", $port `
    -WorkingDirectory $root -RedirectStandardOutput $logFile -RedirectStandardError $logFile -PassThru
$process.Id | Set-Content $pidFile
Write-Output "Polecat started with PID $($process.Id) on $hostName`:$port"