@echo off
setlocal
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYTHON=K:\@@@@@ATLAS\.venv\Scripts\python.exe"

echo === SERVICIO ===
sc.exe query ATLAS_Conocimiento_Test

echo.
echo === PUERTO 5051 ===
netstat -ano | findstr /R /C:"TCP .*:5051 .*LISTENING"

echo.
echo === CONFIG NO SENSIBLE ===
pushd "%ROOT%"
"%PYTHON%" -c "from atlas import create_app; a=create_app(); print('port=',a.config['ATLAS_PORT']); print('cookie=',a.config['SESSION_COOKIE_NAME']); print('knowledge=',a.config['KNOWLEDGE_ENABLED']); print('storage=',a.config['KNOWLEDGE_STORAGE_PATH']); print('ldap_cert=',a.config['LDAP_VALIDATE_CERTIFICATE']); print('tls_ciphers=',a.config['LDAP_TLS_CIPHERS'])"
popd

echo.
echo === HTTP LOCAL ===
powershell -NoProfile -Command "try {$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5051/login' -TimeoutSec 10; Write-Host ('HTTP '+$r.StatusCode+' OK')} catch {Write-Host ('ERROR HTTP: '+$_.Exception.Message); exit 1}"

echo.
echo Logs: %ROOT%\logs\atlas_knowledge_test_stderr.log
pause
