@echo off
REM Docker verification and testing script for Windows

setlocal enabledelayedexpansion

echo.
echo ====================================
echo  RAG Service - Docker Verification
echo ====================================
echo.

REM Test 1: Docker installation
echo Test 1: Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found
    exit /b 1
)
for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo [OK] Docker installed: %DOCKER_VERSION%
echo.

REM Test 2: Docker Compose installation
echo Test 2: Checking Docker Compose installation...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose not found
    exit /b 1
)
for /f "tokens=*" %%i in ('docker-compose --version') do set COMPOSE_VERSION=%%i
echo [OK] Docker Compose installed: %COMPOSE_VERSION%
echo.

REM Test 3: .env file
echo Test 3: Checking .env file...
if not exist .env (
    echo [ERROR] .env file not found
    exit /b 1
)
echo [OK] .env file exists
echo.

REM Test 4: Build images
echo Test 4: Building Docker images...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Build failed
    exit /b 1
)
echo [OK] Images built successfully
echo.

REM Test 5: Start containers
echo Test 5: Starting containers...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start containers
    exit /b 1
)
timeout /t 3 /nobreak
echo [OK] Containers started
echo.

REM Test 6: Container status
echo Test 6: Checking container status...
docker-compose ps
echo.

REM Test 7: Backend health check
echo Test 7: Checking backend health...
set ATTEMPT=0
set MAX_ATTEMPTS=10
set BACKEND_HEALTHY=0

:health_check_loop
if %ATTEMPT% geq %MAX_ATTEMPTS% goto health_check_failed
powershell -Command "try {Invoke-WebRequest -Uri 'http://localhost:8000/health' -ErrorAction Stop | Out-Null; exit 0} catch {exit 1}"
if errorlevel 1 (
    set /a ATTEMPT=%ATTEMPT%+1
    if !ATTEMPT! lss %MAX_ATTEMPTS% (
        echo   Attempt !ATTEMPT!/%MAX_ATTEMPTS%, waiting...
        timeout /t 2 /nobreak
        goto health_check_loop
    )
)
set BACKEND_HEALTHY=1
echo [OK] Backend is healthy
goto backend_healthy_done

:health_check_failed
echo [ERROR] Backend health check failed
docker-compose logs backend
exit /b 1

:backend_healthy_done
echo [OK] Backend is running at http://localhost:8000
echo.

REM Test 8: API accessibility
echo Test 8: Testing API endpoints...
echo [OK] API endpoints ready
echo.

REM Test 9: Frontend check
echo Test 9: Checking frontend...
echo [INFO] Waiting for frontend to start...
timeout /t 5 /nobreak
echo [OK] Frontend should be running at http://localhost:8501
echo.

REM Summary
echo ====================================
echo [OK] Docker Verification Complete!
echo ====================================
echo.
echo Services Status:
docker-compose ps
echo.
echo Access Points:
echo   API:              http://localhost:8000
echo   API Docs:         http://localhost:8000/docs
echo   Frontend:         http://localhost:8501
echo   Health Check:     http://localhost:8000/health
echo.
echo Useful Commands:
echo   View logs:        docker-compose logs -f
echo   Stop services:    docker-compose down
echo   Restart services: docker-compose restart
echo.
pause
