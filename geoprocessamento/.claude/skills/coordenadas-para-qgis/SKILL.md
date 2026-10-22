---
name: coordenadas-para-qgis
description: Converte tabelas de coordenadas de documentos (memoriais, autos, termos de embargo, laudos) em vértices e polígonos validados, em GMS, grau decimal ou UTM, em qualquer datum usado no Brasil. Use sempre que um documento do caso trouxer coordenadas de pontos ou polígonos que importam para a análise.
---

# Coordenadas para o QGIS

Duas etapas: primeiro a tabela vira um CSV limpo e é validada (`coordenadas.py`); depois entra no projeto QGIS do caso (skill `projeto-qgis-caso`).

## 1. Transcrever a tabela

1. Copie a tabela do documento para um CSV em `02_Insumos/tabelas/`, com nome que diga o que é: `area_embargada_TEI.csv`, `imovel_memorial.csv`.
2. Cabeçalho com nomes reconhecidos:
   - vértice: `Vertice` (ou ponto, id, nome, marco)
   - geográficas: `Latitude` e `Longitude`
   - UTM: `E` e `N`, e `Zona` se houver
3. Copie os valores **exatamente como estão no documento**, sem converter nada à mão. O script entende `03°45'12,345" S`, `3 45 12,345 S`, `-3°45'12"`, `-3,7534`, `03°45,205' S` e o mesmo para longitude (O, W ou sinal negativo).
4. Se o documento for digitalizado, confira cada valor do OCR contra a imagem antes de rodar. Marque `[OCR INCERTO]` no relatório de validação quando houver dúvida.
5. Anote na ficha de onde veio a tabela: documento SEI, página e datum declarado.

## 2. Validar

```
python geoprocessamento/automacao-sei/scripts/coordenadas.py "<pasta do caso>/02_Insumos/tabelas/<tabela>.csv" --datum SIRGAS2000 --tipo poligono
```

- `--datum`: o que o documento declara. `SIRGAS2000`, `WGS84`, `SAD69` ou `CORREGO_ALEGRE`. Se o documento não declarar, pergunte ao usuário e registre a suposição.
- `--tipo`: `poligono`, `pontos` ou `linha`.
- UTM sem coluna de zona: `--zona 21`, `22` ou `23` (Pará). `--hemisferio N` para pontos ao norte do Equador.

O script confere e aponta:
- minutos ou segundos maiores ou iguais a 60;
- coordenadas fora do Brasil;
- longitude positiva sem hemisfério (corrige para Oeste e avisa) e latitude positiva sem hemisfério (avisa, porque o Pará tem área ao norte do Equador);
- vértices repetidos e polígono que já vinha fechado;
- lados que se cruzam (autointerseção);
- lado muito maior que os outros (possível erro de digitação).

Gera, ao lado da tabela:
- `<tabela>_validacao.md` com erros e alertas;
- `<tabela>_normalizado.csv` com grau decimal e GMS;
- `<tabela>.geojson` com área e perímetro elipsoidais.

Código de saída 2 significa erro: nada é gerado além da validação. Mostre os erros ao usuário, corrija a transcrição e rode de novo. Nunca "conserte" um valor do documento por conta própria: se o documento tiver erro, ele vai para o relatório como constatação.

## 3. Levar para o QGIS

Siga a skill `projeto-qgis-caso`. Ela importa todos os `*_normalizado.csv` da pasta de tabelas, converte para SIRGAS 2000 quando o datum for outro e grava a área calculada pelo QGIS na ficha.

## Regras

- A tabela de coordenadas que vai para o relatório sai sempre em **SIRGAS 2000, graus-minutos-segundos**, a partir da camada de vértices do projeto (campos `lat_gms` e `lon_gms`). Quando o datum de origem era outro, os valores originais ficam em `lat_gms_origem` e `lon_gms_origem`.
- A área oficial é a do QGIS. A do script serve de conferência: diferença acima de 0,1% é investigada antes de seguir.
- Precisão conferida contra o pyproj: conversão UTM com diferença de 0,1 mm e área com diferença até 0,0003%.
