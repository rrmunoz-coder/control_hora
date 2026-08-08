@echo off
setlocal EnableExtensions
set "PROD=K:\@@@@@ATLAS"
set "PYTHON=%PROD%\.venv\Scripts\python.exe"
set "SERVICE=ATLAS_Conocimiento_Test"

echo ============================================================
echo ATLAS - PRECHECK PILOTO CONOCIMIENTO 5051
echo ============================================================

if not exist "%PROD%\config.ini" (
  echo ERROR: falta %PROD%\config.ini
  exit /b 1
)
if not exist "%PYTHON%" (
  echo ERROR: falta Python productivo conocido: %PYTHON%
  exit /b 1
)
if not exist "%~dp0..\service_entry.py" (
  echo ERROR: el paquete piloto no esta completo.
  exit /b 1
)

netstat -ano | findstr /R /C:"TCP .*:5051 .*LISTENING" >nul
if not errorlevel 1 (
  echo ERROR: el puerto TCP 5051 ya esta en uso.
  netstat -ano | findstr /R /C:"TCP .*:5051 .*LISTENING"
  exit /b 1
)

sc.exe query "%SERVICE%" >nul 2>&1
if not errorlevel 1 (
  echo AVISO: el servicio %SERVICE% ya existe.
  sc.exe query "%SERVICE%"
) else (
  echo OK: servicio piloto aun no instalado.
)

echo OK: config productivo disponible.
echo OK: venv productivo disponible para reutilizacion read-only.
echo OK: puerto 5051 libre.
echo.
echo El ATLAS productivo 5050 NO sera modificado.
pause
