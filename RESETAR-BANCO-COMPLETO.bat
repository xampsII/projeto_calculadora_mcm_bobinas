@echo off
echo ========================================
echo   RESETANDO BANCO DE DADOS COMPLETO
echo ========================================
echo.
echo AVISO: Isso vai APAGAR TODOS OS DADOS!
echo.
pause

echo 1. Parando e removendo TUDO (containers + volumes + imagens)...
docker-compose down -v --rmi all
echo.

echo 2. Reconstruindo imagens do zero...
docker-compose build --no-cache
echo.

echo 3. Iniciando servicos...
docker-compose up -d
echo.

echo 4. Aguardando banco ficar pronto (30 segundos)...
timeout /t 30 /nobreak
echo.

echo 5. Aplicando migracoes...
docker-compose exec backend alembic upgrade head
echo.

echo 6. Populando banco...
docker-compose exec backend python -m app.seeds
echo.

echo 7. Reiniciando backend...
docker-compose restart backend
echo.

echo ========================================
echo   RESET CONCLUIDO!
echo ========================================
echo.
echo Acesse: http://localhost:5173
echo.
pause
