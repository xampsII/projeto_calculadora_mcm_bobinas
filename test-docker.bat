@echo off
echo ========================================
echo    TESTE DO DOCKER - SISTEMA MCM
echo ========================================
echo.

echo [1/6] Verificando Docker...
docker --version
if %errorlevel% neq 0 (
    echo ERRO: Docker nao encontrado! Instale o Docker Desktop primeiro.
    pause
    exit /b 1
)

echo [2/6] Verificando Docker Compose...
docker-compose --version
if %errorlevel% neq 0 (
    echo ERRO: Docker Compose nao encontrado!
    pause
    exit /b 1
)

echo [3/6] Verificando arquivos necessarios...
if not exist "docker-compose.yml" (
    echo ERRO: Arquivo docker-compose.yml nao encontrado!
    pause
    exit /b 1
)

if not exist "package.json" (
    echo ERRO: Arquivo package.json nao encontrado!
    pause
    exit /b 1
)

if not exist "backend\Dockerfile" (
    echo ERRO: Dockerfile do backend nao encontrado!
    pause
    exit /b 1
)

if not exist "src\Dockerfile" (
    echo ERRO: Dockerfile do frontend nao encontrado!
    pause
    exit /b 1
)

echo [4/6] Verificando portas...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo AVISO: Porta 8000 ja esta em uso!
)

netstat -ano | findstr :5173 >nul
if %errorlevel% equ 0 (
    echo AVISO: Porta 5173 ja esta em uso!
)

netstat -ano | findstr :5432 >nul
if %errorlevel% equ 0 (
    echo AVISO: Porta 5432 ja esta em uso!
)

echo [5/6] Limpando cache do Docker...
docker-compose down >nul 2>&1
docker system prune -f >nul 2>&1

echo [6/6] Iniciando Docker Compose...
echo.
echo ========================================
echo    INICIANDO CONSTRUCAO DOS CONTAINERS
echo ========================================
echo.
echo Aguarde alguns minutos enquanto os containers sao construidos...
echo.

docker-compose up --build

echo.
echo ========================================
echo    CONSTRUCAO FINALIZADA
echo ========================================
echo.
echo Se tudo funcionou corretamente:
echo - Frontend: http://localhost:5173
echo - Backend: http://localhost:8000
echo.
pause
