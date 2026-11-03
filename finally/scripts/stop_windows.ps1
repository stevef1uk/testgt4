$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    docker compose stop app
    docker compose rm --force app
} finally {
    Pop-Location
}