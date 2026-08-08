@echo off
net session >nul 2>&1
if errorlevel 1 (
  echo ERROR: ejecuta como Administrador.
  pause
  exit /b 1
)
netsh advfirewall firewall show rule name="ATLAS Conocimiento TEST 5051" >nul 2>&1
if errorlevel 1 (
  netsh advfirewall firewall add rule name="ATLAS Conocimiento TEST 5051" dir=in action=allow protocol=TCP localport=5051
) else (
  echo La regla ya existe.
)
pause
