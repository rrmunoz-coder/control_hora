@echo off
setlocal EnableExtensions
set "SERVICE_NAME=ATLAS_Web"
set "SERVICE_DIR=%~dp0"
for %%I in ("%SERVICE_DIR%..") do set "APP_DIR=%%~fI"
set "NSSM=%SERVICE_DIR%nssm.exe"

echo === SC CONFIG ===
sc qc "%SERVICE_NAME%"
echo.
echo === SC STATUS ===
sc query "%SERVICE_NAME%"

echo.
if exist "%NSSM%" (
    echo === NSSM ===
    echo Application:
    "%NSSM%" get "%SERVICE_NAME%" Application
    echo AppParameters:
    "%NSSM%" get "%SERVICE_NAME%" AppParameters
    echo AppDirectory:
    "%NSSM%" get "%SERVICE_NAME%" AppDirectory
    echo AppEnvironmentExtra:
    "%NSSM%" get "%SERVICE_NAME%" AppEnvironmentExtra
) else (
    echo NSSM no esta copiado en service\. Se omite lectura interna.
)

echo.
echo === PUERTO 5050 ===
netstat -ano | findstr :5050

echo.
echo === RUNTIME PYTHON ===
if exist "%APP_DIR%\.venv\Scripts\python.exe" (
    "%APP_DIR%\.venv\Scripts\python.exe" -c "import sys; print('executable=',sys.executable); print('prefix=',sys.prefix); print('base_prefix=',sys.base_prefix)"
    "%APP_DIR%\.venv\Scripts\python.exe" "%APP_DIR%\tools\diagnose_runtime.py"
) else (
    echo No existe .venv\Scripts\python.exe
)

echo.
echo === LOG ATLAS ===
if exist "%APP_DIR%\logs\atlas.log" (
    powershell -NoProfile -Command "Get-Content -Path '%APP_DIR%\logs\atlas.log' -Tail 30"
) else (
    echo No existe logs\atlas.log
)

pause
