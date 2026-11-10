# Pacote de automação para advocacia

Conjunto de skills, instruções, modelos e roteiros de rotinas para apoiar o trabalho de uma advogada profissional liberal. O pacote é feito para ser copiado para a conta dela e usado com Claude Code, app desktop do Claude e Claude in Chrome.

> **Este pacote não contém dados de clientes.** Exemplos são fictícios. Dados reais devem ficar apenas na conta da advogada.

## Conteúdo

| Caminho | Função |
|---|---|
| `CLAUDE.md` | Regras gerais que valem em toda sessão do pacote |
| `.claude/skills/analise-demanda/` | Analisa uma demanda a partir dos documentos da pasta e propõe a ação |
| `.claude/skills/triagem-email/` | Filtra e organiza e-mails recebidos, salva anexos e registra prazos |
| `.claude/skills/pesquisa-juridica/` | Pesquisa legislação e jurisprudência, com verificação das fontes |
| `.claude/skills/minuta/` | Redige a minuta para revisão, com citações marcadas |
| `.claude/skills/consulta-portais/` | Consulta e download somente leitura em portais, com login feito pela advogada |
| `.claude/skills/agenda-prazos/` | Lança prazos, audiências e ações na agenda "Prazos – Escritório" do Google Agenda |
| `.claude/skills/leitura-documentos/` | Índice local de PDFs e documentos, para ler só o necessário |
| `.claude/skills/tratamento-documentos/` | Fotos e digitalizações para PDF legível e leve |
| `.claude/skills/cadastro-clientes/` | Cadastro por área a partir dos nomes das pastas, com aprovação |
| `.claude/skills/ficha-atendimento/` | Ficha do cliente a partir da gravação do atendimento (Whisper) |
| `.claude/skills/honorarios/` | Lança honorários dos contratos na planilha de controle |
| `.claude/skills/whatsapp-escritorio/` | WhatsApp Web do escritório (desligada até a advogada ativar) |
| `.claude/agents/` | Agentes `triagem-documentos`, `rotina-escritorio` e `revisao-juridica` |
| `.claude/hooks/bloqueio_sigiloso.py` | Barra leitura e escrita em pastas com `SIGILOSO.txt` |
| `.claude/settings.json` | Permissões do projeto e registro do hook de sigilo |
| `scripts/` | Scripts locais: PDF, documentos, fotos, áudio, cadastro, honorários |
| `instalacao/` | Instalador automático (`INSTALAR.cmd`), configuração global, memórias iniciais e guia (`LEIA-ME.md`) |
| `propostas/whatsapp.md` | Proposta para ligar o WhatsApp do escritório à automação (aguarda decisão) |
| `estrutura/criar_pastas.py` | Cria a árvore padrão por área, cliente e caso, com as fichas |
| `estrutura/processos-acompanhados-modelo.md` | Modelo da lista de processos do levantamento de andamentos |
| `rotinas/` | Roteiros das rotinas recorrentes (texto, frequência, conectores) |
| `modelos/` | Local para os modelos de peça do escritório |
| `respostas/questionario.md` | Questionário respondido pela advogada, base das regras do `CLAUDE.md` |
| `checklist-instalacao.md` | Passo a passo de instalação e primeiro uso |

## Princípios

1. **Revisão humana sempre.** Nenhuma minuta, resposta ou protocolo é enviado sem aprovação da advogada.
2. **Credenciais são da advogada.** Senha, certificado digital e autenticação em duas etapas nunca são tratados pelo agente.
3. **Protocolo é manual** nas primeiras fases de uso. A automação prepara, a advogada protocola.
4. **Citações são verificadas.** Toda referência a lei ou acórdão é marcada até ser conferida na fonte oficial.
5. **Prazos são conferidos.** O cálculo automático é ponto de partida, não resposta final.
6. **Sigilo.** Dados de clientes ficam apenas na conta da advogada e em pastas do escritório.

## Como usar

No computador dela: dois cliques em `instalacao/INSTALAR.cmd` (detalhes em `instalacao/LEIA-ME.md`). Depois, seguir o `checklist-instalacao.md`. O que veio da conta de origem e o que ficou de fora está em `instalacao/O-QUE-FOI-PORTADO.md`.
