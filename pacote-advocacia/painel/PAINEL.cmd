@echo off
chcp 65001 >nul
title Painel do escritorio
rem Abre o painel do escritorio no navegador. Deixe esta janela aberta (pode minimizar).
cd /d "%~dp0.."
if not exist "escritorio.local.md" (
  echo O pacote ainda nao foi instalado neste computador. Abrindo a demonstracao com dados ficticios.
  python "%~dp0servidor.py" --demo --abrir
) else (
  python "%~dp0servidor.py" --abrir
)
echo.
echo O painel foi fechado.
pause
