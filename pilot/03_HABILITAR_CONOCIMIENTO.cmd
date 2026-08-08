@echo off
setlocal
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYTHON=K:\@@@@@ATLAS\.venv\Scripts\python.exe"
"%PYTHON%" "%ROOT%\pilot\set_knowledge_feature.py" true
if errorlevel 1 goto :error
sc.exe stop ATLAS_Conocimiento_Test >nul 2>&1
timeout /t 2 /nobreak >nul
sc.exe start ATLAS_Conocimiento_Test
if errorlevel 1 goto :error
echo.
echo Conocimiento HABILITADO solo en el piloto 5051.
echo Abrir: http://claroprod985:5051/conocimiento
pause
exit /b 0
:error
echo ERROR habilitando/reiniciando piloto.
pause
exit /b 1
