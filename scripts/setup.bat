@echo off
REM Setup script for CRM Digital FTE (Windows)

echo ==============================================
echo 🏗️  CRM Digital FTE - Setup Script
echo ==============================================

REM Check Python
echo Checking Python...
python --version
if errorlevel 1 (
    echo Python 3.11+ is required
    exit /b 1
)

REM Check Node.js
echo Checking Node.js...
node --version
if errorlevel 1 (
    echo Node.js 18+ is required
    exit /b 1
)

REM Check Docker
echo Checking Docker...
docker --version
if errorlevel 1 (
    echo Docker is required
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

REM Create .env file
echo Creating .env file...
if not exist prototype\.env (
    copy prototype\.env.example prototype\.env
    echo ✓ Created .env file
    echo ⚠️  Please edit prototype\.env with your credentials
) else (
    echo ✓ .env file already exists
)

REM Start Docker services
echo Starting Docker services (Kafka, Zookeeper)...
cd kafka
docker-compose up -d
cd ..

REM Wait for Kafka to be ready
echo Waiting for Kafka to be ready...
timeout /t 10 /nobreak

echo.
echo ==============================================
echo ✅ Setup Complete!
echo ==============================================
echo.
echo 📋 Next Steps:
echo    1. Edit prototype\.env with your credentials
echo    2. Start the API server:
echo       venv\Scripts\activate
echo       cd prototype && python main.py
echo.
echo    3. Start the Kafka worker:
echo       python kafka\worker.py
echo.
echo    4. Start the frontend:
echo       cd frontend && npm run dev
echo.
echo 📚 Documentation:
echo    - API Docs: http://localhost:8000/docs
echo    - Frontend: http://localhost:3000
echo    - Kafka UI: http://localhost:8080
echo.

pause
