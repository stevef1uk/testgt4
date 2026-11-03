$ErrorActionPreference = "Stop"

$pidFile = Join-Path $env:TEMP "polecat.pid"

if (Test-Path $pidFile) {
    $processId = [int](Get-Content $pidFile -Raw).Trim()
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($null -ne $process) {
        Stop-Process -Id $processId -Force
    }
    Remove-Item $pidFile -Force
}