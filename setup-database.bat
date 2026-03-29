@echo off
echo ========================================
echo CRM Digital FTE - Database Setup
echo ========================================
echo.

cd /d "C:\Program Files\PostgreSQL\15\bin"

echo Step 1: Dropping old database (if exists)...
psql.exe -U postgres -c "DROP DATABASE IF EXISTS crm_digital_fte;"
if %errorlevel% neq 0 (
    echo ERROR: Could not drop database. Check PostgreSQL is running.
    pause
    exit /b 1
)

echo.
echo Step 2: Creating new database...
psql.exe -U postgres -c "CREATE DATABASE crm_digital_fte;"
if %errorlevel% neq 0 (
    echo ERROR: Could not create database. Check PostgreSQL is running.
    pause
    exit /b 1
)

echo.
echo Step 3: Importing schema...
psql.exe -U postgres -d crm_digital_fte -f "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\database\schema.sql"
if %errorlevel% neq 0 (
    echo ERROR: Could not import schema.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database setup completed successfully!
echo ========================================
pause
