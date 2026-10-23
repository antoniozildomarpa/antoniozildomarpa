# Geoprocessamento e fiscalização ambiental

Regras para o trabalho técnico com imagens de satélite, CAR, embargos e autuações.

## Entregas típicas

1. **Carta Imagem** de um caso de embargo ou autuação, feita no QGIS (Layout + Atlas), com:
   - evolução da vegetação ao longo do tempo;
   - visão geral do imóvel no CAR, com vértices;
   - tabela de coordenadas dos vértices;
   - imagens Planet recortadas na área.
   Skill: `producao-carta-imagem`.
2. **Busca e recorte de imagens** Landsat, Sentinel-2 e ResourceSat-1, em cor real no estilo natural já validado, com foco no polígono e num buffer ao redor.
   Skill: `landsat-estilo-natural-tiarg`.

## Padrões técnicos

- Sistema de referência de coordenadas: SIRGAS 2000, coordenadas geográficas (EPSG:4674).
- Formato das coordenadas na tabela: graus-minutos-segundos.
- Tamanho do buffer: definido caso a caso, sem padrão fixo. Pergunte antes de recortar.
- Formatos de saída: PDF do layout, GeoTIFF dos recortes e vetores em SHP, GPKG e KML.
- Órgão e modelo de relatório: IBAMA (embargos e autos de infração).

## Regras

- Sempre informe a data, o sensor e a resolução de cada imagem usada.
- Nunca altere o projeto QGIS original. Trabalhe em cópia.
- Coordenadas e áreas calculadas são conferidas antes de entrar em relatório ou carta.
- Imagens com nuvem sobre a área de interesse são descartadas ou sinalizadas.
- Nomes de autuados, CPF/CNPJ e números de autos ficam fora do repositório.
