"""Paleta padrão de cores suaves e rótulos para os mapas dos casos, por papel da camada.

Uso nos scripts: aplicar_estilo(camada, "foco", rotulo="nome"). Papéis: foco, imovel, hidrografia, uc,
ti, app, desmatamento, referencia, vertices. Ajuste aqui para mudar o padrão de todos os mapas.

Regras do padrão:
- linhas finas: o mínimo que ainda se enxerga sobre a imagem (0,2 a 0,35 mm a 300 dpi);
- rótulos sempre com buffer (halo) branco, para leitura sobre imagem;
- rótulos sempre exibidos, colocados fora da área principal sempre que possível.
"""

from qgis.core import (
    QgsFillSymbol,
    QgsLabelObstacleSettings,
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
    # papel: (polígono, linha, ponto) — larguras em mm
    "foco": ({"color": "214,96,77,70", "outline_color": "192,57,43", "outline_width": "0.35"},
             {"line_color": "192,57,43", "line_width": "0.4"},
             {"name": "circle", "color": "192,57,43", "size": "2", "outline_color": "255,255,255", "outline_width": "0.2"}),
    "imovel": ({"color": "0,0,0,0", "outline_color": "230,145,56", "outline_width": "0.3", "outline_style": "dash"},
               {"line_color": "230,145,56", "line_width": "0.3"},
               {"name": "square", "color": "230,145,56", "size": "1.8", "outline_width": "0.2"}),
    "hidrografia": ({"color": "174,214,241,180", "outline_color": "93,173,226", "outline_width": "0.2"},
                    {"line_color": "93,173,226", "line_width": "0.4"},
                    {"name": "circle", "color": "93,173,226", "size": "1.5", "outline_width": "0.2"}),
    "uc": ({"color": "130,190,130,60", "outline_color": "76,140,76", "outline_width": "0.3"},
           {"line_color": "76,140,76", "line_width": "0.3"},
           {"name": "circle", "color": "76,140,76", "size": "1.6", "outline_width": "0.2"}),
    "ti": ({"color": "214,180,130,60", "outline_color": "160,115,60", "outline_width": "0.3"},
           {"line_color": "160,115,60", "line_width": "0.3"},
           {"name": "circle", "color": "160,115,60", "size": "1.6", "outline_width": "0.2"}),
    "app": ({"color": "120,190,205,60", "outline_color": "60,140,170", "outline_width": "0.25", "outline_style": "dash"},
            {"line_color": "60,140,170", "line_width": "0.25"},
            {"name": "circle", "color": "60,140,170", "size": "1.5", "outline_width": "0.2"}),
    "desmatamento": ({"color": "240,180,90,110", "outline_color": "210,130,40", "outline_width": "0.25"},
                     {"line_color": "210,130,40", "line_width": "0.3"},
                     {"name": "circle", "color": "210,130,40", "size": "1.6", "outline_width": "0.2"}),
    "referencia": ({"color": "0,0,0,0", "outline_color": "120,120,120", "outline_width": "0.25"},
                   {"line_color": "120,120,120", "line_width": "0.25"},
                   {"name": "circle", "color": "120,120,120", "size": "1.4", "outline_width": "0.2"}),
    "vertices": (None, None,
                 {"name": "circle", "color": "70,70,70", "size": "1.4", "outline_color": "255,255,255", "outline_width": "0.2"}),
}

PAPEIS = sorted(PALETA)


def formato_rotulo(tamanho=6.5):
    """Texto cinza-escuro com buffer branco: legível sobre imagem e sobre fundo claro."""
    fmt = QgsTextFormat()
    fmt.setFont(QFont("Arial"))
    fmt.setSize(tamanho)
    fmt.setColor(QColor(40, 40, 40))
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(0.8)
    buf.setColor(QColor(255, 255, 255, 230))
    fmt.setBuffer(buf)
    return fmt


def rotular(camada, campo, tipo):
    cfg = QgsPalLayerSettings()
    cfg.fieldName = campo
    cfg.enabled = True
    cfg.setFormat(formato_rotulo())
    if tipo == QgsWkbTypes.PointGeometry:
        # ao lado do ponto, em várias posições possíveis, sem cobrir o símbolo
        cfg.placement = QgsPalLayerSettings.OrderedPositionsAroundPoint
        cfg.dist = 1.0
    elif tipo == QgsWkbTypes.PolygonGeometry:
        # fora do polígono, para não cobrir a informação principal
        cfg.placement = getattr(QgsPalLayerSettings, "OutsidePolygons", QgsPalLayerSettings.AroundPoint)
        cfg.dist = 1.0
    else:
        cfg.placement = QgsPalLayerSettings.Curved if hasattr(QgsPalLayerSettings, "Curved") else QgsPalLayerSettings.Line
    # sempre exibir: evita sobreposição quando possível; se não houver espaço, mostra mesmo assim
    try:
        from qgis.core import Qgis
        cfg.placementSettings().setOverlapHandling(Qgis.LabelOverlapHandling.AllowOverlapIfRequired)
    except (ImportError, AttributeError):
        cfg.displayAll = True
    camada.setLabeling(QgsVectorLayerSimpleLabeling(cfg))
    camada.setLabelsEnabled(True)


def obstaculo_interno(camada):
    """Faz o interior do polígono funcionar como obstáculo: rótulos de outras camadas evitam cobri-lo."""
    if not camada.labeling():
        cfg = QgsPalLayerSettings()
        cfg.enabled = False
        cfg.drawLabels = False
    else:
        cfg = camada.labeling().settings()
    obs = cfg.obstacleSettings()
    obs.setIsObstacle(True)
    obs.setType(QgsLabelObstacleSettings.PolygonInterior)
    obs.setFactor(2.0)
    cfg.setObstacleSettings(obs)
    camada.setLabeling(QgsVectorLayerSimpleLabeling(cfg))
    camada.setLabelsEnabled(True)


def aplicar_estilo(camada, papel, rotulo=None):
    """Aplica o símbolo do papel conforme a geometria da camada. rotulo: campo para rótulo."""
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
        rotular(camada, rotulo, tipo)
    if papel == "foco" and tipo == QgsWkbTypes.PolygonGeometry:
        obstaculo_interno(camada)
    camada.triggerRepaint()
