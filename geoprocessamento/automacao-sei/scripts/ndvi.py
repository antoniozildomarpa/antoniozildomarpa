"""Análise de NDVI de um caso: índice, classes, polígonos, tabelas, comparação com a cor real e rascunho de interpretação.

Uso (Python do QGIS; no Windows, pelo PowerShell):
    python-qgis.bat ndvi.py --pasta "<caso>" --nome S2_2025-07-19 \
        --vermelho "<caso>/02_Insumos/imagens/S2_2025-07-19_B04.tif" \
        --nir "<caso>/02_Insumos/imagens/S2_2025-07-19_B08.tif" \
        --escala 0.0001 --deslocamento -0.1 \
        --mascara "<caso>/02_Insumos/imagens/S2_2025-07-19_SCL.tif" --mascara-validos 4 5 6 7 \
        --area "<caso>/03_Geo/vetores_produzidos/caso.gpkg:poligono_area" \
        --rgb "<caso>/02_Insumos/imagens/S2_2025-07-19.tif" \
        --sensor "Sentinel-2B MSI L2A" --data 2025-07-19 --resolucao 10

    --vermelho e --nir aceitam "arquivo:banda" (padrão banda 1). Podem ser o mesmo arquivo multibanda.
    --escala/--deslocamento convertem o valor gravado em reflectância (Landsat C2 L2: 0.0000275 e -0.2;
    Sentinel-2 L2A depois de jan/2022: 0.0001 e -0.1; antes: 0.0001 e 0).

Gera, na pasta do caso:
    03_Geo/raster/ndvi/<nome>_ndvi.tif              NDVI (float32, nodata -9999) e estilo .qml
    03_Geo/raster/ndvi/<nome>_ndvi_classes.tif      classes (1 byte, 0 = sem dado) e estilo .qml
    03_Geo/raster/ndvi/<nome>_ndvi_tabela.csv/.md   área e NDVI por classe, dentro da área de interesse
    03_Geo/raster/ndvi/<nome>_ndvi_interpretacao.md rascunho da interpretação simplificada
    03_Geo/raster/ndvi/<nome>_ndvi.json             resumo, classes, comparação e perguntas de conferência
    03_Geo/raster/ndvi/conferencia/                 painel (cor real | NDVI | classes | divergências) e amostras por classe
    03_Geo/vetores_produzidos/ndvi/                 polígonos das classes em GPKG, SHP e KML
    caso.gpkg e caso.qgz                            as camadas de classes entram no projeto do caso (grupo Produzidos)

As classes são indicativas, por faixa de NDVI. Os limites padrão estão em CLASSES_PADRAO e podem ser trocados
com --classes <arquivo.json> (mesma estrutura), depois da conferência visual e com aprovação do usuário.
"""

import argparse
import csv
import gc
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from osgeo import gdal, ogr, osr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coordenadas import area_elipsoidal  # noqa: E402

gdal.UseExceptions()
ogr.UseExceptions()

NODATA = -9999.0

# Faixas para reflectância de superfície, calibradas para a Amazônia na estação seca.
# Cores suaves (padrão cartográfico). "aspecto" descreve como a classe costuma aparecer na cor real.
CLASSES_PADRAO = [
    {"codigo": 1, "classe": "Água ou sombra", "min": -1.0, "max": 0.0, "cor": "#7fa7c9",
     "aspecto": "superfície escura, azulada ou negra: rio, lago, açude, sombra de nuvem ou de relevo"},
    {"codigo": 2, "classe": "Solo exposto ou área queimada", "min": 0.0, "max": 0.25, "cor": "#d9b48f",
     "aspecto": "tons bege, rosados, cinza ou negros (queimada): solo, estrada, área recém-desmatada ou queimada"},
    {"codigo": 3, "classe": "Pastagem ou vegetação rasteira", "min": 0.25, "max": 0.55, "cor": "#efe3a6",
     "aspecto": "verde-claro a amarelado, textura lisa e homogênea, às vezes com árvores isoladas"},
    {"codigo": 4, "classe": "Vegetação em regeneração", "min": 0.55, "max": 0.75, "cor": "#a9cf8f",
     "aspecto": "verde médio, textura irregular, sem o dossel rugoso e as sombras entre copas da floresta"},
    {"codigo": 5, "classe": "Floresta densa", "min": 0.75, "max": 1.0, "cor": "#4f8a5b",
     "aspecto": "verde-escuro, textura rugosa (copas) com sombras finas entre as árvores"},
]
VEGETACAO_MIN = 0.55     # NDVI a partir do qual se espera vegetação lenhosa
SEM_VEGETACAO_MAX = 0.25  # NDVI abaixo do qual não se espera vegetação


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def fmt(v, casas=2):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def hex_rgb(cor):
    cor = cor.lstrip("#")
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))


# ---------- leitura e alinhamento ----------

def separar(arg):
    """'arquivo:banda' -> (arquivo, banda). Cuida da letra de unidade do Windows (C:\\...)."""
    caminho, banda = arg, 1
    if ":" in arg:
        base, fim = arg.rsplit(":", 1)
        if fim.isdigit() and len(base) > 1:
            caminho, banda = base, int(fim)
    return caminho, banda


def alinhar(arquivo, banda, grade, metodo):
    """Lê uma banda reamostrada para a grade de referência (mesmo SRC, extensão e resolução)."""
    ds = gdal.Open(arquivo)
    gt, w, h, wkt = grade
    opcoes = gdal.WarpOptions(format="MEM", outputBounds=(gt[0], gt[3] + h * gt[5], gt[0] + w * gt[1], gt[3]),
                              width=w, height=h, dstSRS=wkt, resampleAlg=metodo, srcBands=[banda] if banda else None)
    out = gdal.Warp("", ds, options=opcoes)
    b = out.GetRasterBand(1)
    arr = b.ReadAsArray().astype("float64")
    nd = ds.GetRasterBand(banda or 1).GetNoDataValue()
    return arr, nd


def ler_rgb(arquivo, grade):
    ds = gdal.Open(arquivo)
    gt, w, h, wkt = grade
    opcoes = gdal.WarpOptions(format="MEM", outputBounds=(gt[0], gt[3] + h * gt[5], gt[0] + w * gt[1], gt[3]),
                              width=w, height=h, dstSRS=wkt, resampleAlg="average", srcBands=[1, 2, 3])
    out = gdal.Warp("", ds, options=opcoes)
    return np.stack([out.GetRasterBand(i).ReadAsArray() for i in (1, 2, 3)]).astype("float64")


def ler_area(arg):
    """Polígono de interesse (união das feições), em SIRGAS 2000 (EPSG:4674)."""
    caminho, camada = arg, None
    if ":" in arg:
        base, fim = arg.rsplit(":", 1)
        if len(base) > 1 and not fim.startswith("\\") and not fim.startswith("/"):
            caminho, camada = base, fim
    ds = ogr.Open(caminho)
    lyr = ds.GetLayerByName(camada) if camada else ds.GetLayer(0)
    if lyr is None:
        raise RuntimeError(f"Camada '{camada}' não encontrada em {caminho}")
    srs_destino = osr.SpatialReference()
    srs_destino.ImportFromEPSG(4674)
    srs_destino.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    uniao = None
    for f in lyr:
        g = f.GetGeometryRef().Clone()
        srs = g.GetSpatialReference() or lyr.GetSpatialRef()
        if srs is not None:
            srs = srs.Clone()
            srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            g.Transform(osr.CoordinateTransformation(srs, srs_destino))
        uniao = g if uniao is None else uniao.Union(g)
    if uniao is None:
        raise RuntimeError(f"A camada de área de interesse está vazia: {arg}")
    uniao.AssignSpatialReference(srs_destino)
    return uniao


# ---------- área elipsoidal de geometrias OGR em SIRGAS 2000 ----------

def area_ha(geom):
    """Área elipsoidal (ha) de Polygon/MultiPolygon em graus (EPSG:4674): anel externo menos os buracos."""
    total = 0.0
    tipo = ogr.GT_Flatten(geom.GetGeometryType())
    poligonos = [geom] if tipo == ogr.wkbPolygon else [geom.GetGeometryRef(i) for i in range(geom.GetGeometryCount())] \
        if tipo in (ogr.wkbMultiPolygon, ogr.wkbGeometryCollection) else []
    for p in poligonos:
        if ogr.GT_Flatten(p.GetGeometryType()) != ogr.wkbPolygon:
            continue
        for i in range(p.GetGeometryCount()):
            anel = p.GetGeometryRef(i)
            pts = [(anel.GetY(k), anel.GetX(k)) for k in range(anel.GetPointCount())]
            if len(pts) < 4:
                continue
            a = area_elipsoidal(pts[:-1], "SIRGAS2000") / 10000
            total += a if i == 0 else -a
    return total


# ---------- classificação ----------

def classificar(ndvi, valido, classes):
    cls = np.zeros(ndvi.shape, dtype="uint8")
    for c in classes:
        sel = valido & (ndvi >= c["min"]) & (ndvi < c["max"] if c["max"] < 1.0 else ndvi <= c["max"])
        cls[sel] = c["codigo"]
    return cls


def mem_raster(arr, grade, tipo):
    gt, w, h, wkt = grade
    ds = gdal.GetDriverByName("MEM").Create("", w, h, 1, tipo)
    ds.SetGeoTransform(gt)
    ds.SetProjection(wkt)
    ds.GetRasterBand(1).WriteArray(arr)
    return ds


def gravar_tif(caminho, arr, grade, tipo, nodata=None, descricao=None):
    gt, w, h, wkt = grade
    ds = gdal.GetDriverByName("GTiff").Create(str(caminho), w, h, 1, tipo, options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform(gt)
    ds.SetProjection(wkt)
    b = ds.GetRasterBand(1)
    if nodata is not None:
        b.SetNoDataValue(nodata)
    if descricao:
        b.SetDescription(descricao)
    b.WriteArray(arr)
    b.FlushCache()
    ds = None


def peneirar(cls, valido, grade, minimo_px):
    """Remove manchas menores que a área mínima (pixels), absorvidas pela classe vizinha."""
    if minimo_px <= 1:
        return cls
    ds = mem_raster(cls, grade, gdal.GDT_Byte)
    msk = mem_raster(valido.astype("uint8"), grade, gdal.GDT_Byte)
    b = ds.GetRasterBand(1)
    gdal.SieveFilter(b, msk.GetRasterBand(1), b, int(minimo_px), 8)
    out = b.ReadAsArray()
    out[~valido] = 0
    return out


def area_para_mascara(area_geo, grade):
    """Rasteriza a área de interesse na grade (1 = dentro)."""
    gt, w, h, wkt = grade
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    g = area_geo.Clone()
    g.Transform(osr.CoordinateTransformation(area_geo.GetSpatialReference(), srs))
    drv = ogr.GetDriverByName("Memory")
    vds = drv.CreateDataSource("")
    lyr = vds.CreateLayer("a", srs, ogr.wkbMultiPolygon)
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(g)
    lyr.CreateFeature(f)
    ds = gdal.GetDriverByName("MEM").Create("", w, h, 1, gdal.GDT_Byte)
    ds.SetGeoTransform(gt)
    ds.SetProjection(wkt)
    gdal.RasterizeLayer(ds, [1], lyr, burn_values=[1], options=["ALL_TOUCHED=FALSE"])
    dentro = ds.GetRasterBand(1).ReadAsArray().astype(bool)
    # contorno, para desenhar nos painéis
    ds2 = gdal.GetDriverByName("MEM").Create("", w, h, 1, gdal.GDT_Byte)
    ds2.SetGeoTransform(gt)
    ds2.SetProjection(wkt)
    lyr2 = vds.CreateLayer("c", srs, ogr.wkbMultiLineString)
    f2 = ogr.Feature(lyr2.GetLayerDefn())
    f2.SetGeometry(g.GetBoundary())
    lyr2.CreateFeature(f2)
    gdal.RasterizeLayer(ds2, [1], lyr2, burn_values=[1], options=["ALL_TOUCHED=TRUE"])
    contorno = ds2.GetRasterBand(1).ReadAsArray().astype(bool)
    return dentro, contorno, g


def poligonizar(cls, ndvi, valido, grade, classes):
    """Polígonos das classes (SRC da imagem) com código, classe e NDVI médio; devolve lista de (geom, attrs)."""
    gt, w, h, wkt = grade
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    ds = mem_raster(cls, grade, gdal.GDT_Byte)
    msk = mem_raster((cls > 0).astype("uint8"), grade, gdal.GDT_Byte)
    vds = ogr.GetDriverByName("Memory").CreateDataSource("")
    lyr = vds.CreateLayer("p", srs, ogr.wkbPolygon)
    lyr.CreateField(ogr.FieldDefn("codigo", ogr.OFTInteger))
    gdal.Polygonize(ds.GetRasterBand(1), msk.GetRasterBand(1), lyr, 0, ["8CONNECTED=8"])
    # NDVI médio por polígono: rasteriza o número de cada polígono e soma por grupo
    lyr.CreateField(ogr.FieldDefn("pid", ogr.OFTInteger))
    feats = []
    for i, f in enumerate(lyr, start=1):
        f.SetField("pid", i)
        lyr.SetFeature(f)
    ids = gdal.GetDriverByName("MEM").Create("", w, h, 1, gdal.GDT_Int32)
    ids.SetGeoTransform(gt)
    ids.SetProjection(wkt)
    gdal.RasterizeLayer(ids, [1], lyr, options=["ATTRIBUTE=pid"])
    pid = ids.GetRasterBand(1).ReadAsArray()
    sel = valido & (pid > 0)
    n = int(pid.max()) + 1
    soma = np.bincount(pid[sel], weights=ndvi[sel], minlength=n)
    cont = np.bincount(pid[sel], minlength=n)
    nomes = {c["codigo"]: c["classe"] for c in classes}
    lyr.ResetReading()
    for f in lyr:
        i = f.GetField("pid")
        cod = f.GetField("codigo")
        if cod not in nomes:
            continue
        media = soma[i] / cont[i] if i < n and cont[i] else None
        feats.append((f.GetGeometryRef().Clone(), {"codigo": cod, "classe": nomes[cod],
                                                   "ndvi_medio": round(float(media), 3) if media is not None else None}))
    return feats, srs


def para_sirgas(feats, srs):
    destino = osr.SpatialReference()
    destino.ImportFromEPSG(4674)
    destino.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    t = osr.CoordinateTransformation(srs, destino)
    out = []
    for g, attrs in feats:
        g.Transform(t)
        g.AssignSpatialReference(destino)
        out.append((g, attrs))
    return out, destino


def recortar(feats, area_geo):
    out = []
    for g, attrs in feats:
        if not g.Intersects(area_geo):
            continue
        r = g.Intersection(area_geo)
        if r is None or r.IsEmpty():
            continue
        tipo = ogr.GT_Flatten(r.GetGeometryType())
        if tipo == ogr.wkbGeometryCollection:
            mp = ogr.Geometry(ogr.wkbMultiPolygon)
            for i in range(r.GetGeometryCount()):
                p = r.GetGeometryRef(i)
                if ogr.GT_Flatten(p.GetGeometryType()) == ogr.wkbPolygon:
                    mp.AddGeometry(p)
            r = mp
        if ogr.GT_Flatten(r.GetGeometryType()) not in (ogr.wkbPolygon, ogr.wkbMultiPolygon):
            continue
        r.AssignSpatialReference(area_geo.GetSpatialReference())
        out.append((r, dict(attrs)))
    return out


def gravar_vetor(caminho, driver, nome, feats, srs, opcoes=None, transformar_para=None):
    drv = ogr.GetDriverByName(driver)
    if driver != "GPKG" and Path(caminho).exists():
        drv.DeleteDataSource(str(caminho))
    if driver == "GPKG" and Path(caminho).exists():
        ds = ogr.Open(str(caminho), 1)
        if ds.GetLayerByName(nome) is not None:
            ds.DeleteLayer(nome)
        if ds.GetLayerByName("layer_styles") is not None:  # estilo antigo da camada refeita
            ds.ExecuteSQL(f"DELETE FROM layer_styles WHERE f_table_name = '{nome}'")
    else:
        ds = drv.CreateDataSource(str(caminho))
    srs_saida = srs
    t = None
    if transformar_para is not None:
        srs_saida = osr.SpatialReference()
        srs_saida.ImportFromEPSG(transformar_para)
        srs_saida.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        t = osr.CoordinateTransformation(srs, srs_saida)
    lyr = ds.CreateLayer(nome, srs_saida, ogr.wkbMultiPolygon, options=opcoes or [])
    for campo, tipo in [("codigo", ogr.OFTInteger), ("classe", ogr.OFTString), ("ndvi_medio", ogr.OFTReal),
                        ("area_ha", ogr.OFTReal)]:
        fd = ogr.FieldDefn(campo, tipo)
        if campo == "classe":
            fd.SetWidth(60)
        lyr.CreateField(fd)
    for g, attrs in feats:
        f = ogr.Feature(lyr.GetLayerDefn())
        for k, v in attrs.items():
            if v is not None:
                f.SetField(k, v)
        geo = ogr.ForceToMultiPolygon(g.Clone())
        if t is not None:
            geo.Transform(t)
        f.SetGeometry(geo)
        lyr.CreateFeature(f)
    ds = None


# ---------- comparação com a cor real ----------

def comparar_visual(rgb, ndvi, cls, valido, dentro, classes, grade):
    """Cor média de cada classe na imagem em cor real e pixels em que NDVI e aspecto visual divergem."""
    r, g, b = rgb
    soma = r + g + b
    with np.errstate(divide="ignore", invalid="ignore"):
        vari = np.where(np.abs(g + r - b) > 1, (g - r) / (g + r - b), 0.0)  # verde visível (VARI)
    vari = np.clip(vari, -1, 1)
    brilho = soma / 3
    todos = valido & (soma > 3)
    ok = todos & dentro
    veg_sem_verde_todos = todos & (ndvi >= VEGETACAO_MIN) & ((vari < 0) | (brilho > 200))
    verde_sem_veg_todos = todos & (ndvi < SEM_VEGETACAO_MAX) & (vari > 0.1) & (brilho < 200)
    divergencia = np.zeros(ndvi.shape, dtype="uint8")  # mapa no recorte inteiro; números só na área de interesse
    divergencia[veg_sem_verde_todos] = 1
    divergencia[verde_sem_veg_todos] = 2
    divergencia = peneirar(divergencia, todos, grade, 6)  # pixels soltos são ruído, não divergência
    veg_sem_verde = (divergencia == 1) & dentro
    verde_sem_veg = (divergencia == 2) & dentro
    por_classe = []
    for c in classes:
        sel = ok & (cls == c["codigo"])
        n = int(sel.sum())
        if n == 0:
            continue
        por_classe.append({
            "codigo": c["codigo"], "classe": c["classe"], "pixels": n,
            "cor_media_rgb": [int(round(float(x[sel].mean()))) for x in (r, g, b)],
            "verde_visivel_medio": round(float(vari[sel].mean()), 3),
            "brilho_medio": round(float(brilho[sel].mean()), 1),
            "divergentes_pct": round(100 * float(((veg_sem_verde | verde_sem_veg) & sel).sum()) / n, 1),
            "aspecto_esperado": c["aspecto"],
        })
    total = int(ok.sum())
    resumo = {
        "pixels_comparados": total,
        "vegetacao_no_ndvi_sem_verde_na_imagem_pct": round(100 * float(veg_sem_verde.sum()) / total, 1) if total else 0,
        "verde_na_imagem_sem_vegetacao_no_ndvi_pct": round(100 * float(verde_sem_veg.sum()) / total, 1) if total else 0,
    }
    resumo["concordancia_pct"] = round(100 - resumo["vegetacao_no_ndvi_sem_verde_na_imagem_pct"]
                                       - resumo["verde_na_imagem_sem_vegetacao_no_ndvi_pct"], 1)
    # ordem esperada: quanto maior o NDVI da classe, mais verde na imagem
    ordem = [p["verde_visivel_medio"] for p in sorted(por_classe, key=lambda p: p["codigo"]) if p["codigo"] >= 2]
    resumo["verde_acompanha_ndvi"] = all(a <= b + 0.02 for a, b in zip(ordem, ordem[1:])) if len(ordem) > 1 else None
    return divergencia, por_classe, resumo


# ---------- imagens de conferência ----------

def rampa_ndvi(ndvi, valido):
    """NDVI em cores: marrom (baixo) -> amarelo -> verde-escuro (alto)."""
    pontos = [(-0.2, (120, 120, 160)), (0.0, (166, 97, 26)), (0.25, (223, 194, 125)), (0.55, (217, 239, 139)),
              (0.75, (102, 189, 99)), (0.9, (26, 120, 60))]
    out = np.zeros((3,) + ndvi.shape, dtype="float64")
    v = np.clip(ndvi, pontos[0][0], pontos[-1][0])
    xs = [p[0] for p in pontos]
    for k in range(3):
        out[k] = np.interp(v, xs, [p[1][k] for p in pontos])
    out[:, ~valido] = 255
    return out.astype("uint8")


def pintar_classes(cls, classes):
    out = np.full((3,) + cls.shape, 255, dtype="uint8")
    for c in classes:
        rgb = hex_rgb(c["cor"])
        for k in range(3):
            out[k][cls == c["codigo"]] = rgb[k]
    return out


def pintar_divergencia(div, rgb):
    base = rgb.mean(axis=0) if rgb is not None else np.full(div.shape, 200.0)
    cinza = (200 + 0.2 * (base - 128)).clip(170, 235).astype("uint8")
    out = np.stack([cinza, cinza, cinza])
    for cod, cor in ((1, (200, 60, 160)), (2, (40, 120, 220))):
        for k in range(3):
            out[k][div == cod] = cor[k]
    return out


def com_contorno(img, contorno):
    out = img.copy()
    for k, v in enumerate((255, 230, 0)):
        out[k][contorno] = v
    return out


def salvar_painel(caminho, quadros, titulos, legenda_classes, rodape):
    """Painel lado a lado com títulos, usando o Qt do QGIS."""
    from qgis.PyQt.QtCore import Qt, QRectF
    from qgis.PyQt.QtGui import QColor, QFont, QImage, QPainter

    h, w = quadros[0].shape[1:]
    escala = max(1.0, 420 / max(h, w))
    qw, qh = int(w * escala), int(h * escala)
    margem, topo, base = 16, 34, 30 + 18 * ((len(legenda_classes) + 3) // 4)
    W = margem + len(quadros) * (qw + margem)
    H = topo + qh + base
    img = QImage(W, H, QImage.Format_RGB32)
    img.fill(QColor(255, 255, 255))
    p = QPainter(img)
    p.setRenderHint(QPainter.SmoothPixmapTransform, False)
    fonte = QFont("Arial", 11)
    fonte.setBold(True)
    for i, (q, t) in enumerate(zip(quadros, titulos)):
        rgba = np.dstack([q[0], q[1], q[2], np.full(q.shape[1:], 255, "uint8")]).copy()
        bgra = rgba[:, :, [2, 1, 0, 3]].copy()
        qi = QImage(bgra.data, w, h, 4 * w, QImage.Format_ARGB32).copy()
        x = margem + i * (qw + margem)
        p.drawImage(QRectF(x, topo, qw, qh), qi)
        p.setPen(QColor(150, 150, 150))
        p.drawRect(QRectF(x, topo, qw, qh))
        p.setPen(QColor(40, 40, 40))
        p.setFont(fonte)
        p.drawText(QRectF(x, 6, qw, topo - 8), Qt.AlignCenter, t)
    fonte2 = QFont("Arial", 9)
    p.setFont(fonte2)
    y = topo + qh + 10
    for j, (cor, nome) in enumerate(legenda_classes):
        col, lin = j % 4, j // 4
        x = margem + col * (W - 2 * margem) / 4
        p.fillRect(QRectF(x, y + lin * 18, 14, 12), QColor(*cor))
        p.setPen(QColor(120, 120, 120))
        p.drawRect(QRectF(x, y + lin * 18, 14, 12))
        p.setPen(QColor(40, 40, 40))
        p.drawText(QRectF(x + 20, y + lin * 18 - 2, 360, 16), Qt.AlignLeft | Qt.AlignVCenter, nome)
    p.setPen(QColor(90, 90, 90))
    p.drawText(QRectF(margem, H - 20, W - 2 * margem, 16), Qt.AlignLeft | Qt.AlignVCenter, rodape)
    p.end()
    img.save(str(caminho))


def salvar_amostras(caminho, rgb, cls, dentro, classes, lado=40, por_classe=3, semente=7):
    """Recortes da cor real no centro de manchas de cada classe, para comparar o aspecto visual."""
    from qgis.PyQt.QtCore import Qt, QRectF
    from qgis.PyQt.QtGui import QColor, QFont, QImage, QPainter

    rng = np.random.default_rng(semente)
    h, w = cls.shape
    linhas = []
    meio = lado // 2
    # pixel "de miolo": a classe ocupa a maior parte da janela em volta
    for c in classes:
        sel = (cls == c["codigo"]) & dentro
        ys, xs = np.nonzero(sel)
        if len(ys) == 0:
            continue
        candidatos = rng.permutation(len(ys))[:400]
        escolhidos = []
        for k in candidatos:
            y, x = ys[k], xs[k]
            y0, x0 = max(0, y - meio), max(0, x - meio)
            janela = cls[y0:y0 + lado, x0:x0 + lado]
            if janela.shape != (lado, lado):
                continue
            if (janela == c["codigo"]).mean() < 0.85:
                continue
            if any(abs(y - a) < lado and abs(x - b) < lado for a, b in escolhidos):
                continue
            escolhidos.append((y, x))
            if len(escolhidos) == por_classe:
                break
        if escolhidos:
            linhas.append((c, escolhidos))
    if not linhas:
        return False
    zoom = 3
    cel = lado * zoom
    rotulo = 230
    W = rotulo + por_classe * (cel + 10) + 10
    H = 10 + len(linhas) * (cel + 10)
    img = QImage(W, H, QImage.Format_RGB32)
    img.fill(QColor(255, 255, 255))
    p = QPainter(img)
    fonte = QFont("Arial", 9)
    fonte.setBold(True)
    for i, (c, pts) in enumerate(linhas):
        y = 10 + i * (cel + 10)
        p.fillRect(QRectF(10, y + 4, 14, 12), QColor(*hex_rgb(c["cor"])))
        p.setPen(QColor(40, 40, 40))
        p.setFont(fonte)
        p.drawText(QRectF(30, y, rotulo - 36, cel), Qt.AlignLeft | Qt.TextWordWrap, c["classe"])
        for j, (cy, cx) in enumerate(pts):
            y0, x0 = max(0, cy - meio), max(0, cx - meio)
            q = rgb[:, y0:y0 + lado, x0:x0 + lado].clip(0, 255).astype("uint8")
            rgba = np.dstack([q[0], q[1], q[2], np.full(q.shape[1:], 255, "uint8")])[:, :, [2, 1, 0, 3]].copy()
            qi = QImage(rgba.data, lado, lado, 4 * lado, QImage.Format_ARGB32).copy()
            x = rotulo + j * (cel + 10)
            p.drawImage(QRectF(x, y, cel, cel), qi)
            p.setPen(QColor(150, 150, 150))
            p.drawRect(QRectF(x, y, cel, cel))
    p.end()
    img.save(str(caminho))
    return True


# ---------- estilos e projeto QGIS ----------

def iniciar_qgis():
    """QGIS com suporte a texto e imagens (necessário para os painéis). None se este Python não tiver QGIS."""
    try:
        from qgis.core import QgsApplication
    except ImportError:
        return None, False
    if QgsApplication.instance() is not None:
        return None, True
    app = QgsApplication([], True)
    app.initQgis()
    return app, True


def estilos_e_projeto(pasta, nome, tif_ndvi, tif_cls, gpkg_caso, camadas_caso, vetores_soltos, classes,
                      registrar_projeto=True):
    """Grava os estilos (rampa do NDVI e classes, .qml ao lado de cada arquivo) e põe as camadas no projeto do caso."""
    from qgis.core import (QgsCategorizedSymbolRenderer, QgsColorRampShader, QgsFillSymbol,
                           QgsPalettedRasterRenderer, QgsProject, QgsRasterLayer, QgsRasterShader,
                           QgsRendererCategory, QgsSingleBandPseudoColorRenderer, QgsVectorLayer)
    from qgis.PyQt.QtGui import QColor

    try:
        r = QgsRasterLayer(str(tif_ndvi), f"NDVI {nome}")
        itens = [QgsColorRampShader.ColorRampItem(v, QColor(*cor), txt) for v, cor, txt in [
            (-0.2, (120, 120, 160), "-0,20 (água ou sombra)"), (0.0, (166, 97, 26), "0,00"),
            (0.25, (223, 194, 125), "0,25"), (0.55, (217, 239, 139), "0,55"),
            (0.75, (102, 189, 99), "0,75"), (0.9, (26, 120, 60), "0,90 (vegetação densa)")]]
        rampa = QgsColorRampShader(-0.2, 0.9)
        rampa.setColorRampType(QgsColorRampShader.Interpolated)
        rampa.setColorRampItemList(itens)
        try:  # legenda em degraus com rótulos, mais legível que a barra contínua (QGIS 3.18+)
            from qgis.core import QgsColorRampLegendNodeSettings
            ajuste = QgsColorRampLegendNodeSettings()
            ajuste.setUseContinuousLegend(False)
            rampa.setLegendSettings(ajuste)
        except ImportError:
            pass
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(rampa)
        rend = QgsSingleBandPseudoColorRenderer(r.dataProvider(), 1, shader)
        rend.setClassificationMin(-0.2)
        rend.setClassificationMax(0.9)
        r.setRenderer(rend)
        r.saveNamedStyle(str(Path(tif_ndvi).with_suffix(".qml")))
        rc = QgsRasterLayer(str(tif_cls), f"Classes de NDVI {nome}")
        rc.setRenderer(QgsPalettedRasterRenderer(rc.dataProvider(), 1, [
            QgsPalettedRasterRenderer.Class(c["codigo"], QColor(c["cor"]), c["classe"]) for c in classes]))
        rc.saveNamedStyle(str(Path(tif_cls).with_suffix(".qml")))

        def categorias(presentes=None):
            """Só as classes que existem na camada entram na legenda."""
            cats = []
            for c in classes:
                if presentes is not None and c["codigo"] not in presentes:
                    continue
                s = QgsFillSymbol.createSimple({"color": c["cor"], "outline_color": "#8a8a8a", "outline_width": "0.1",
                                                "outline_width_unit": "MM"})
                cats.append(QgsRendererCategory(c["codigo"], s, c["classe"]))
            return QgsCategorizedSymbolRenderer("codigo", cats)

        # .qml ao lado dos SHP e do GPKG avulso: o QGIS aplica o estilo sozinho ao abrir
        for arq in vetores_soltos:
            v = QgsVectorLayer(str(arq), Path(arq).stem, "ogr")
            if v.isValid():
                v.setRenderer(categorias(set(v.uniqueValues(v.fields().indexOf("codigo")))))
                v.saveNamedStyle(str(Path(arq).with_suffix(".qml")))
        camadas_vetor = []
        for camada in camadas_caso:
            v = QgsVectorLayer(f"{gpkg_caso}|layername={camada}", camada, "ogr")
            v.setRenderer(categorias(set(v.uniqueValues(v.fields().indexOf("codigo")))))
            v.saveStyleToDatabase("classes_ndvi", "Classes de NDVI", True, "")
            camadas_vetor.append(v)

        if registrar_projeto:
            qgz = pasta / "03_Geo" / "caso.qgz"
            projeto = QgsProject.instance()
            if qgz.exists() and projeto.read(str(qgz)):
                raiz = projeto.layerTreeRoot()
                grupo = raiz.findGroup("Produzidos") or raiz.insertGroup(0, "Produzidos")
                for lyr in [*camadas_vetor, r]:
                    for velha in projeto.mapLayersByName(lyr.name()):
                        projeto.removeMapLayer(velha.id())
                    projeto.addMapLayer(lyr, False)
                    grupo.addLayer(lyr)
                projeto.write()
                projeto.clear()
            else:
                print("Aviso: caso.qgz não encontrado; as camadas ficaram só nos arquivos.")
    finally:
        gc.collect()


# ---------- textos ----------

def texto_interpretacao(info, tabela, comp):
    area_total = info["area_interesse_ha"]
    linhas = [
        f"# Interpretação do NDVI – {info['nome']} (rascunho)",
        "",
        "> Rascunho gerado pelo script. O agente-ndvi revisa depois da conferência visual e o redator adapta ao documento.",
        "",
        "## O que é o NDVI",
        "",
        "O NDVI (Índice de Vegetação por Diferença Normalizada) mede o vigor da vegetação a partir da luz que ela "
        "reflete. Folhas verdes refletem muito o infravermelho próximo e absorvem o vermelho; solo, água e áreas "
        "queimadas não. O índice vai de -1 a 1: quanto mais perto de 1, mais densa e vigorosa a vegetação.",
        "",
        "## Resultado na área de interesse",
        "",
        f"Imagem {info['sensor']} de {info['data_br']}, resolução de {fmt(info['resolucao'], 0)} m. "
        f"A área de interesse tem {fmt(area_total)} ha; o NDVI médio dentro dela foi de {fmt(info['ndvi_medio_area'], 2)}.",
        "",
    ]
    ordenadas = sorted([t for t in tabela if t["area_ha"] > 0], key=lambda t: -t["area_ha"])
    if ordenadas:
        partes = [f"{t['classe'].lower()} em {fmt(t['area_ha'])} ha ({fmt(t['pct'], 1)}%)" for t in ordenadas]
        linhas.append("Pelas faixas de NDVI, a área se divide em: " + "; ".join(partes) + ".")
        linhas.append("")
        dom = ordenadas[0]
        linhas.append(f"A classe predominante é {dom['classe'].lower()}, com {fmt(dom['pct'], 1)}% da área.")
        sem_veg = sum(t["area_ha"] for t in tabela if t["codigo"] in (2,))
        if sem_veg > 0:
            linhas.append(f"Há {fmt(sem_veg)} ha com NDVI típico de solo exposto ou área queimada, isto é, sem cobertura "
                          "vegetal na data da imagem.")
        linhas.append("")
    if info.get("sem_dado_ha", 0) > 0.005:
        linhas += [f"Ficaram sem classificação {fmt(info['sem_dado_ha'])} ha (nuvem, sombra mascarada ou falta de dado).", ""]
    linhas += ["## Comparação com a imagem em cor real", ""]
    if comp:
        linhas.append(
            f"O NDVI concorda com o aspecto visual da imagem em cor real em {fmt(comp['concordancia_pct'], 1)}% da área "
            f"comparada. Em {fmt(comp['vegetacao_no_ndvi_sem_verde_na_imagem_pct'], 1)}% o NDVI indica vegetação, mas a "
            f"imagem não parece verde; em {fmt(comp['verde_na_imagem_sem_vegetacao_no_ndvi_pct'], 1)}% a imagem parece "
            "verde, mas o NDVI não indica vegetação.")
        if comp.get("verde_acompanha_ndvi") is False:
            linhas.append("O verde visível não cresce junto com o NDVI das classes: conferir data, névoa e alinhamento "
                          "entre as imagens antes de usar as classes.")
        linhas += ["", "[COMPARAÇÃO VISUAL: descrever, classe por classe, se o aspecto na cor real confirma a classe do "
                   "NDVI, e explicar as divergências (névoa, sombra, data diferente, queimada recente, pasto seco).]", ""]
    else:
        linhas += ["Sem imagem em cor real informada (--rgb); a comparação visual não foi feita.", ""]
    linhas += [
        "## Limitações",
        "",
        "- As classes são indicativas, definidas por faixas de NDVI; não substituem classificação supervisionada nem vistoria.",
        "- O NDVI muda com a estação: pasto seco pode cair na faixa de solo exposto e vegetação em regeneração densa "
        "pode alcançar a faixa de floresta.",
        "- Névoa, fumaça e sombra de nuvem baixam o NDVI.",
        f"- Manchas menores que {fmt(info['area_minima_ha'], 2)} ha foram incorporadas à classe vizinha (área mínima mapeada).",
    ]
    return "\n".join(linhas) + "\n"


# ---------- principal ----------

def executar(a):
    pasta = Path(a.pasta)
    dir_r = pasta / "03_Geo" / "raster" / "ndvi"
    dir_conf = dir_r / "conferencia"
    dir_v = pasta / "03_Geo" / "vetores_produzidos" / "ndvi"
    for d in (dir_r, dir_conf, dir_v / "shp", dir_v / "kml"):
        d.mkdir(parents=True, exist_ok=True)
    classes = json.loads(Path(a.classes).read_text(encoding="utf-8")) if a.classes else CLASSES_PADRAO

    arq_r, banda_r = separar(a.vermelho)
    arq_n, banda_n = separar(a.nir)
    ref = gdal.Open(arq_r)
    grade = (ref.GetGeoTransform(), ref.RasterXSize, ref.RasterYSize, ref.GetProjection())
    ref = None
    red, nd_r = alinhar(arq_r, banda_r, grade, "near")
    nir, nd_n = alinhar(arq_n, banda_n, grade, "bilinear" if arq_n != arq_r else "near")

    valido = np.isfinite(red) & np.isfinite(nir) & (red != 0) & (nir != 0)
    for arr, nd in ((red, nd_r), (nir, nd_n)):
        if nd is not None:
            valido &= arr != nd
    if a.mascara:
        arq_m, banda_m = separar(a.mascara)
        m, _ = alinhar(arq_m, banda_m, grade, "near")
        valido &= np.isin(m, a.mascara_validos) if a.mascara_validos else (m != 0)
    red = red * a.escala + a.deslocamento
    nir = nir * a.escala + a.deslocamento
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red)
    valido &= np.isfinite(ndvi) & ((nir + red) > 0)
    ndvi = np.clip(np.where(valido, ndvi, NODATA), -1, 1)
    ndvi[~valido] = NODATA

    area_geo = ler_area(a.area)
    dentro, contorno, _ = area_para_mascara(area_geo, grade)
    if not dentro.any():
        raise RuntimeError("A área de interesse não cai dentro da imagem. Confira o SRC e o recorte.")

    gt = grade[0]
    pixel_m2 = abs(gt[1] * gt[5])
    srs_img = osr.SpatialReference()
    srs_img.ImportFromWkt(grade[3])
    if srs_img.IsGeographic():
        raise RuntimeError("A imagem está em coordenadas geográficas; use o recorte em UTM (o original da cena).")
    minimo_px = a.area_minima_ha * 10000 / pixel_m2
    cls = classificar(ndvi, valido, classes)
    cls = peneirar(cls, valido, grade, minimo_px)

    nome = a.nome
    tif_ndvi = dir_r / f"{nome}_ndvi.tif"
    tif_cls = dir_r / f"{nome}_ndvi_classes.tif"
    gravar_tif(tif_ndvi, ndvi.astype("float32"), grade, gdal.GDT_Float32, NODATA, "NDVI")
    gravar_tif(tif_cls, cls, grade, gdal.GDT_Byte, 0, "Classe de NDVI")

    feats, srs = poligonizar(cls, np.where(valido, ndvi, 0), valido, grade, classes)
    feats, srs_geo = para_sirgas(feats, srs)
    for g, attrs in feats:
        attrs["area_ha"] = round(area_ha(g), 4)
    feats_area = recortar(feats, area_geo)
    for g, attrs in feats_area:
        attrs["area_ha"] = round(area_ha(g), 4)

    base = f"{nome}_classes_ndvi"
    camada_recorte = f"ndvi_{nome}_classes".lower().replace("-", "_")
    camada_area = f"{camada_recorte}_area"
    gpkg = dir_v / f"{base}.gpkg"
    if gpkg.exists():
        gpkg.unlink()
    gravar_vetor(gpkg, "GPKG", camada_recorte, feats, srs_geo)
    gravar_vetor(gpkg, "GPKG", camada_area, feats_area, srs_geo)
    gravar_vetor(dir_v / "shp" / f"{base}.shp", "ESRI Shapefile", base, feats, srs_geo, ["ENCODING=UTF-8"])
    gravar_vetor(dir_v / "shp" / f"{base}_area.shp", "ESRI Shapefile", f"{base}_area", feats_area, srs_geo,
                 ["ENCODING=UTF-8"])
    gravar_vetor(dir_v / "kml" / f"{base}.kml", "KML", camada_recorte, feats, srs_geo, transformar_para=4326)
    gravar_vetor(dir_v / "kml" / f"{base}_area.kml", "KML", camada_area, feats_area, srs_geo, transformar_para=4326)
    # as mesmas camadas no caso.gpkg, para o projeto do caso e o zip de Geoinformação
    gpkg_caso = pasta / "03_Geo" / "vetores_produzidos" / "caso.gpkg"
    if gpkg_caso.exists():
        gravar_vetor(gpkg_caso, "GPKG", camada_recorte, feats, srs_geo)
        gravar_vetor(gpkg_caso, "GPKG", camada_area, feats_area, srs_geo)

    # tabela por classe, dentro da área de interesse
    area_total = round(area_ha(area_geo), 4)
    tabela = []
    for c in classes:
        sel = (cls == c["codigo"]) & dentro & valido
        ha = sum(at["area_ha"] for _, at in feats_area if at["codigo"] == c["codigo"])
        tabela.append({"codigo": c["codigo"], "classe": c["classe"], "faixa": f"{fmt(c['min'], 2)} a {fmt(c['max'], 2)}",
                       "area_ha": round(ha, 2), "pct": round(100 * ha / area_total, 1) if area_total else 0,
                       "ndvi_medio": round(float(ndvi[sel].mean()), 3) if sel.any() else None})
    classificada = sum(t["area_ha"] for t in tabela)
    sem_dado = max(0.0, area_total - classificada)
    # conferência independente: área pela contagem de pixels (plana, no SRC da imagem) contra a soma dos polígonos
    pixels_ha = float(((cls > 0) & dentro).sum()) * pixel_m2 / 10000
    dif_pct = 100 * (classificada - pixels_ha) / pixels_ha if pixels_ha else 0.0
    if abs(dif_pct) > 2:
        print(f"ATENÇÃO: soma dos polígonos ({fmt(classificada)} ha) difere {fmt(dif_pct, 1)}% da contagem de pixels "
              f"({fmt(pixels_ha)} ha). Confira o recorte e o SRC antes de usar.")
    ndvi_area = ndvi[dentro & valido]

    with open(dir_r / f"{nome}_ndvi_tabela.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["Classe", "Faixa de NDVI", "Área (ha)", "Área (%)", "NDVI médio"])
        for t in [t for t in tabela if t["area_ha"] > 0]:  # classe ausente fica só no JSON
            w.writerow([t["classe"], t["faixa"], fmt(t["area_ha"]), fmt(t["pct"], 1),
                        fmt(t["ndvi_medio"], 2) if t["ndvi_medio"] is not None else "–"])
        if sem_dado > 0.005:
            w.writerow(["Sem dado (nuvem ou máscara)", "–", fmt(sem_dado), fmt(100 * sem_dado / area_total, 1), "–"])
        w.writerow(["Total", "", fmt(area_total), "100,0", fmt(float(ndvi_area.mean()), 2) if ndvi_area.size else "–"])

    data_br = datetime.strptime(a.data, "%Y-%m-%d").strftime("%d/%m/%Y") if a.data else "[DATA NÃO INFORMADA]"
    resol = a.resolucao or round(math.sqrt(pixel_m2), 1)
    md = [f"Tabela: Classes de NDVI na área de interesse – imagem {a.sensor} de {data_br}",
          "| Classe | Faixa de NDVI | Área (ha) | Área (%) | NDVI médio |",
          "| --- | --- | --- | --- | --- |"]
    for t in [t for t in tabela if t["area_ha"] > 0]:
        md.append(f"| {t['classe']} | {t['faixa']} | {fmt(t['area_ha'])} | {fmt(t['pct'], 1)} | "
                  f"{fmt(t['ndvi_medio'], 2) if t['ndvi_medio'] is not None else '–'} |")
    if sem_dado > 0.005:
        md.append(f"| Sem dado (nuvem ou máscara) | – | {fmt(sem_dado)} | {fmt(100 * sem_dado / area_total, 1)} | – |")
    md.append(f"| **Total** | | **{fmt(area_total)}** | **100,0** | "
              f"**{fmt(float(ndvi_area.mean()), 2) if ndvi_area.size else '–'}** |")
    md.append(f"Fonte: elaborado pelo autor a partir de imagem {a.sensor} de {data_br} ({fmt(resol, 0)} m). "
              "Áreas elipsoidais, SIRGAS 2000.")
    (dir_r / f"{nome}_ndvi_tabela.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # comparação com a cor real e imagens de conferência
    comp, por_classe, rgb = None, [], None
    if a.rgb:
        rgb = ler_rgb(a.rgb, grade)
        div, por_classe, comp = comparar_visual(rgb, np.where(valido, ndvi, -1), cls, valido, dentro, classes, grade)
        gravar_tif(dir_r / f"{nome}_ndvi_divergencias.tif", div, grade, gdal.GDT_Byte, 0,
                   "1 = vegetação no NDVI sem verde visível; 2 = verde visível sem vegetação no NDVI")

    info = {"nome": nome, "sensor": a.sensor, "data": a.data, "data_br": data_br, "resolucao": resol,
            "area_interesse_ha": area_total, "classificada_ha": round(classificada, 2), "sem_dado_ha": round(sem_dado, 2),
            "ndvi_medio_area": float(ndvi_area.mean()) if ndvi_area.size else float("nan"),
            "area_minima_ha": a.area_minima_ha}
    (dir_r / f"{nome}_ndvi_interpretacao.md").write_text(texto_interpretacao(info, tabela, comp), encoding="utf-8")

    painel = dir_conf / f"{nome}_painel_ndvi.png"
    amostras = dir_conf / f"{nome}_amostras_classes.png"
    app, tem_qgis = iniciar_qgis()
    imagens_ok = tem_qgis
    if tem_qgis:
        # painel enquadrado na área de interesse com folga, para a comparação ficar legível
        ys, xs = np.nonzero(dentro)
        folga = int(0.35 * max(ys.max() - ys.min(), xs.max() - xs.min())) + 5
        y0, y1 = max(0, ys.min() - folga), min(cls.shape[0], ys.max() + folga + 1)
        x0, x1 = max(0, xs.min() - folga), min(cls.shape[1], xs.max() + folga + 1)
        janela = (slice(y0, y1), slice(x0, x1))
        quadros = [com_contorno(rampa_ndvi(ndvi, valido), contorno),
                   com_contorno(pintar_classes(cls, classes), contorno)]
        if rgb is not None:
            quadros.insert(0, com_contorno(rgb.clip(0, 255).astype("uint8"), contorno))
            quadros.append(com_contorno(pintar_divergencia(div, rgb), contorno))
        quadros = [q[(slice(None),) + janela] for q in quadros]
        titulos = ["NDVI", "Classes de NDVI"]
        if rgb is not None:
            titulos.insert(0, "Cor real")
            titulos.append("Divergências NDVI × cor real")
        legenda = [(hex_rgb(c["cor"]), c["classe"]) for c in classes]
        if rgb is not None:
            legenda += [((200, 60, 160), "NDVI vegetação, sem verde na imagem"),
                        ((40, 120, 220), "Verde na imagem, NDVI sem vegetação")]
        salvar_painel(painel, quadros, titulos, legenda,
                      f"{a.sensor}, {data_br}, {fmt(resol, 0)} m. Contorno amarelo: área de interesse ({fmt(area_total)} ha).")
        if rgb is not None:
            salvar_amostras(amostras, rgb, cls, dentro, classes)
    else:
        print("Aviso: sem QGIS neste Python; painel e amostras não foram gerados.")

    resumo = {
        "gerado_em": agora(), **info,
        "classes_usadas": classes, "limites_padrao": a.classes is None,
        "tabela": tabela,
        "conferencia_area": {"poligonos_ha": round(classificada, 2), "pixels_ha": round(pixels_ha, 2),
                             "diferenca_pct": round(dif_pct, 2)},
        "comparacao_visual": {"resumo": comp, "por_classe": por_classe} if comp else None,
        "arquivos": {
            "ndvi": str(tif_ndvi), "classes": str(tif_cls), "vetores_gpkg": str(gpkg),
            "vetores_shp": str(dir_v / "shp"), "vetores_kml": str(dir_v / "kml"),
            "camadas_caso_gpkg": [camada_recorte, camada_area] if gpkg_caso.exists() else [],
            "tabela_md": str(dir_r / f"{nome}_ndvi_tabela.md"),
            "interpretacao": str(dir_r / f"{nome}_ndvi_interpretacao.md"),
            "painel": str(painel) if imagens_ok else None,
            "amostras": str(amostras) if imagens_ok and rgb is not None else None,
        },
        "conferencia": {
            "perguntas": [
                "As áreas das classes somam a área de interesse da ficha (diferença só de sem dado)?",
                "No painel, cada classe corresponde ao que se vê na cor real (floresta escura e rugosa, pasto liso e claro, solo bege)?",
                "As divergências (magenta e azul) têm explicação: névoa, sombra, queimada recente, pasto seco, borda de classe?",
                "Os limites das classes servem para esta região e estação, ou precisam de ajuste (com aprovação do usuário)?",
                "A imagem do NDVI é a mesma cena da cor real (mesma data)?",
            ],
            "conferido": False,
        },
    }
    (dir_r / f"{nome}_ndvi.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")

    if not a.sem_projeto and tem_qgis:
        estilos_e_projeto(pasta, nome, tif_ndvi, tif_cls, gpkg_caso,
                          [camada_recorte, camada_area] if gpkg_caso.exists() else [],
                          [dir_v / "shp" / f"{base}.shp", dir_v / "shp" / f"{base}_area.shp"], classes)

    print(f"NDVI {nome}: área de interesse {fmt(area_total)} ha, NDVI médio {fmt(info['ndvi_medio_area'], 2)}")
    for t in tabela:
        print(f"  {t['classe']:<34} {fmt(t['area_ha']):>10} ha  {fmt(t['pct'], 1):>5}%")
    if sem_dado > 0.005:
        print(f"  {'Sem dado':<34} {fmt(sem_dado):>10} ha")
    if comp:
        print(f"Concordância NDVI × cor real: {fmt(comp['concordancia_pct'], 1)}%")
    print(f"Resumo: {dir_r / f'{nome}_ndvi.json'}")
    return resumo


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pasta", required=True, help="Pasta do caso")
    ap.add_argument("--nome", required=True, help="Prefixo dos arquivos, com sensor e data (ex.: S2_2025-07-19)")
    ap.add_argument("--vermelho", required=True, help="Banda do vermelho: arquivo[:banda]")
    ap.add_argument("--nir", required=True, help="Banda do infravermelho próximo: arquivo[:banda]")
    ap.add_argument("--escala", type=float, default=1.0, help="Multiplicador para reflectância")
    ap.add_argument("--deslocamento", type=float, default=0.0, help="Soma depois da escala")
    ap.add_argument("--mascara", help="Máscara de nuvem: arquivo[:banda] (SCL do Sentinel-2 ou 0/1)")
    ap.add_argument("--mascara-validos", type=int, nargs="*", help="Valores válidos da máscara (SCL: 4 5 6 7)")
    ap.add_argument("--area", required=True, help="Polígono da área de interesse: arquivo[:camada]")
    ap.add_argument("--rgb", help="Recorte em cor real da mesma cena, para a comparação visual")
    ap.add_argument("--sensor", required=True)
    ap.add_argument("--data", help="Data da cena, AAAA-MM-DD")
    ap.add_argument("--resolucao", type=float, help="Resolução em metros (padrão: a do pixel)")
    ap.add_argument("--classes", help="JSON com as classes, se os limites padrão forem trocados")
    ap.add_argument("--area-minima-ha", type=float, default=0.5, help="Área mínima mapeada (ha)")
    ap.add_argument("--sem-projeto", action="store_true", help="Não mexe no caso.qgz")
    a = ap.parse_args(argv)
    executar(a)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    os._exit(0)  # evita a queda do QGIS ao encerrar o processo
