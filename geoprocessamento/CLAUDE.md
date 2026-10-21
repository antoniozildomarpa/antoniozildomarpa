# Geoprocessamento e fiscalização ambiental

Regras para o trabalho técnico com imagens de satélite, CAR, embargos e autuações. Itens marcados `[A CONFIRMAR]` ainda precisam ser preenchidos por você.

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

- Sistema de referência de coordenadas: `[A CONFIRMAR]` (ex.: SIRGAS 2000, UTM ou geográficas).
- Formato das coordenadas na tabela: `[A CONFIRMAR]` (graus decimais, graus-minutos-segundos ou UTM).
- Tamanho padrão do buffer: `[A CONFIRMAR]`.
- Formato de saída: `[A CONFIRMAR]` (PDF do layout, PNG, GeoTIFF).
- Órgão e modelo de relatório usados: `[A CONFIRMAR]`.

## Regras

- Sempre informe a data, o sensor e a resolução de cada imagem usada.
- Nunca altere o projeto QGIS original. Trabalhe em cópia.
- Coordenadas e áreas calculadas são conferidas antes de entrar em relatório ou carta.
- Imagens com nuvem sobre a área de interesse são descartadas ou sinalizadas.
- Nomes de autuados, CPF/CNPJ e números de autos ficam fora do repositório.
