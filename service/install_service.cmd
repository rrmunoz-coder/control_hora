@echo off
setlocal EnableExtensions

set "SERVICE_NAME=ATLAS_Web"
set "DISPLAY_NAME=ATLAS - Gestion de Capacidad"
set "SERVICE_DIR=%~dp0"
for %%I in ("%SERVICE_DIR%..") do set "APP_DIR=%%~fI"
set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"
set "ENTRY_FILE=%APP_DIR%\service_entry.py"
set "CONFIG_FILE=%APP_DIR%\config.ini"
set "LOG_DIR=%APP_DIR%\logs"

net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: ejecuta este archivo como Administrador.
    pause
    exit /b 1
)

set "NSSM=%SERVICE_DIR%nssm.exe"
if not exist "%NSSM%" (
    for /f "delims=" %%N in ('where nssm.exe 2^>nul') do (
        if not defined NSSM_FOUND set "NSSM_FOUND=%%N"
    )
    if defined NSSM_FOUND set "NSSM=%NSSM_FOUND%"
)

if not exist "%NSSM%" (
    echo ERROR: no se encontro nssm.exe.
    echo Copia NSSM x64 dentro de:
    echo %SERVICE_DIR%
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: no existe el Python del entorno virtual:
    echo %PYTHON_EXE%
    pause
    exit /b 1
)

if not exist "%ENTRY_FILE%" (
    echo ERROR: no existe:
    echo %ENTRY_FILE%
    pause
    exit /b 1
)

if not exist "%CONFIG_FILE%" (
    echo ERROR: no existe:
    echo %CONFIG_FILE%
    pause
    exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo.
echo Aplicacion: %APP_DIR%
echo Python:     %PYTHON_EXE%
echo Servicio:   %SERVICE_NAME%
echo.

sc.exe query "%SERVICE_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo El servicio ya existe. Se detendra y reinstalara.
    "%NSSM%" stop "%SERVICE_NAME%" confirm >nul 2>&1
    "%NSSM%" remove "%SERVICE_NAME%" confirm
)

"%NSSM%" install "%SERVICE_NAME%" "%PYTHON_EXE%"
if errorlevel 1 goto :error

"%NSSM%" set "%SERVICE_NAME%" AppDirectory "%APP_DIR%"
"%NSSM%" set "%SERVICE_NAME%" AppParameters "%ENTRY_FILE%"
"%NSSM%" set "%SERVICE_NAME%" DisplayName "%DISPLAY_NAME%"
"%NSSM%" set "%SERVICE_NAME%" Description "Plataforma web ATLAS Flask + Waitress + Oracle + LDAP"
"%NSSM%" set "%SERVICE_NAME%" Start SERVICE_AUTO_START
"%NSSM%" set "%SERVICE_NAME%" AppExit Default Restart
"%NSSM%" set "%SERVICE_NAME%" AppRestartDelay 5000
"%NSSM%" set "%SERVICE_NAME%" AppThrottle 1500
"%NSSM%" set "%SERVICE_NAME%" AppNoConsole 1

"%NSSM%" set "%SERVICE_NAME%" AppStdout "%LOG_DIR%\atlas_stdout.log"
"%NSSM%" set "%SERVICE_NAME%" AppStderr "%LOG_DIR%\atlas_stderr.log"
"%NSSM%" set "%SERVICE_NAME%" AppRotateFiles 1
"%NSSM%" set "%SERVICE_NAME%" AppRotateOnline 1
"%NSSM%" set "%SERVICE_NAME%" AppRotateBytes 10485760
"%NSSM%" set "%SERVICE_NAME%" AppRotateSeconds 86400

sc.exe failure "%SERVICE_NAME%" reset= 86400 actions= restart/5000/restart/10000/restart/30000
sc.exe failureflag "%SERVICE_NAME%" 1

"%NSSM%" start "%SERVICE_NAME%"
if errorlevel 1 goto :error

echo.
echo Servicio instalado e iniciado.
sc.exe query "%SERVICE_NAME%"
echo.
echo Logs:
echo %LOG_DIR%\atlas_stdout.log
echo %LOG_DIR%\atlas_stderr.log
pause
exit /b 0

:error
echo.
echo ERROR al instalar o iniciar el servicio.
echo Revisa:
echo %LOG_DIR%\atlas_stderr.log
pause
exit /b 1
