@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
rem Etapa 1 da importacao: inventario do OneDrive (so nomes, tamanhos e datas; nenhum arquivo e aberto).
set "PACOTE=%~dp0.."
set "SCRIPT=%PACOTE%\scripts\inventario_pastas.py"
for /f %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "HOJE=%%d"
set "CLIENTES="
for /f "usebackq delims=" %%c in (`powershell -NoProfile -Command "$m = Select-String -Path '%PACOTE%\escritorio.local.md' -Pattern 'Pasta Clientes: `(.+)`' -ErrorAction SilentlyContinue; if ($m) { $m.Matches[0].Groups[1].Value }"`) do set "CLIENTES=%%c"
if defined CLIENTES (
  set "SAIDA=!CLIENTES!\_inventario\inventario-%HOJE%"
) else (
  set "SAIDA=%USERPROFILE%\Desktop\Inventario OneDrive %HOJE%"
)
echo.
echo Inventario do OneDrive: so le nomes, tamanhos e datas. Nada e aberto, baixado, movido ou apagado.
echo Relatorio em: !SAIDA!
echo.
python "%SCRIPT%" --saida "!SAIDA!" %*
if errorlevel 1 (
  echo.
  echo OneDrive nao encontrado, ou ha mais de um. Arraste a pasta do OneDrive do escritorio para esta janela e tecle Enter:
  set /p "RAIZ=Pasta: "
  python "%SCRIPT%" --raiz !RAIZ! --saida "!SAIDA!"
)
if defined SEM_PAUSA goto :fim
if exist "!SAIDA!\resumo.md" start "" notepad "!SAIDA!\resumo.md"
echo.
echo Proximo passo: abrir o Claude Code na pasta Escritorio-Claude e pedir
echo "seguir a importacao do OneDrive" (skill importacao-onedrive).
pause
:fim
