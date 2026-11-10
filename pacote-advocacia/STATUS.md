# Status do pacote de advocacia

Este arquivo é o ponto de partida para retomar o trabalho, em qualquer sessão. Atualize-o a cada etapa concluída.

Última atualização: 2026-11-10

## Pacote de instalação (2026-11-10)

O pacote está pronto para ser instalado no computador da advogada, na conta Claude dela: dois cliques em `instalacao/INSTALAR.cmd` (guia em `instalacao/LEIA-ME.md`). O inventário do que veio da conta de origem e do que ficou de fora (geoprocessamento, uso pessoal, dados reais de clientes) está em `instalacao/O-QUE-FOI-PORTADO.md`.

Testes feitos aqui, só com dados fictícios: os seis scripts de `scripts/` (PDF com OCR, conversão de Word, fotos para PDF com correção de rotação e brilho e limite de tamanho, transcrição pelo Whisper, cadastro por nomes de pastas com aprovação, lançamento de honorários); o hook de sigilo (sete casos, incluindo o Claude Code de verdade barrando a leitura); o instalador numa pasta falsa, duas vezes seguidas, sem duplicar configurações e preservando as que já existiam; o Claude Code enxergando as 12 skills e os 3 agentes do projeto. Não testados aqui: a instalação dos programas pelo winget e o instalador oficial do Claude Code (este computador já os tinha).

## Painel do escritório (protótipo, 2026-11-10)

Pasta `painel/`. O usuário pediu em 2026-11-10 um painel com ícones para que a advogada e as colaboradoras não precisem usar o terminal. Ele deve funcionar no computador e no celular, inclusive fora do escritório.

- **Servidor:** `painel/servidor.py`, em Python puro. Escuta só em 127.0.0.1:8765.
- **Atalhos:** `PAINEL.cmd` abre o painel. `DEMONSTRACAO.cmd` abre a versão com dados fictícios. `PAINEL-NO-CELULAR.cmd` liga o acesso remoto pelo `tailscale serve`, só para os aparelhos da conta do escritório, e nunca abre o painel na internet.
- **Perfis e PIN:** o PIN tem 6 números e fica só como hash PBKDF2 em `painel/usuarios.json`, que não vai para o GitHub. A primeira configuração só pode ser feita no próprio computador. Cinco erros bloqueiam o perfil por 5 minutos. A sessão fica em cookie HttpOnly e SameSite=Strict, e as ações exigem o cabeçalho X-Painel.
- **Telas:**
  - início com indicadores, ações rápidas, próximos prazos e fichas pendentes;
  - prazos, com conferência só pela advogada;
  - clientes e ficha: "Conferido" registra quem conferiu, só a advogada decide dado em conflito e a aba Documentos lista os arquivos da pasta;
  - fotos para PDF, com câmera ou arquivos;
  - atendimento: grava no navegador e transcreve pelo Whisper;
  - pedir ao Claude (`claude -p` com a skill certa);
  - novo cliente e honorários;
  - importação do OneDrive em cinco passos;
  - tarefas e instruções para usar no celular.
- **Visual:** paleta e logomarca do cartão. Os ícones de aplicativo para o celular saem do monograma, com manifesto e service worker. O service worker não guarda dados de clientes no aparelho.
- **Segurança no servidor:** pastas sigilosas não aparecem nem contam. Nenhum caminho sai da pasta Clientes, e nenhum botão apaga arquivo. Antes de alterar uma ficha, o painel guarda uma cópia em `_historico-ficha/`.

Testado com dados fictícios, no navegador automatizado:
- tela de entrada (computador e celular), início e ficha no tamanho de computador;
- PIN errado recusado;
- colaboradora barrada ao decidir;
- conferência recusada quando a ficha mudou;
- tentativa de sair da pasta do cliente e de abrir a pasta sigilosa, as duas recusadas.

Corrigido no teste: a pasta sigilosa entrava na contagem de clientes.

Falta:
1. Testar as telas no tamanho de celular.
2. Testar de ponta a ponta fotos, gravação e honorários.
3. Conferir os comandos do Tailscale e se ele envia o cabeçalho X-Forwarded-For e o X-Forwarded-Proto `[VERIFICAR]`.
4. Fazer o instalador criar o atalho do painel e iniciá-lo com o Windows.
5. Fazer a skill `agenda-prazos` gravar também em `Clientes/_painel/prazos.csv`, que é o arquivo que o painel lê.

## Importação do OneDrive e ficha cadastral (2026-11-10)

Preparado para rodar no computador dela, na conta dela. O usuário decidiu em 2026-11-10 que a varredura das pastas reais acontece lá, e não nesta conta. Skill `importacao-onedrive`, em cinco etapas com aprovação entre elas:
1. Inventário: `inventario_pastas.py`, ou dois cliques em `instalacao/INVENTARIO-ONEDRIVE.cmd`. Lê só nomes, tamanhos e datas.
2. Cópia aprovada: `migrar_pastas.py`. Copia para `Clientes/{Área}/{Cliente}/_importado-onedrive/` e não altera o OneDrive.
3. Extração: `extrair_cliente.py`. Lê PDF com OCR, Word (inclusive .doc antigo, pelo Word), Excel, fotos e HEIC, e-mail, texto e áudio (com `--audio`). Separa os dados candidatos, cada um com a fonte, e descarta os dados do próprio escritório.
4. Ficha: `ficha-cliente.md`, a partir de `modelos/ficha-cliente-modelo.md`, com fonte e `[CONFIRMAR]` em cada dado.
5. Planilha geral: `consolidar_cadastro.py`.

Pastas com `SIGILOSO.txt` não são listadas, copiadas nem lidas. O instalador libera para o Claude Code as pastas Clientes, Financeiro e o OneDrive (este só quando houver um único). A leitura do conteúdo depende de autorização dela, porque a questão 12 cobriu só nomes. A autorização é registrada em `Clientes/_inventario/andamento.md`.

Testado aqui com um OneDrive fictício: procuração em PDF, petição em Word, foto de RG, e-mail, áudio e vídeo, pasta sigilosa e um segundo cliente. Resultados:
- a cópia rodou duas vezes sem duplicar;
- a extração encontrou CPF, RG, NIT, nascimento, estado civil, profissão, filiação, endereço, CEP, telefone, e-mail, CNJ e NB;
- a planilha contou os `[CONFIRMAR]` e `[DECIDIR]`.

Limite visto: o OCR de foto junta palavras e pode perder linhas.

Durante o teste do atalho, o script pegou o OneDrive real deste computador, porque só uma das variáveis de ambiente tinha sido trocada. Ele listou nomes e totais. O relatório foi apagado sem ser aberto. Só os totais apareceram na conversa. Daí veio a correção: com mais de um OneDrive, o script e o instalador não escolhem sozinhos.

## Onde estamos

- **Fase atual:** questionário respondido, salvo em `respostas/questionario.md`. É o original de outubro (blocos A a F, 23 perguntas), recuperado em 2026-11-09 de um .txt na Área de Trabalho do usuário, com as respostas dela. Das 23 perguntas, 21 estão respondidas; a 22 (segredo de justiça) e a 23 (dados que podem sair do computador) estão parciais. O bloco G (financeiro, perguntas 24 a 28) foi acrescentado e está pendente. Em 2026-11-10, o `CLAUDE.md`, as cinco skills, o script de pastas, as rotinas e o checklist foram revisados com base nas respostas (ver "Revisão de 2026-11-10"). Próximo passo: criar os modelos de documento sobre o papel timbrado.
- **Principais respostas:** previdenciário (RPPS cerca de 100 processos, RGPS cerca de 50), família e sucessões (50), público (50), consumidor (15), ambiental (4). Trabalha no TJPA, cerca de 100 processos na 1ª instância e 15 na 2ª, principalmente pelo PJe e pelo INSS. Escritório individual com duas colaboradoras, que também mexem em pastas e prazos. Os prazos são controlados em agenda física, e já houve perda e quase perda de prazo. As pastas estão por área e por cliente, hoje no OneDrive, com migração planejada para o Google Drive. Não tem modelos de peça nem sistema de gestão. Autorizou a leitura dos nomes de pastas e arquivos.
- **Papel timbrado:** a advogada escolheu o modelo A, que está em `H:\Meu Drive\_advocacia\logomarca\modelos-papel-timbrado\modelo_timbrado_A.docx` (faixa azul texturizada com onda e filetes dourados). A inscrição foi confirmada como **OAB/PA 25.617** e já está corrigida na arte da 1ª página, no rodapé das páginas seguintes e na procuração de exemplo. Os modelos de documento (procuração, contrato de honorários, declaração de hipossuficiência, petição e requerimento) serão montados sobre esse papel em `modelos/`.
- **Pacote inicial:** criado e commitado (commit `e333d19`), em rascunho. Não foi testado com caso real.
- **Estrutura de pastas:** padrão novo `Clientes/{Área}/{Cliente}/{Caso}/`, seguindo a organização dela por área e por cliente (questão 8). Pastas existentes não são movidas sem aprovação; os nomes das áreas serão ajustados depois do mapeamento.

## Revisão de 2026-11-10

- `CLAUDE.md`: seção "Perfil do escritório"; processos em segredo de justiça fora da automação (pasta marcada com `SIGILOSO.txt`); limites de ação mantidos apesar da resposta 21, com aprovação de envio e protocolo só pela advogada; minutas automáticas permitidas como rascunho; prazos administrativos (INSS, regime próprio) com regra própria e mesma prioridade dos judiciais; CPC, art. 219, marcado `[VERIFICAR]`; nova estrutura de pastas com `ficha-cliente.md` e `ficha-processo.md`; papel timbrado A e documentos de praxe.
- `analise-demanda`: novo caminho de pastas, parada em `SIGILOSO.txt`, fases administrativas e contrarrazões, prazos do INSS e feriados locais, atualização da ficha do caso.
- `triagem-email`: prioridade para PJe e INSS, conteúdo e anexos salvos na pasta do caso, anotação na ficha, análise e minuta `v1` automáticas para itens urgentes com prazo. `remetentes.md` e `ultima-triagem.txt` passam para a raiz da pasta `Clientes`.
- `minuta`: papel timbrado A, OAB/PA 25.617 preenchida, documentos de praxe de caso novo (procuração, contrato, declaração de hipossuficiência), estrutura do requerimento administrativo e das contrarrazões.
- `pesquisa-juridica`: TJPA, STF e TRF1 primeiro; legislação municipal e do instituto no RPPS; normas do INSS.
- `consulta-portais`: PJe do TJPA e Meu INSS como portais principais; exigências do INSS anotadas na ficha.
- `estrutura/criar_pastas.py`: recebe `--area`, `--processo` ou `--inss`, cria a pasta do cliente e a do caso com as fichas, nunca sobrescreve e acrescenta o caso novo na ficha do cliente. Testado com dados fictícios.
- Rotinas, checklist, `README.md` e `modelos/README.md` ajustados.

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

- [ ] Confirmar a planilha do Google Sheets como base do financeiro (decisão 11; questão 24).
- [x] Informar onde ficam as pastas: hoje no OneDrive, com migração para o Google Drive (questão 9, 2026-11-09).
- [x] Salvar o questionário (blocos A a F) em `respostas/questionario.md` (2026-11-09).
- [x] Respostas ao questionário original: 21 respondidas, 22 e 23 parciais (2026-11-09).
- [ ] Fechar as questões 22 (segredo de justiça fora da automação ou com regras próprias) e 23 (confirmar que dados de clientes podem ser processados na conta dela).
- [ ] Respostas do bloco G (financeiro, questões 24 a 28).
- [x] Escolher o papel timbrado: modelo A (2026-11-09).
- [x] Confirmar a OAB: OAB/PA 25.617 (2026-11-09).
- [ ] Criar os modelos de procuração, contrato de honorários, declaração de hipossuficiência, petição e requerimento sobre o modelo A, em `modelos/`, com dados fictícios e citações marcadas `[VERIFICAR]`.
- [x] Autorização para ler apenas os **nomes** de pastas e arquivos: autorizado (questão 12, 2026-11-09).
- [x] Área de atuação e tribunais principais (blocos A e B, 2026-11-09).
- [ ] Definir como ela terá acesso ao repositório (ver "Acesso ao repositório").
- [x] Revisar `CLAUDE.md` e skills com base nas respostas (2026-11-10).
- [x] Criar a ficha de processo (tribunal, instância, sistema, fase, próximo prazo, status): gerada pelo `criar_pastas.py` (2026-11-10).
- [x] Etapa de levantamento de andamentos nos portais (2026-11-10): aviso à advogada, login feito por ela, leitura pelo Claude dos processos de `processos-acompanhados.md`. Ver `rotinas/levantamento-andamentos.md` e a skill `consulta-portais`.
- [ ] Para ligar o levantamento: escolher o canal de aviso, preencher `processos-acompanhados.md`, conferir os termos de uso do PJe/TJPA e do Meu INSS e ver com ela quais ações no PJe registram ciência de intimação.
- [x] Canal de aviso: celular, com WhatsApp quando o canal estiver pronto (decisão de 2026-11-10).
- [x] Skill `agenda-prazos`: todo prazo, audiência, perícia e ação necessária vai para a agenda "Prazos – Escritório" do Google Agenda, com `[CONFERIR]` e lembretes no celular (2026-11-10).
- [ ] Criar na conta dela a agenda "Prazos – Escritório" e decidir se as colaboradoras veem ou editam.
- [x] Pacote de instalação automática para o computador e a conta dela (2026-11-10).
- [x] Skills novas da questão 20: cadastro de clientes, tratamento de fotos, ficha por atendimento, honorários, leitura econômica de documentos (2026-11-10). A do WhatsApp foi criada desligada.
- [ ] Instalar no computador dela e seguir o `checklist-instalacao.md`.
- [x] WhatsApp, decisões de 2026-11-10: número exclusivo do escritório; exportação de conversas não começa agora; transcrição pelo Whisper; as duas colaboradoras podem dar comandos; aviso de privacidade fica para depois.
- [ ] WhatsApp: decidir o caminho D (WhatsApp Web do escritório no Chrome, lido pelo Claude em horários marcados), aceitando os limites descritos em `propostas/whatsapp.md`; conferir os termos do WhatsApp; escolher o computador e testar com dados fictícios.
- [ ] Definir o e-mail do escritório (Gmail ou Outlook). O questionário original não perguntou, e a triagem depende disso.
- [ ] Mapear os nomes das pastas atuais no OneDrive (autorizado) e ajustar os nomes das áreas.
- [ ] Documentos de praxe automáticos ao criar a pasta (questão 20, item 3): a skill `minuta` já descreve o fluxo; faltam os modelos `.docx` de procuração, contrato e declaração sobre o papel A.
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
2. Ler `respostas/questionario.md` e ver quais perguntas ainda estão com `Status: pendente`.
3. Ler `README.md` e `CLAUDE.md`.
4. Continuar pela primeira pendência não marcada.
