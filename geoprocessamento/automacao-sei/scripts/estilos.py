"""Paleta padrão de cores suaves para os mapas dos casos, por papel da camada.

Uso nos scripts: aplicar_estilo(camada, "foco"). Papéis: foco, imovel, hidrografia, uc, ti, app,
desmatamento, referencia, vertices. Ajuste as cores aqui para mudar o padrão de todos os mapas.
"""

from qgis.core import (
    QgsFillSymbol,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes,
)
from qgis.PyQt.QtGui import QColor, QFont

PALETA = {
    # papel: (polígono, linha, ponto)
    "foco": ({"color": "214,96,77,70", "outline_color": "192,57,43", "outline_width": "0.6"},
             {"line_color": "192,57,43", "line_width": "0.7"},
             {"name": "circle", "color": "192,57,43", "size": "2.2", "outline_color": "255,255,255"}),
    "imovel": ({"color": "0,0,0,0", "outline_color": "230,145,56", "outline_width": "0.55", "outline_style": "dash"},
               {"line_color": "230,145,56", "line_width": "0.55"},
               {"name": "square", "color": "230,145,56", "size": "2"}),
    "hidrografia": ({"color": "174,214,241,180", "outline_color": "93,173,226", "outline_width": "0.3"},
                    {"line_color": "93,173,226", "line_width": "0.6"},
                    {"name": "circle", "color": "93,173,226", "size": "1.6"}),
    "uc": ({"color": "130,190,130,60", "outline_color": "76,140,76", "outline_width": "0.45"},
           {"line_color": "76,140,76", "line_width": "0.5"},
           {"name": "circle", "color": "76,140,76", "size": "1.8"}),
    "ti": ({"color": "214,180,130,60", "outline_color": "160,115,60", "outline_width": "0.45"},
           {"line_color": "160,115,60", "line_width": "0.5"},
           {"name": "circle", "color": "160,115,60", "size": "1.8"}),
    "app": ({"color": "120,190,205,60", "outline_color": "60,140,170", "outline_width": "0.4", "outline_style": "dash"},
            {"line_color": "60,140,170", "line_width": "0.4"},
            {"name": "circle", "color": "60,140,170", "size": "1.6"}),
    "desmatamento": ({"color": "240,180,90,110", "outline_color": "210,130,40", "outline_width": "0.35"},
                     {"line_color": "210,130,40", "line_width": "0.5"},
                     {"name": "circle", "color": "210,130,40", "size": "1.8"}),
    "referencia": ({"color": "0,0,0,0", "outline_color": "120,120,120", "outline_width": "0.35"},
                   {"line_color": "120,120,120", "line_width": "0.35"},
                   {"name": "circle", "color": "120,120,120", "size": "1.5"}),
    "vertices": (None, None,
                 {"name": "circle", "color": "70,70,70", "size": "1.6", "outline_color": "255,255,255", "outline_width": "0.3"}),
}

PAPEIS = sorted(PALETA)


def aplicar_estilo(camada, papel, rotulo=None):
    """Aplica o símbolo do papel conforme a geometria da camada. rotulo: campo para rótulo discreto."""
    if papel not in PALETA:
        raise ValueError(f"Papel '{papel}' desconhecido. Use um de: {', '.join(PAPEIS)}")
    poli, linha, ponto = PALETA[papel]
    tipo = QgsWkbTypes.geometryType(camada.wkbType())
    if tipo == QgsWkbTypes.PolygonGeometry and poli:
        simbolo = QgsFillSymbol.createSimple(poli)
    elif tipo == QgsWkbTypes.LineGeometry and linha:
        simbolo = QgsLineSymbol.createSimple(linha)
    elif tipo == QgsWkbTypes.PointGeometry and ponto:
        simbolo = QgsMarkerSymbol.createSimple(ponto)
    else:
        return
    camada.renderer().setSymbol(simbolo)
    if rotulo:
        cfg = QgsPalLayerSettings()
        cfg.fieldName = rotulo
        cfg.enabled = True
        fmt = QgsTextFormat()
        fmt.setFont(QFont("Arial"))
        fmt.setSize(6.5)
        fmt.setColor(QColor(50, 50, 50))
        buf = QgsTextBufferSettings()
        buf.setEnabled(True)
        buf.setSize(0.8)
        buf.setColor(QColor(255, 255, 255, 220))
        fmt.setBuffer(buf)
        cfg.setFormat(fmt)
        if tipo == QgsWkbTypes.PointGeometry:  # rótulo ao lado do ponto, sem cobrir o símbolo
            cfg.placement = QgsPalLayerSettings.OrderedPositionsAroundPoint
            cfg.dist = 1.2
        camada.setLabeling(QgsVectorLayerSimpleLabeling(cfg))
        camada.setLabelsEnabled(True)
    camada.triggerRepaint()
