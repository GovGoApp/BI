@echo off
echo === BI de Suprimentos - Pipeline ===
echo.

echo [1/3] Extraindo dados do Zoho...
python pipeline/extract.py
if errorlevel 1 goto erro

echo.
echo [2/3] Transformando dados...
python pipeline/transform.py
if errorlevel 1 goto erro

echo.
echo [2b/3] Regenerando indexes (apos transform)...
python pipeline/generate_indexes.py
if errorlevel 1 goto erro

echo.
echo [3/3] Gerando dashboard...
python pipeline/build.py
if errorlevel 1 goto erro

echo.
echo Dashboard gerado em: dist\index.html
echo Abrir: dist\index.html
goto fim

:erro
echo.
echo ERRO: pipeline interrompido.
exit /b 1

:fim
