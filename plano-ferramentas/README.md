# Plano de instalação das ferramentas do Claude

Plano para instalar as 18 ferramentas escolhidas em 2026-10-21, **pelo Claude Code sempre que possível**. Cobre as três frentes: geoprocessamento e fiscalização ambiental, escritório de advocacia e organização pessoal.

Este plano vale para a **sua conta**. A instalação na conta da advogada segue o `pacote-advocacia/ferramentas/`, com as regras de lá.

Legenda: `[ ]` pendente · `[~]` instalado, em teste · `[x]` aprovado para uso

## Como cada item é instalado

Nem tudo pode ser feito só pelo terminal. Três situações:

| Tipo | Quem faz | Itens |
|---|---|---|
| **Pelo Claude Code, por mim**, em arquivos do repositório (`.claude/`, `CLAUDE.md`, skills) | Eu, com a sua aprovação em cada commit | 1, 2, 15, 16, 17, 18, e plugins 7, 11 e 12 via configuração |
| **Pelo Claude Code, com um passo seu** (autorizar login OAuth ou instalar no seu computador) | Você digita o comando ou autoriza no navegador | 9, 11, 12, 13, 14 |
| **Fora do terminal**, uma única vez | Você, no navegador ou no app | 10 (app desktop) e a autorização inicial dos conectores |

Os itens 3, 4, 5, 6 e 8 já estão disponíveis. Basta usar e testar.

## Regras gerais

1. **Uma fase por vez.** Só avance quando os testes da fase anterior passarem.
2. **Teste com dados fictícios** antes de usar com casos reais, principalmente em processos, autuações e dados de clientes.
3. **Conectores são lidos no início da sessão.** Depois de ligar um conector, abra uma sessão nova.
4. **Comandos e menus mudam.** Se um comando não funcionar, rode `/help` no Claude Code ou peça "como instalo X na versão atual".
5. **Nada é enviado sem a sua aprovação**: e-mail, protocolo, publicação ou mensagem a terceiros.
6. **Sessão na nuvem e terminal local são diferentes.** As sessões na nuvem (como esta) não acessam o seu computador. QGIS, Chrome e arquivos locais exigem o Claude Code instalado no seu computador ou o app desktop.

## Decisões a tomar antes de começar

- [x] **E-mail:** os dois, Gmail e Outlook (Microsoft 365). Item 13 conecta ambos.
- [x] **Gerenciador de tarefas:** Notion (recomendação aceita por padrão; pode ser trocado). Motivo: junta tarefas, notas e bases de dados (ex.: controle de embargos ou processos) num só lugar, tem plano pessoal gratuito, app no celular e interface em português. Asana é mais voltado a equipes; ClickUp é mais complexo de configurar.
- [x] **Pastas por frente:** `geoprocessamento/`, `pacote-advocacia/` e `pessoal/`, cada uma com `CLAUDE.md`.
- [x] **Claude Code no seu computador:** já instalado.

---

## Fase 1: Fundação (dia 1)

### 15. Contexto por frente (equivalente aos Projetos, no Claude Code)
- [~] **Estrutura criada e preenchida em 2026-10-21.** Falta o teste.
- **Como:** em vez de Projetos no claude.ai, cada frente vira uma pasta do repositório com seu próprio `CLAUDE.md` (instruções lidas automaticamente em toda sessão aberta ali).
- **Feito por mim:**
  1. Criar `geoprocessamento/CLAUDE.md`: padrões de carta imagem, fontes de imagem, sistema de coordenadas, regras de entrega.
  2. Criar `pessoal/CLAUDE.md`: rotina, prioridades, formato do planejamento.
  3. `pacote-advocacia/CLAUDE.md` já existe.
- **Opcional:** criar também os Projetos no claude.ai, para conversas pelo celular.
- **Teste:** abrir uma sessão na pasta e pedir "resuma as regras desta frente".

### 13. Conectores de e-mail (Gmail e Outlook)
- [x] **Gmail:** conectado em 2026-10-22.
- [x] **Outlook pessoal:** resolvido por encaminhamento para o Gmail (2026-10-22). Pendente: Outlook do IBAMA. Conector Microsoft 365: No histórico do pacote de advocacia ele aparecia com conexão incompleta; refaça a autorização.
  - **Decidido (2026-10-21):** o conector Microsoft 365 recusou o login, porque aceita apenas conta corporativa ou de estudante. Solução adotada: o Outlook pessoal encaminha para o Gmail, mantendo cópia no Outlook. O Claude lê o Outlook pelo conector do Gmail; respostas como Outlook continuam no próprio Outlook.
- **Como:** conecte uma vez em https://claude.ai/customize/connectors com a mesma conta do Claude Code. Os conectores da conta passam a aparecer nas sessões do Claude Code.
- **No terminal:** abra uma sessão nova e rode `/mcp` para confirmar que o conector aparece e está autenticado.
- **Recomendação:** exigir confirmação para envio.
- **Teste:** "liste os 5 e-mails mais recentes sem resposta". Depois: "rascunhe uma resposta ao segundo, sem enviar".

### 14. Gerenciador de tarefas: Notion
- [~] **Conectado e quadro criado em 2026-10-22**, com cinco frentes (Geo, Advocacia, Pessoal, DRE, Casa).
- **Como:** crie a conta em notion.so, se ainda não tiver. Depois, escolha um caminho:
  - **Pela conta:** conecte o conector Notion em https://claude.ai/customize/connectors e confira com `/mcp`.
  - **Pelo terminal local:** `claude mcp add --transport http notion https://mcp.notion.com/mcp`, depois `/mcp` para autenticar no navegador.
  - **Pelo plugin Productivity (item 11):** o plugin já traz o servidor do Notion; basta autenticar com `/mcp`.
- **Observação:** nesta sessão na nuvem, Notion e Asana falharam ao conectar porque o proxy da rede bloqueou. Para usar nas sessões na nuvem, é preciso liberar o domínio na política de rede do ambiente.
- **Montagem:** quadro com três colunas (A fazer, Fazendo, Feito) e etiquetas por frente (Geo, Advocacia, Pessoal).
- **Teste:** "crie a tarefa 'Teste de integração' na coluna A fazer, com etiqueta Pessoal" e confira no app.

## Fase 2: Produtividade e rotina (dias 2 e 3)

Depende da Fase 1.

### 11. Plugin Productivity (Anthropic)
- [~] **Instalado em 2026-10-22.** Falta o teste (skill `start` e planejamento do dia).
- **Pelo terminal:**
  ```
  /plugin marketplace add anthropics/knowledge-work-plugins
  /plugin install productivity@knowledge-work-plugins
  ```
- **Já declarado em `.claude/settings.json`** (2026-10-21), junto com o Legal. Ao abrir o Claude Code na pasta do repositório, ele pede para confiar no marketplace e instalar os plugins. Aceite e confira com `/plugin`.
- **O que traz:** skills de gestão de tarefas, planejamento do dia, memória de contexto e atualização de status.
- **Teste:** rodar a skill de início (`start`) e depois "planeje meu dia de amanhã com base na agenda e nas tarefas abertas".

### 3. Morning brief (`/morning`)
- [~] **Testado à mão em 2026-10-22** e agendado (item 2).
- **Pelo terminal:** digite `/morning` ou peça "configure meu morning brief". Defina o que entra: agenda, e-mails importantes, tarefas vencendo, prazos.
- **Teste:** rodar uma vez manualmente e ajustar.

### 2. Tarefas agendadas
- [~] **Rotinas 1 e 2 agendadas em 2026-10-22.** Rotinas 3 e 4 dependem da Fase 3.
- **Feito por mim:** eu crio as tarefas agendadas direto daqui, uma por vez, com o horário no seu fuso.
- **Rotinas propostas:**
  1. Morning brief: dias úteis, cedo.
  2. Revisão semanal: sábado ao meio-dia (antes era sexta à tarde), com o que foi feito, o que ficou e as prioridades seguintes.
  3. Alerta de prazos: diário, a partir da planilha de processos (depois da Fase 3).
  4. Novos embargos e autuações da semana, se houver fonte pública ou planilha de controle.
- **Teste:** revisar as saídas da primeira semana de cada rotina antes de manter.

## Fase 3: Documentos e dados (dias 4 a 6)

Já disponíveis. Falta padronizar o uso.

### 4. Claude Docs
- [~] **Doc de teste criado em 2026-10-22:** "Relatório técnico – Caso Teste 02 (fictício)", https://claude.ai/artifact/LUdd2LtUkBCuyKvGh6Pvwp. Comentário e exportação testados e aprovados.
- **Teste:** "crie um doc de relatório técnico de embargo com dados fictícios". Comente um trecho no doc e peça para o Claude responder ao comentário.
- **Uso:** pareceres, relatórios técnicos, minutas. Exporta para Word, PDF e Google Docs.
- **Cuidado:** verifique com quem o doc está compartilhado antes de pôr dados reais.

### 5. PDF + PDF Viewer
- [ ] **Teste:** com um PDF fictício ou público: extrair texto, gerar índice de peças, juntar dois arquivos, abrir no visualizador (`/pdf-viewer:open`) e anotar.
- **Cuidado:** número ou data extraído por OCR é conferido no original.

### 6. Planilhas (xlsx) + Google Sheets
- [~] **Criadas e testadas em 2026-10-22** (6 planilhas, dados fictícios).
- **Feito por mim, com a sua aprovação:** criar no Drive as planilhas-base (Controle de processos, Controle de embargos e cartas imagem, Financeiro), com dados fictícios.
- **Teste:** ler e atualizar uma linha de teste.

### 7. Dataviz + Build Dashboard (plugin Data, já instalado)
- [~] **Painel criado em 2026-10-22:** "Embargos e financeiro", https://claude.ai/artifact/LCcDSmG3U9bDie8wxxixUL (privado).
- **Teste:** a partir de uma planilha da Fase 3, "monte um painel com indicadores e gráficos".
- **Uso:** área desmatada por ano, embargos por município, receita e inadimplência do escritório.

## Fase 4: Navegação e automação de tela (semana 2)

Exige o seu computador. Não funciona nas sessões na nuvem.

### 9. Claude in Chrome
- [ ] **Passos:**
  1. Instale a extensão oficial "Claude" da Anthropic na loja do Chrome e confira o fornecedor.
  2. No Claude Code local, rode `/chrome` para conectar o terminal à extensão.
  3. Aprove só os sites necessários: SICAR, Planet, portais dos tribunais e dos órgãos ambientais.
- **Teste:** com você já logado, "consulte o imóvel X no SICAR e liste as informações, sem baixar nada".
- **Cuidado:** login, certificado digital, CAPTCHA e senhas ficam sempre com você.

### 10. App desktop com controle do computador (QGIS)
- [ ] **Exceção ao terminal:** o controle de tela funciona pelo app desktop do Claude (Windows ou Mac). Instale o app, ative o controle do computador nas configurações e, no Mac, conceda acessibilidade e gravação de tela.
- **Teste:** com um projeto QGIS de cópia, "abra o projeto de teste, atualize o Atlas e exporte o layout em PDF".
- **Alternativa pelo terminal:** automatizar o QGIS por script PyQGIS, sem controle de tela. É mais rápido e repetível. Avaliar junto com a skill `producao-carta-imagem`.

## Fase 5: Pesquisa e jurídico (semana 2)

### 8. Deep Research
- [ ] **Teste:** "pesquise as normas federais e estaduais sobre embargo de área por desmatamento ilegal e gere um relatório com fontes".
- **Cuidado:** toda norma ou decisão citada é conferida na fonte oficial.

### 12. Plugin Legal (Anthropic)
- [~] **Instalado em 2026-10-22.** Falta o teste com contrato fictício.
- **Pelo terminal** (o marketplace do item 11 já estará adicionado):
  ```
  /plugin install legal@knowledge-work-plugins
  ```
- **O que traz:** revisão de contratos, avaliação de risco, checagem de conformidade, briefing de reunião e pedido de assinatura.
- **Limite:** foi feito com foco nos EUA. Use pela estrutura e pelo método, nunca como fonte de direito brasileiro.
- **Teste:** revisar um contrato fictício e comparar com a sua própria análise.
- **Registro:** atualizar o status em `pacote-advocacia/ferramentas/02-terceiros.md`.

## Fase 6: Ajustes no Claude Code (semana 2)

Feito por mim, em arquivos do repositório.

### 16. Hooks de segurança
- [~] **Gancho do SEI criado em 2026-10-22** (bloqueia assinar, enviar processo e senha no navegador); falta ver disparar no computador.
- Hook em `.claude/settings.json` que bloqueia envio de e-mail, mensagem ou protocolo sem confirmação explícita.
- **Teste:** pedir um envio e confirmar que o hook bloqueia.

### 17. Session Start Hook
- [ ] Script que instala Python, GDAL e rasterio nas sessões na nuvem, para os scripts de satélite rodarem direto.
- **Teste:** abrir uma sessão nova e rodar um recorte de imagem de teste.

### 18. Menos pedidos de permissão
- [ ] Rodar `/fewer-permission-prompts` depois de algumas semanas de uso, quando houver histórico suficiente.
- **Teste:** revisar a lista proposta antes de aplicar. Só comandos de leitura.

## Fase 7: Novas skills (contínuo, a partir da semana 3)

### 1. Skill Creator
- [ ] **Feito por mim:** as novas skills ficam em `.claude/skills/` de cada frente, versionadas no Git.
- **Candidatas:**
  1. Relatório técnico de embargo ou autuação.
  2. Análise de sobreposição com o CAR e áreas protegidas.
  3. Laudo de evolução da vegetação, a partir da skill de Landsat.
  4. Revisão semanal pessoal.
- **Teste:** rodar cada skill com um caso antigo já concluído e comparar.

---

## Cronograma resumido

| Fase | Itens | Quando | Depende de |
|---|---|---|---|
| 1. Fundação | 15, 13, 14 | Dia 1 | Decisões de e-mail e tarefas |
| 2. Produtividade | 11, 3, 2 | Dias 2 e 3 | Fase 1 |
| 3. Documentos e dados | 4, 5, 6, 7 | Dias 4 a 6 | Nenhuma |
| 4. Navegação e tela | 9, 10 | Semana 2 | Claude Code local e app desktop |
| 5. Pesquisa e jurídico | 8, 12 | Semana 2 | Item 11 (marketplace) |
| 6. Claude Code | 16, 17, 18 | Semana 2 | Item 18 só após semanas de uso |
| 7. Novas skills | 1 | Semana 3 em diante | Fases 1 a 5 |

## Para retomar

Atualizado em 2026-10-22, com as Fases 1 e 2 concluídas e a Fase 3 em andamento.

- **Feito:** clone em `C:\Users\Work\Projetos\antoniozildomarpa`, na branch `claude/modest-gates-nhyd9t`. Conectores Gmail, Calendar, Drive, Notion e QGIS ligados. Plugins Productivity, Legal e frontend-design instalados. Quadro de Tarefas no Notion com cinco frentes. `/morning` testado e duas rotinas agendadas (morning brief e revisão semanal). Planilhas-base criadas no Drive (ver registro).
- **Para continuar em qualquer sessão:** peça "leia `plano-ferramentas/README.md` e continue de onde paramos".

### Próximos passos

1. Fase 3: testar Claude Docs (item 4), PDF e visualizador (item 5) e painel com Dataviz (item 7).
2. Fase 5: testar o plugin Legal com contrato fictício (item 12) e o Deep Research (item 8).
3. Fase 6: hook que bloqueia envio sem confirmação (item 16).
4. E-mails pendentes: Outlook para a DRE não entrega; "Enviar e-mail como" do Hotmail no Gmail falha; regra de encaminhamento ainda ativa no Outlook do IBAMA.

## Registro de andamento

Anote aqui cada item concluído, com data e observações.

| Data | Item | Status | Observação |
|---|---|---|---|
| 2026-10-21 | Plano | criado | 18 ferramentas aprovadas; instalação preferencial pelo Claude Code |
| 2026-10-21 | Decisões | tomadas | Gmail e Outlook; Notion; Claude Code já instalado |
| 2026-10-21 | 15 | em teste | Pastas `geoprocessamento/` e `pessoal/` com `CLAUDE.md`; `CLAUDE.md` raiz como índice |
| 2026-10-21 | 11, 12 | declarados | Plugins Productivity e Legal em `.claude/settings.json`; falta instalar e testar |
| 2026-10-21 | 15 | preenchido | `[A CONFIRMAR]` resolvidos: SIRGAS 2000 geográficas, GMS, buffer por caso, saídas PDF/GeoTIFF/SHP-GPKG, modelo IBAMA; horário flexível, revisão sexta 16h |
| 2026-10-21 | 13, 14 | diagnóstico | No terminal local: Microsoft 365 e Notion (plugin Design) aguardam autenticação via `/mcp`; Gmail não está conectado na conta |
| 2026-10-21 | 13 | adiado | Microsoft 365 só aceita conta corporativa ou de estudante; alternativa para o Outlook a decidir (ver item 13) |
| 2026-10-21 | 13 | encaminhamento | Outlook encaminha para o Gmail, com cópia (configurado pelo usuário). Falta ligar o conector Gmail e testar |
| 2026-10-22 | 13 | Gmail ligado | Conector Gmail ativo no Claude Code local; encaminhamento do Outlook ainda sem teste |
| 2026-10-22 | 13 | concluído | Outlook (antoniozildomar@hotmail.com) encaminha para o Gmail, com cópia; teste confirmado pelo conector Gmail. Correção: o destino estava apontando para o próprio hotmail |
| 2026-10-22 | 14 | Notion ligado | Conector Notion ativo; `notion-get-self` confirmou o espaço "Espaço de Zildomar Oliveira" |
| 2026-10-22 | 14 | quadro criado | Banco "Quadro de Tarefas" (página privada no nível do espaço; a "Página inicial" não aceita bancos): Status A fazer/Fazendo/Feito, Frente Geo/Advocacia/Pessoal, Prazo; visão "Quadro" em kanban com filtro rápido por frente |
| 2026-10-22 | 3 | testado | `/morning` rodado uma vez à mão: dia sem agenda, nada pendente; renderização conferida |
| 2026-10-22 | 2 | agendado | Rotina "Morning brief (dias úteis 6h30)", `trig_01R96Tiu3XTWr9GeMyKUQHeU`: seg–sex 6h30 Brasília (cron `30 9 * * 1-5` UTC), nuvem B3, Sonnet 5.5; Calendar, Gmail, Slack e Notion; com botões de ação; entrega como artifact privado. Revisar as saídas da primeira semana |
| 2026-10-22 | 2 | agendado | Rotina "Revisão semanal (sábado 12h)", `trig_01WsrwYTSWqdUdjd3XUqAuyQ`: sábado 12h Brasília (cron `0 15 * * 6` UTC), nuvem B3, Sonnet 5.5; Notion, Calendar e Gmail; feito, ficou, próxima semana e e-mails sem resposta; entrega como artifact privado. Horário mudado de sexta 16h para sábado 12h a pedido do usuário |
| 2026-10-22 | 6 | criado e testado | Pasta "Planilhas base (teste)" no Drive com 6 planilhas Google, dados fictícios: Controle de processos; Controle de embargos e cartas imagem (área adotada por fórmula: duas de três fontes com diferença até 1%, senão a maior); Financeiro (abas Lançamentos e Recebimentos); Rotina Casa, Rotina DRE e Rotina ADV (próxima vez e situação por fórmula). Planilhas em pt_BR: fórmulas com `;` e decimais com vírgula. Leitura e atualização de linha conferidas |
| 2026-10-22 | 14 | frentes | Frentes DRE (roxo) e Casa (amarelo) acrescentadas ao Quadro de Tarefas; pedidos das duas rotinas atualizados com as cinco frentes |
| 2026-10-22 | 13 | pendente | Gmail da DRE: encaminhar para o Gmail principal (configuração do usuário), depois testar e criar marcador "DRE". Outlook do IBAMA: confirmar com a TI do órgão antes de encaminhar ou ligar o conector Microsoft 365 com a conta corporativa |
| 2026-10-22 | 13 | DRE encaminhando | Gmail institucional da DRE (SEDUC-PA) encaminha para o Gmail principal, com cópia; teste confirmado com dois e-mails vindos de outro Gmail. Marcador "DRE" criado; filtro automático fica com o usuário (o conector não cria filtros). Pendências: e-mails do Outlook para a DRE não chegaram nem na DRE; "Enviar e-mail como" do Hotmail no Gmail falha |
| 2026-10-22 | 9, 13 | IBAMA pelo Chrome | Encaminhamento do Outlook do IBAMA para o Gmail não entrega (bloqueio do órgão). Decisão do usuário: ler o Outlook web do IBAMA pelo Claude in Chrome, só leitura e sob pedido, sem entrar nas rotinas da nuvem. Teste: caixa aberta com a sessão já logada, sem abrir nem baixar mensagens. A regra de encaminhamento ainda aparece ativa no Outlook do IBAMA |
| 2026-10-22 | 11, 12 | instalados | Productivity e Legal ativos; conferido com `/mcp`. Gmail, Calendar, Drive, Notion e QGIS conectados. Servidores dos plugins (Figma, Box, Amplitude, Hex, Intercom) sem autenticação e Definite com endpoint quebrado, todos fora do plano. Plugin frontend-design instalado |
| 2026-10-22 | 7 | criado | Painel "Embargos e financeiro" (artifact privado LCcDSmG3U9bDie8wxxixUL), lendo ao vivo as planilhas Controle de embargos e Financeiro pelo conector Google Sheets: casos, área adotada, cartas pendentes, divergência entre fontes (TEI, AI, SEI), gráfico de áreas por caso, recebido, a receber, despesas e saldo. Verificação automática sem erros. Falta a sua revisão |
| 2026-10-22 | 4 | doc de teste | Relatório técnico fictício no Claude Docs (identificação, metodologia, análise das áreas com a regra de adoção, evolução da vegetação, conclusão com tarefas, anexos). Falta: comentar um trecho e pedir resposta; exportar para Word/PDF |
| 2026-10-22 | 4 | comentário ok | Comentário com @Claude no doc: linha Bioma incluída na tabela e resposta postada no próprio comentário; conferido pelo usuário |
| 2026-10-22 | 4 | exportação ok | Doc exportado e conferido na pasta Downloads. Claude Docs testado por completo |
| 2026-10-22 | 1, 16 | planejado | Plano da automação do fluxo SEI → análise → documento técnico → despacho em `geoprocessamento/automacao-sei/PLANO.md`: 9 etapas, 8 agentes, 10 skills novas, 4 conferências, fases A a I. Aguarda respostas às perguntas em aberto |
| 2026-10-22 | 1 | automação SEI: fases A e B | Scripts `caso.py`, `coordenadas.py` e `projeto_qgis.py` e skills `estrutura-caso`, `coordenadas-para-qgis` e `projeto-qgis-caso`. Testados na nuvem (QGIS 3.34) com casos fictícios; conferência de precisão contra o pyproj. Falta rodar no computador do usuário |
| 2026-10-22 | 1 | automação SEI: fase C | `figura_mapa.py` (área útil, legenda sobreposta no canto livre, escala e norte, UTM da zona, 300 dpi), `estilos.py` (paleta suave por papel) e skills `figura-mapa-legenda` e `padrao-cartografico` (objetivo, cores suaves, sequência de mapas, elementos técnicos, conferência final). Testado na nuvem com QGIS 3.34 |
| 2026-10-22 | 1 | padrão cartográfico ampliado | Linhas finas; rótulos com buffer, sempre exibidos e revisados automaticamente; revisão e ajuste automático de brilho, contraste e saturação das imagens (`revisao_imagem.py`); grade só com traços na borda e intervalo pela escala; escala gráfica refinada com texto junto à barra |
| 2026-10-22 | 1 | automação SEI: fase D | `minuta.py` (Word a partir de conteúdo com marcadores: figuras, tabelas e anexos numerados, áreas e coordenadas dos dados do caso, ABNT para ilustrações, versões sem sobrescrever) e `revisar_minuta.py` (consistência); skill `redacao-documento-tecnico`; agentes `agente-redator` e `agente-revisor` em `.claude/agents/` |
| 2026-10-22 | 1 | automação SEI: fase E | `anexos.py` (anexos com nome e número da minuta, versões anteriores guardadas, verificação de PDF, zip, extensão e tamanho, manifesto) e zip de Geoinformação com todas as camadas em SHP, GPKG e KML e LEIA-ME; skill `anexos-e-pacote`; agente `agente-empacotador` |
| 2026-10-22 | 1 | automação SEI: fase H | `georreferenciar.py` (pontos em GMS, decimal ou UTM, qualquer datum; RMS de controle e de verificação em metros; ponto suspeito pela queda do RMS; limite caso a caso com referência de 0,2 mm na escala; GeoTIFF SIRGAS 2000; uso medição ou só ilustração); skill `georreferenciamento`; grade das figuras com GMS de dois dígitos |
| 2026-10-22 | 1, 16 | automação SEI: F, G, I e gancho | Skills `leitura-processo-sei`, `protocolo-sei` e `caso-sei`; agentes `agente-sei-leitura`, `agente-sei-protocolo`, `agente-leitor`, `agente-geo` e `agente-figuras`; gancho que bloqueia assinar, enviar processo e senha no navegador (item 16). Roteiro de teste no computador em `geoprocessamento/automacao-sei/TESTE_LOCAL.md` |
| 2026-10-22 | 1 | automação SEI: J | Agente `agente-imagens` (Landsat, Sentinel-2, ResourceSat-1 e Planet), a partir das skills `landsat-estilo-natural-tiarg` e `producao-carta-imagem`; integrado ao `agente-geo`, à `caso-sei`, ao `PLANO.md` e ao roteiro de teste. Decisão: a cor validada da skill prevalece para imagens baixadas |
