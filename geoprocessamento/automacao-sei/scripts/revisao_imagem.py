"""Revisão de brilho e contraste de imagens de satélite (uso nos mapas e figuras dos casos).

Mede a imagem como ela aparece no mapa (na extensão e no sistema do mapa) e, se estiver escura,
apagada ou estourada, ajusta brilho, gama e contraste no próprio estilo da camada (sem alterar o
arquivo e sem mudar o equilíbrio de cores do estilo natural).

Uso em script (QGIS já iniciado):
    from revisao_imagem import revisar
    relatorio = revisar(camada_raster, extensao, crs, ajustar=True)

Uso no terminal, para conferir um recorte (GeoTIFF):
    python-qgis.bat revisao_imagem.py <imagem.tif> [--ajustar] [--qml]
    --qml grava <imagem>.qml com o ajuste: o QGIS abre a imagem já ajustada.
"""

import argparse
import json
import sys

import numpy as np
from qgis.core import (
    QgsApplication,
    QgsContrastEnhancement,
    QgsCoordinateTransform,
    QgsCoordinateTransformContext,
    QgsMapRendererSequentialJob,
    QgsMapSettings,
    QgsMultiBandColorRenderer,
    QgsRasterLayer,
    QgsSingleBandGrayRenderer,
)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor, QImage

# faixas de referência (luminância 0 a 255, medida como a imagem aparece no mapa)
BRILHO_MIN, BRILHO_MAX, BRILHO_ALVO = 105, 150, 125
CONTRASTE_MIN = 18          # desvio-padrão da luminância
ESCUROS_MAX = 0.10          # fração de pixels quase pretos (< 25)
ESTOURADOS_MAX = 0.03       # fração de pixels quase brancos (> 250)
SATURACAO_MAX = 0.40        # saturação média (0 a 1): acima disso a imagem perde o aspecto natural e suave


def medir(camada, extensao, crs, lado=500):
    ms = QgsMapSettings()
    ms.setLayers([camada])
    ms.setDestinationCrs(crs)
    ms.setExtent(extensao)
    ms.setBackgroundColor(QColor(0, 0, 0, 0))  # fora da imagem fica transparente e não entra na medida
    prop = extensao.width() / extensao.height() if extensao.height() else 1
    ms.setOutputSize(QSize(lado, max(1, int(lado / prop))) if prop >= 1 else QSize(max(1, int(lado * prop)), lado))
    job = QgsMapRendererSequentialJob(ms)
    job.start()
    job.waitForFinished()
    img = job.renderedImage().convertToFormat(QImage.Format_ARGB32)
    ptr = img.constBits()
    ptr.setsize(img.sizeInBytes())
    a = np.frombuffer(ptr, np.uint8).reshape(img.height(), img.bytesPerLine())[:, : img.width() * 4]
    a = a.reshape(img.height(), img.width(), 4).astype(float)
    b, g, r, alfa = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    validos = alfa > 0
    if not validos.any():
        return {"pixels_validos": 0}
    lum = (0.299 * r + 0.587 * g + 0.114 * b)[validos]
    mx = np.maximum(np.maximum(r, g), b)[validos]
    mn = np.minimum(np.minimum(r, g), b)[validos]
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    return {
        "saturacao": round(float(sat.mean()), 3),
        "brilho": round(float(lum.mean()), 1),
        "contraste": round(float(lum.std()), 1),
        "escuros_pct": round(100 * float((lum < 25).mean()), 1),
        "estourados_pct": round(100 * float((lum > 250).mean()), 1),
        "pixels_validos": int(validos.sum()),
    }


def diagnostico(m):
    problemas = []
    if not m.get("pixels_validos"):
        return ["a imagem não cobre a área do mapa"]
    if m["brilho"] < BRILHO_MIN:
        problemas.append(f"escura (brilho {m['brilho']}, mínimo {BRILHO_MIN})")
    if m["brilho"] > BRILHO_MAX:
        problemas.append(f"clara demais (brilho {m['brilho']}, máximo {BRILHO_MAX})")
    if m["contraste"] < CONTRASTE_MIN:
        problemas.append(f"pouco contraste (desvio {m['contraste']}, mínimo {CONTRASTE_MIN})")
    if m["escuros_pct"] / 100 > ESCUROS_MAX:
        problemas.append(f"{m['escuros_pct']}% de pixels quase pretos")
    if m["estourados_pct"] / 100 > ESTOURADOS_MAX:
        problemas.append(f"{m['estourados_pct']}% de pixels estourados")
    if m.get("saturacao", 0) > SATURACAO_MAX + 0.02:
        problemas.append(f"cores saturadas demais (saturação {m['saturacao']}, máximo {SATURACAO_MAX})")
    return problemas


def _realce_linear(camada, extensao, crs, corte=(0.02, 0.98)):
    """Realce linear pelos percentis 2%-98% da área do mapa, com os MESMOS limites em todas as bandas
    (preserva o equilíbrio de cores do estilo natural). Devolve (mínimo, máximo) aplicados ou None."""
    renderizador = camada.renderer()
    prov = camada.dataProvider()
    ext = extensao
    if crs != camada.crs():
        ext = QgsCoordinateTransform(crs, camada.crs(), QgsCoordinateTransformContext()).transformBoundingBox(extensao)
    if isinstance(renderizador, QgsMultiBandColorRenderer):
        bandas = [renderizador.redBand(), renderizador.greenBand(), renderizador.blueBand()]
    elif isinstance(renderizador, QgsSingleBandGrayRenderer):
        bandas = [renderizador.grayBand()]
    else:
        return None
    # percentis lidos dos próprios pixels da área (estatísticas gravadas no arquivo podem estar desatualizadas)
    largura = max(1, min(800, int(ext.width() / camada.rasterUnitsPerPixelX())))
    altura = max(1, min(800, int(ext.height() / camada.rasterUnitsPerPixelY())))
    mins, maxs = [], []
    for b in bandas:
        bloco = prov.block(b, ext, largura, altura)
        valores = np.array([bloco.value(i, j) for i in range(0, altura, max(1, altura // 300))
                            for j in range(0, largura, max(1, largura // 300)) if not bloco.isNoData(i, j)], dtype=float)
        if valores.size == 0:
            return None
        mins.append(np.percentile(valores, corte[0] * 100))
        maxs.append(np.percentile(valores, corte[1] * 100))
    vmin, vmax = min(mins), max(maxs)
    if vmax <= vmin:
        return None
    tipo = prov.dataType(bandas[0])

    def realce():
        ce = QgsContrastEnhancement(tipo)
        ce.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum, True)
        ce.setMinimumValue(vmin)
        ce.setMaximumValue(vmax)
        return ce

    if isinstance(renderizador, QgsMultiBandColorRenderer):
        renderizador.setRedContrastEnhancement(realce())
        renderizador.setGreenContrastEnhancement(realce())
        renderizador.setBlueContrastEnhancement(realce())
    else:
        renderizador.setContrastEnhancement(realce())
    return float(vmin), float(vmax)


def _ajustar_gama(camada, filtro, extensao, crs):
    """Busca a gama que leva o brilho médio para perto do alvo (gama > 1 clareia)."""
    baixo, alto = 0.3, 4.0
    m = medir(camada, extensao, crs)
    for _ in range(14):
        meio = (baixo + alto) / 2
        filtro.setGamma(meio)
        m = medir(camada, extensao, crs)
        if abs(m["brilho"] - BRILHO_ALVO) < 3:
            break
        if m["brilho"] < BRILHO_ALVO:
            baixo = meio
        else:
            alto = meio
    return m


def revisar(camada, extensao, crs, ajustar=True):
    """Mede, ajusta se preciso e devolve o relatório com antes e depois."""
    antes = medir(camada, extensao, crs)
    problemas = diagnostico(antes)
    rel = {"camada": camada.name(), "antes": antes, "problemas_antes": problemas, "ajuste": None,
           "depois": antes, "problemas_depois": problemas}
    if not ajustar or not problemas or not antes.get("pixels_validos"):
        return rel

    filtro = camada.pipe().brightnessFilter()
    if filtro is None:
        rel["problemas_depois"] = problemas + ["camada sem filtro de brilho: ajuste manual no QGIS"]
        return rel
    filtro.setBrightness(0)
    filtro.setGamma(1.0)
    filtro.setContrast(0)
    if camada.hueSaturationFilter() is not None:
        camada.hueSaturationFilter().setSaturation(0)

    realce = _realce_linear(camada, extensao, crs)
    depois = _ajustar_gama(camada, filtro, extensao, crs)
    contraste = 0
    while depois["contraste"] < CONTRASTE_MIN and contraste < 45:
        contraste += 15
        filtro.setContrast(contraste)
        depois = _ajustar_gama(camada, filtro, extensao, crs)
    if depois["estourados_pct"] / 100 > ESTOURADOS_MAX and contraste > 0:
        contraste = max(0, contraste - 15)
        filtro.setContrast(contraste)
        depois = _ajustar_gama(camada, filtro, extensao, crs)

    # cores suaves: se o realce saturou demais, reduz a saturação até o limite
    saturacao = 0
    hs = camada.hueSaturationFilter()
    if hs is not None and depois.get("saturacao", 0) > SATURACAO_MAX:
        baixo, alto = -100, 0
        for _ in range(8):
            meio = (baixo + alto) // 2
            hs.setSaturation(meio)
            m = medir(camada, extensao, crs)
            if m["saturacao"] > SATURACAO_MAX:
                alto = meio
            else:
                baixo = meio
        saturacao = baixo
        hs.setSaturation(saturacao)
        depois = _ajustar_gama(camada, filtro, extensao, crs)

    camada.triggerRepaint()
    rel["ajuste"] = {"saturacao": saturacao,"realce_linear_2_98": [round(v, 2) for v in realce] if realce else None,
                     "gama": round(filtro.gamma(), 2), "contraste": contraste, "brilho": 0}
    rel["depois"] = depois
    rel["problemas_depois"] = diagnostico(depois)
    return rel


def main(argv=None):
    ap = argparse.ArgumentParser(description="Revisão de brilho e contraste de uma imagem.")
    ap.add_argument("imagem")
    ap.add_argument("--ajustar", action="store_true")
    ap.add_argument("--qml", action="store_true", help="Grava o estilo ajustado ao lado da imagem")
    a = ap.parse_args(argv)
    app = QgsApplication([], False) if QgsApplication.instance() is None else None
    if app:
        app.initQgis()
    camada = QgsRasterLayer(a.imagem, "imagem")
    if not camada.isValid():
        sys.exit(f"Não abri {a.imagem}")
    rel = revisar(camada, camada.extent(), camada.crs(), ajustar=a.ajustar)
    if a.qml and rel["ajuste"]:
        camada.saveNamedStyle(a.imagem.rsplit(".", 1)[0] + ".qml")
        rel["qml"] = a.imagem.rsplit(".", 1)[0] + ".qml"
    print(json.dumps(rel, ensure_ascii=False, indent=2))
    if app:
        sys.stdout.flush()
        import os
        os._exit(0)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
