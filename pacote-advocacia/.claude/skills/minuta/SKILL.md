---
name: minuta
description: Redige uma minuta de peça ou documento jurídico para revisão da advogada, a partir de uma análise já feita, com fundamentos marcados e versionamento na pasta do processo. Use quando a advogada pedir a minuta de uma petição, resposta, recurso, notificação ou parecer. Nunca protocola nem envia.
---

# Minuta

Objetivo: produzir um rascunho completo, bem estruturado e fácil de revisar. A advogada decide o conteúdo final.

## Pré-requisitos

- Existe uma análise em `03 Análise/` ou a advogada passou o contexto por escrito.
- Se não houver modelo em `modelos/` para o tipo de peça, use a estrutura geral abaixo e avise.
- Confirme o tipo de peça, o juízo ou órgão, a parte representada e o pedido principal antes de redigir.

## Estrutura geral (quando não houver modelo)

1. Endereçamento (juízo ou órgão, com número do processo)
2. Qualificação das partes (dados a confirmar com o cliente, marcados como `[CONFIRMAR]`)
3. Síntese dos fatos, com referência aos documentos
4. Fundamentos jurídicos, com as citações da pasta de pesquisa
5. Pedidos, numerados
6. Provas e documentos anexos, com lista dos arquivos
7. Fecho com local e data em aberto (`[DATA]`) e espaço para assinatura da advogada

## Marcações obrigatórias

- `[VERIFICAR]` em toda citação não marcada como Conferido na pesquisa.
- `[CONFIRMAR]` em todo dado pessoal, valor, data ou número que não esteja em documento.
- `[DECIDIR]` em todo ponto em que a estratégia depende de escolha da advogada.

As marcações ficam no texto para que nada passe despercebido. Remova-as só depois da conferência.

## Passos

1. Leia a análise e os documentos da pasta, sem reproduzir dados desnecessários.
2. Acione a skill `pesquisa-juridica` para citações que ainda não estejam registradas.
3. Redija o rascunho na estrutura adequada.
4. Revise o próprio texto: coerência entre fatos e pedidos, nenhum pedido sem fundamento, nenhuma citação sem marca.
5. Salve em `04 Minutas/AAAA-MM-DD_tipo_cliente_v1.docx` (ou `.md` se o docx não for necessário). Se já existir versão, crie `v2`, sem sobrescrever.
6. Crie um resumo de duas linhas no início da resposta e uma lista de `[DECIDIR]` e `[CONFIRMAR]`.

## Regras

- Não use linguagem que assuma fatos não documentados.
- Não inclua jurisprudência sem a marca de status da pesquisa.
- Não assine, não data como definitiva e não preencha número de OAB ou dados de registro. Use `[OAB]` e confirme.
- Não protocole. O protocolo é ato da advogada, feito por ela.
- Ao final, informe o caminho do arquivo salvo e o que ainda precisa ser conferido.
