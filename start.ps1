# PowerShell script to launch all RecruitmentAgent services
# Usage: .\start.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RecruitmentAgent - Starting Services  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Service 1: Streamlit Main App (port 8501)
Write-Host "[1/4] Starting Streamlit App..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; Write-Host 'Streamlit App (http://localhost:8501)' -ForegroundColor Yellow; uv run streamlit run main.py"

Start-Sleep -Seconds 2

# Service 2: Flask LiveKit Token Server (port 5001)
Write-Host "[2/4] Starting Flask Token Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\Interview'; Write-Host 'Flask Token Server (http://localhost:5001)' -ForegroundColor Yellow; uv run python livekit_token.py"

Start-Sleep -Seconds 2

# Service 3: LiveKit Interview Agent
Write-Host "[3/4] Starting LiveKit Agent..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\Interview'; Write-Host 'LiveKit Agent Runner' -ForegroundColor Yellow; uv run python agent_runner.py dev"

Start-Sleep -Seconds 2

# Service 4: React Interview Frontend (port 5173)
Write-Host "[4/4] Starting React Frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\Interview\frontend'; Write-Host 'React Frontend (http://localhost:5173)' -ForegroundColor Yellow; npm run dev"

Write-Host ""
Write-Host "All 4 services started!" -ForegroundColor Green
Write-Host ""
Write-Host "  Streamlit App:     http://localhost:8501" -ForegroundColor White
Write-Host "  Flask Token API:   http://localhost:5001" -ForegroundColor White
Write-Host "  React Frontend:    http://localhost:5173" -ForegroundColor White
Write-Host ""
