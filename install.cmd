@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PYTHON_BASE=%~1"
if "%PYTHON_BASE%"=="" set "PYTHON_BASE=python"

echo ATLAS S.2.0 - instalacion Python
echo Python base: %PYTHON_BASE%

if not exist ".venv\Scripts\python.exe" (
    "%PYTHON_BASE%" -m venv .venv
    if errorlevel 1 goto :error
)

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto :error

if not exist config.ini (
    copy config.ini.example config.ini >nul
    echo Se creo config.ini desde el perfil HTTPS recomendado.
    echo Edita Oracle, LDAP, CA y secret_key antes de iniciar.
)

.venv\Scripts\python.exe scripts\validar_release.py
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m compileall -q atlas tests *.py tools
if errorlevel 1 goto :error

echo.
echo Instalacion Python completada.
echo Siguiente: editar config.ini, ejecutar SQL y seguir docs\INSTALACION_S_2_0.md
exit /b 0

:error
echo ERROR durante la instalacion. Revisa la salida anterior.
exit /b 1
