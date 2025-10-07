@echo off
echo ========================================
echo   REINICIAR DOCKER COM CORRECOES
echo ========================================
echo.
echo Parando containers...
docker-compose down
echo.
echo Limpando cache...
docker system prune -f
echo.
echo Reconstruindo containers...
echo (Isso pode demorar alguns minutos)
echo.
docker-compose up --build --force-recreate
