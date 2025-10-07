@echo off
echo ========================================
echo      BACKUP DO BANCO DE DADOS
echo ========================================
echo.

REM Criar pasta de backups se nÃ£o existir
if not exist "backups" mkdir backups

REM Gerar nome do arquivo com data e hora
set DATA=%date:~-4,4%-%date:~-7,2%-%date:~-10,2%
set HORA=%time:~0,2%-%time:~3,2%-%time:~6,2%
set HORA=%HORA: =0%
set ARQUIVO=backups\backup_%DATA%_%HORA%.sql

echo Criando backup do banco de dados...
echo Arquivo: %ARQUIVO%
echo.

docker exec -t project_db_1 pg_dump -U postgres mcm_bobinas > %ARQUIVO%

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo      BACKUP CRIADO COM SUCESSO!
    echo ========================================
    echo.
    echo Arquivo salvo em: %ARQUIVO%
    echo.
    
    REM Mostrar tamanho do arquivo
    for %%A in (%ARQUIVO%) do echo Tamanho: %%~zA bytes
    echo.
) else (
    echo.
    echo ========================================
    echo      ERRO AO CRIAR BACKUP!
    echo ========================================
    echo.
    echo Verifique se o Docker estÃ¡ rodando.
    echo.
)

pause
