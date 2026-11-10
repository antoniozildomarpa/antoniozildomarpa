# O que veio da conta de origem e o que ficou de fora

Inventário feito em 2026-11-10 na configuração do Claude Code da conta onde o pacote foi montado. Critério: levar tudo o que serve à advocacia; deixar de fora geoprocessamento, uso pessoal e qualquer dado real de cliente.

## Portado

| Item | Origem | Ajuste feito |
|---|---|---|
| Regras globais de escrita sem cara de IA | `CLAUDE.md` global | Sem as regras da operação de geoprocessamento |
| Skill `escrita-sem-cara-de-ia` | skills globais | Sem mudança |
| Skill `requerimento-revisao-proventos` (IPASET, Gratificação de Ensino Especial) | skills globais | Exemplo trocado por dados fictícios; nomes, CPF e números de processo reais retirados; caminhos genéricos; citações das leis marcadas para conferência |
| Hook de aviso de sessão longa | `hooks/alerta_sessao.py` | Mensagem adaptada a clientes e processos |
| Modelo de HANDOFF | `templates/` | Reescrito para casos jurídicos |
| Leitura econômica de PDF e documentos | skill `economia-tokens-documentos` | Reescrita como `scripts/ler_pdf.py` e `scripts/converter_docs.py`, só com processamento local (sem Gemini, sem chaves de API), com classificação de peças jurídicas |
| Modelo de três agentes (triagem barata, rotina, revisão) | `agents/` | Recriados para o escritório: `triagem-documentos`, `rotina-escritorio`, `revisao-juridica` |
| Memória do papel timbrado | memória do projeto | Caminho relativo ao pacote |
| Pacote do escritório (skills, rotinas, propostas, questionário, papel timbrado) | repositório | Caminhos locais trocados por relativos |

## Novo, criado para o escritório

Skills `leitura-documentos`, `tratamento-documentos`, `cadastro-clientes`, `ficha-atendimento`, `honorarios` e `whatsapp-escritorio` (desligada até ela ativar); scripts `tratar_imagens.py`, `transcrever.py`, `mapear_pastas.py` e `lancar_honorario.py`; hook `bloqueio_sigiloso.py`; permissões que bloqueiam envio e exclusão de e-mail, exclusão de evento e compartilhamento de arquivo pelo Drive.

## Ficou de fora, e por quê

| Item | Motivo |
|---|---|
| Skills de Landsat, carta imagem e a triagem IBAMA/SEI; memórias de QGIS, pareceres e operações | Geoprocessamento |
| Agents `triagem-haiku`, `revisao-opus`, `redacao-sonnet` | Escritos para processos ambientais; substituídos pelos três agentes do escritório |
| Agent de ficção | Uso pessoal |
| Memórias de casos de revisão de aposentadoria e de precatórios | Têm nomes e dados de clientes reais. As regras de método que estão nelas (leitura de contracheque, hierarquia de fontes) podem ser reescritas sem dados, se ela quiser usar no escritório |
| Plugins `claude-mem`, `task-observer`, `headroom` | De terceiros; gravam o histórico das sessões em bancos próprios. Com dados de clientes, o risco não compensa |
| Plugins `ralph-loop`, `context7`, `microsoft-docs`, `dataverse`, `security-guidance`, `claude-code-setup`, `frontend-design`, `youdotcom` | Ferramentas de programação ou de outros sistemas, sem uso no escritório |
| Skills padrão da Anthropic (Word, PDF, Excel, PowerPoint, pesquisa, navegador) | Já vêm em toda conta Claude; aparecem sozinhas na conta dela |
| Configuração de permissões amplas (`dontAsk`, comandos liberados) | Adequada a quem programa; para o escritório o padrão é perguntar antes de agir |
| Credenciais, histórico de conversas, chaves de API | Nunca são transferidos |

## Sugestões para depois

- Plugin oficial de área jurídica da Anthropic (repositório `knowledge-work-plugins`), se existir na conta dela e se fizer sentido para o direito brasileiro: testar com dados fictícios antes `[VERIFICAR]`.
- Conectores de jurisprudência e legislação brasileiros: seguir `ferramentas/02-terceiros.md`, com teste antes de instalar.
