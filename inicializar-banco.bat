@echo off
echo ========================================
echo   INICIALIZAR BANCO DE DADOS
echo ========================================
echo.

echo [1/3] Executando migracoes do Alembic...
docker exec -it project-backend-1 alembic upgrade head

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha ao executar migracoes!
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Populando dados iniciais (seeds)...
docker exec -it project-backend-1 python -m app.seeds

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha ao popular dados!
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Reiniciando backend...
docker-compose restart backend

echo.
echo ========================================
echo   BANCO INICIALIZADO COM SUCESSO!
echo ========================================
echo.
echo Dados criados:
echo - Usuarios: admin@nfe.com / admin123
echo - Unidades de medida
echo - Fornecedores
echo - Materias-primas
echo - Produtos
echo.
echo Acesse: http://localhost:5173
echo.
pause
