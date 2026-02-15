# start.ps1 — Launch both the FastAPI backend and the Vite dev frontend (Windows)
# Usage:  cd catphish-api; .\start.ps1

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "  Catphish Voice Verification" -ForegroundColor Cyan
Write-Host "  ===========================" -ForegroundColor Cyan
Write-Host ""

# 1. Start FastAPI backend
Write-Host "[1/2] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
$backend = Start-Process -NoNewWindow -PassThru -FilePath "python" `
    -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" `
    -WorkingDirectory "$RootDir\server"

Write-Host "  Backend PID: $($backend.Id)" -ForegroundColor Green

# 2. Start Vite frontend
Write-Host "[2/2] Starting Vite frontend on http://localhost:3001 ..." -ForegroundColor Yellow
$frontend = Start-Process -NoNewWindow -PassThru -FilePath "npm" `
    -ArgumentList "run", "dev" `
    -WorkingDirectory "$RootDir"

Write-Host "  Frontend PID: $($frontend.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "  Backend  -> http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Frontend -> http://localhost:3001" -ForegroundColor Cyan
Write-Host "  Health   -> http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers." -ForegroundColor Gray

try {
    $backend.WaitForExit()
} finally {
    Write-Host "`nShutting down..." -ForegroundColor Yellow
    if (!$backend.HasExited) { Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue }
    if (!$frontend.HasExited) { Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue }
    Write-Host "Done." -ForegroundColor Green
}
