# Build frontend for production and serve on LAN
param(
    [string]$ApiUrl = "http://127.0.0.1:8000",
    [int]$Port = 3000
)

$ErrorActionPreference = "Stop"
$frontend = Join-Path $PSScriptRoot "..\frontend"
Set-Location $frontend

$env:REACT_APP_API_URL = $ApiUrl
Write-Host "Building frontend with API: $ApiUrl"
npm run build

Write-Host "Serving frontend at http://0.0.0.0:$Port"
npx --yes serve -s build -l $Port
