---
name: agenda-prazos
description: Registra automaticamente no Google Agenda da advogada, numa agenda própria do escritório, os prazos processuais e administrativos, audiências, perícias e ações necessárias identificados na triagem de e-mail, no levantamento de andamentos dos portais e nas análises, com lembretes no celular. Use sempre que outra skill encontrar um prazo ou uma ação com data, ou quando a advogada pedir para lançar, conferir ou corrigir prazos na agenda.
---

# Agenda de prazos

Objetivo: nenhum prazo fica só no papel. Hoje os prazos estão em agenda física e já houve perda e quase perda de prazo (questões 13 e 14). Esta skill lança cada prazo no Google Agenda dela, com lembretes que chegam no celular.

## Onde lançar

- Somente na agenda **"Prazos – Escritório"**, criada uma vez na conta Google da advogada. Nunca criar, alterar ou apagar eventos em outras agendas dela.
- Compartilhamento com as duas colaboradoras: `[DECIDIR]` com a advogada (ver ou editar).
- A agenda física continua em uso até esta skill ser validada lado a lado por algumas semanas.

## O que vira evento

| Tipo | Origem | Formato do evento |
|---|---|---|
| Prazo processual | Intimação no PJe, e-mail do tribunal, análise | Dia inteiro, na data de vencimento |
| Prazo administrativo | Exigência ou diligência do INSS, regime próprio | Dia inteiro, na data de vencimento |
| Audiência ou perícia | PJe, e-mail, intimação | Com horário e local |
| Ação necessária | E-mail ou conversa pedindo providência sem prazo formal (juntar documento, falar com cliente, retornar contato) | Dia inteiro, na data sugerida, marcado como ação |

## Título e descrição

Título: `[CONFERIR] PRAZO | {peça ou providência} | {cliente} | {nº do processo ou requerimento}`.
Para audiência: `[CONFERIR] AUDIÊNCIA | ...`. Para ação: `[CONFERIR] AÇÃO | ...`.

Descrição, sempre nesta ordem:

```
Origem: e-mail de AAAA-MM-DD de {remetente} | levantamento PJe de AAAA-MM-DD | carta de exigência ...
Texto da fonte: "{trecho copiado, sem alterar}"
Contagem: {regra usada} – {data inicial} a {data final}
Pasta: Clientes/{Área}/{Cliente}/{Caso}/
Chave: {nº do processo}|{tipo}|{data de vencimento}
Status: a conferir pela advogada
```

O `[CONFERIR]` só sai do título quando a advogada disser que conferiu. A conferência do prazo é sempre dela.

## Lembretes

- Prazos: notificações 7, 3 e 1 dia antes, às 8h, e no próprio dia às 8h.
- Audiências e perícias: 2 dias antes e 2 horas antes.
- Ações: no dia, às 8h.

As notificações chegam no celular pelo app do Google Agenda. Quando o canal de WhatsApp estiver ligado (ver `propostas/whatsapp.md`), o mesmo aviso também vai para o WhatsApp dela.

## Passos

1. Receba o prazo de outra skill (`triagem-email`, `consulta-portais`, `analise-demanda`) ou da advogada.
2. Monte a chave. Procure na agenda "Prazos – Escritório" um evento com a mesma chave.
3. Se não existir, crie o evento com título, descrição e lembretes acima.
4. Se existir com os mesmos dados, não faça nada.
5. Se existir com data diferente, não apague o antigo: crie o novo, acrescente na descrição do antigo "possível substituição por {nova data}, conferir" e avise a advogada.
6. Acrescente na `ficha-processo.md` uma linha: data, prazo lançado, link ou título do evento.
7. Ao final, informe na conversa quantos eventos foram criados, quantos já existiam e quais têm divergência.

## Regras

- Se o vencimento não puder ser calculado com segurança, crie o evento na data mais cedo possível e escreva na descrição "data provável, conferir".
- Não converter prazo sem indicar a regra. Prazo processual em dias úteis; prazo administrativo conforme o documento do órgão (ver `CLAUDE.md`).
- Processos com `SIGILOSO.txt` não entram na agenda pela automação.
- Nunca apagar evento. Mudanças só acrescentam informação.
- Não convidar clientes nem terceiros para os eventos.
