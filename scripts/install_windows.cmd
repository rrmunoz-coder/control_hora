@echo off
setlocal

set DESTINO=%~1
if "%DESTINO%"=="" set DESTINO=K:\@@@@@ATLAS

echo Instalando ATLAS en %DESTINO%

if not exist "%DESTINO%" mkdir "%DESTINO%"

xcopy "%~dp0.." "%DESTINO%" /E /I /Y

echo.
echo Completar config.ini desde config.ini.example antes de iniciar el servicio.
echo Luego ejecutar service\install_service.cmd o service\restart_service.cmd.

endlocal
