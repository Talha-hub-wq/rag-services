@echo off
REM Docker startup helper script for Windows

echo.
echo ========================================
echo  RAG Service - Docker Startup
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo.
    echo [ERROR] .env file not found!
    echo [INFO] Please copy .env.example to .env and configure your settings.
    echo.
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist documents mkdir documents
if not exist logs mkdir logs
echo [OK] Directories created
echo.

REM Check Docker installation
docker --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Docker is not installed or not in PATH!
    echo [INFO] Install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)
echo [OK] Docker is installed
echo.

REM Check Docker Compose installation
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Docker Compose is not installed or not in PATH!
    echo [INFO] Docker Compose should be included with Docker Desktop
    echo.
    pause
    exit /b 1
)
echo [OK] Docker Compose is installed
echo.

REM Build images
echo.
echo Building Docker images...
docker-compose build --no-cache
if errorlevel 1 (
    echo.
    echo [ERROR] Docker build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Setup Complete!
echo ========================================
echo.
echo To start the services, run:
echo   docker-compose up -d
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop the services:
echo   docker-compose down
echo.
echo API will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend will be available at: http://localhost:8501
echo.
pause
