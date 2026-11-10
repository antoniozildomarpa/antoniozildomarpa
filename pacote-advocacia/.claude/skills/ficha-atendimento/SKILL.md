---
name: ficha-atendimento
description: Cria ou atualiza a ficha do cliente a partir da gravação ou das anotações de um atendimento presencial: transcreve o áudio no computador (Whisper), extrai dados pessoais, relato, documentos entregues e pendências, e propõe área e caso. Use depois de um atendimento, quando a advogada ou uma colaboradora entregar o áudio ou o texto.
---

# Ficha a partir do atendimento

Pedido da advogada (questão 20, item 4).

## Antes de gravar

O cliente precisa saber e concordar que o atendimento será gravado para registro interno. O texto do aviso e a forma de registrar o consentimento são decisão da advogada `[DECIDIR]`; a base legal na LGPD deve ser conferida `[VERIFICAR]`. Sem consentimento, use só as anotações escritas.

## Passos

1. **Transcrição.** `python scripts/transcrever.py "<arquivo de áudio>" --com-tempo`. O texto sai ao lado do áudio (`.txt`). O áudio não sai do computador.
2. **Extração.** Leia a transcrição e separe:
   - dados pessoais ditos no atendimento (nome, CPF, RG, estado civil, profissão, endereço, telefone);
   - relato dos fatos, em ordem de data;
   - pedido do cliente (o que ele quer);
   - documentos entregues e documentos que faltam;
   - prazos ou datas mencionados (perícia, audiência, carta do INSS).
3. **Ficha do cliente.** Se a pasta do cliente existir, acrescente um bloco em `## Atendimentos` de `ficha-cliente.md` com a data e o resumo. Se não existir, proponha área e caso e pergunte antes de criar a pasta com `estrutura/criar_pastas.py`.
4. **Ficha do caso.** Se o caso for identificado, acrescente o relato e as pendências na `ficha-processo.md`.
5. **Prazos.** Datas e prazos citados vão para a skill `agenda-prazos`, com `[CONFERIR]`.
6. **Pendências.** Liste para a advogada: documentos a pedir, dados a confirmar, próximo passo sugerido.

## Regras

- Tudo o que vem da transcrição e não foi conferido em documento fica `[CONFIRMAR]`, em especial números (CPF, valores, datas). O Whisper erra nomes e números.
- Não registrar na ficha opiniões ou comentários pessoais sobre o cliente; só fatos e pedidos.
- O áudio e a transcrição ficam em `00 Documentação do cliente/atendimentos/`, com o nome `AAAA-MM-DD_atendimento`.
