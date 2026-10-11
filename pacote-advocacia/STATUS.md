# Status do pacote de advocacia

Este arquivo é o ponto de partida para retomar o trabalho, em qualquer sessão. Atualize-o a cada etapa concluída.

Última atualização: 2026-10-11

## Onde estamos

- **Fase atual:** coleta de respostas da advogada (questionário de 23 perguntas, entregue por você a ela).
- **Pacote inicial:** criado e commitado (commit `e333d19`), em rascunho. Não foi testado com caso real.
- **Estrutura de pastas:** o padrão atual é só uma proposta. A advogada já tem pastas organizadas por cliente e processo, então o pacote deve se adaptar ao que existe, não o contrário.

## Decisões já tomadas

1. Ela usará Claude in Chrome, app desktop do Claude e Claude Code, conforme a necessidade de cada ação.
2. Consultas em portais serão somente leitura e download, com a sessão dela. Peticionamento fica manual nas primeiras fases.
3. Credenciais, senhas, certificado digital e autenticação em duas etapas nunca são tratados pelo agente.
4. Nenhum envio de e-mail, protocolo ou resposta a cliente sem aprovação explícita dela.
5. Toda citação jurídica é marcada `[VERIFICAR]` até conferência na fonte oficial.
6. Dados de clientes ficam só na conta dela. O pacote não contém dados reais.
7. O pacote é portável: skills, instruções, modelos e roteiros são transferidos. Conexões, rotinas agendadas e acessos são recriados na conta dela.
8. **Toda a implementação real (cadastro automático de clientes, painel financeiro, planilha e rotinas) será feita na conta dela**, não nesta sessão.
9. **Esta sessão não lê nem processa dados reais de clientes.** Os conectores aqui (Drive, Calendar) pertencem à conta do usuário que está conduzindo o trabalho, não à advogada. Nesta sessão, só usamos dados fictícios.
10. Painel financeiro: arquivo HTML local, com lançamento por formulário, pensado para computador e celular.
11. Backup automático: proposta de usar uma planilha do Google Sheets na conta dela como base única, com o painel HTML por cima. O histórico de versões do Drive faz o backup. Aguarda confirmação dela.
12. Cadastro automático de clientes: mapear primeiro os nomes de pastas e arquivos; extrair só campos mínimos (nome, número CNJ, tribunal, vara, área, situação); gerar lista proposta com origem de cada dado; ela aprova antes de qualquer importação. Não altera documentos.

## Pendências

- [ ] Confirmar a planilha do Google Sheets como base do financeiro (decisão 11).
- [ ] Informar onde ficam as pastas: Google Drive, OneDrive/SharePoint ou computador local.
- [ ] Respostas ao questionário (blocos A a F), a serem salvas em `respostas/questionario.md`.
- [ ] Confirmar se ela autoriza a leitura apenas dos **nomes** de pastas e arquivos, para mapear a organização atual.
- [ ] Definir área de atuação e tribunais principais (questões A e B).
- [ ] Verificar se há processos em **segredo de justiça** e se precisam de regras separadas (questão 22).
- [ ] Confirmar quais dados podem sair do computador dela (questão 23).
- [ ] Respostas financeiras (regime, formas de recebimento, tipos de honorário, valores de terceiros, controle atual).
- [ ] Definir como ela terá acesso ao repositório (ver "Acesso ao repositório").
- [ ] Revisar `CLAUDE.md` e skills com base nas respostas.
- [ ] Criar a ficha de processo (tribunal, instância, sistema, fase, próximo prazo, status), por causa dos muitos processos em andamento.
- [ ] Protótipo do painel financeiro com dados fictícios, para teste em computador e celular.
- [ ] Script de backup e sincronização na conta dela, com o passo a passo de instalação.
- [ ] Cadastro automático de clientes, na conta dela, com revisão antes da importação.
- [ ] Teste com caso fictício, conforme `checklist-instalacao.md`.
- [ ] Criar as rotinas na conta dela, uma por vez.
- [ ] Testar as ferramentas nativas, na ordem de `ferramentas/README.md`, com dados fictícios.
- [ ] Verificar a cobertura do Brasil no Legal Data Hunter antes de qualquer instalação.
- [ ] Testar o conector da Jurídico AI com dez decisões e comparar com a fonte oficial.
- [ ] Conferir as normas do CNJ e dos tribunais em que ela atua sobre uso de IA em processos, e registrar em `03 Análise/normas-ia.md` (ver `CLAUDE.md`, seção de qualidade e autoria).
- [ ] Reunir de duas a três peças antigas já aprovadas por ela, para servirem de referência de estilo na skill `minuta`.

## Ferramentas em avaliação

Índice e critérios em `ferramentas/README.md`. Ordem: primeiro as nativas do Claude, depois as de terceiros.

- **Nativas:** skills de Word, PDF e planilha; Claude Docs; visualização (dataviz); Claude Code; rotinas agendadas; Claude in Chrome; app desktop. Detalhes em `ferramentas/01-claude-nativo.md`.
- **Terceiros:** conector de jurisprudência da Jurídico AI; servidores comunitários para dados públicos de tribunais; plugin "Legal"; Legal Data Hunter (verificar se cobre o Brasil); Stintwell. Detalhes em `ferramentas/02-terceiros.md`.
- **Descartadas:** ferramentas de EUA, Espanha, Emirados, Vietnã e Japão, e LegalizaObra por enquanto.

Todas as ferramentas estão pendentes de teste. Nenhuma foi instalada nesta sessão.

## Premissas em aberto

- E-mail: Gmail ou Outlook ainda não definido. Só o Outlook (Microsoft 365) aparece como conector, com conexão incompleta.
- Local das pastas: Drive, OneDrive/SharePoint ou outro, ainda não confirmado.
- Sistema de gestão de processos: não definido.
- Acesso ao repositório: o repositório é privado, na conta do usuário. Para que ela trabalhe a partir dele, é preciso adicioná-la como colaboradora ou exportar o pacote como arquivo.

## Acesso ao repositório

Opções para ela começar na conta dela:

1. **Colaboradora no repositório privado**, para clonar e trabalhar nele com o Claude Code.
2. **Exportar o pacote** como arquivo compactado e importar na conta dela, sem histórico do Git.

## Para retomar

1. Ler este arquivo.
2. Ler `respostas/` (quando existir).
3. Ler `README.md` e `CLAUDE.md`.
4. Continuar pela primeira pendência não marcada.
