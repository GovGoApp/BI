@echo off
chcp 65001 >nul
mode con cols=160 lines=50
title Atualizar BI Suprimentos

set ROOT=C:\Users\Haroldo Duraes\Desktop\Scripts\BI\bi-supply
set PYTHON=C:\ProgramData\anaconda3\python.exe
set ENV=%ROOT%\zoho\zoho.env
set LOG=%ROOT%\atualizar.log

if not exist "%ROOT%" (
    echo ERRO: pasta do projeto nao encontrada:
    echo   %ROOT%
    goto erro
)

if not exist "%PYTHON%" (
    echo ERRO: Python nao encontrado em:
    echo   %PYTHON%
    echo Verifique se o Anaconda esta instalado nesse caminho.
    goto erro
)

cd /d "%ROOT%"

echo.
echo ============================================
echo   ATUALIZACAO BI SUPRIMENTOS
echo ============================================
echo.

echo [1/5] Extraindo dados do Zoho Analytics...
"%PYTHON%" pipeline\extract.py --env-file "%ENV%" > "%LOG%" 2>&1
if errorlevel 1 (
    echo   ERRO na extracao. Veja: %LOG%
    type "%LOG%"
    goto erro
)
echo   OK

echo.
echo [2/5] Calculando metricas...
"%PYTHON%" pipeline\transform.py > "%LOG%" 2>&1
if errorlevel 1 (
    echo   ERRO. Veja: %LOG%
    goto erro
)
echo   OK

echo.
echo [3/5] Gerando indexes...
"%PYTHON%" pipeline\generate_indexes.py > "%LOG%" 2>&1
if errorlevel 1 (
    echo   ERRO. Veja: %LOG%
    goto erro
)
echo   OK

echo.
echo [4/5] Atualizando elementos NL-SQL...
"%PYTHON%" nlsql\refresh_elements.py >> "%LOG%" 2>&1
if errorlevel 1 (
    echo   AVISO: alguns elementos nao foram atualizados (continua...)
) else (
    echo   OK
)

echo.
echo [5/5] Gerando dashboard HTML...
"%PYTHON%" pipeline\build.py > "%LOG%" 2>&1
if errorlevel 1 (
    echo   ERRO. Veja: %LOG%
    goto erro
)
echo   OK

echo.
echo ============================================
echo   CONCLUIDO! Abra: dist\index.html
echo   Log completo:   %LOG%
echo ============================================
echo.
pause
exit /b 0

:erro
echo.
echo ============================================
echo   ERRO! Log completo em: %LOG%
echo ============================================
echo.
pause
exit /b 1