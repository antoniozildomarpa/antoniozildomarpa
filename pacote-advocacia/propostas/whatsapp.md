# Proposta: WhatsApp do escritório ligado à automação

Data: 2026-11-10. Situação: **proposta, aguarda decisão da advogada.** Nada aqui foi instalado.

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
| **D. Claude in Chrome lendo o WhatsApp Web** | Com ela logada no WhatsApp Web, o Claude lê as conversas na tela. | Só como consulta pontual, com ela presente. Não serve para acompanhar o dia todo e expõe as conversas pessoais se o número for o mesmo. |

**Sugestão:** começar pelo caminho A agora, para testar a extração, e montar o caminho B com o número exclusivo do escritório.

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

Os colaboradores podem ter o número deles autorizado para comandos, se ela quiser `[DECIDIR]`.

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

1. Número exclusivo do escritório: sim ou não?
2. Começar pelo caminho A (exportar conversas) enquanto o B não fica pronto?
3. Aviso de privacidade aos clientes sobre o uso de ferramenta na organização das mensagens: texto e momento de envio `[DECIDIR]`.
4. Transcrição no computador (Whisper) ou em nuvem.
5. Quem além dela pode dar comandos ("abrir caso").
6. Orçamento mensal aceitável.
