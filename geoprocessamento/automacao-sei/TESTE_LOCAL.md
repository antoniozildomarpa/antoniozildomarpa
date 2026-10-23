# Roteiro de teste no seu computador

Tudo foi construído e testado na nuvem com dados fictícios (QGIS 3.34). Este roteiro valida no seu computador, na ordem. Abra o Claude Code na pasta do repositório (`C:\Users\Work\Projetos\antoniozildomarpa`), rode `git pull` e peça cada passo ao Claude.

Marque cada item ao concluir.

## 0. Preparação (uma vez)

- [ ] `pip install python-docx` (para a minuta em Word).
- [ ] Localizar o Python do QGIS: `C:\Program Files\QGIS <versão>\bin\python-qgis.bat` (ou `python-qgis-ltr.bat`). Anotar a versão do QGIS na ficha de decisões do `PLANO.md`.
- [ ] Localizar o `ogr2ogr.exe` na mesma pasta `bin` do QGIS.

## 1. Fases A a E e H, com os exemplos fictícios

Peça ao Claude: "Rode o teste local das Fases A a H com os exemplos de `geoprocessamento/automacao-sei/exemplos/`, numa pasta de teste `H:\Meu Drive\_GEO\_DEMANDAS_EMI\teste`".

- [ ] A: caso criado com as 15 subpastas, ficha e registro.
- [ ] B: `ficticio_gms.csv` = 78,6332 ha; `ficticio_utm_sad69.csv` = 99,9955 ha no QGIS; `ficticio_com_erros.csv` dá erro.
- [ ] C: figura gerada com legenda no canto livre, escala refinada, grade na borda, rótulos com buffer. Compare com `Figura_exemplo_area_embargada.png`.
- [ ] D: minuta em Word abre no Word; figura com título acima e fonte abaixo; tabela de coordenadas inteira.
- [ ] E: zip de Geoinformação com `gpkg/`, `shp/` e `kml/`; KML abre no Google Earth.
- [ ] H: croqui fictício georreferenciado; o P6 é apontado como suspeito; sem ele, RMS ≈ 3,7 m.

## 2. Com dados reais, ainda sem SEI

- [ ] Escolher um caso já concluído (que você conhece bem) e refazer só o geoprocessamento e uma figura. Comparar com o que você entregou.
- [ ] Testar uma consulta ao SISCOM e uma à SEMAS-PA pelo servidor QGIS, com o recorte salvo em `consultas_online`.

- [x] Imagens (`agente-imagens`): num caso já concluído, pedir uma Sentinel-2 e uma Landsat do ano da infração. Conferir se ele aplica o buffer padrão (2 km abaixo de 10 ha ou ponto; 3 km a partir de 10 ha), mede a nuvem só no polígono, salva em `02_Insumos/imagens/` e registra sensor, data e resolução. Comparar a cor com uma imagem que você já aprovou. Landsat refeito com realce comum às 3 bandas (23/10/2026).
- [x] Planet: com o plugin aberto e a sua sessão ativa, pedir um mosaico mensal e conferir o nome `planetMosaico_MM_AAAA`. Mosaico 07/2025 e cena diária de 13/08/2025 aprovados; nuvem confirmada na prévia, porque a medida automática não pega sombra nem névoa (23/10/2026).

- [ ] NDVI (`agente-ndvi`): com a área de teste e a Sentinel-2 de 19/07/2025, pedir as bandas B04, B08 e SCL ao `agente-imagens` e rodar a análise. Conferir: classes somando 391,24 ha, polígonos em `03_Geo/vetores_produzidos/ndvi/` (GPKG, SHP e KML), painel de comparação com a cor real e a interpretação.

## 3. Leitura no SEI (somente leitura)

- [ ] Abrir no Chrome um processo já concluído e pedir: "use a skill leitura-processo-sei neste processo, sem baixar nada". Conferir se a demanda foi bem identificada.
- [ ] Repetir permitindo baixar 1 ou 2 documentos para uma pasta de teste.

## 4. Lançamento no SEI

- [ ] Confirmar se há um processo de teste ou de treinamento no SEI do IBAMA.
- [ ] No processo de teste: documento em branco, um anexo externo, colar texto curto, um link para o anexo e um despacho. Conferir.
- [ ] Testar o gancho de segurança: pedir ao Claude para clicar em "Assinar" no processo de teste. O esperado é a ação ser bloqueada.

## 5. Primeiro caso real completo

- [ ] Pedir: "inicie o caso do processo aberto" (skill `caso-sei`) e acompanhar as quatro conferências.
- [ ] Ao final, anotar no `PLANO.md` o que ajustar.
