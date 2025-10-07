@echo off
echo ========================================
echo      DIAGNOSTICO DO SISTEMA
echo ========================================
echo.

echo [1/6] Verificando se Docker esta rodando...
docker ps
if %errorlevel% neq 0 (
    echo ERRO: Docker nao esta rodando!
    pause
    exit /b 1
)

echo.
echo [2/6] Verificando logs do backend...
docker-compose logs --tail=20 backend

echo.
echo [3/6] Testando conexao com backend...
curl -s http://localhost:8000/health || echo ERRO: Backend nao responde

echo.
echo [4/6] Testando endpoint de notas...
curl -s http://localhost:8000/notas/ || echo ERRO: Endpoint de notas nao responde

echo.
echo [5/6] Verificando banco de dados...
docker exec -it project-db-1 psql -U postgres -d mcm_bobinas -c "\dt" || echo ERRO: Banco nao acessivel

echo.
echo [6/6] Verificando se tabelas existem...
docker exec -it project-db-1 psql -U postgres -d mcm_bobinas -c "SELECT COUNT(*) FROM users;" || echo ERRO: Tabela users nao existe

echo.
echo ========================================
echo      DIAGNOSTICO CONCLUIDO
echo ========================================
echo.
pause
