@echo off
echo ========================================
echo   DIAGNOSTICO - ENDPOINTS COM ERRO 500
echo ========================================
echo.

echo [1/4] Verificando se Docker esta rodando...
docker ps | findstr backend
if %errorlevel% neq 0 (
    echo ERRO: Backend nao esta rodando!
    pause
    exit /b 1
)

echo.
echo [2/4] Testando endpoint de materias-primas...
curl -s http://localhost:8000/materias-primas/ || echo ERRO: Endpoint materias-primas falha

echo.
echo [3/4] Testando endpoint de produtos-finais...
curl -s http://localhost:8000/produtos-finais/ || echo ERRO: Endpoint produtos-finais falha

echo.
echo [4/4] Verificando tabelas no banco...
docker exec -it project-db-1 psql -U postgres -d mcm_bobinas -c "\dt"

echo.
echo [5/4] Verificando se tabela materias_primas existe...
docker exec -it project-db-1 psql -U postgres -d mcm_bobinas -c "SELECT COUNT(*) FROM materias_primas;"

echo.
echo [6/4] Verificando se tabela materia_prima_precos existe...
docker exec -it project-db-1 psql -U postgres -d mcm_bobinas -c "SELECT COUNT(*) FROM materia_prima_precos;"

echo.
echo ========================================
echo   DIAGNOSTICO CONCLUIDO
echo ========================================
pause
