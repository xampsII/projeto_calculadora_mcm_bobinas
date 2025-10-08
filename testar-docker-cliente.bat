@echo off
echo ========================================
echo   TESTANDO DOCKER PARA CLIENTE
echo ========================================
echo.
echo IMPORTANTE:
echo 1. Feche o frontend local (porta 5173)
echo 2. Isso vai resetar o banco Docker
echo.
pause

echo 1. Limpando ambiente Docker anterior...
docker-compose down -v
echo.

echo 2. Iniciando servicos...
docker-compose up -d --build
echo.

echo 3. Aguardando banco ficar pronto (15 segundos)...
timeout /t 15 /nobreak
echo.

echo 4. Aplicando migracoes...
docker-compose exec backend alembic upgrade head
echo.

echo 5. Populando banco...
docker-compose exec backend python -m app.seeds
echo.

echo 6. Verificando logs do backend...
docker-compose logs backend --tail=50
echo.

echo ========================================
echo   TESTE CONCLUIDO!
echo ========================================
echo.
echo Acesse: http://localhost:5173
echo Backend: http://localhost:8000/docs
echo.
echo Para ver logs em tempo real:
echo docker-compose logs -f
echo.
pause
