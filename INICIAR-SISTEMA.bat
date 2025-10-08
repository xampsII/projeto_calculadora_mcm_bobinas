@echo off
echo ========================================
echo   INICIALIZANDO SISTEMA NFE
echo ========================================
echo.

echo 1. Parando containers antigos...
docker-compose down -v
echo.

echo 2. Iniciando servicos...
docker-compose up -d
echo.

echo 3. Aguardando banco de dados ficar pronto (30 segundos)...
timeout /t 30 /nobreak
echo.

echo 4. Aplicando migracoes do banco...
docker-compose exec backend alembic upgrade head
echo.

echo 5. Populando banco com dados iniciais...
docker-compose exec backend python -m app.seeds
echo.

echo 6. Verificando status dos servicos...
docker-compose ps
echo.

echo ========================================
echo   SISTEMA PRONTO!
echo ========================================
echo.
echo Acesse: http://localhost:5173
echo API: http://localhost:8000/docs
echo.
echo Para ver logs:
echo   docker-compose logs -f
echo.
echo Para parar:
echo   docker-compose down
echo.
pause
