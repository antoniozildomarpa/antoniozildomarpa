---
name: georreferenciamento
description: Georreferencia mapas, croquis e imagens escaneados de um caso a partir de pontos de controle, com erro de cada ponto, RMS em metros, detecção de ponto suspeito e decisão de uso (medição ou só ilustração) pelo limite definido para o caso. Use quando um documento do processo trouxer mapa ou imagem que precise ser sobreposto às demais camadas no QGIS.
---

# Georreferenciamento com controle de erro

O script `geoprocessamento/automacao-sei/scripts/georreferenciar.py` roda com o Python do QGIS (usa o GDAL).

## 1. Preparar

1. Salve o mapa escaneado em `02_Insumos/mapas_scan/` (JPG, PNG ou TIF). Se ele vier em PDF, exporte a página como imagem com boa resolução (300 dpi ou mais).
2. Anote a fonte: documento SEI, página e escala do mapa original, se houver.
3. Escolha os pontos de controle, bem distribuídos (cantos e centro, nunca todos alinhados):
   - cruzamentos da grade de coordenadas impressa no mapa (melhor opção);
   - vértices com coordenadas escritas no próprio documento;
   - feições bem definidas que aparecem na imagem de referência (cruzamento de estradas, cantos de cerca), com a coordenada lida no QGIS.
4. Mínimo de 3 pontos para a transformação afim; use de 6 a 10. Separe 1 ou 2 como **verificação** (não entram no ajuste e medem o erro de forma independente).

Tabela de pontos (`<mapa>_pontos.csv`):

```
id;coluna;linha;latitude;longitude;uso
P1;298,7;251,6;03°43'30,000" S;049°42'54,000" O;controle
P8;691,9;358,6;03°43'48,000" S;049°41'24,000" O;verificacao
```

`coluna` e `linha` são a posição do ponto na imagem, em pixels, a partir do canto superior esquerdo. As coordenadas podem estar em GMS, grau decimal ou UTM (`e;n;zona`), em SIRGAS 2000, WGS 84, SAD69 ou Córrego Alegre (`--datum`). Também serve o arquivo `.points` do georreferenciador do QGIS.

## 2. Definir o limite de erro (caso a caso)

O limite depende da fonte, da resolução e da qualidade do material. Pergunte ao usuário. Referências que o script mostra:
- mapa com escala conhecida: **0,2 mm na escala do mapa** (1:25.000 → 5 m; 1:50.000 → 10 m; 1:100.000 → 20 m);
- sem escala: 2 pixels no terreno.

## 3. Rodar

```
"<python-qgis.bat>" geoprocessamento/automacao-sei/scripts/georreferenciar.py --pasta "<caso>" \
  --imagem "<caso>/02_Insumos/mapas_scan/croqui.jpg" --pontos "<caso>/02_Insumos/mapas_scan/croqui_pontos.csv" \
  --escala-mapa 25000 --limite-m 10 --fonte "Croqui do auto de infração (SEI 12345678, p. 3), escala 1:25.000"
```

O script:
- converte os pontos para SIRGAS 2000 e calcula em UTM da zona (metros);
- escolhe a transformação mais simples que serve (polinomial de 1ª ordem; sobe para 2ª só se reduzir muito o erro e houver pontos suficientes);
- calcula o erro de cada ponto, o RMS de controle e o RMS de verificação;
- **aponta o ponto suspeito** cuja retirada derruba o erro (ex.: "sem o ponto P6, o RMS cai de 72,02 m para 3,68 m"). Não retira ponto sozinho: confira a posição e a coordenada, corrija ou tire da tabela e rode de novo;
- gera `03_Geo/georreferenciados/<mapa>_georref.tif` em SIRGAS 2000, compactado e com fundo transparente;
- grava o relatório `<mapa>_georref.json` e `.md`, a ficha e o registro.

Código 2 = RMS acima do limite: o raster existe, mas fica marcado como **somente ilustrativo**.

## 4. Conferir

1. Adicione o raster ao projeto (`projeto_qgis.py --bases <tif>`).
2. Faça uma figura de conferência com uma camada independente por cima (polígono de coordenadas do documento, limite do CAR, estrada de referência), só com o contorno (papel `referencia`), e veja se as feições coincidem.
3. Mostre ao usuário: RMS, limite, uso permitido e a figura de conferência.

## Regras

- Georreferenciamento acima do limite **nunca** serve para medir área, distância ou sobreposição. Só ilustra, e o documento diz isso.
- Sempre registre no documento técnico a fonte do mapa, os pontos usados, o RMS e o limite adotado (Metodologia).
- O mapa original não é alterado; o resultado é um arquivo novo.
- O zip de Geoinformação leva os georreferenciados (pasta `georreferenciados/`).
