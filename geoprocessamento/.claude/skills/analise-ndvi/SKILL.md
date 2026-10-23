---
name: analise-ndvi
description: Análise de NDVI de um caso técnico - índice, classes (floresta densa, vegetação em regeneração, pastagem, solo exposto, água), polígonos das classes em SHP, GPKG e KML, tabela de áreas, comparação com o aspecto visual da imagem em cor real e interpretação simplificada para quem não é especialista. Use quando o plano de análise do caso pedir NDVI ou classes de cobertura da vegetação.
---

# Análise de NDVI

Etapa opcional do fluxo: só entra quando o plano aprovado na Conferência 1 pede. Quem faz é o `agente-ndvi`, com o script `geoprocessamento/automacao-sei/scripts/ndvi.py` (Python do QGIS; no Windows, pelo PowerShell e sem `-I`).

## O que o NDVI precisa

- **Bandas do vermelho e do infravermelho próximo (NIR) da mesma cena**, em reflectância de superfície, recortadas com o mesmo buffer da imagem em cor real. Quem baixa é o `agente-imagens`:

  | Sensor | Vermelho | NIR | Máscara de nuvem | Escala e deslocamento |
  | --- | --- | --- | --- | --- |
  | Sentinel-2 L2A | `B04` | `B08` | `SCL` (válidos 4, 5, 6, 7) | 0,0001 e -0,1 (cenas a partir de 25/01/2022); 0,0001 e 0 antes |
  | Landsat 8 e 9 C2 L2 | `SR_B4` (`red`) | `SR_B5` (`nir08`) | `QA_PIXEL` convertido em 0/1 | 0,0000275 e -0,2 |
  | Landsat 5 e 7 C2 L2 | `SR_B3` (`red`) | `SR_B4` (`nir08`) | `QA_PIXEL` convertido em 0/1 | 0,0000275 e -0,2 |
  | ResourceSat-1 LISS-3 | `BAND3` | `BAND4` | sem máscara; conferir na prévia | sem escala (valores digitais: o NDVI sai comparável só dentro da mesma cena) |
  | PlanetScope | banda 3 | banda 4 | `udm2` | só com produto de reflectância (analytic SR), que exige pedido no Planet; peça autorização antes |

- **A imagem em cor real da mesma cena**, para a comparação visual (`--rgb`).
- **O polígono da área de interesse** original, sem buffer.

## Classes padrão

| Classe | NDVI | Aspecto esperado na cor real |
| --- | --- | --- |
| Água ou sombra | abaixo de 0,00 | escuro, azulado ou negro |
| Solo exposto ou área queimada | 0,00 a 0,25 | bege, rosado, cinza; negro se queimada |
| Pastagem ou vegetação rasteira | 0,25 a 0,55 | verde-claro a amarelado, liso e homogêneo |
| Vegetação em regeneração | 0,55 a 0,75 | verde médio, textura irregular |
| Floresta densa | 0,75 ou mais | verde-escuro, rugoso, com sombra entre copas |

As faixas valem para reflectância de superfície na Amazônia, estação seca. Em outra região ou estação, ou se a comparação visual mostrar erro sistemático, proponha novos limites num JSON (mesma estrutura de `CLASSES_PADRAO` do script) e use `--classes` **só depois da aprovação do usuário**. Registre os limites usados na ficha.

Área mínima mapeada: 0,5 ha (manchas menores entram na classe vizinha). Ajuste com `--area-minima-ha` se o caso pedir mais detalhe.

## Como rodar

```
python-qgis.bat ndvi.py --pasta "<caso>" --nome S2_2025-07-19 \
    --vermelho "<caso>/02_Insumos/imagens/S2_2025-07-19_B04.tif" --nir "<caso>/02_Insumos/imagens/S2_2025-07-19_B08.tif" \
    --escala 0.0001 --deslocamento -0.1 \
    --mascara "<caso>/02_Insumos/imagens/S2_2025-07-19_SCL.tif" --mascara-validos 4 5 6 7 \
    --area "<caso>/03_Geo/vetores_produzidos/caso.gpkg:<camada do polígono>" \
    --rgb "<caso>/02_Insumos/imagens/S2_2025-07-19.tif" \
    --sensor "Sentinel-2B MSI L2A" --data 2025-07-19 --resolucao 10
```

## Onde fica cada produto

| Produto | Pasta do caso |
| --- | --- |
| NDVI e classes (GeoTIFF com estilo .qml) | `03_Geo/raster/ndvi/` |
| Polígonos das classes: recorte inteiro e só a área de interesse | `03_Geo/vetores_produzidos/ndvi/` (`.gpkg`, `shp/`, `kml/`, com estilo .qml ao lado dos SHP) |
| As mesmas camadas no projeto e no zip de Geoinformação | `caso.gpkg` e `caso.qgz` (grupo Produzidos) |
| Tabela por classe (área em ha e %, NDVI médio), pronta para a minuta | `03_Geo/raster/ndvi/<nome>_ndvi_tabela.md` e `.csv` |
| Rascunho da interpretação simplificada | `03_Geo/raster/ndvi/<nome>_ndvi_interpretacao.md` |
| Painel (cor real, NDVI, classes, divergências) e amostras da cor real por classe | `03_Geo/raster/ndvi/conferencia/` |
| Resumo, comparação e perguntas de conferência | `03_Geo/raster/ndvi/<nome>_ndvi.json` |

## Comparação com o aspecto visual

O script mede, dentro da área de interesse:
- a cor média de cada classe na imagem em cor real e o verde visível (índice VARI);
- se o verde visível cresce junto com o NDVI das classes;
- onde os dois divergem: **magenta** = o NDVI indica vegetação, mas a imagem não parece verde (névoa, fumaça, nuvem fina, data diferente); **azul** = a imagem parece verde, mas o NDVI não indica vegetação (pasto seco, desalinhamento, borda de classe).

O agente abre o painel e as amostras e escreve a comparação classe por classe: o que a cor real confirma, o que diverge e por quê. O texto substitui o marcador `[COMPARAÇÃO VISUAL: ...]` do rascunho; o revisor bloqueia a minuta se o marcador ficar.

## Interpretação para quem não é especialista

- Explique o NDVI em uma frase antes dos números.
- Diga a classe predominante e as áreas, em hectares e porcentagem.
- Use "indica", "é compatível com"; nunca afirme que a área "é" pastagem ou floresta só pelo NDVI.
- Sempre as limitações: classes indicativas, efeito da estação, névoa e sombra, área mínima mapeada.

## Figuras do documento

Com `figura_mapa.py`, como qualquer figura (skill `figura-mapa-legenda`):
- classes: `--camadas <poligono> ndvi_<nome>_classes_area --estilos <poligono>=contorno --nomes "<poligono>=Área de interesse" "ndvi_<nome>_classes_area=Classes de NDVI"`;
- NDVI contínuo: `--camadas <poligono> "NDVI <nome>" --estilos <poligono>=contorno --nomes ... "NDVI <nome>=NDVI"`.

Na fonte da figura: sensor, data e resolução da imagem e "classes de NDVI por faixas de valor".
