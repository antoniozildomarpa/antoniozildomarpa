@echo off
chcp 65001 >nul
title Painel no celular
rem Liga o acesso do celular ao painel pela rede particular do Tailscale (so aparelhos da conta do escritorio).
rem Requer: Tailscale instalado e conectado neste computador, e o painel aberto (PAINEL.cmd).
where tailscale >nul 2>nul
if errorlevel 1 (
  echo O Tailscale nao esta instalado. Baixe em https://tailscale.com/download e entre com a conta do escritorio.
  pause
  exit /b 1
)
echo Ligando o acesso pelo Tailscale (somente aparelhos da conta do escritorio)...
tailscale serve --bg --https=443 http://127.0.0.1:8765
echo.
tailscale serve status
echo.
echo Abra no celular o endereco https://...ts.net mostrado acima e adicione a tela inicial.
echo Para desligar o acesso: tailscale serve --https=443 off
pause
