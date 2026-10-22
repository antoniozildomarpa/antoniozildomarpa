---
name: projeto-qgis-caso
description: Cria ou atualiza o projeto QGIS padrão de um caso técnico (SIRGAS 2000, grupos fixos, vértices e polígonos das coordenadas validadas, bases oficiais) e grava as áreas calculadas na ficha. Use depois de validar coordenadas com coordenadas-para-qgis e sempre que for montar ou atualizar o projeto de um caso.
---

# Projeto QGIS do caso

O script `geoprocessamento/automacao-sei/scripts/projeto_qgis.py` monta `03_Geo/caso.qgz` e `03_Geo/vetores_produzidos/caso.gpkg`.

## Como rodar

Use o Python do QGIS. Escolha um caminho:

1. **Terminal (preferido):** procure o `python-qgis.bat` da versão instalada, por exemplo `C:\Program Files\QGIS 3.40.0\bin\python-qgis.bat` (ou `python-qgis-ltr.bat`), e rode:
   ```
   "<caminho>\python-qgis.bat" geoprocessamento/automacao-sei/scripts/projeto_qgis.py --pasta "<pasta do caso>"
   ```
2. **Servidor QGIS do Claude Code ou console Python do QGIS:** execute
   ```python
   import sys; sys.path.insert(0, r"<repositório>\geoprocessamento\automacao-sei\scripts")
   import projeto_qgis; projeto_qgis.main(["--pasta", r"<pasta do caso>"])
   ```
   O script trabalha num projeto separado: o projeto aberto na tela não é alterado.

Opções:
- `--tabelas a.csv b.csv`: só essas tabelas normalizadas (padrão: todas de `02_Insumos/tabelas/`).
- `--tipo poligono|pontos|linha`.
- `--bases <arquivos>`: camadas de `H:\Meu Drive\_GEO\_VETORES` (ou rasters) a referenciar no projeto, sem copiar.

## O que o projeto tem

| Item | Valor |
| --- | --- |
| Sistema de referência | SIRGAS 2000, EPSG:4674 |
| Elipsoide para medidas | GRS80 (EPSG:7019) |
| Caminhos | Relativos (a pasta do caso pode mudar de lugar) |
| Grupos | Demanda, Produzidos, Bases oficiais, Imagens |
| Camadas de coordenadas | `vertices_<tabela>` (rótulo pelo nome do vértice, GMS em SIRGAS) e `poligono_<tabela>` (área em ha e perímetro em m) |

## Rodar de novo

Pode rodar quantas vezes precisar. A cada vez:
- guarda uma cópia `caso_backup_<data_hora>.qgz` antes de mexer;
- substitui só as camadas de coordenadas e bases deste script, mantendo o resto do projeto (camadas e layouts acrescentados depois);
- atualiza as áreas na ficha e registra a etapa `geo`.

Feche o projeto do caso no QGIS antes de rodar, para o GeoPackage não ficar bloqueado.

## Bases online (SISCOM e SEMAS-PA)

As conexões do QGIS com o SISCOM (IBAMA) e a SEMAS-PA ficam no QGIS do usuário. Para usá-las:
1. Pelo servidor QGIS do Claude Code, carregue a camada pela conexão salva e filtre pela área do caso.
2. Exporte o recorte usado para `02_Insumos/consultas_online/<fonte>_<camada>_<AAAAMMDD_HHMM>.gpkg`.
3. Passe o recorte com `--bases` e anote fonte, data e hora em `consultas_online` na ficha.
O recorte guardado é o que vale para o relatório: o dado online pode mudar depois.

## Conferência

Depois de rodar, mostre ao usuário:
- área e perímetro de cada polígono, e a diferença em relação à validação (deve ser menor que 0,1%);
- qualquer alerta de geometria inválida;
- a lista de camadas por grupo.

Testado em 2026-10-22 com QGIS 3.34: projeto, conversão SAD69 → SIRGAS 2000, rótulos, atualização com cópia de segurança e três execuções seguidas sem erro.
