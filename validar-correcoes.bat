@echo off
echo ========================================
echo   VALIDANDO CORRECOES
echo ========================================
echo.

echo Verificando arquivos corrigidos...
echo.

echo [1/3] Verificando migracao 0001...
findstr /C:"menor_unidade_id" backend\alembic\versions\0001_initial_migration.py > nul
if %errorlevel% == 0 (
    echo ✓ 0001_initial_migration.py CORRIGIDO
) else (
    echo ✗ 0001_initial_migration.py NAO CORRIGIDO
)

echo [2/3] Verificando migracao 0002...
findstr /C:"menor_unidade_id" backend\alembic\versions\0002_populate_unidades.py > nul
if %errorlevel% == 0 (
    echo ✓ 0002_populate_unidades.py CORRIGIDO
) else (
    echo ✗ 0002_populate_unidades.py NAO CORRIGIDO
)

echo [3/3] Verificando arquivos de documentacao...
if exist "CLIENTE-LEIA-ME.txt" (
    echo ✓ CLIENTE-LEIA-ME.txt CRIADO
) else (
    echo ✗ CLIENTE-LEIA-ME.txt NAO ENCONTRADO
)

echo.
echo ========================================
echo   RESULTADO
echo ========================================
echo.
echo Se todos os itens acima estao com ✓:
echo   ✓ Correcoes aplicadas com sucesso!
echo   ✓ Pronto para testar Docker
echo.
echo Proximo passo:
echo   1. Feche seu frontend local
echo   2. Execute: testar-docker-cliente.bat
echo.
pause
