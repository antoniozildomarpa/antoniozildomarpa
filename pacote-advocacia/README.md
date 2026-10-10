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
| `estrutura/criar_pastas.py` | Cria a árvore padrão de pastas de um cliente ou processo |
| `rotinas/` | Roteiros das rotinas recorrentes (texto, frequência, conectores) |
| `modelos/` | Local para os modelos de peça do escritório |
| `checklist-instalacao.md` | Passo a passo de instalação e primeiro uso |

## Princípios

1. **Revisão humana sempre.** Nenhuma minuta, resposta ou protocolo é enviado sem aprovação da advogada.
2. **Credenciais são da advogada.** Senha, certificado digital e autenticação em duas etapas nunca são tratados pelo agente.
3. **Protocolo é manual** nas primeiras fases de uso. A automação prepara, a advogada protocola.
4. **Citações são verificadas.** Toda referência a lei ou acórdão é marcada até ser conferida na fonte oficial.
5. **Prazos são conferidos.** O cálculo automático é ponto de partida, não resposta final.
6. **Sigilo.** Dados de clientes ficam apenas na conta da advogada e em pastas do escritório.

## Como usar

Leia o `checklist-instalacao.md` antes do primeiro uso.
