---
name: analise-demanda
description: Analisa uma demanda jurídica a partir dos documentos da pasta do processo ou cliente, identifica o tipo de ação necessária, calcula prazos, pesquisa fundamentos e propõe o encaminhamento. Use quando a advogada pedir análise de uma demanda, de uma intimação, de uma notificação ou de um novo caso.
---

# Análise de demanda

Objetivo: transformar documentos recebidos em um diagnóstico curto, com a ação proposta, os fundamentos e os próximos passos. Não redige a peça (isso é a skill `minuta`) e não envia nada.

## Entradas

- Pasta do caso, no padrão `Clientes/{Área}/{Cliente}/{Caso}/`, e a pasta `00 Documentação do cliente` do cliente.
- `ficha-cliente.md` e `ficha-processo.md`, se existirem.
- Notas da triagem em `03 Análise`, se existirem.
- Pedido ou contexto dado pela advogada na conversa.

Se a pasta do caso tiver o arquivo `SIGILOSO.txt`, pare e informe. Processos em segredo de justiça ficam fora da automação.

## Passos

1. **Inventário.** Liste os documentos das pastas `00` a `02` e `06` antes de abrir qualquer um. Informe o que existe e o que parece faltar. Nos casos previdenciários, confira se há os documentos que o INSS ou o regime próprio costumam exigir e liste os ausentes.
2. **Leitura.** Leia os documentos relevantes. Para cada um, anote data, partes, tipo e pedido principal.
3. **Fatos.** Monte uma linha do tempo com fatos documentados, indicando a fonte de cada um.
4. **Demanda.** Identifique o que a parte quer e em que momento o caso está: requerimento administrativo (INSS ou regime próprio), exigência ou diligência administrativa, inicial, contestação, recurso, contrarrazões, cumprimento, extrajudicial ou consultivo.
5. **Prazos.** Liste prazos abertos ou previsíveis, com a data da intimação ou do aviso, a regra usada e o vencimento. Prazo processual: dias úteis. Prazo administrativo (exigência do INSS, regime próprio): copie o prazo do documento e a forma de contagem indicada nele. Marque como "conferir" qualquer prazo com dúvida sobre termo inicial, suspensão, forma de contagem ou feriado local (Tucuruí, Novo Repartimento, Pará).
6. **Fundamentos.** Acione a skill `pesquisa-juridica` para legislação e jurisprudência aplicáveis. Não cite de memória.
7. **Proposta.** Apresente de duas a três alternativas de ação, com prós, contras e risco processual. Indique qual você recomenda e por quê.
8. **Encaminhamento.** Liste os próximos passos: documentos a obter, dados a confirmar com o cliente, peça a redigir (acionar `minuta`), prazos a registrar.
9. **Ficha.** Atualize `ficha-processo.md` com a fase, o próximo prazo e o status. Não apague informações anteriores; acrescente com data.

## Saída

Crie ou atualize `03 Análise/AAAA-MM-DD_analise_v1.md` com:

```
# Análise: {cliente} – {processo ou consultivo}
Data: AAAA-MM-DD

## Resumo (3 linhas)
## Fatos documentados (linha do tempo com fonte)
## Demanda e momento processual
## Prazos (data da intimação, regra, vencimento, status: conferir/ok)
## Fundamentos (cada item com [VERIFICAR] se não conferido na fonte oficial)
## Alternativas de ação (prós, contras, risco)
## Recomendação
## Próximos passos
## Documentos faltantes
```

## Regras

- Não afirme fatos que não estejam nos documentos. Se algo for inferência, diga.
- Não calcule prazo sem indicar a regra usada.
- Não recomende ação com base em jurisprudência que não tenha sido verificada.
- Se faltar documento essencial, pare e peça à advogada antes de concluir.
- Ao final, pergunte se a advogada quer seguir para a minuta. Quando a análise foi acionada pela triagem de e-mail com prazo em aberto, siga direto para a minuta como rascunho `v1`, conforme a skill `triagem-email`.
