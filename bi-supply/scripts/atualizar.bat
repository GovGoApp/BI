@echo off
chcp 65001 >nul
mode con cols=160 lines=50
title Atualizar BI Suprimentos

set ROOT=C:\Users\Haroldo Duraes\Desktop\Scripts\BI\bi-supply
set PYTHON=C:\ProgramData\anaconda3\python.exe
set ENV=%ROOT%\zoho\zoho.env
set LOG=%ROOT%\atualizar.log

:: ── Verificações iniciais ──────────────────────
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

:: ── 1. Extração ──────────────────────────────
echo [1/5] Extraindo dados do Zoho Analytics...
"%PYTHON%" pipeline/extract.py --env-file "%ENV%" > "%LOG%" 2>&1
if errorlevel 1 (
    echo.
    echo   ERRO na extracao. Detalhes em: atualizar.log
    echo   Ultimas linhas:
    echo   ----------------------------------------
    "%PYTHON%" -c "import sys; lines=open(r'%LOG%',encoding='utf-8',errors='replace').readlines(); [print('  '+l,end='') for l in lines[-12:]]"
    goto erro
)
"%PYTHON%" -c "import sys; [print('  '+l,end='') for l in open(r'%LOG%',encoding='utf-8',errors='replace') if 'Concluido' in l or 'Pulando' in l or 'Token' in l]"

:: ── 2. Transform ─────────────────────────────
echo.
echo [2/5] Calculando metricas...
"%PYTHON%" pipeline/transform.py > "%LOG%" 2>&1
if errorlevel 1 (
    echo   ERRO. Detalhes em: atualizar.log
    goto erro
)
"%PYTHON%" -c "import sys; [print('  '+l,end='') for l in open(r'%LOG%',encoding='utf-8',errors='replace') if 'Concluido' in l or 'Total' in l or 'arqs' in l or 'NFE:' in l]"

:: ── 3. Indexes ───────────────────────────────
echo.
echo [3/5] Gerando indexes...
"%PYTHON%" pipeline/generate_indexes.py > "%LOG%" 2>&1
if errorlevel 1 (
    echo   ERRO. Detalhes em: atualizar.log
    goto erro
)
"%PYTHON%" -c "import sys; [print('  '+l,end='') for l in open(r'%LOG%',encoding='utf-8',errors='replace') if 'Total:' in l or 'Indexes' in l]"

:: ── 4. Refresh NL-SQL elements ───────────────
echo.
echo [4/5] Atualizando elementos NL-SQL (Relatorio)...
"%PYTHON%" nlsql/refresh_elements.py >> "%LOG%" 2>&1
if errorlevel 1 (
    echo   AVISO: alguns elementos nao foram atualizados ^(continua...^)
    echo   Verifique atualizar.log para detalhes.
) else (
    "%PYTHON%" -c "import sys; [print('  '+l,end='') for l in open(r'%LOG%',encoding='utf-8',errors='replace') if 'Concluido' in l]"
)

:: ── 5. Build ─────────────────────────────────
echo.
echo [5/5] Gerando dashboard HTML...
"%PYTHON%" pipeline/build.py > "%LOG%" 2>&1
if errorlevel 1 (
    echo   ERRO. Detalhes em: atualizar.log
    goto erro
)
"%PYTHON%" -c "import sys; [print('  '+l,end='') for l in open(r'%LOG%',encoding='utf-8',errors='replace') if 'Gerado' in l or 'elementos' in l or 'Dimens' in l or 'NL-SQL' in l]"

echo.
echo ============================================
echo   CONCLUIDO! Abra: dist\index.html
echo   Log completo:   atualizar.log
echo ============================================
echo.
pause
exit /b 0

:erro
echo.
echo ============================================
echo   ERRO! Log completo em: atualizar.log
echo ============================================
echo.
pause
exit /b 1
