# Start API for LAN / production access (binds to all network interfaces)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\backend

Write-Host "Starting Society Management API on http://0.0.0.0:8000"
.\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000
