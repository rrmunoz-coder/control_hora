@echo off
setlocal EnableExtensions
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYTHON=K:\@@@@@ATLAS\.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
  echo ERROR: falta %PYTHON%
  pause
  exit /b 1
)

"%PYTHON%" "%ROOT%\pilot\preparar_config_piloto.py"
if errorlevel 1 goto :error

pushd "%ROOT%"
"%PYTHON%" -c "from atlas import create_app; a=create_app(); print('CONFIG_OK port=',a.config['ATLAS_PORT'],'cookie=',a.config['SESSION_COOKIE_NAME'],'knowledge=',a.config['KNOWLEDGE_ENABLED'])"
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" goto :error

echo.
echo OK: piloto preparado con conocimiento APAGADO.
echo Siguiente paso: ejecutar SQL 70 y luego SQL 71 en DBeaver.
pause
exit /b 0

:error
echo ERROR preparando el piloto. No instales el servicio hasta corregirlo.
pause
exit /b 1
