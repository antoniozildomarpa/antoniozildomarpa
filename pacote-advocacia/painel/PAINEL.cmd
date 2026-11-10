@echo off
chcp 65001 >nul
title Painel do escritorio
rem Abre o painel do escritorio no navegador. Deixe esta janela aberta (pode minimizar).
rem Com /fundo (atalho da inicializacao do Windows), liga o painel sem abrir o navegador.
cd /d "%~dp0.."
set ABRIR=--abrir
if /i "%~1"=="/fundo" set ABRIR=
if not exist "escritorio.local.md" (
  echo O pacote ainda nao foi instalado neste computador. Abrindo a demonstracao com dados ficticios.
  python "%~dp0servidor.py" --demo %ABRIR%
) else (
  python "%~dp0servidor.py" %ABRIR%
)
if errorlevel 3 if not errorlevel 4 exit /b 0
echo.
echo O painel foi fechado.
if /i not "%~1"=="/fundo" pause
