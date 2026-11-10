@echo off
chcp 65001 >nul
title Painel do escritorio - demonstracao
rem Demonstracao com dados ficticios. PINs de treino: Dra. Leulla 111111, Colaboradora 1 222222, Colaboradora 2 333333.
python "%~dp0servidor.py" --demo --abrir --porta 8766
pause
