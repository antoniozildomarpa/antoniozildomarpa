# Exemplos fictícios

Tabelas inventadas para testar os scripts. Nenhum dado real.

| Arquivo | Para testar | Comando |
| --- | --- | --- |
| `ficticio_gms.csv` | Polígono em GMS, SIRGAS 2000, já fechado | `python ../scripts/coordenadas.py ficticio_gms.csv` |
| `ficticio_utm_sad69.csv` | Polígono em UTM zona 22S, datum SAD69 | `python ../scripts/coordenadas.py ficticio_utm_sad69.csv --datum SAD69` |
| `ficticio_com_erros.csv` | Minutos ≥ 60 e lados que se cruzam (deve dar erro) | `python ../scripts/coordenadas.py ficticio_com_erros.csv` |

Resultados esperados: 78,6332 ha no primeiro, 99,9955 ha no segundo (após conversão para SIRGAS 2000, no QGIS) e código de saída 2 no terceiro.

## Figura de mapa (Fase C)

| Arquivo | Uso |
| --- | --- |
| `ficticio_imovel_car.geojson` | Imóvel fictício que envolve a área de `ficticio_gms.csv` |
| `ficticio_hidrografia.geojson` | Rio fictício |
| `Figura_exemplo_area_embargada.png` | Resultado esperado de `figura_mapa.py` (gerado com uma imagem de fundo fictícia, não incluída) |

Para reproduzir: crie um caso, valide `ficticio_gms.csv`, rode `projeto_qgis.py --bases ficticio_imovel_car.geojson ficticio_hidrografia.geojson` e depois o comando de exemplo da skill `figura-mapa-legenda`, sem a camada de imagem.

