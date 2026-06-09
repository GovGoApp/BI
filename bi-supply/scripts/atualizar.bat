@echo off
chcp 65001 >nul
mode con cols=160 lines=60
title Atualizar BI Suprimentos

set ROOT=C:\Users\Haroldo Duraes\Desktop\Scripts\BI\bi-supply
set PYTHON=C:\ProgramData\anaconda3\python.exe
set PS=powershell -NoProfile -Command
set LOG=%ROOT%\atualizar.log

if not exist "%ROOT%" (
    echo ERRO: pasta do projeto nao encontrada:
    echo   %ROOT%
    goto erro
)
if not exist "%PYTHON%" (
    echo ERRO: Python nao encontrado em:
    echo   %PYTHON%
    goto erro
)

cd /d "%ROOT%"

echo.
echo ============================================
echo   ATUALIZACAO BI SUPRIMENTOS
echo ============================================
echo.

:: -- 1. Refresh SQL (Zoho) ----------------------------------------------------
echo [1/3] Atualizando dados via SQL (Zoho Analytics)...
"%PYTHON%" nlsql\refresh_elements.py 2>&1 | %PS% "$input | Tee-Object -FilePath '%LOG%'"
if errorlevel 1 ( echo. & echo   ERRO no refresh! & goto erro )

:: -- 2. Indexes (posicionamento) ----------------------------------------------
echo.
echo [2/3] Gerando posicionamento das abas...
"%PYTHON%" pipeline\generate_indexes.py 2>&1 | %PS% "$input | Tee-Object -FilePath '%LOG%'"
if errorlevel 1 ( echo. & echo   ERRO nos indexes! & goto erro )

:: -- 3. Build HTML ------------------------------------------------------------
echo.
echo [3/3] Gerando dashboard HTML...
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