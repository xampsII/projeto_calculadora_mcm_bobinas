@echo off
echo ========================================
echo    RESTAURAR BACKUP DO BANCO
echo ========================================
echo.

if not exist "backups" (
    echo ERRO: Pasta de backups nao encontrada!
    echo.
    pause
    exit /b 1
)

echo Backups disponiveis:
echo.
dir /b backups\*.sql
echo.

set /p ARQUIVO=Digite o nome do arquivo de backup (ex: backup_2025-10-07_20-30-00.sql): 
set CAMINHO_COMPLETO=backups\%ARQUIVO%

if not exist "%CAMINHO_COMPLETO%" (
    echo.
    echo ERRO: Arquivo nao encontrado: %CAMINHO_COMPLETO%
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo      ATENCAO: ISSO IRA SUBSTITUIR
echo      TODOS OS DADOS ATUAIS DO BANCO!
echo ========================================
echo.
set /p CONFIRMAR=Tem certeza? (S/N): 

if /i not "%CONFIRMAR%"=="S" (
    echo.
    echo Operacao cancelada.
    echo.
    pause
    exit /b 0
)

echo.
echo Restaurando backup...
echo.

type "%CAMINHO_COMPLETO%" | docker exec -i project_db_1 psql -U postgres -d mcm_bobinas

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    BACKUP RESTAURADO COM SUCESSO!
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo      ERRO AO RESTAURAR BACKUP!
    echo ========================================
    echo.
)

pause
