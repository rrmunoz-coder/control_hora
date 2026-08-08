@echo off
setlocal EnableExtensions
set "SERVICE=ATLAS_Conocimiento_Test"
set "DISPLAY=ATLAS - Conocimiento TEST"
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYTHON=K:\@@@@@ATLAS\.venv\Scripts\python.exe"
set "ENTRY=%ROOT%\service_entry.py"
set "NSSM=K:\@@@@@ATLAS\service\nssm.exe"
set "LOGDIR=%ROOT%\logs"

net session >nul 2>&1
if errorlevel 1 (
  echo ERROR: ejecuta como Administrador.
  pause
  exit /b 1
)
if not exist "%NSSM%" (
  echo ERROR: no existe NSSM productivo: %NSSM%
  pause
  exit /b 1
)
if not exist "%PYTHON%" (
  echo ERROR: no existe Python productivo: %PYTHON%
  pause
  exit /b 1
)
if not exist "%ROOT%\config.ini" (
  echo ERROR: primero ejecuta 01_PREPARAR_PILOTO.cmd
  pause
  exit /b 1
)
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

sc.exe query "%SERVICE%" >nul 2>&1
if not errorlevel 1 (
  "%NSSM%" stop "%SERVICE%" confirm >nul 2>&1
  "%NSSM%" remove "%SERVICE%" confirm
)

"%NSSM%" install "%SERVICE%" "%PYTHON%"
if errorlevel 1 goto :error
"%NSSM%" set "%SERVICE%" AppDirectory "%ROOT%"
"%NSSM%" set "%SERVICE%" AppParameters "%ENTRY%"
"%NSSM%" set "%SERVICE%" DisplayName "%DISPLAY%"
"%NSSM%" set "%SERVICE%" Description "Piloto ATLAS modulo de conocimiento - puerto 5051"
"%NSSM%" set "%SERVICE%" Start SERVICE_DEMAND_START
"%NSSM%" set "%SERVICE%" AppExit Default Restart
"%NSSM%" set "%SERVICE%" AppRestartDelay 5000
"%NSSM%" set "%SERVICE%" AppNoConsole 1
"%NSSM%" set "%SERVICE%" AppStdout "%LOGDIR%\atlas_knowledge_test_stdout.log"
"%NSSM%" set "%SERVICE%" AppStderr "%LOGDIR%\atlas_knowledge_test_stderr.log"
"%NSSM%" set "%SERVICE%" AppRotateFiles 1
"%NSSM%" set "%SERVICE%" AppRotateOnline 1
"%NSSM%" set "%SERVICE%" AppRotateBytes 10485760

"%NSSM%" start "%SERVICE%"
if errorlevel 1 goto :error

timeout /t 2 /nobreak >nul
sc.exe query "%SERVICE%"
netstat -ano | findstr /R /C:"TCP .*:5051 .*LISTENING"
echo.
echo Piloto: http://claroprod985:5051/login
echo Produccion sigue en: http://claroprod985:5050
pause
exit /b 0

:error
echo ERROR instalando/iniciando %SERVICE%
echo Revisa %LOGDIR%\atlas_knowledge_test_stderr.log
pause
exit /b 1
