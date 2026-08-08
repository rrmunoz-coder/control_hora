@echo off
setlocal
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYTHON=K:\@@@@@ATLAS\.venv\Scripts\python.exe"
"%PYTHON%" "%ROOT%\pilot\set_knowledge_feature.py" false
if errorlevel 1 goto :error
sc.exe stop ATLAS_Conocimiento_Test >nul 2>&1
timeout /t 2 /nobreak >nul
sc.exe start ATLAS_Conocimiento_Test
if errorlevel 1 goto :error
echo Conocimiento DESHABILITADO en piloto.
pause
exit /b 0
:error
echo ERROR deshabilitando/reiniciando piloto.
pause
exit /b 1
