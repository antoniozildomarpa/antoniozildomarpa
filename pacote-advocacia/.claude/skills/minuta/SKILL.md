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

## Estilo e referência

- Se a pasta `modelos/` ou a pasta de peças aprovadas tiver peças anteriores da advogada, use-as como referência de estilo: tamanho dos parágrafos, forma de citar, tratamento, vocabulário e estrutura dos pedidos.
- Não copie trechos de peças anteriores sem conferir se os fatos e as partes são os do caso atual.
- Prefira fatos específicos do processo a fundamentação genérica. Se um parágrafo puder valer para qualquer caso, reescreva-o ou marque `[DECIDIR]`.
- Evite frases de preenchimento e expressões vagas. Cada parágrafo deve sustentar um fato ou um pedido.

## Limpeza de formatação

Antes de salvar, verifique e corrija:

- nenhum símbolo de Markdown (`**`, `#`, `|`, `---`, crases de código) no texto final;
- estilos do modelo aplicados (títulos, recuos, fonte, espaçamento), e não formatação manual;
- numeração de pedidos e de parágrafos contínua, sem saltos;
- marcações `[VERIFICAR]`, `[CONFIRMAR]`, `[DECIDIR]` e `[OAB]` visíveis e padronizadas, para serem removidas só após conferência;
- sem caracteres de rascunho ou comentários do assistente dentro do arquivo. Comentários ficam na resposta, não no documento.

## Registro de apoio por IA

- Ao salvar a minuta, registre em `03 Análise/AAAA-MM-DD_registro-minuta.md` o nome do arquivo, a data, as fontes usadas e as marcações pendentes.
- Esse registro é interno, para a política do escritório. Não é parte da peça e não deve ser incluído nela.
- Não inclua no documento nenhuma menção à ferramenta usada, salvo se a advogada decidir fazê-lo conforme as normas do tribunal.

## Regras

- Não use linguagem que assuma fatos não documentados.
- Não inclua jurisprudência sem a marca de status da pesquisa.
- Não assine, não data como definitiva e não preencha número de OAB ou dados de registro. Use `[OAB]` e confirme.
- Não protocole. O protocolo é ato da advogada, feito por ela.
- Ao final, informe o caminho do arquivo salvo e o que ainda precisa ser conferido.
