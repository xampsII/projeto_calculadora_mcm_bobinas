@echo off
echo ========================================
echo   RESETANDO BANCO DE DADOS COMPLETAMENTE
echo ========================================
echo.
echo AVISO: Isso vai apagar TODOS os dados!
echo.
pause

echo 1. Parando tudo...
docker-compose down
echo.

echo 2. Removendo volumes antigos...
docker volume rm project_postgres_data
echo.

echo 3. Limpando sistema Docker...
docker system prune -f
echo.

echo 4. Reconstruindo imagens...
docker-compose build --no-cache
echo.

echo 5. Iniciando servicos...
docker-compose up -d
echo.

echo 6. Aguardando banco inicializar (40 segundos)...
timeout /t 40 /nobreak
echo.

echo 7. Verificando status...
docker-compose ps
echo.

echo 8. Aplicando migracoes...
docker-compose exec backend alembic upgrade head
echo.

echo 9. Populando banco...
docker-compose exec backend python -m app.seeds
echo.

echo 10. Verificando dados...
docker-compose exec db psql -U nfeuser -d nfedb -c "SELECT COUNT(*) FROM materias_primas;"
echo.

echo 11. Reiniciando backend...
docker-compose restart backend
echo.

echo ========================================
echo   PRONTO!
echo ========================================
echo.
echo Acesse: http://localhost:5173
echo.
pause
