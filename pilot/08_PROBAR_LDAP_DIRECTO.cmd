@echo off
setlocal
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PYTHON=K:\@@@@@ATLAS\.venv\Scripts\python.exe"
pushd "%ROOT%"
"%PYTHON%" tools\test_ldap_bind.py
popd
pause
