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

$HostName = if ($env:BACKEND_HOST) { $env:BACKEND_HOST } else { "127.0.0.1" }
$Port = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { "8000" }

python -m uvicorn backend.app.main:app --host $HostName --port $Port