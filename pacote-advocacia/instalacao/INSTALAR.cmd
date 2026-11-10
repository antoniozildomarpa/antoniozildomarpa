@echo off
rem Instalador do pacote do escritorio. Dois cliques para rodar.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1" %*
echo.
pause
