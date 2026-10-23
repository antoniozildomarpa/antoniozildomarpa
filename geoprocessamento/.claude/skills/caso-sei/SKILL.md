---
name: caso-sei
description: Conduz o fluxo completo de um caso técnico, da demanda no SEI ao despacho - triagem, pasta e ficha, leitura, geoprocessamento, figuras, redação, revisão, anexos e lançamento no SEI - chamando os agentes certos e parando nas quatro conferências do usuário. Use quando o usuário pedir para iniciar, continuar ou retomar um caso ("inicie o caso do processo aberto", "continue o caso X").
---

# Fluxo completo do caso (coordenação)

Você é a coordenadora. Não faz o trabalho especializado: chama o agente certo, confere o produto de cada etapa e para nas conferências. O plano completo está em `geoprocessamento/automacao-sei/PLANO.md`.

## Início ou retomada

- **Caso novo**: o usuário abriu o processo no SEI. Comece pela etapa 1.
- **Caso em andamento**: rode `python geoprocessamento/automacao-sei/scripts/caso.py situacao --pasta "<pasta>"`, leia `00_Ficha/registro.md` e continue da primeira etapa não concluída.

## Etapas

| # | Etapa | Quem faz | Produto conferido antes de seguir |
| --- | --- | --- | --- |
| 1 | Triagem no SEI (só leitura) | `agente-sei-leitura` | Pasta e ficha criadas; documentos em `01_Processo_SEI/` |
| 2 | Leitura dos documentos | `agente-leitor` | Fatos, coordenadas validadas, mapas identificados |
| — | **Conferência 1**: entendimento da demanda, tipo de documento e plano de análise | **Usuário** | Aprovação registrada na ficha |
| 3 | Geoprocessamento | `agente-geo` | Projeto QGIS, resultados na ficha, carta imagem |
| 3a | Imagens de satélite (quando o caso pedir) | `agente-imagens` | Recortes em `02_Insumos/imagens/`; sensor, data, resolução e nuvem na ficha |
| — | **Conferência 2**: áreas, sobreposições e carta imagem | **Usuário** | Aprovação registrada |
| 4 | Figuras do corpo do texto | `agente-figuras` | Figuras conferidas (objetivo, rótulos, imagem, grade, escala) |
| 5 | Redação | `agente-redator` | Minuta sem pendência na revisão automática |
| 6 | Revisão independente | `agente-revisor` | Relatório sem bloqueios (correções voltam ao redator) |
| — | **Conferência 3**: o usuário lê e aprova a minuta | **Usuário** | Versão aprovada registrada |
| 7 | Pacote de anexos | `agente-empacotador` | Manifesto sem pendência; Geoinformação em SHP, GPKG e KML |
| — | **Conferência 4**: autoriza lançar no SEI; define nível de acesso, tipo do documento externo e destino | **Usuário** | Autorização registrada |
| 8 | Lançamento no SEI | `agente-sei-protocolo` | Números SEI registrados; prints em `07_SEI/` |
| — | **Assinatura e envio** | **Usuário** | — |

A etapa 3a pode começar assim que o polígono original estiver validado, em paralelo ao restante do geoprocessamento. As etapas 2 e 3 podem correr em paralelo quando os documentos já estão baixados e as coordenadas validadas. As etapas de SEI (1 e 8) nunca rodam ao mesmo tempo que outra que use o navegador.

## Em cada conferência

1. Mostre ao usuário, de forma curta, o que foi produzido (com os arquivos e as figuras).
2. Faça as perguntas que só ele responde.
3. Registre a resposta: `caso.py registrar --etapa conferencia_N --texto "<decisão do usuário>"`.
4. Sem aprovação explícita, não siga.

## Regras gerais

- Toda etapa concluída é registrada (`caso.py registrar`).
- Dados do caso ficam na pasta do caso, nunca no repositório.
- Assinar, enviar e digitar senha são sempre do usuário (há um gancho de segurança que bloqueia essas ações no navegador).
- Diante de qualquer dúvida de mérito, pergunte em vez de supor.
- Ao fim, atualize a tarefa do caso no Notion (frente Geo) e informe ao usuário o que falta ele fazer.
