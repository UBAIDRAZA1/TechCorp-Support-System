# CRM Digital FTE - Complete Setup Script (Windows)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CRM Digital FTE - Complete Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ROOT = "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte"
$PG_BIN = "C:\Program Files\PostgreSQL\15\bin"

Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
try {
    Set-Location "$PROJECT_ROOT\kafka"
    $dockerStatus = docker-compose ps -q
    if ($dockerStatus) {
        Write-Host "Docker containers already running" -ForegroundColor Green
    } else {
        Write-Host "Starting Kafka..." -ForegroundColor Yellow
        docker-compose up -d
        Start-Sleep -Seconds 30
        Write-Host "Kafka started successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "Docker not running. Start Docker Desktop first!" -ForegroundColor Red
}

Write-Host ""
Write-Host "[2/6] Database Setup..." -ForegroundColor Yellow
Write-Host "Note: If password prompt fails, use pgAdmin instead" -ForegroundColor Cyan

Write-Host ""
Write-Host "[3/6] Python Dependencies..." -ForegroundColor Yellow
Set-Location $PROJECT_ROOT

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

Write-Host "Installing Python packages..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt --quiet
Write-Host "Python dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "[4/6] Frontend Dependencies..." -ForegroundColor Yellow
Set-Location "$PROJECT_ROOT\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install --silent
    Write-Host "Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Frontend dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/6] Environment Setup..." -ForegroundColor Yellow

if (-not (Test-Path "$PROJECT_ROOT\prototype\.env")) {
    Copy-Item "$PROJECT_ROOT\prototype\.env.example" "$PROJECT_ROOT\prototype\.env"
    Write-Host "Environment file created" -ForegroundColor Green
    Write-Host "Edit .env file with your API keys" -ForegroundColor Cyan
} else {
    Write-Host "Environment file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Now run services in 3 terminals:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 (API):" -ForegroundColor Cyan
Write-Host "  cd C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\prototype" -ForegroundColor White
Write-Host "  ..\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 (Worker):" -ForegroundColor Cyan
Write-Host "  cd C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python kafka\worker.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 3 (Frontend):" -ForegroundColor Cyan
Write-Host "  cd C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Kafka UI: http://localhost:8080" -ForegroundColor White
Write-Host ""

Set-Location $PROJECT_ROOT
