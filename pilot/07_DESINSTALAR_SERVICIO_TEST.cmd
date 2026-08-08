@echo off
setlocal
set "NSSM=K:\@@@@@ATLAS\service\nssm.exe"
net session >nul 2>&1
if errorlevel 1 (
  echo ERROR: ejecuta como Administrador.
  pause
  exit /b 1
)
if not exist "%NSSM%" (
  echo ERROR: no existe %NSSM%
  pause
  exit /b 1
)
"%NSSM%" stop ATLAS_Conocimiento_Test confirm >nul 2>&1
"%NSSM%" remove ATLAS_Conocimiento_Test confirm
sc.exe query ATLAS_Conocimiento_Test
pause
