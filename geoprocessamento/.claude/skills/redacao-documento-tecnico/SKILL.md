---
name: redacao-documento-tecnico
description: Escreve e monta em Word a minuta de Relatório Técnico, Informação Técnica, Parecer Técnico ou Manifestação Técnica de um caso do SEI, na estrutura genérica (Objetivo, Resumo, Metodologia, Análises, Resultados e/ou Conclusão, Relação de Anexos), com figuras, tabelas e anexos numerados automaticamente e números puxados dos dados do caso. Use na etapa de redação e sempre que a minuta precisar de nova versão.
---

# Redação do documento técnico

O texto é escrito em `05_Documento/conteudo.md`, com marcadores. O script `minuta.py` monta o Word, e `revisar_minuta.py` faz a primeira revisão. Requer `pip install python-docx` (uma vez).

## 1. Antes de escrever

1. Leia a ficha (`00_Ficha/ficha.md`): pedido, setor demandante, documento da demanda, tipo de documento.
2. Leia os resultados do geoprocessamento (áreas na ficha, `03_Geo/resultados_coordenadas.json`) e as figuras conferidas (`04_Figuras/*.json`).
3. Escreva, em uma frase, **a resposta ao pedido**. Ela orienta todo o texto e aparece na conclusão.

## 2. Estrutura

| Seção | Conteúdo | Obrigatória |
| --- | --- | --- |
| Objetivo | O que foi pedido, por quem (setor e documento SEI) e o que este documento responde | Sim |
| Resumo | Só em documento extenso (mais de 2.500 palavras): a resposta em um parágrafo | Se extenso |
| Metodologia | Dados usados (com fonte e data), sistema de referência, procedimentos, ferramentas | Sim |
| Análises | O que foi verificado, com as figuras e tabelas | Sim |
| Resultados e/ou Conclusão | A resposta ao pedido, em itens curtos e objetivos | Sim |
| Relação de Anexos | Gerada sozinha pelo script; não escreva | Automática |

Nos primeiros casos, esta estrutura genérica é a base. Os documentos aprovados viram modelos para casos semelhantes: guarde-os em `geoprocessamento/modelos/` sem dados pessoais.

## 3. Estilo

- **Leitor não especialista** (advogados, chefias, procuradores, pareceristas): frases curtas, termos técnicos explicados na primeira vez, sem jargão desnecessário.
- Impessoal e objetivo ("foi verificado", "constatou-se"), sem adjetivos de opinião.
- Cada afirmação técnica tem base: um dado, uma figura, uma tabela ou um anexo citado.
- Números com unidade e no padrão brasileiro (78,63 ha; 3.550,29 m). **Nunca digite área, perímetro ou coordenada**: use os marcadores.
- Coordenadas sempre em SIRGAS 2000, graus-minutos-segundos, pela tabela automática.
- Imagens sempre com sensor e data.
- Nada de conclusão que vá além do que as análises mostram. Se algo não pôde ser verificado, diga claramente.

## 4. Marcadores

| Marcador | Resultado |
| --- | --- |
| `[[FIGURA:1]]` (sozinho na linha) | Título "Figura 1 – ..." acima, a imagem e a fonte abaixo (ABNT), a partir do JSON da figura |
| `[[ANEXO:chave\|Descrição]]` | "Anexo N", numerado pela ordem da primeira citação; nas seguintes, `[[ANEXO:chave]]`. A chave vira o nome do arquivo (`Anexo_2_Carta_Imagem`) |
| `[[AREA:camada]]` / `[[PERIMETRO:camada]]` | Valor calculado no QGIS, da ficha |
| `[[TABELA_COORDENADAS:camada\|Título]]` (sozinho na linha) | "Tabela N – Título" acima, vértices em GMS e a fonte abaixo |
| `Tabela: Título` na linha antes de uma tabela com `\|` | Título numerado da tabela; uma linha `Fonte: ...` logo depois vira a fonte |
| `[[NUP]]`, `[[TIPO]]`, `[[DEMANDANTE]]`, `[[DOCUMENTO_DEMANDA]]` | Dados da ficha |

Cite cada figura e tabela no texto antes de ela aparecer ("conforme a Figura 1", "na Tabela 1"). Exemplo completo em `geoprocessamento/automacao-sei/exemplos/conteudo_exemplo.md`.

Chaves de anexo usuais: `carta_imagem`, `mapa_localizacao`, `demonstrativo_car`, `documento_imovel`, `geoinformacao` (zip dos vetores).

## 5. Montar e revisar

```
python geoprocessamento/automacao-sei/scripts/minuta.py --pasta "<pasta do caso>"
python geoprocessamento/automacao-sei/scripts/revisar_minuta.py --pasta "<pasta do caso>"
```

- Cada execução gera uma versão nova (`minuta_v1.docx`, `minuta_v2.docx`...), nunca sobrescreve.
- `anexos.json` guarda a lista numerada, usada na etapa de anexos.
- A revisão automática grava `revisao_vN.md`. Pendências bloqueantes (marcador não resolvido, lacuna, seção ausente, figura citada e inexistente, numeração fora de ordem) têm de ser resolvidas antes de seguir.
- Depois, o `agente-revisor` faz a revisão de mérito, sem ter escrito o texto.
- Por fim, a Conferência 3: o usuário lê a minuta e aprova.

## 6. Formatação do Word

Calibri 12, justificado, espaçamento 1,15, seções numeradas em caixa alta. Figuras com 16 cm de largura. Tabelas com cabeçalho repetido e sem quebra entre páginas (até 20 linhas). A identificação curta no topo (Processo, Assunto) ajuda na leitura; o cabeçalho oficial é o do SEI.
