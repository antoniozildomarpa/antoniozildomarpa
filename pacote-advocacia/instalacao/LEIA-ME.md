# Instalação no computador do escritório

Pacote preparado em 2026-11-10 para a conta Claude da Dra. Leulla Mendanha. Windows 10 ou 11.

## Antes de começar

- Plano do Claude dela ativo (Pro ou Max), com login no navegador.
- Conta Google do escritório (Drive e Agenda).
- Uns 3 GB livres no disco (Python, Node, bibliotecas e o modelo do Whisper).
- Internet durante a instalação.

## Instalação automática

1. Copie a pasta `pacote-advocacia` (ou descompacte o .zip) para qualquer lugar do computador dela, por exemplo a Área de Trabalho.
2. Abra `pacote-advocacia\instalacao` e dê dois cliques em `INSTALAR.cmd`.
3. Se o Windows perguntar se permite alterações (instalação do Git, Python e Node), responda Sim.
4. O instalador pergunta onde fica a pasta `Clientes`. Se o Google Drive para computador já estiver instalado, ele sugere `G:\Meu Drive\Escritorio\Clientes`; basta apertar Enter ou digitar outro caminho.
5. Ao final aparece o resumo. O relatório fica em `Escritorio-Claude\instalacao\ultima-instalacao.txt`.

Se algum programa acabou de ser instalado e o instalador pedir, reinicie o computador e rode `INSTALAR.cmd` de novo. Rodar mais de uma vez não duplica nada.

### O que o instalador faz

| Onde | O que |
|---|---|
| Programas | Git, Python 3.12 e Node.js (pelo winget), Claude Code (instalador oficial da Anthropic) |
| `%USERPROFILE%\Escritorio-Claude` | O pacote: regras do escritório, 12 skills, 3 agentes, hook de sigilo, scripts, rotinas, modelos e papel timbrado |
| `%USERPROFILE%\.claude` | Regras globais de escrita, skills `escrita-sem-cara-de-ia` e `requerimento-revisao-proventos`, aviso de sessão longa e modelo de handoff. O que já existir é guardado em `.claude\backups` e as configurações são juntadas, não substituídas |
| Bibliotecas | Leitura de PDF com OCR, conversão de Word e Excel, tratamento de fotos, planilha, transcrição de áudio (Whisper) |
| Memórias | Três memórias iniciais do projeto (papel timbrado, leitura econômica de documentos, estado da automação) |

O instalador não pede, não lê e não grava senha, token ou certificado.

## Passos que só ela pode fazer

1. **Login no Claude Code.** Abrir o PowerShell, digitar `cd "$env:USERPROFILE\Escritorio-Claude"` e depois `claude`. Na primeira vez, o navegador abre para ela entrar com a conta dela. Depois, o Claude Code pergunta se confia na pasta: responder que sim (sem isso, as permissões do projeto ficam desligadas).
2. **Conectores.** No claude.ai, em Configurações > Conectores: Google Drive, Google Agenda e o e-mail do escritório (Gmail ou Outlook, ainda a definir).
3. **Claude in Chrome.** Instalar a extensão pela Chrome Web Store e entrar com a conta dela.
4. **Google Drive para computador.** Para a pasta `Clientes` existir no disco e o Claude Code enxergá-la.
5. **Agenda "Prazos – Escritório".** Criar no Google Agenda e ligar as notificações do app no celular.
6. **Claude Desktop (opcional).** Para usar as skills também no app ou no claude.ai: Configurações > Capacidades > Skills > enviar os `.zip` de `Escritorio-Claude\instalacao\para-claude-ai` `[VERIFICAR o caminho do menu]`.

Depois disso, seguir o `checklist-instalacao.md`, na ordem.

## Uso no dia a dia

- Abrir o Claude Code sempre na pasta `Escritorio-Claude` (é ali que as regras, as skills e o hook de sigilo valem). No app Claude Desktop, aba Code, escolher essa pasta.
- Para marcar um processo em segredo de justiça: criar um arquivo `SIGILOSO.txt` na pasta do caso.
- Se a conversa ficar longa, o aviso de sessão longa sugere abrir outra e gerar um `HANDOFF.md`.

## Atualizações

Nova versão do pacote: substituir a pasta `pacote-advocacia` e rodar `INSTALAR.cmd` de novo. Arquivos que ela editou depois da última instalação (por exemplo, o `STATUS.md`) não são sobrescritos, e a instalação anterior inteira fica guardada em `Escritorio-Claude-backup-<data>`.

## Opções avançadas

`powershell -ExecutionPolicy Bypass -File instalar.ps1 -Destino "D:\Escritorio-Claude" -PastaClientes "G:\Meu Drive\Escritorio\Clientes" -SemWhisper`

- `-SemWhisper`: não instala a transcrição de áudio (economiza cerca de 1 GB).
- `-SemPrerequisitos`: não confere nem instala Git, Python, Node e Claude Code.
- `-SemDependencias`: não instala bibliotecas.
