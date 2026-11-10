<#
Instalador do pacote de automação do escritório (Dra. Leulla Mendanha).

O que faz, na ordem:
  1. Instala, se faltarem: Git, Python 3.12, Node.js LTS (via winget) e o Claude Code (instalador oficial).
  2. Copia o pacote para a pasta do escritório (padrão: %USERPROFILE%\Escritorio-Claude), com backup se já existir.
  3. Grava escritorio.local.md com os caminhos das pastas Clientes e Financeiro.
  4. Instala as regras globais, as skills globais, o hook de sessão longa e o modelo de handoff em %USERPROFILE%\.claude,
     sem apagar o que já existe (faz backup e junta as configurações).
  5. Instala as bibliotecas Python e Node usadas pelos scripts.
  6. Cria as memórias iniciais do projeto.
  7. Baixa o modelo do Whisper (transcrição de áudio).
  8. Gera os .zip das skills para enviar ao Claude Desktop / claude.ai, se ela quiser usá-las fora do Claude Code.
  9. Confere a instalação e mostra os passos que só ela pode fazer (login, conectores, extensão do Chrome).

Nunca pede, lê ou grava senha, token ou certificado.

Uso normal: dois cliques em INSTALAR.cmd.
Uso avançado:
  powershell -ExecutionPolicy Bypass -File instalar.ps1 [-Destino <pasta>] [-PastaClientes <pasta>] [-PastaFinanceiro <pasta>]
      [-SemPrerequisitos] [-SemDependencias] [-SemWhisper] [-Teste] [-ClaudeHome <pasta>]
#>
param(
    [string]$Destino = "$env:USERPROFILE\Escritorio-Claude",
    [string]$PastaClientes = "",
    [string]$PastaFinanceiro = "",
    [string]$ClaudeHome = "$env:USERPROFILE\.claude",
    [switch]$SemPrerequisitos,
    [switch]$SemDependencias,
    [switch]$SemWhisper,
    [switch]$Teste
)

$ErrorActionPreference = "Stop"
$Origem = Split-Path -Parent $PSScriptRoot          # pasta pacote-advocacia
$Carimbo = Get-Date -Format "yyyyMMdd-HHmmss"
$Resumo = New-Object System.Collections.Generic.List[string]
$Pendencias = New-Object System.Collections.Generic.List[string]

function Etapa($texto) { Write-Host ""; Write-Host "== $texto" -ForegroundColor Cyan }
function Ok($texto) { Write-Host "   OK  $texto" -ForegroundColor Green; $Resumo.Add("OK   $texto") }
function Aviso($texto) { Write-Host "   !!  $texto" -ForegroundColor Yellow; $Resumo.Add("AVISO $texto") }
function Tem($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function AtualizaPath {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                "$env:USERPROFILE\.local\bin"
}
function Pergunta($texto, $padrao) {
    if ($Teste) { return $padrao }
    $r = Read-Host "$texto [$padrao]"
    if ([string]::IsNullOrWhiteSpace($r)) { return $padrao } else { return $r.Trim('"') }
}
function SalvaJson($obj, $caminho) {
    $json = ConvertTo-Json -InputObject $obj -Depth 30
    [IO.File]::WriteAllText($caminho, $json, (New-Object Text.UTF8Encoding $false))
}

Write-Host "Instalador do pacote do escritório" -ForegroundColor White
Write-Host "Origem:  $Origem"
Write-Host "Destino: $Destino"

# ---------------------------------------------------------------- 1. pré-requisitos
Etapa "1. Programas necessários"
if ($SemPrerequisitos) {
    Aviso "conferência de programas pulada (-SemPrerequisitos)"
} else {
    $programas = @(
        @{ cmd = "git";    id = "Git.Git";            nome = "Git" },
        @{ cmd = "python"; id = "Python.Python.3.12"; nome = "Python 3.12" },
        @{ cmd = "node";   id = "OpenJS.NodeJS.LTS";  nome = "Node.js LTS" }
    )
    foreach ($p in $programas) {
        if (Tem $p.cmd) { Ok "$($p.nome) já instalado" ; continue }
        if (-not (Tem "winget")) { Aviso "winget não encontrado: instale $($p.nome) manualmente"; $Pendencias.Add("Instalar $($p.nome)"); continue }
        Write-Host "   instalando $($p.nome)..."
        winget install --id $p.id -e --silent --accept-source-agreements --accept-package-agreements | Out-Null
        AtualizaPath
        if (Tem $p.cmd) { Ok "$($p.nome) instalado" } else { Aviso "$($p.nome) instalado, mas só aparece depois de reiniciar o Windows"; $Pendencias.Add("Reiniciar o computador e rodar o instalador de novo") }
    }
    if (Tem "claude") {
        Ok "Claude Code já instalado"
    } else {
        Write-Host "   instalando o Claude Code (instalador oficial da Anthropic)..."
        try {
            Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
            AtualizaPath
            if (Tem "claude") { Ok "Claude Code instalado" } else { Aviso "Claude Code instalado; abra um terminal novo para usar"; }
        } catch {
            Aviso "não foi possível instalar o Claude Code automaticamente: $($_.Exception.Message)"
            $Pendencias.Add("Instalar o Claude Code: https://claude.com/claude-code")
        }
    }
}
$Py = "python"
if (-not (Tem $Py) -and (Tem "py")) { $Py = "py" }

# ---------------------------------------------------------------- 2. cópia do pacote
Etapa "2. Pasta do escritório"
if (Test-Path $Destino) {
    $backup = "$Destino-backup-$Carimbo"
    robocopy $Destino $backup /E /NFL /NDL /NJH /NJS /NP | Out-Null
    Ok "backup da instalação anterior em $backup"
}
# /XO: não sobrescreve arquivo que ela editou depois (mais novo no destino)
robocopy $Origem $Destino /E /XO /XD ".git" "para-claude-ai" "__pycache__" "node_modules" /XF "escritorio.local.md" /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "falha ao copiar o pacote (robocopy $LASTEXITCODE)" }
Ok "pacote copiado para $Destino"

# ---------------------------------------------------------------- 3. caminhos locais
Etapa "3. Pastas de clientes e financeiro"
$local = Join-Path $Destino "escritorio.local.md"
if (Test-Path $local) {
    Ok "escritorio.local.md já existe (mantido)"
} else {
    if (-not $PastaClientes) {
        $sugestao = "$Destino\Clientes"
        foreach ($l in "G", "H", "I") { if (Test-Path "${l}:\Meu Drive") { $sugestao = "${l}:\Meu Drive\Escritorio\Clientes"; break } }
        $PastaClientes = Pergunta "Pasta Clientes (de preferência dentro do Google Drive)" $sugestao
    }
    if (-not $PastaFinanceiro) { $PastaFinanceiro = Pergunta "Pasta Financeiro" (Join-Path (Split-Path $PastaClientes -Parent) "Financeiro") }
    New-Item -ItemType Directory -Force $PastaClientes, $PastaFinanceiro | Out-Null
    $texto = @"
# Caminhos deste computador

Gerado pelo instalador em $(Get-Date -Format "yyyy-MM-dd HH:mm"). Ajuste aqui se as pastas mudarem.

- Pasta Clientes: ``$PastaClientes``
- Pasta Financeiro: ``$PastaFinanceiro``
- Planilha de honorários: ``$PastaFinanceiro\Controle_Honorarios.xlsx``
- Pasta do pacote: ``$Destino``

Toda referência a `Clientes/` nas skills e rotinas aponta para a pasta Clientes acima.
"@
    [IO.File]::WriteAllText($local, $texto, (New-Object Text.UTF8Encoding $false))
    Ok "escritorio.local.md gravado (Clientes: $PastaClientes)"
}

# ---------------------------------------------------------------- 4. configuração global
Etapa "4. Configuração global do Claude Code"
$g = Join-Path $PSScriptRoot "global"
$bkGlobal = Join-Path $ClaudeHome "backups\pacote-$Carimbo"
New-Item -ItemType Directory -Force (Join-Path $ClaudeHome "skills"), (Join-Path $ClaudeHome "hooks"), (Join-Path $ClaudeHome "templates") | Out-Null

foreach ($sk in Get-ChildItem (Join-Path $g "skills") -Directory) {
    $alvo = Join-Path $ClaudeHome "skills\$($sk.Name)"
    if (Test-Path $alvo) {
        robocopy $alvo (Join-Path $bkGlobal "skills\$($sk.Name)") /E /XD node_modules /NFL /NDL /NJH /NJS /NP | Out-Null
    }
    robocopy $sk.FullName $alvo /E /NFL /NDL /NJH /NJS /NP | Out-Null
    Ok "skill global $($sk.Name)"
}
Copy-Item (Join-Path $g "hooks\alerta_sessao.py") (Join-Path $ClaudeHome "hooks\") -Force
Copy-Item (Join-Path $g "templates\HANDOFF_modelo.md") (Join-Path $ClaudeHome "templates\") -Force
Ok "hook de sessão longa e modelo de handoff"

# CLAUDE.md global: bloco entre marcadores, substituído a cada instalação
$claudeMd = Join-Path $ClaudeHome "CLAUDE.md"
$ini = "<!-- inicio: pacote do escritorio -->"; $fim = "<!-- fim: pacote do escritorio -->"
$bloco = "$ini`r`n" + (Get-Content (Join-Path $g "CLAUDE.md") -Raw -Encoding UTF8) + "`r`n$fim"
if (Test-Path $claudeMd) {
    New-Item -ItemType Directory -Force $bkGlobal | Out-Null
    Copy-Item $claudeMd (Join-Path $bkGlobal "CLAUDE.md")
    $atual = Get-Content $claudeMd -Raw -Encoding UTF8
    $padrao = [regex]::Escape($ini) + "[\s\S]*?" + [regex]::Escape($fim)
    if ($atual -match $padrao) { $novo = [regex]::Replace($atual, $padrao, { param($m) $bloco }) }
    else { $novo = $atual.TrimEnd() + "`r`n`r`n" + $bloco }
} else { $novo = $bloco }
[IO.File]::WriteAllText($claudeMd, $novo, (New-Object Text.UTF8Encoding $false))
Ok "regras globais no CLAUDE.md (bloco do pacote)"

# settings.json global: só acrescenta o hook, sem mexer no resto
$settings = Join-Path $ClaudeHome "settings.json"
$cmdHook = "python `"" + ((Join-Path $ClaudeHome "hooks\alerta_sessao.py") -replace "\\", "/") + "`""
if (Test-Path $settings) {
    New-Item -ItemType Directory -Force $bkGlobal | Out-Null
    Copy-Item $settings (Join-Path $bkGlobal "settings.json")
    $cfg = Get-Content $settings -Raw -Encoding UTF8 | ConvertFrom-Json
} else { $cfg = New-Object PSObject }
if (-not $cfg.PSObject.Properties["hooks"]) { $cfg | Add-Member -NotePropertyName hooks -NotePropertyValue (New-Object PSObject) }
if (-not $cfg.hooks.PSObject.Properties["UserPromptSubmit"]) { $cfg.hooks | Add-Member -NotePropertyName UserPromptSubmit -NotePropertyValue @() }
$jaTem = $false
foreach ($grupo in @($cfg.hooks.UserPromptSubmit)) { foreach ($h in @($grupo.hooks)) { if ($h.command -like "*alerta_sessao.py*") { $jaTem = $true } } }
if (-not $jaTem) {
    $novoGrupo = [PSCustomObject]@{ hooks = @([PSCustomObject]@{ type = "command"; command = $cmdHook; timeout = 10; statusMessage = "Verificando tamanho da sessao..." }) }
    $cfg.hooks.UserPromptSubmit = @(@($cfg.hooks.UserPromptSubmit) + $novoGrupo)
    SalvaJson $cfg $settings
    Ok "hook de sessão longa registrado no settings.json"
} else { Ok "hook de sessão longa já estava no settings.json" }

# ---------------------------------------------------------------- 5. bibliotecas
Etapa "5. Bibliotecas Python e Node"
if ($SemDependencias) {
    Aviso "instalação de bibliotecas pulada (-SemDependencias)"
} else {
    $req = Join-Path $PSScriptRoot "requirements.txt"
    if ($SemWhisper) {
        $tmp = Join-Path $env:TEMP "req-sem-whisper.txt"
        Get-Content $req | Where-Object { $_ -notmatch "^(faster-whisper|av)" } | Set-Content $tmp -Encoding ASCII
        $req = $tmp
    }
    & $Py -m pip install --user --upgrade -r $req
    if ($LASTEXITCODE -eq 0) { Ok "bibliotecas Python instaladas" } else { Aviso "pip terminou com erro; veja as mensagens acima"; $Pendencias.Add("Rever a instalação das bibliotecas Python") }
    $scriptsReq = Join-Path $ClaudeHome "skills\requerimento-revisao-proventos\scripts"
    if ((Tem "npm") -and (Test-Path (Join-Path $scriptsReq "package.json"))) {
        Push-Location $scriptsReq; npm install --silent | Out-Null; Pop-Location
        Ok "biblioteca docx (Node) da skill de revisão de proventos"
    } else { Aviso "npm não encontrado: a skill requerimento-revisao-proventos não gera o Word até instalar o Node.js" }
}

# ---------------------------------------------------------------- 6. memórias
Etapa "6. Memórias iniciais"
$codificado = ($Destino -replace "[^A-Za-z0-9]", "-")
$mem = Join-Path $ClaudeHome "projects\$codificado\memory"
New-Item -ItemType Directory -Force $mem | Out-Null
$indice = Join-Path $mem "MEMORY.md"
$linhas = @()
if (Test-Path $indice) { $linhas = @(Get-Content $indice -Encoding UTF8) }
foreach ($f in Get-ChildItem (Join-Path $PSScriptRoot "memoria") -Filter *.md) {
    $alvo = Join-Path $mem $f.Name
    if (-not (Test-Path $alvo)) { Copy-Item $f.FullName $alvo }
    $desc = (Select-String -Path $f.FullName -Pattern "^description:\s*(.+)$" | Select-Object -First 1).Matches.Groups[1].Value
    $linha = "- [$($f.BaseName)]($($f.Name)) - $desc"
    if (-not ($linhas | Where-Object { $_ -like "*($($f.Name))*" })) { $linhas += $linha }
}
[IO.File]::WriteAllLines($indice, [string[]]$linhas, (New-Object Text.UTF8Encoding $false))
Ok "memórias em $mem"

# ---------------------------------------------------------------- 7. Whisper
Etapa "7. Modelo de transcrição (Whisper)"
if ($SemWhisper -or $SemDependencias -or $Teste) {
    Aviso "download do modelo pulado; acontece no primeiro uso"
} else {
    & $Py (Join-Path $Destino "scripts\transcrever.py") --baixar-modelo --modelo small
    if ($LASTEXITCODE -eq 0) { Ok "modelo small do Whisper baixado" } else { Aviso "modelo não baixado agora; será baixado no primeiro uso" }
}

# ---------------------------------------------------------------- 8. zips para o claude.ai
Etapa "8. Skills em .zip para o Claude Desktop / claude.ai"
$zips = Join-Path $Destino "instalacao\para-claude-ai"
New-Item -ItemType Directory -Force $zips | Out-Null
$pastasSkills = @(Get-ChildItem (Join-Path $Destino ".claude\skills") -Directory) + @(Get-ChildItem (Join-Path $g "skills") -Directory)
foreach ($sk in $pastasSkills) {
    $z = Join-Path $zips "$($sk.Name).zip"
    if (Test-Path $z) { Remove-Item $z -Force }
    Compress-Archive -Path $sk.FullName -DestinationPath $z
}
Ok "$($pastasSkills.Count) skills em $zips"

# ---------------------------------------------------------------- 9. conferência
Etapa "9. Conferência"
$verif = @(
    @{ nome = "Python";      teste = { & $Py --version 2>&1 } },
    @{ nome = "Claude Code"; teste = { claude --version 2>&1 } },
    @{ nome = "Node.js";     teste = { node --version 2>&1 } }
)
foreach ($v in $verif) {
    try { $saida = & $v.teste; if ($LASTEXITCODE -eq 0 -or $saida) { Ok "$($v.nome): $saida" } else { Aviso "$($v.nome) não respondeu" } }
    catch { Aviso "$($v.nome) não encontrado" }
}
if (-not $SemDependencias) {
    $mods = "pymupdf,rapidocr_onnxruntime,markitdown,img2pdf,PIL,openpyxl,docx"
    if (-not $SemWhisper) { $mods += ",faster_whisper,av" }
    $faltam = & $Py -c "import importlib.util as u; print(','.join(m for m in '$mods'.split(',') if not u.find_spec(m)))"
    if ($faltam) { Aviso "bibliotecas faltando: $faltam"; $Pendencias.Add("Instalar bibliotecas: $faltam") } else { Ok "bibliotecas Python presentes" }
}
$tmpPastas = Join-Path $env:TEMP "teste-pastas-$Carimbo"
$saidaPastas = & $Py (Join-Path $Destino "estrutura\criar_pastas.py") --base $tmpPastas --area "Consumidor" --cliente "Cliente Ficticio" --dry-run 2>&1
if ($LASTEXITCODE -eq 0) { Ok "criar_pastas.py (simulação)" } else { Aviso "criar_pastas.py falhou: $saidaPastas" }
$sigTeste = Join-Path $env:TEMP "teste-sigilo-$Carimbo"
New-Item -ItemType Directory -Force $sigTeste | Out-Null
Set-Content (Join-Path $sigTeste "SIGILOSO.txt") "teste" -Encoding ASCII
$payload = '{"tool_name":"Read","tool_input":{"file_path":"' + ((Join-Path $sigTeste "doc.pdf") -replace "\\", "/") + '"}}'
$resp = $payload | & $Py (Join-Path $Destino ".claude\hooks\bloqueio_sigiloso.py")
if ($resp -match '"deny"') { Ok "hook de sigilo bloqueia pasta com SIGILOSO.txt" } else { Aviso "hook de sigilo não bloqueou o teste" }
Remove-Item $sigTeste, $tmpPastas -Recurse -Force -ErrorAction SilentlyContinue

# ---------------------------------------------------------------- final
$relatorio = Join-Path $Destino "instalacao\ultima-instalacao.txt"
$texto = "Instalação de $Carimbo`r`nDestino: $Destino`r`n`r`n" + ($Resumo -join "`r`n") + "`r`n`r`nPendências:`r`n" + (($Pendencias | ForEach-Object { "- $_" }) -join "`r`n")
[IO.File]::WriteAllText($relatorio, $texto, (New-Object Text.UTF8Encoding $false))

Write-Host ""
Write-Host "Instalação concluída. Relatório: $relatorio" -ForegroundColor White
if ($Pendencias.Count) { Write-Host "Pendências:" -ForegroundColor Yellow; $Pendencias | ForEach-Object { Write-Host "  - $_" } }
Write-Host @"

Passos que só a advogada pode fazer (ver instalacao\LEIA-ME.md):
  1. Abrir o terminal, entrar na pasta e fazer login:  cd "$Destino"  e depois  claude
  2. No claude.ai (Configurações > Conectores): ligar Google Drive, Google Agenda e o e-mail do escritório.
  3. No Chrome: instalar a extensão Claude in Chrome e entrar com a conta dela.
  4. Instalar o Google Drive para computador, para a pasta Clientes ficar no disco.
  5. Criar no Google Agenda a agenda "Prazos – Escritório".
  6. Seguir o checklist-instalacao.md, na ordem.
"@
