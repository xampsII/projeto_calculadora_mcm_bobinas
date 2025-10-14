@echo off
echo ========================================
echo CAPTURANDO LOGS DO BACKEND
echo ========================================
echo.

echo Verificando se Docker esta rodando...
docker-compose ps

echo.
echo ========================================
echo LOGS COMPLETOS DO BACKEND (ultimas 200 linhas):
echo ========================================
echo.

docker-compose logs backend --tail=200 > logs-backend-erro.txt

echo.
echo ✅ Logs salvos em: logs-backend-erro.txt
echo.
echo Abra o arquivo logs-backend-erro.txt e procure por:
echo   - ERROR
echo   - Traceback
echo   - Exception
echo.
echo Envie o conteudo desse arquivo para analise.
echo.
pause

