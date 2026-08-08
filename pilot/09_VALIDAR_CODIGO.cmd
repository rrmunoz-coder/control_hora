@echo off
setlocal
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYTHON=K:\@@@@@ATLAS\.venv\Scripts\python.exe"
pushd "%ROOT%"
"%PYTHON%" -m compileall -q atlas tests *.py tools
if errorlevel 1 goto :error
"%PYTHON%" -c "import pytest" >nul 2>&1
if errorlevel 1 (
  echo AVISO: pytest no esta instalado en el venv productivo; se omite pytest en servidor.
) else (
  "%PYTHON%" -m pytest -q
  if errorlevel 1 goto :error
)
popd
echo VALIDACION OK
pause
exit /b 0
:error
popd
echo VALIDACION CON ERROR
pause
exit /b 1
