# Exemplos da análise de NDVI (imagem fictícia)

Imagem sintética, no formato da Sentinel-2 (B04, B08, SCL e cor real), gerada por `gerar_imagem_ficticia.py` em volta da área de teste de `../teste_imagens/` (391,24 ha). Não é uma cena real.

A imagem tem floresta, pastagem, regeneração, solo exposto, estrada, rio, uma nuvem mascarada (2 ha dentro da área) e uma mancha de névoa fora da área, para testar as divergências.

- `Painel_comparacao_ndvi_ficticio.png`: cor real, NDVI, classes e divergências (a névoa aparece em magenta).
- `Amostras_classes_ficticio.png`: recortes da cor real no miolo de cada classe.
- `Figura_classes_ndvi_ficticio.png` e `Figura_ndvi_ficticio.png`: figuras do documento, geradas com `figura_mapa.py`.
- `Tabela_ndvi_ficticio.md`: tabela pronta para a minuta (as classes somam 389,25 ha; os 2,00 ha restantes são a nuvem).

Para refazer: `python-qgis.bat gerar_imagem_ficticia.py <area_teste_imagens.gpkg> <pasta do caso>/02_Insumos/imagens` e depois `ndvi.py` como na skill `analise-ndvi`.
