$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    docker compose up -d app
} finally {
    Pop-Location
}