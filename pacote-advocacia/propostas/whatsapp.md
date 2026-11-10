# Proposta: WhatsApp do escritório ligado à automação

Data: 2026-11-10. Situação: **proposta com decisões parciais.** Nada aqui foi instalado.

## Decisões de 2026-11-10

1. Haverá um número exclusivo do escritório.
2. A exportação de conversas (caminho A) **não começa agora**.
3. O texto do aviso de privacidade aos clientes será definido depois.
4. Transcrição pelo Whisper, no computador.
5. Além da advogada, as duas colaboradoras podem dar comandos ("abrir caso").
6. Em estudo: o Claude usar o WhatsApp Web do número do escritório, aberto no Chrome (caminho D, detalhado abaixo).

## O que se quer

1. Acompanhar as conversas do WhatsApp que tratam de advocacia.
2. Levar as informações importantes para a ficha do cliente e do caso.
3. Salvar na pasta do cliente os documentos recebidos.
4. Transcrever os áudios.
5. Avisar a advogada quando chegar mensagem nova de alguém pedindo informação ou procurando os serviços dela.
6. Quando ela mandar, criar a pasta do caso a partir da conversa e salvar nela os documentos.
7. Mandar para o WhatsApp dela os avisos de prazo e de levantamento nos portais.

## Ponto de partida: um número só do escritório

A recomendação é ter um **número exclusivo do escritório**, com o app WhatsApp Business, separado do WhatsApp pessoal dela.

Motivos:

- A automação só lê o que é do escritório. Conversas de família e pessoais nunca passam pela ferramenta.
- O sigilo profissional e a proteção de dados dos clientes ficam mais fáceis de cumprir com um canal só profissional. A base legal e as obrigações (LGPD, Código de Ética da OAB) devem ser conferidas antes da implantação `[VERIFICAR]`.
- Clientes previdenciários mandam laudos e dados de saúde, que são dados sensíveis. Um canal separado, com aviso de privacidade, reduz o risco.
- O app WhatsApp Business tem recursos nativos que já ajudam sem automação: mensagem de saudação, mensagem de ausência, etiquetas ("novo contato", "cliente", "aguardando documento") e catálogo de serviços.

## Formas de ligar o WhatsApp à automação

| Caminho | Como funciona | Avaliação |
|---|---|---|
| **A. Exportar conversa** | Ela (ou um colaborador) usa "Exportar conversa > Incluir mídia" e salva numa pasta do Drive. O Claude lê o arquivo, transcreve os áudios, atualiza a ficha e organiza os documentos. | Funciona já, sem custo, dentro das regras do WhatsApp. É manual: uma conversa por vez. Bom para testar a extração antes de automatizar. |
| **B. API oficial do WhatsApp (Meta)** | O número do escritório é ligado à plataforma oficial de negócios do WhatsApp (Cloud API). Cada mensagem recebida chega a um serviço intermediário, que salva o texto e os arquivos no Drive, manda os áudios para transcrição e chama o Claude para classificar e extrair as informações. | **Recomendado** para a automação contínua. É o caminho permitido pelo WhatsApp. Exige configuração técnica, um serviço intermediário e tem custo por mensagem enviada pelo escritório. Verificar se o número pode continuar usando o app WhatsApp Business ao mesmo tempo (recurso de coexistência) e a tabela de preços atual `[VERIFICAR]`. |
| **C. Ferramentas não oficiais (WhatsApp Web automatizado)** | Programas que conectam ao WhatsApp Web lendo o QR code e passam a ler tudo. | **Não recomendado.** Contraria os termos de uso do WhatsApp `[VERIFICAR]`, pode levar ao bloqueio do número e dá acesso a todas as conversas, inclusive pessoais, para um programa de terceiros. Risco alto para dados de clientes. |
| **D. Claude in Chrome lendo o WhatsApp Web** | O WhatsApp Web do número do escritório fica aberto no Chrome de um computador do escritório. Em horários marcados, o Claude abre as conversas não lidas, lê, baixa os anexos e os áudios, transcreve com o Whisper e organiza. | Viável com o número exclusivo, porque não há conversa pessoal na tela. Sem custo de API e sem serviço intermediário. Tem limites (ver abaixo): não é instantâneo, depende do computador ligado e os termos do WhatsApp sobre uso automatizado precisam ser conferidos `[VERIFICAR]`. |

**Sugestão atual:** testar o caminho D com dados fictícios. O caminho B fica como evolução, se o D não der conta do volume ou se os termos do WhatsApp o impedirem.

## Caminho D em detalhe: WhatsApp Web no Chrome

### Como funcionaria

1. Num computador do escritório que fica ligado no horário de trabalho, o WhatsApp Web do número do escritório fica conectado no Chrome. Quem faz o pareamento pelo QR code é a advogada ou uma colaboradora. O Claude não faz essa etapa.
2. Uma rotina roda em horários marcados (sugestão: a cada hora, das 8h às 18h, em dias úteis) usando o Claude in Chrome.
3. Em cada rodada, o Claude:
   - abre só as conversas com mensagem nova;
   - decide se o assunto é de advocacia; se não for, sai sem guardar nada;
   - identifica o cliente pelo telefone e pelo nome, comparando com as fichas;
   - baixa documentos, fotos e áudios para `Clientes/_WhatsApp/Entrada/{telefone}/AAAA-MM-DD/`;
   - transcreve os áudios com o Whisper e salva o `.txt` ao lado;
   - acrescenta na `ficha-cliente.md` (e na `ficha-processo.md`, se o caso for identificado) o resumo com data;
   - move os documentos para `00 Documentação do cliente` ou `01 Entrada` do caso;
   - lança prazos ou providências pela skill `agenda-prazos`;
   - avisa a advogada e as colaboradoras sobre contatos novos e pedidos de informação.
4. Comando "abrir caso": a advogada ou uma colaboradora escreve o comando numa conversa combinada, por exemplo o grupo interno "Comandos – Escritório", só com as três. Na rodada seguinte, o Claude lê o comando, cria a pasta, move os documentos daquela conversa, monta a ficha e gera os documentos de praxe.

### Limites que é preciso aceitar

- **Não é instantâneo.** O Claude só vê a mensagem na rodada seguinte. Para urgências, a notificação normal do WhatsApp no celular continua sendo a primeira.
- **Confirmação de leitura.** Abrir a conversa no WhatsApp Web marca as mensagens como lidas, e o cliente vê os tiques azuis sem ter recebido resposta. Saída: desligar a confirmação de leitura no número do escritório, ou aceitar e combinar com as colaboradoras o tempo de resposta `[DECIDIR]`.
- **Computador ligado e sessão ativa.** Se o computador desligar ou o WhatsApp Web desconectar, a rodada não acontece. A rotina avisa quando encontrar a sessão desconectada e não tenta reconectar.
- **Aplicativo do celular.** O Claude não opera o app no celular. Só o WhatsApp Web, ou o WhatsApp para computador, no computador.
- **Volume.** Com muitas conversas por dia, cada rodada fica longa. Se isso acontecer, o caminho B passa a valer a pena.
- **Termos do WhatsApp.** Os termos restringem o acesso por meios automatizados `[VERIFICAR]`. O Claude in Chrome usa o navegador como uma pessoa, em ritmo humano, o que reduz o risco, mas não o elimina. Se o número for advertido ou bloqueado, a rotina para.

### Regras do caminho D

- O Claude **não escreve nem envia mensagem a clientes**. Não clica em "responder", não manda áudio, não apaga, não arquiva e não bloqueia contatos.
- Avisos internos: só pela notificação do celular (agenda e app do Claude) ou, se a advogada autorizar, mensagem no grupo interno "Comandos – Escritório". Nunca para clientes.
- Conversas de processos com `SIGILOSO.txt`: registrar só que houve mensagem, sem resumo.
- Comandos só valem se vierem da advogada ou de uma das duas colaboradoras, no grupo interno.

## Como ficaria o caminho B

```
Cliente manda mensagem no WhatsApp do escritório
        │
        ▼
API oficial do WhatsApp ──► Serviço intermediário (por exemplo, n8n ou Make)
                                 │
                                 ├─ salva texto e arquivos no Drive: Clientes/_WhatsApp/Entrada/{telefone}/AAAA-MM-DD/
                                 ├─ áudio ─► transcrição (Whisper no computador ou serviço de voz em nuvem) ─► texto
                                 └─ chama o Claude com o texto e a lista de clientes
                                          │
                                          ├─ assunto de advocacia? se não, ignora e não guarda resumo
                                          ├─ é cliente com pasta? atualiza ficha, move documentos para
                                          │    00 Documentação do cliente ou 01 Entrada do caso
                                          ├─ é contato novo pedindo serviço? marca como "novo contato"
                                          ├─ tem prazo ou providência? aciona agenda-prazos
                                          └─ manda aviso para o WhatsApp pessoal da advogada
```

### Avisos que ela receberia no WhatsApp pessoal

- "Novo contato pedindo atendimento: {nome}, {assunto em uma linha}. Transcrição na pasta."
- "Cliente {nome} mandou 3 documentos (RG, comprovante, laudo). Salvos em {pasta}."
- "Cliente {nome} pergunta sobre o andamento do processo {número}."
- Avisos de prazo e do levantamento nos portais.

### Comando para abrir caso

Ela responde ao aviso com um comando curto, por exemplo:

```
abrir caso | Previdenciário RGPS | INSS
```

O serviço confere que a mensagem veio do número dela (só ela pode dar comandos) e roda o `criar_pastas.py` com a área e o cliente. Depois:

- move os documentos daquela conversa para `00 Documentação do cliente`;
- cria a `ficha-cliente.md` com os dados da conversa, marcados `[CONFIRMAR]`;
- gera os documentos de praxe (procuração, contrato, declaração de hipossuficiência) pela skill `minuta`.

As duas colaboradoras também podem dar comandos (decisão de 2026-11-10).

### O que continua proibido

- **Responder cliente automaticamente.** A automação não responde. Quem responde é ela ou um colaborador. As mensagens nativas de saudação e ausência do WhatsApp Business, escritas por ela, podem ficar ligadas.
- Ler conversas de processos marcados com `SIGILOSO.txt`. Essas conversas não são resumidas.
- Guardar resumo de conversa que não seja de advocacia.

## Transcrição de áudio

O Claude não transcreve áudio sozinho. A transcrição é feita antes, por um destes caminhos:

- **Whisper** (programa gratuito, roda no computador). Os áudios não saem do computador para transcrever. Depende de um computador ligado.
- **Serviço de voz em nuvem**, por exemplo Google ou OpenAI. Funciona sempre, tem custo por minuto e os áudios passam por mais um fornecedor `[VERIFICAR]`.

O texto transcrito é salvo junto do áudio, com o mesmo nome e extensão `.txt`.

## Custos e responsabilidades a decidir

- Número exclusivo do escritório (chip).
- API oficial: custo por mensagem que o escritório envia. As mensagens dos clientes e os avisos para ela entram na tabela da Meta `[VERIFICAR]`.
- Serviço intermediário: n8n instalado num computador ou servidor (gratuito, exige manutenção) ou n8n ou Make em nuvem (mensalidade).
- Chamadas à API do Claude e transcrição, cobradas por uso.
- Quem cuida da manutenção técnica.

## Decisões pendentes da advogada

1. Texto e momento do aviso de privacidade aos clientes (fica para depois).
2. Caminho D: aceitar os limites acima? Desligar a confirmação de leitura no número do escritório?
3. Qual computador fica ligado com o WhatsApp Web e com o Whisper instalado.
4. Frequência das rodadas.
5. Orçamento mensal, só se for preciso passar ao caminho B.
