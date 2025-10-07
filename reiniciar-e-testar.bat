@echo off
chcp 65001 >nul
cls

echo ========================================
echo   REINICIAR E TESTAR - CORREÇÕES 500
echo ========================================
echo.

echo [1/4] Parando Docker...
docker-compose down
if %errorlevel% neq 0 (
    echo ERRO: Falha ao parar Docker
    pause
    exit /b 1
)

echo.
echo [2/4] Limpando sistema...
docker system prune -f

echo.
echo [3/4] Iniciando Docker com rebuild...
docker-compose up --build -d
if %errorlevel% neq 0 (
    echo ERRO: Falha ao iniciar Docker
    pause
    exit /b 1
)

echo.
echo [4/4] Aguardando backend iniciar (15 segundos)...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo   TESTANDO ENDPOINTS
echo ========================================

echo.
echo [Teste 1] GET /produtos-finais/
curl -s http://localhost:8000/produtos-finais/ | findstr /C:"[" >nul
if %errorlevel% equ 0 (
    echo ✅ Endpoint /produtos-finais/ funcionando!
) else (
    echo ❌ Endpoint /produtos-finais/ com erro
)

echo.
echo [Teste 2] GET /produtos-finais/materias-primas-disponiveis
curl -s http://localhost:8000/produtos-finais/materias-primas-disponiveis | findstr /C:"[" >nul
if %errorlevel% equ 0 (
    echo ✅ Endpoint /materias-primas-disponiveis funcionando!
) else (
    echo ❌ Endpoint /materias-primas-disponiveis com erro
)

echo.
echo [Teste 3] GET /materias-primas/
curl -s http://localhost:8000/materias-primas/ | findstr /C:"items" >nul
if %errorlevel% equ 0 (
    echo ✅ Endpoint /materias-primas/ funcionando!
) else (
    echo ❌ Endpoint /materias-primas/ com erro
)

echo.
echo ========================================
echo   LOGS DO BACKEND
echo ========================================
echo.
echo Últimas 30 linhas do log do backend:
docker logs --tail 30 project-backend-1

echo.
echo ========================================
echo   RESULTADO
echo ========================================
echo.
echo ✅ Sistema reiniciado com sucesso!
echo.
echo 📊 Próximos passos:
echo 1. Acessar http://localhost:5173
echo 2. Ir em "Produtos"
echo 3. Verificar que NÃO há mais erro 500
echo 4. Se listas estiverem vazias, executar: inicializar-banco.bat
echo.
echo 🔍 Para ver logs em tempo real:
echo    docker logs -f project-backend-1
echo.

pause

