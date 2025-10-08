@echo off
echo ========================================
echo   CORRIGINDO MIGRACAO DO BANCO DE DADOS
echo ========================================
echo.

echo 1. Parando Docker...
docker-compose down -v
echo.

echo 2. Iniciando Docker novamente...
docker-compose up -d
echo.

echo 3. Aguardando banco ficar pronto...
timeout /t 10 /nobreak > nul
echo.

echo 4. Aplicando migracao corrigida...
docker-compose exec backend alembic upgrade head
echo.

echo 5. Populando banco com dados iniciais...
docker-compose exec backend python -m app.seeds
echo.

echo 6. Reiniciando backend...
docker-compose restart backend
echo.

echo ========================================
echo   CORRECAO CONCLUIDA!
echo ========================================
echo.
echo Agora acesse: http://localhost:5173
echo.
pause
