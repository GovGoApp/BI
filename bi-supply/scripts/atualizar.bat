@echo off
chcp 65001 >nul
mode con cols=160 lines=60
title Atualizar BI Suprimentos

set ROOT=C:\Users\Haroldo Duraes\Desktop\Scripts\BI\bi-supply
set PYTHON=C:\ProgramData\anaconda3\python.exe
set PS=powershell -NoProfile -Command
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

:: -- 1. Extracao --------------------------------------------------------------
echo [1/5] Extraindo dados do Zoho Analytics...
"%PYTHON%" pipeline\extract.py --env-file "%ENV%" 2>&1 | %PS% "$input | Tee-Object -FilePath '%LOG%'"
if errorlevel 1 ( echo. & echo   ERRO na extracao! & goto erro )

:: -- 2. Transform -------------------------------------------------------------
echo.
echo [2/5] Calculando metricas...
"%PYTHON%" pipeline\transform.py 2>&1 | %PS% "$input | Tee-Object -FilePath '%LOG%'"
if errorlevel 1 ( echo. & echo   ERRO no transform! & goto erro )

:: -- 3. Indexes ---------------------------------------------------------------
echo.
echo [3/5] Gerando indexes...
"%PYTHON%" pipeline\generate_indexes.py 2>&1 | %PS% "$input | Tee-Object -FilePath '%LOG%'"
if errorlevel 1 ( echo. & echo   ERRO nos indexes! & goto erro )

:: -- 4. Refresh NL-SQL --------------------------------------------------------
echo.
echo [4/5] Atualizando elementos NL-SQL...
"%PYTHON%" nlsql\refresh_elements.py 2>&1 | %PS% "$input | Tee-Object -Append -FilePath '%LOG%'"
if errorlevel 1 ( echo   AVISO: alguns elementos nao atualizados. Continuando... )

:: -- 5. Build -----------------------------------------------------------------
echo.
echo [5/5] Gerando dashboard HTML...
"%PYTHON%" pipeline\build.py 2>&1 | %PS% "$input | Tee-Object -FilePath '%LOG%'"
if errorlevel 1 ( echo. & echo   ERRO no build! & goto erro )

echo.
echo ============================================
echo   CONCLUIDO! Abra: dist\index.html
echo   Log salvo em:   %LOG%
echo ============================================
echo.
pause
exit /b 0

:erro
echo.
echo ============================================
echo   ERRO! Veja o log acima ou em: %LOG%
echo ============================================
echo.
pause
exit /b 1