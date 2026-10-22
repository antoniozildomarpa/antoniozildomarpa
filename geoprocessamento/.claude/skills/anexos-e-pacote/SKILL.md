---
name: anexos-e-pacote
description: Prepara os anexos de um caso para o SEI com os nomes e a numeração da minuta (Anexo_N_Chave), monta o zip de Geoinformação com todas as camadas em SHP, GPKG e KML e um LEIA-ME, e confere formato, integridade e tamanho. Use depois da Conferência 3 (minuta aprovada) e antes de lançar no SEI.
---

# Anexos e pacote de Geoinformação

O script `geoprocessamento/automacao-sei/scripts/anexos.py` usa a lista numerada de `05_Documento/anexos.json` (gerada pela minuta). Os números e nomes seguem a ordem de citação no texto.

## 1. Reunir os arquivos de origem

Para cada anexo da lista, exceto a Geoinformação:
- **Carta imagem e mapas**: o PDF exportado do layout do QGIS (skill `producao-carta-imagem`).
- **Documentos do imóvel** (demonstrativo do CAR etc.): o PDF baixado do sistema de origem.
- Coloque o arquivo em `06_Anexos/fontes/` com o nome começando pela chave (`carta_imagem.pdf`, `demonstrativo_car.pdf`) ou informe com `--fonte chave=caminho`.

## 2. Montar

```
python geoprocessamento/automacao-sei/scripts/anexos.py --pasta "<pasta do caso>" \
  --fonte carta_imagem="<arquivo>.pdf" --fonte demonstrativo_car="<arquivo>.pdf"
```

No Windows, se o `ogr2ogr` não estiver no PATH, informe o do QGIS: `--ogr2ogr "C:\Program Files\QGIS 3.40.0\bin\ogr2ogr.exe"`.

O que acontece:
- cada anexo é copiado com o nome final: `Anexo_1_Demonstrativo_Car.pdf`, `Anexo_2_Carta_Imagem.pdf`;
- a versão anterior de um anexo vai para `06_Anexos/_anteriores/<data_hora>/`, nunca é apagada;
- o anexo `geoinformacao` é montado sozinho (seção 3);
- cada arquivo é conferido: PDF válido, zip íntegro, extensão aceita no SEI, tamanho abaixo do limite (`--limite-mb`, padrão 50 MB; confira o limite configurado no SEI do órgão);
- `06_Anexos/manifesto.json` registra número, descrição, arquivo, tamanho e situação; a ficha e o registro são atualizados.

Código de saída 2 = falta anexo ou há arquivo com problema. Resolva e rode de novo.

## 3. Geoinformação (zip)

Formatos usados nos casos: **SHP, GPKG e KML**. O zip `Anexo_N_Geoinformacao.zip` leva:

| Pasta | Conteúdo | Sistema |
| --- | --- | --- |
| `gpkg/geoinformacao.gpkg` | Todas as camadas num só arquivo: produzidas na análise, bases de `02_Insumos/vetores_baixados` e consultas de `02_Insumos/consultas_online` | SIRGAS 2000 (EPSG:4674) |
| `shp/` | Cada camada em Shapefile, com .prj e codificação UTF-8 | SIRGAS 2000 (EPSG:4674) |
| `kml/` | Cada camada em KML, para abrir no Google Earth | WGS 84 (EPSG:4326, exigido pelo formato) |
| `georreferenciados/` | Mapas e imagens georreferenciados do caso, se houver | o do arquivo |
| `LEIA-ME.txt` | Processo, formatos, camadas (produzida ou base), áreas calculadas, consultas online com data e hora, como abrir | — |

Bases que chegam em outro formato (GeoJSON, KMZ etc.) são convertidas para SIRGAS 2000 ao entrar no pacote.

## 4. Conferir antes do SEI (Conferência 4)

Mostre ao usuário:
- a lista do manifesto: número, descrição, arquivo e tamanho de cada anexo;
- o conteúdo do zip de Geoinformação (camadas e formatos);
- avisos, se houver.

Só com a aprovação do usuário o caso segue para o lançamento no SEI.

## Regras

- O nome do anexo vem da minuta. Para mudar um nome ou a ordem, mude o texto (`conteudo.md`) e gere a minuta de novo; nunca renomeie o arquivo à mão.
- Não inclua no zip dados que não foram usados na análise.
- Dados pessoais só quando fizerem parte do documento oficial anexado (ex.: demonstrativo do CAR).
