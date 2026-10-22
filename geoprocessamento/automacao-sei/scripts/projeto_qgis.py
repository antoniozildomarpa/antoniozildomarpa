"""Cria (ou atualiza) o projeto QGIS padrão do caso e importa as coordenadas validadas.

Roda com o Python do QGIS. No Windows, por exemplo:
    "C:\\Program Files\\QGIS 3.40.0\\bin\\python-qgis.bat" projeto_qgis.py --pasta "<pasta do caso>"
Também roda colado no console Python do QGIS ou pelo servidor QGIS do Claude Code
(nesse caso, chame main(["--pasta", r"<pasta do caso>"])).

O que faz:
    1. Cria 03_Geo/caso.qgz em SIRGAS 2000 (EPSG:4674), elipsoide GRS80, caminhos relativos.
       Se já existir, guarda uma cópia de segurança e só acrescenta ou substitui as camadas deste script.
    2. Grupos: Demanda, Produzidos, Bases oficiais, Imagens.
    3. Para cada *_normalizado.csv de 02_Insumos/tabelas (saída de coordenadas.py):
       vértices e polígono (ou linha) em 03_Geo/vetores_produzidos/caso.gpkg, convertidos para
       EPSG:4674 quando o datum de origem for outro, com área e perímetro elipsoidais.
    4. Acrescenta as camadas de base passadas em --bases (sem copiar, só referência).
    5. Grava 03_Geo/resultados_coordenadas.json, atualiza a ficha e o registro do caso.
"""

import argparse
import csv
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeature,
    QgsField,
    QgsFillSymbol,
    QgsGeometry,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)

from qgis.core import Qgis

if Qgis.QGIS_VERSION_INT >= 33800:
    from qgis.PyQt.QtCore import QMetaType

    T_TEXTO, T_REAL, T_INT = QMetaType.Type.QString, QMetaType.Type.Double, QMetaType.Type.Int
else:  # QGIS anterior a 3.38
    from qgis.PyQt.QtCore import QVariant

    T_TEXTO, T_REAL, T_INT = QVariant.String, QVariant.Double, QVariant.Int

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caso  # noqa: E402  (ficha e registro)
from coordenadas import para_gms  # noqa: E402

CRS_CASO = "EPSG:4674"
ELIPSOIDE = "EPSG:7019"  # GRS80
GRUPOS = ["Demanda", "Produzidos", "Bases oficiais", "Imagens"]


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def iniciar_qgis():
    """Inicia o QGIS sem interface quando o script roda fora do QGIS."""
    if QgsApplication.instance() is not None:
        return None
    app = QgsApplication([], False)
    app.initQgis()
    return app


def grupo(projeto, nome):
    raiz = projeto.layerTreeRoot()
    g = raiz.findGroup(nome)
    if g is None:
        pos = GRUPOS.index(nome) if nome in GRUPOS else len(raiz.children())
        g = raiz.insertGroup(min(pos, len(raiz.children())), nome)
    return g


def remover_camada(projeto, nome):
    for camada in projeto.mapLayersByName(nome):
        projeto.removeMapLayer(camada.id())


def gravar_no_gpkg(camada, gpkg, nome, projeto):
    opcoes = QgsVectorFileWriter.SaveVectorOptions()
    opcoes.driverName = "GPKG"
    opcoes.layerName = nome
    opcoes.fileEncoding = "UTF-8"
    opcoes.actionOnExistingFile = (
        QgsVectorFileWriter.CreateOrOverwriteLayer if Path(gpkg).exists() else QgsVectorFileWriter.CreateOrOverwriteFile
    )
    if hasattr(QgsVectorFileWriter, "writeAsVectorFormatV3"):
        resultado = QgsVectorFileWriter.writeAsVectorFormatV3(camada, str(gpkg), projeto.transformContext(), opcoes)
    else:
        resultado = QgsVectorFileWriter.writeAsVectorFormatV2(camada, str(gpkg), projeto.transformContext(), opcoes)
    if resultado[0] != QgsVectorFileWriter.NoError:
        raise RuntimeError(f"Falha ao gravar {nome} em {gpkg}: {resultado[1]}")
    return QgsVectorLayer(f"{gpkg}|layername={nome}", nome, "ogr")


def rotular(camada, campo):
    cfg = QgsPalLayerSettings()
    cfg.fieldName = campo
    cfg.enabled = True
    camada.setLabeling(QgsVectorLayerSimpleLabeling(cfg))
    camada.setLabelsEnabled(True)


def ler_normalizado(caminho):
    with open(caminho, encoding="utf-8") as fh:
        linhas = list(csv.DictReader(fh, delimiter=";"))
    if not linhas:
        raise ValueError(f"Tabela vazia: {caminho}")
    return linhas


def importar_coordenadas(projeto, csv_norm, gpkg, medidor, tipo):
    linhas = ler_normalizado(csv_norm)
    nome_base = Path(csv_norm).stem.replace("_normalizado", "")
    epsg_origem = int(linhas[0]["epsg"])
    destino = QgsCoordinateReferenceSystem(CRS_CASO)
    origem = QgsCoordinateReferenceSystem(f"EPSG:{epsg_origem}")
    transf = QgsCoordinateTransform(origem, destino, projeto) if epsg_origem != 4674 else None

    pontos = []
    for linha in linhas:
        p = QgsPointXY(float(linha["lon_dec"]), float(linha["lat_dec"]))
        pontos.append(transf.transform(p) if transf else p)

    # vértices
    cv = QgsVectorLayer(f"Point?crs={CRS_CASO}", f"vertices_{nome_base}", "memory")
    pv = cv.dataProvider()
    campos = [QgsField("vertice", T_TEXTO), QgsField("ordem", T_INT), QgsField("lat_gms", T_TEXTO), QgsField("lon_gms", T_TEXTO)]
    if transf:  # guarda também a coordenada como veio, no datum de origem
        campos += [QgsField("lat_gms_origem", T_TEXTO), QgsField("lon_gms_origem", T_TEXTO), QgsField("datum_origem", T_TEXTO)]
    pv.addAttributes(campos)
    cv.updateFields()
    feats = []
    for i, (linha, p) in enumerate(zip(linhas, pontos), start=1):
        f = QgsFeature(cv.fields())
        f.setGeometry(QgsGeometry.fromPointXY(p))
        atributos = [linha["vertice"], i, para_gms(p.y(), "lat"), para_gms(p.x(), "lon")]
        if transf:
            atributos += [linha["lat_gms"], linha["lon_gms"], linha["datum"]]
        f.setAttributes(atributos)
        feats.append(f)
    pv.addFeatures(feats)

    camadas = [(cv, "vertices")]
    medidas = {"camada": f"poligono_{nome_base}" if tipo == "poligono" else f"vertices_{nome_base}", "n_vertices": len(pontos)}

    if tipo in ("poligono", "linha") and len(pontos) >= (3 if tipo == "poligono" else 2):
        geom_tipo = "Polygon" if tipo == "poligono" else "LineString"
        nome = f"{'poligono' if tipo == 'poligono' else 'linha'}_{nome_base}"
        cg = QgsVectorLayer(f"{geom_tipo}?crs={CRS_CASO}", nome, "memory")
        pg = cg.dataProvider()
        pg.addAttributes([QgsField("nome", T_TEXTO), QgsField("area_ha", T_REAL), QgsField("perimetro_m", T_REAL), QgsField("n_vertices", T_INT)])
        cg.updateFields()
        geom = QgsGeometry.fromPolygonXY([pontos + [pontos[0]]]) if tipo == "poligono" else QgsGeometry.fromPolylineXY(pontos)
        area_ha = medidor.measureArea(geom) / 10000 if tipo == "poligono" else None
        perimetro = medidor.measurePerimeter(geom) if tipo == "poligono" else medidor.measureLength(geom)
        f = QgsFeature(cg.fields())
        f.setGeometry(geom)
        f.setAttributes([nome_base, round(area_ha, 4) if area_ha is not None else None, round(perimetro, 2), len(pontos)])
        pg.addFeatures([f])
        camadas.append((cg, tipo))
        medidas.update({"camada": nome, "area_ha": round(area_ha, 4) if area_ha is not None else None, "perimetro_m": round(perimetro, 2)})
        if not geom.isGeosValid():
            medidas["alerta"] = "Geometria inválida segundo o QGIS (GEOS). Confira a ordem dos vértices."

    # compara com o cálculo próprio de coordenadas.py, se o GeoJSON estiver ao lado
    gj = Path(csv_norm).with_name(f"{nome_base}.geojson")
    if gj.exists() and medidas.get("area_ha"):
        props = [ft["properties"] for ft in json.loads(gj.read_text(encoding="utf-8"))["features"] if ft["geometry"]["type"] == "Polygon"]
        if props and props[0].get("area_ha"):
            dif = 100 * (medidas["area_ha"] - props[0]["area_ha"]) / props[0]["area_ha"]
            medidas["diferenca_validacao_pct"] = round(dif, 4)
            if abs(dif) > 0.1:
                medidas["alerta"] = f"Área do QGIS difere {dif:.3f}% da validação. Confira o datum de origem."

    resultado = []
    for camada, papel in camadas:
        nome = camada.name()
        remover_camada(projeto, nome)
        salva = gravar_no_gpkg(camada, gpkg, nome, projeto)
        if papel == "vertices":
            salva.renderer().setSymbol(QgsMarkerSymbol.createSimple({"name": "circle", "color": "255,255,0", "size": "2", "outline_color": "0,0,0"}))
            rotular(salva, "vertice")
        elif papel == "poligono":
            salva.renderer().setSymbol(QgsFillSymbol.createSimple({"color": "0,0,0,0", "outline_color": "255,0,0", "outline_width": "0.6"}))
        else:
            salva.renderer().setSymbol(QgsLineSymbol.createSimple({"line_color": "255,0,0", "line_width": "0.6"}))
        projeto.addMapLayer(salva, False)
        grupo(projeto, "Demanda").addLayer(salva)
        resultado.append(nome)
    medidas["camadas_gpkg"] = resultado
    medidas["datum_origem"] = linhas[0]["datum"]
    return medidas


def adicionar_bases(projeto, caminhos):
    adicionadas = []
    for c in caminhos:
        p = Path(c)
        if p.suffix.lower() in (".tif", ".tiff", ".jp2", ".vrt", ".ecw"):
            camada, destino = QgsRasterLayer(str(p), p.stem), "Imagens"
        else:
            camada, destino = QgsVectorLayer(str(p), p.stem, "ogr"), "Bases oficiais"
        if not camada.isValid():
            print(f"AVISO: não abriu {p}")
            continue
        remover_camada(projeto, camada.name())
        projeto.addMapLayer(camada, False)
        grupo(projeto, destino).addLayer(camada)
        adicionadas.append(str(p))
    return adicionadas


def main(argv=None):
    ap = argparse.ArgumentParser(description="Projeto QGIS padrão do caso.")
    ap.add_argument("--pasta", required=True, help="Pasta do caso")
    ap.add_argument("--tabelas", nargs="*", help="CSVs normalizados (padrão: 02_Insumos/tabelas/*_normalizado.csv)")
    ap.add_argument("--tipo", default="poligono", choices=["poligono", "pontos", "linha"])
    ap.add_argument("--bases", nargs="*", default=[], help="Camadas de base para referenciar no projeto")
    a = ap.parse_args(argv)

    app = iniciar_qgis()
    try:
        return executar(a)
    finally:
        if app is not None:
            app.exitQgis()


def executar(a):
    projeto = QgsProject()
    try:
        return montar(a, projeto)
    finally:
        # libera camadas antes de encerrar o QGIS; sem isso o PyQGIS pode travar ao sair
        projeto.clear()


def montar(a, projeto):
    pasta = Path(a.pasta)
    geo = pasta / "03_Geo"
    (geo / "vetores_produzidos").mkdir(parents=True, exist_ok=True)
    arq_projeto = geo / "caso.qgz"
    gpkg = geo / "vetores_produzidos" / "caso.gpkg"

    if arq_projeto.exists():
        copia = geo / f"caso_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.qgz"
        shutil.copy2(arq_projeto, copia)
        if not projeto.read(str(arq_projeto)):
            raise RuntimeError(f"Não consegui abrir {arq_projeto}")
        print(f"Projeto existente aberto; cópia de segurança em {copia.name}")
    else:
        projeto.setCrs(QgsCoordinateReferenceSystem(CRS_CASO))
        projeto.setEllipsoid(ELIPSOIDE)
        projeto.setTitle(pasta.name)
    for g in GRUPOS:
        grupo(projeto, g)

    medidor = QgsDistanceArea()
    medidor.setSourceCrs(QgsCoordinateReferenceSystem(CRS_CASO), projeto.transformContext())
    medidor.setEllipsoid(ELIPSOIDE)

    tabelas = a.tabelas if a.tabelas else sorted(str(p) for p in (pasta / "02_Insumos" / "tabelas").glob("*_normalizado.csv"))
    resultados = [importar_coordenadas(projeto, t, gpkg, medidor, a.tipo) for t in tabelas]
    bases = adicionar_bases(projeto, a.bases)

    try:
        projeto.setFilePathStorage(Qgis.FilePathType.Relative)
    except AttributeError:
        projeto.writeEntryBool("Paths", "/Absolute", False)
    projeto.setFileName(str(arq_projeto))
    if not projeto.write():
        raise RuntimeError(f"Não consegui gravar {arq_projeto}")

    saida = {"projeto": str(arq_projeto), "gpkg": str(gpkg), "em": agora(), "coordenadas": resultados, "bases": bases}
    (geo / "resultados_coordenadas.json").write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    ficha_json = pasta / "00_Ficha" / "ficha.json"
    if ficha_json.exists():
        ficha = json.loads(ficha_json.read_text(encoding="utf-8"))
        nomes = {r["camada"] for r in resultados}
        ficha["areas"] = [x for x in ficha.get("areas", []) if not (isinstance(x, dict) and x.get("camada") in nomes)]
        for r in resultados:
            ficha["areas"].append({k: r[k] for k in ("camada", "area_ha", "perimetro_m", "n_vertices", "datum_origem") if k in r}
                                  | {"calculo": "QGIS, elipsoidal GRS80", "em": agora()})
        for item in [f"{n} (caso.gpkg)" for r in resultados for n in r["camadas_gpkg"]] + bases:
            if item not in ficha.setdefault("camadas", []):
                ficha["camadas"].append(item)
        ficha_json.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
        caso.gravar_ficha_md(pasta, ficha)
        resumo = "; ".join(f"{r['camada']}: {r.get('area_ha', '—')} ha" for r in resultados) or "sem tabelas"
        caso.registrar_linha(pasta, "geo", f"Projeto QGIS gravado (caso.qgz). Coordenadas importadas: {resumo}. Bases: {len(bases)}.")

    print(json.dumps(saida, ensure_ascii=False, indent=2))
    return saida


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
