---
name: minuta
description: Redige uma minuta de peça ou documento jurídico para revisão da advogada, no papel timbrado do escritório, a partir de uma análise já feita, com fundamentos marcados e versionamento na pasta do processo. Use quando a advogada pedir a minuta de um requerimento administrativo, petição inicial, contrarrazões, recurso, notificação ou parecer, ou os documentos de praxe de um caso novo (procuração, contrato de honorários, declaração de hipossuficiência). Nunca protocola nem envia.
---

# Minuta

Objetivo: produzir um rascunho completo, bem estruturado e fácil de revisar. A advogada decide o conteúdo final.

## Pré-requisitos

- Existe uma análise em `03 Análise/` ou a advogada passou o contexto por escrito. Documentos de praxe não exigem análise.
- Se não houver modelo em `modelos/` para o tipo de peça, use a estrutura geral abaixo e avise. A advogada ainda não tem modelos próprios (questão 18); os modelos por área estão sendo criados.
- Confirme o tipo de peça, o juízo ou órgão, a parte representada e o pedido principal antes de redigir. Quando a minuta for gerada pela triagem de e-mail, registre essas premissas no topo da resposta, como `[CONFIRMAR]`.
- Se a pasta do caso tiver `SIGILOSO.txt`, não redija.

## Papel timbrado

- Toda minuta em Word parte do papel oficial, modelo A: `H:\Meu Drive\_advocacia\logomarca\modelos-papel-timbrado\modelo_timbrado_A.docx`. Abra uma cópia, apague o texto de exemplo e escreva sobre ela, mantendo cabeçalho, rodapé e estilos.
- Corpo em Times New Roman 12, justificado, espaçamento 1,5, como no modelo.
- Dados fixos da advogada, que podem ser preenchidos sem marcação: Leulla Mendanha, OAB/PA 25.617, endereços de Tucuruí e Novo Repartimento conforme o `CLAUDE.md`.

## Documentos de praxe de caso novo

Quando uma pasta de caso for criada e a documentação do cliente estiver em `00 Documentação do cliente`, gere em `04 Minutas/`, como `v1`:

1. Procuração (`AAAA-MM-DD_procuracao_{cliente}_v1.docx`).
2. Contrato de prestação de serviços advocatícios (`AAAA-MM-DD_contrato_{cliente}_v1.docx`). Valores e forma de pagamento ficam como `[DECIDIR]` enquanto o bloco G do questionário (honorários) não for respondido.
3. Declaração de hipossuficiência (`AAAA-MM-DD_declaracao-hipossuficiencia_{cliente}_v1.docx`), para todo cliente, ainda que só seja usada se o caso couber.

Os dados do cliente vêm dos documentos da pasta. O que não estiver legível ou não existir fica `[CONFIRMAR]`.

## Peças mais frequentes

Requerimento administrativo (INSS ou regime próprio), petição inicial e contrarrazões (questão 17). Para cada uma, enquanto não houver modelo:

- **Requerimento administrativo:** órgão e unidade, qualificação do requerente, número do benefício ou do requerimento anterior, fatos, fundamento, pedido, documentos anexos.
- **Petição inicial:** segue a estrutura geral abaixo.
- **Contrarrazões:** endereçamento ao juízo de origem e ao tribunal, síntese do recurso da parte contrária, rebate ponto a ponto, pedido de não provimento.

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
- marcações `[VERIFICAR]`, `[CONFIRMAR]` e `[DECIDIR]` visíveis e padronizadas, para serem removidas só após conferência;
- sem caracteres de rascunho ou comentários do assistente dentro do arquivo. Comentários ficam na resposta, não no documento.

## Registro de apoio por IA

- Ao salvar a minuta, registre em `03 Análise/AAAA-MM-DD_registro-minuta.md` o nome do arquivo, a data, as fontes usadas e as marcações pendentes.
- Esse registro é interno, para a política do escritório. Não é parte da peça e não deve ser incluído nela.
- Não inclua no documento nenhuma menção à ferramenta usada, salvo se a advogada decidir fazê-lo conforme as normas do tribunal.

## Regras

- Não use linguagem que assuma fatos não documentados.
- Não inclua jurisprudência sem a marca de status da pesquisa.
- Não assine e não date como definitiva. A inscrição OAB/PA 25.617 está confirmada e pode ser preenchida; qualquer outro número de registro fica `[CONFIRMAR]`.
- Não protocole. O protocolo é ato da advogada, feito por ela.
- Ao final, informe o caminho do arquivo salvo e o que ainda precisa ser conferido.
