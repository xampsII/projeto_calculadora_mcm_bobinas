@echo off
echo ========================================
echo    MCM Bobinas - Setup Docker
echo ========================================
echo.

echo Verificando se Docker estÃ¡ instalado...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Docker nÃ£o estÃ¡ instalado ou nÃ£o estÃ¡ no PATH
    echo Baixe em: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Docker encontrado!
echo.

echo Verificando se Docker Compose estÃ¡ disponÃ­vel...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Docker Compose nÃ£o estÃ¡ disponÃ­vel
    pause
    exit /b 1
)

echo Docker Compose encontrado!
echo.

echo Iniciando aplicaÃ§Ã£o...
echo Isso pode levar alguns minutos na primeira execuÃ§Ã£o...
echo.

docker-compose up --build

echo.
echo AplicaÃ§Ã£o finalizada.
pause
