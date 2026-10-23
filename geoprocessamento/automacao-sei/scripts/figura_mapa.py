"""Gera a figura de mapa para o corpo do texto: só a área útil, com legenda sobreposta no melhor canto.

Roda com o Python do QGIS (ver skill projeto-qgis-caso). Exemplo:
    python-qgis.bat figura_mapa.py --pasta "<caso>" --numero 1 --nome-curto area_embargada \
        --objetivo "Mostrar a área embargada dentro do imóvel" \
        --legenda-figura "Área embargada no interior do imóvel, sobre imagem PlanetScope de 10/05/2026" \
        --camadas poligono_area_embargada imovel_car hidrografia imagem_planet \
        --foco poligono_area_embargada \
        --nomes "poligono_area_embargada=Área embargada" "imovel_car=Imóvel (CAR)"

O que sai em 04_Figuras/:
    Figura_01_<nome-curto>.png    a figura, 300 dpi, sem cabeçalho e sem quadro de dados técnicos
    Figura_01_<nome-curto>.json   objetivo, legenda da figura, camadas, escala, canto da legenda e a
                                  pergunta de conferência a responder olhando a figura
O layout também é guardado no projeto do caso (Figura_01), para ajuste fino no QGIS.
"""

import argparse
import gc
import json
import os
import math
import shutil
import sys
from datetime import datetime
from pathlib import Path

from qgis.core import (
    QgsApplication,
    QgsBasicNumericFormat,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemMapGrid,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsMapLayerLegendUtils,
    QgsPrintLayout,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsTextFormat,
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QColor, QFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caso  # noqa: E402
from estilos import PAPEIS, aplicar_estilo  # noqa: E402
from revisao_imagem import revisar as revisar_imagem  # noqa: E402

FONTE = "Arial"
FUNDO_LEGENDA = QColor(255, 255, 255, 220)
MARGEM_MM = 3.0
PREFERENCIA = ["inf_dir", "inf_esq", "sup_dir", "sup_esq"]



def raster_tematico(lyr):
    """NDVI, classes e outros rasters com rampa ou paleta: entram na legenda e não passam pela revisão de imagem."""
    return lyr.renderer() is not None and lyr.renderer().type() in ("singlebandpseudocolor", "paletted")

def mm(valor):
    return QgsLayoutMeasurement(valor, QgsUnitTypes.LayoutMillimeters)


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def iniciar_qgis():
    if QgsApplication.instance() is not None:
        return None
    app = QgsApplication([], False)
    app.initQgis()
    return app


def formato_texto(tamanho, negrito=False):
    f = QgsTextFormat()
    fonte = QFont(FONTE)
    fonte.setBold(negrito)
    f.setFont(fonte)
    f.setSize(tamanho)
    f.setSizeUnit(QgsUnitTypes.RenderPoints)
    return f


def crs_utm(lon, lat):
    """SIRGAS 2000 / UTM da zona do centro (EPSG 31978-31985 sul, 31972-31976 norte)."""
    zona = int(math.floor((lon + 180) / 6)) + 1
    if lat >= 0 and 18 <= zona <= 22:
        return QgsCoordinateReferenceSystem(f"EPSG:{31954 + zona}")
    return QgsCoordinateReferenceSystem(f"EPSG:{31960 + zona}")


def seta_norte():
    for pasta in QgsApplication.svgPaths():
        p = Path(pasta) / "arrows"
        if p.exists():
            setas = sorted(p.glob("NorthArrow_0*.svg"))
            if setas:
                return str(setas[min(1, len(setas) - 1)])
    return ":/images/north_arrows/layout_default_north_arrow.svg"


def retangulo_canto(canto, extensao, largura_mu, altura_mu, margem_mu):
    x0, y0, x1, y1 = extensao.xMinimum(), extensao.yMinimum(), extensao.xMaximum(), extensao.yMaximum()
    esq = canto.endswith("esq")
    inf = canto.startswith("inf")
    xa = x0 + margem_mu if esq else x1 - margem_mu - largura_mu
    ya = y0 + margem_mu if inf else y1 - margem_mu - altura_mu
    return QgsRectangle(xa, ya, xa + largura_mu, ya + altura_mu)


def sobreposicao(ret, foco):
    g = QgsGeometry.fromRect(ret)
    inter = g.intersection(foco)
    return inter.area() if inter and not inter.isEmpty() else 0.0


def posicao_mm(canto, quadro, largura_item, altura_item):
    """Posição do item dentro do quadro do mapa (x, y, largura, altura em mm)."""
    mx, my, mw, mh = quadro
    x = mx + MARGEM_MM if canto.endswith("esq") else mx + mw - MARGEM_MM - largura_item
    y = my + mh - MARGEM_MM - altura_item if canto.startswith("inf") else my + MARGEM_MM
    return QgsLayoutPoint(x, y)


# intervalos "redondos" da grade, em segundos de grau
INTERVALOS_S = [1, 2, 3, 5, 10, 15, 20, 30, 60, 120, 180, 300, 600, 900, 1200, 1800,
                3600, 7200, 10800, 18000, 36000]


def intervalo_grade(largura_graus, alvo=4):
    """Intervalo que dá cerca de 3 a 5 divisões na largura do mapa, qualquer que seja a escala."""
    largura_s = largura_graus * 3600
    for iv in INTERVALOS_S:
        if largura_s / iv <= alvo + 1:
            return iv / 3600
    return INTERVALOS_S[-1] / 3600


def adicionar_grade(mapa, projeto):
    """Grade só com traços curtos na borda (sem linhas sobre o mapa) e valores em GMS (S/O)."""
    geo = QgsCoordinateReferenceSystem("EPSG:4674")
    ext = QgsCoordinateTransform(mapa.crs(), geo, projeto).transformBoundingBox(mapa.extent())
    iv = intervalo_grade(ext.width())
    grade = QgsLayoutItemMapGrid("Grade", mapa)
    grade.setEnabled(True)
    grade.setCrs(geo)
    grade.setIntervalX(iv)
    grade.setIntervalY(iv)
    grade.setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
    grade.setFrameStyle(QgsLayoutItemMapGrid.ExteriorTicks)
    grade.setFrameWidth(1.2)          # comprimento do traço, mm
    grade.setFramePenSize(0.2)
    grade.setFramePenColor(QColor(70, 70, 70))
    grade.setAnnotationEnabled(True)
    # GMS com dois dígitos em minutos e segundos (3°45'00" S); só minutos quando o intervalo é de minutos
    v = "abs(@grid_number)"
    graus = f"floor({v} + 1e-9)"
    minutos_total = f"(({v} - {graus}) * 60)"
    hemi = "if(@grid_axis = 'x', if(@grid_number < 0, 'O', 'L'), if(@grid_number < 0, 'S', 'N'))"
    if iv * 3600 >= 60:
        expr = f"concat({graus}, '°', lpad(round({minutos_total}), 2, '0'), '′ ', {hemi})"
    else:
        minutos = f"floor({minutos_total} + 1e-9)"
        segundos = f"round(({minutos_total} - {minutos}) * 60)"
        expr = f"concat({graus}, '°', lpad({minutos}, 2, '0'), '′', lpad({segundos}, 2, '0'), '″ ', {hemi})"
    grade.setAnnotationFormat(QgsLayoutItemMapGrid.CustomFormat)
    grade.setAnnotationExpression(expr)
    grade.setAnnotationTextFormat(formato_texto(5.5))
    grade.setAnnotationFrameDistance(0.6)
    for lado, exibir, direcao in [
        (QgsLayoutItemMapGrid.Left, QgsLayoutItemMapGrid.LatitudeOnly, QgsLayoutItemMapGrid.Vertical),
        (QgsLayoutItemMapGrid.Bottom, QgsLayoutItemMapGrid.LongitudeOnly, QgsLayoutItemMapGrid.Horizontal),
        (QgsLayoutItemMapGrid.Right, QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Vertical),
        (QgsLayoutItemMapGrid.Top, QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Horizontal),
    ]:
        grade.setAnnotationDisplay(exibir, lado)
        grade.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, lado)
        grade.setAnnotationDirection(direcao, lado)
    mapa.grids().addGrid(grade)
    return {"intervalo": f"{round(iv * 3600)}\"" if iv * 3600 < 60 else f"{round(iv * 60)}'", "graus": iv}


def montar_figura(a, projeto):
    pasta = Path(a.pasta)
    arq_projeto = pasta / "03_Geo" / "caso.qgz"
    if not projeto.read(str(arq_projeto)):
        raise RuntimeError(f"Não consegui abrir {arq_projeto}. Rode antes a skill projeto-qgis-caso.")

    camadas = []
    for nome in a.camadas:
        achadas = projeto.mapLayersByName(nome)
        if not achadas:
            disponiveis = sorted(l.name() for l in projeto.mapLayers().values())
            raise RuntimeError(f"Camada '{nome}' não está no projeto. Disponíveis: {disponiveis}")
        camadas.append(achadas[0])
    nomes_legenda = dict(n.split("=", 1) for n in a.nomes)
    for item in a.estilos:
        nome, papel = item.split("=", 1)
        rotulo = None
        if ":" in papel:
            papel, rotulo = papel.split(":", 1)
        achadas = projeto.mapLayersByName(nome)
        if not achadas:
            raise RuntimeError(f"Camada '{nome}' de --estilos não está no projeto.")
        aplicar_estilo(achadas[0], papel, rotulo)
    foco_nomes = a.foco or [a.camadas[0]]

    # sistema da figura: UTM da zona do foco, para formas e escala corretas
    geo = QgsCoordinateReferenceSystem("EPSG:4674")
    geoms = []
    for nome in foco_nomes:
        lyr = projeto.mapLayersByName(nome)[0]
        t = QgsCoordinateTransform(lyr.crs(), geo, projeto)
        for f in lyr.getFeatures():
            g = QgsGeometry(f.geometry())
            g.transform(t)
            geoms.append(g)
    if not geoms:
        raise RuntimeError(f"As camadas de foco {foco_nomes} não têm feições.")
    foco_geo = QgsGeometry.unaryUnion(geoms)
    c = foco_geo.centroid().asPoint()
    crs_mapa = crs_utm(c.x(), c.y())
    foco = QgsGeometry(foco_geo)
    foco.transform(QgsCoordinateTransform(geo, crs_mapa, projeto))

    # informação principal: o que os rótulos não devem cobrir (padrão: a mesma camada do foco)
    principal_nomes = a.principal or foco_nomes
    partes = []
    for nome in principal_nomes:
        achadas = projeto.mapLayersByName(nome)
        if not achadas:
            raise RuntimeError(f"Camada '{nome}' de --principal não está no projeto.")
        t = QgsCoordinateTransform(achadas[0].crs(), crs_mapa, projeto)
        for f in achadas[0].getFeatures():
            g = QgsGeometry(f.geometry())
            g.transform(t)
            partes.append(g)
    principal = QgsGeometry.unaryUnion(partes) if partes else foco

    # quadro do mapa na página: com grade, sobra espaço à esquerda e embaixo para os valores
    larg, alt = a.largura_mm, a.altura_mm
    if a.sem_grade:
        quadro = (0.0, 0.0, larg, alt)
    else:
        quadro = (6.0, 1.5, larg - 7.5, alt - 6.5)
    mx, my, mw, mh = quadro

    # extensão: foco com margem, no formato do quadro
    bb = foco.boundingBox()
    lado = max(bb.width(), bb.height())
    bb.grow(lado * a.margem)
    proporcao = mw / mh
    if bb.width() / bb.height() < proporcao:
        extra = (bb.height() * proporcao - bb.width()) / 2
        bb = QgsRectangle(bb.xMinimum() - extra, bb.yMinimum(), bb.xMaximum() + extra, bb.yMaximum())
    else:
        extra = (bb.width() / proporcao - bb.height()) / 2
        bb = QgsRectangle(bb.xMinimum(), bb.yMinimum() - extra, bb.xMaximum(), bb.yMaximum() + extra)

    layout = QgsPrintLayout(projeto)
    layout.initializeDefaults()
    nome_layout = f"Figura_{a.numero:02d}"
    layout.setName(nome_layout)
    layout.pageCollection().page(0).setPageSize(QgsLayoutSize(larg, alt))

    mapa = QgsLayoutItemMap(layout)
    mapa.attemptMove(QgsLayoutPoint(mx, my))
    mapa.attemptResize(QgsLayoutSize(mw, mh))
    mapa.setCrs(crs_mapa)
    mapa.setLayers(camadas)
    mapa.setKeepLayerSet(True)
    mapa.setExtent(bb)
    mapa.setFrameEnabled(True)
    mapa.setFrameStrokeColor(QColor(120, 120, 120))
    mapa.setFrameStrokeWidth(mm(0.2))
    layout.addLayoutItem(mapa)
    escala = mapa.scale()
    grade_info = None if a.sem_grade else adicionar_grade(mapa, projeto)

    # revisão de brilho e contraste das imagens de satélite, na área exata da figura
    imagens = []
    for lyr in camadas:
        if isinstance(lyr, QgsRasterLayer) and not raster_tematico(lyr):
            imagens.append(revisar_imagem(lyr, mapa.extent(), crs_mapa, ajustar=(a.ajuste_imagem == "auto")))
    mu_por_mm = mapa.extent().width() / mw

    itens = []  # (nome, item, largura_mm, altura_mm, cantos permitidos)

    if not a.sem_legenda:
        legenda = QgsLayoutItemLegend(layout)
        legenda.setLinkedMap(mapa)
        legenda.setAutoUpdateModel(False)
        raiz = legenda.model().rootGroup()
        raiz.removeAllChildren()
        for lyr in camadas:
            if isinstance(lyr, QgsRasterLayer) and not raster_tematico(lyr):
                continue  # a imagem de fundo é citada na legenda da figura, não na legenda do mapa
            no = raiz.addLayer(lyr)
            rotulo_legenda = nomes_legenda.get(lyr.name())
            if rotulo_legenda:
                no.setUseLayerName(False)  # sem isso, setName renomearia a camada no projeto
                no.setName(rotulo_legenda)
                no.setCustomProperty("legend/title-label", rotulo_legenda)
                # camada de símbolo único: o texto desenhado é o do item de legenda, não o do nó;
                # em camada por classes, o nome fica só no título e as classes mantêm os seus nomes
                if len(legenda.model().layerLegendNodes(no)) == 1:
                    QgsMapLayerLegendUtils.setLegendNodeUserLabel(no, 0, rotulo_legenda)
                legenda.model().refreshLayerLegend(no)
            if isinstance(lyr, QgsRasterLayer):
                # tira a linha "Band 1: ..." da legenda do NDVI e de rasters por classe
                nos = legenda.model().layerLegendNodes(no)
                manter = [i for i, n in enumerate(nos) if not str(n.data(Qt.DisplayRole) or "").startswith(("Band ", "Banda "))]
                if len(manter) < len(nos):
                    QgsMapLayerLegendUtils.setLegendNodeOrder(no, manter)
                    legenda.model().refreshLayerLegend(no)
        legenda.setTitle("Legenda")
        legenda.setLegendFilterByMapEnabled(False)  # as camadas já são escolhidas; o filtro zera o tamanho antes do desenho
        legenda.setResizeToContents(True)
        for estilo, tam, neg in [(QgsLegendStyle.Title, 7, True), (QgsLegendStyle.Subgroup, 6.5, True),
                                 (QgsLegendStyle.SymbolLabel, 6.5, False)]:
            try:
                legenda.rstyle(estilo).setTextFormat(formato_texto(tam, neg))
            except AttributeError:
                fonte = QFont(FONTE, tam)
                fonte.setBold(neg)
                legenda.setStyleFont(estilo, fonte)
        legenda.setSymbolWidth(5)
        legenda.setSymbolHeight(3)
        legenda.setBoxSpace(1.5)
        legenda.setBackgroundEnabled(True)
        legenda.setBackgroundColor(FUNDO_LEGENDA)
        legenda.setFrameEnabled(True)
        legenda.setFrameStrokeColor(QColor(150, 150, 150))
        legenda.setFrameStrokeWidth(mm(0.15))
        layout.addLayoutItem(legenda)
        legenda.updateLegend()
        legenda.adjustBoxSize()
        itens.append(("legenda", legenda, None, None, PREFERENCIA))

    if not a.sem_escala:
        barra = QgsLayoutItemScaleBar(layout)
        barra.setStyle("Single Box")
        barra.setLinkedMap(mapa)
        km = mapa.extent().width() > 4000
        unidade = QgsUnitTypes.DistanceKilometers if km else QgsUnitTypes.DistanceMeters
        barra.applyDefaultSize(unidade)  # define a unidade; chamar sem argumento voltaria para metros
        barra.setUnitLabel("km" if km else "m")
        barra.setNumberOfSegmentsLeft(0)
        barra.setNumberOfSegments(2)
        formato_num = QgsBasicNumericFormat()
        formato_num.setThousandsSeparator(".")
        formato_num.setDecimalSeparator(",")
        formato_num.setShowThousandsSeparator(True)
        barra.setNumericFormat(formato_num)
        # traço refinado: barra baixa, contorno fino, texto pequeno e colado à barra
        barra.setHeight(1.0)
        barra.setLineWidth(0.15)
        barra.setLabelBarSpace(0.5)
        try:
            barra.setTextFormat(formato_texto(5.5))
        except AttributeError:
            barra.setFont(QFont(FONTE, 5))
        barra.setBackgroundEnabled(True)
        barra.setBackgroundColor(FUNDO_LEGENDA)
        layout.addLayoutItem(barra)
        barra.setBoxContentSpace(0.8)
        barra.refreshItemSize()
        itens.append(("escala", barra, None, None, ["inf_esq", "inf_dir"]))

    if not a.sem_norte:
        norte = QgsLayoutItemPicture(layout)
        norte.setPicturePath(seta_norte())
        norte.setLinkedMap(mapa)
        norte.setNorthMode(QgsLayoutItemPicture.GridNorth)
        norte.attemptResize(QgsLayoutSize(7, 10))
        norte.setBackgroundEnabled(False)
        layout.addLayoutItem(norte)
        itens.append(("norte", norte, 7, 10, ["sup_dir", "sup_esq"]))

    # o tamanho real da legenda e da escala só existe depois de um primeiro desenho
    QgsLayoutExporter(layout).renderPageToImage(0, QSize(400, 300))
    for item in (it[1] for it in itens if it[2] is None):
        if isinstance(item, QgsLayoutItemLegend):
            item.adjustBoxSize()
        elif isinstance(item, QgsLayoutItemScaleBar):
            item.refreshItemSize()
            item.attemptResize(item.minimumSize())  # encolhe a caixa ao tamanho da barra refinada
    itens = [(n, it, w if w is not None else it.sizeWithUnits().width(), h if h is not None else it.sizeWithUnits().height(), perm)
             for n, it, w, h, perm in itens]

    # escolhe os cantos: legenda primeiro, depois escala e norte nos cantos que sobrarem
    ocupados, cantos = set(), {}
    for nome, item, w_mm, h_mm, permitidos in itens:
        opcoes = [cn for cn in permitidos if cn not in ocupados] or [cn for cn in PREFERENCIA if cn not in ocupados]
        notas = []
        for cn in opcoes:
            ret = retangulo_canto(cn, mapa.extent(), w_mm * mu_por_mm, h_mm * mu_por_mm, MARGEM_MM * mu_por_mm)
            notas.append((sobreposicao(ret, foco), PREFERENCIA.index(cn), cn))
        notas.sort()
        escolhido = notas[0][2]
        cantos[nome] = {"canto": escolhido, "sobreposicao_m2": round(notas[0][0], 1), "tamanho_mm": [round(w_mm, 1), round(h_mm, 1)]}
        ocupados.add(escolhido)
        item.attemptMove(posicao_mm(escolhido, quadro, w_mm, h_mm))

    pasta_fig = pasta / "04_Figuras"
    pasta_fig.mkdir(parents=True, exist_ok=True)
    base = pasta_fig / f"Figura_{a.numero:02d}_{a.nome_curto}"
    exportador = QgsLayoutExporter(layout)
    cfg = QgsLayoutExporter.ImageExportSettings()
    cfg.dpi = a.dpi
    estado = exportador.exportToImage(f"{base}.png", cfg)
    if estado != QgsLayoutExporter.Success:
        raise RuntimeError(f"Falha ao exportar a figura (código {estado}).")

    alertas = [f"A {n} cobre parte da área de foco ({c['sobreposicao_m2']} m²). Aumente --margem ou reduza a legenda."
               for n, c in cantos.items() if c["sobreposicao_m2"] > 0]

    # revisão automática dos rótulos: todos exibidos? algum cobre a área de foco ou ficou fora do mapa?
    rotulos = {"exibidos": 0, "nao_posicionados": 0, "sobre_a_informacao_principal": [], "cortados_na_borda": []}
    try:
        resultados_rotulos = exportador.labelingResults().get(mapa.uuid())
    except AttributeError:
        resultados_rotulos = None
    if resultados_rotulos is not None:
        moldura = QgsGeometry.fromRect(mapa.extent())
        por_texto = {}  # rótulos curvos vêm letra a letra: junta pelo texto
        for pos in resultados_rotulos.allLabels():
            if getattr(pos, "isUnplaced", False):
                rotulos["nao_posicionados"] += 1
                continue
            g = QgsGeometry.fromRect(pos.labelRect)
            chave = (pos.layerID, pos.featureId, pos.labelText)
            por_texto[chave] = g if chave not in por_texto else por_texto[chave].combine(g)
        for (_, _, texto), ret in por_texto.items():
            rotulos["exibidos"] += 1
            if ret.intersects(principal) and ret.intersection(principal).area() > 0.3 * ret.area():
                rotulos["sobre_a_informacao_principal"].append(texto)
            if not moldura.contains(ret):
                rotulos["cortados_na_borda"].append(texto)
        if hasattr(resultados_rotulos, "unplacedLabels"):
            rotulos["nao_posicionados"] = max(rotulos["nao_posicionados"], len(resultados_rotulos.unplacedLabels()))
    for im in imagens:
        if im["problemas_depois"]:
            alertas.append(f"Imagem {im['camada']}: {'; '.join(im['problemas_depois'])}. Ajuste manualmente e confira.")
    if rotulos["nao_posicionados"]:
        alertas.append(f"{rotulos['nao_posicionados']} rótulo(s) sem espaço para aparecer. Reduza camadas rotuladas ou divida a figura.")
    if rotulos["sobre_a_informacao_principal"]:
        alertas.append(f"Rótulos sobre a informação principal: {', '.join(rotulos['sobre_a_informacao_principal'])}. Confira se atrapalham a leitura.")
    if rotulos["cortados_na_borda"]:
        alertas.append(f"Rótulos cortados na borda: {', '.join(rotulos['cortados_na_borda'])}. Aumente --margem.")
    meta = {
        "figura": f"Figura {a.numero}",
        "arquivo": f"{base.name}.png",
        "objetivo": a.objetivo,
        "legenda_figura": f"Figura {a.numero} – {a.legenda_figura}",
        "fonte": a.fonte,
        "camadas": a.camadas,
        "nomes_na_legenda": nomes_legenda,
        "foco": foco_nomes,
        "sistema_da_figura": crs_mapa.authid(),
        "grade": grade_info,
        "escala_aproximada": f"1:{round(escala, -2):,.0f}".replace(",", "."),
        "tamanho_mm": [larg, alt],
        "dpi": a.dpi,
        "cantos": cantos,
        "imagens": imagens,
        "rotulos": rotulos,
        "alertas": alertas,
        "conferencia": [
            "O objetivo foi atendido por esta figura?",
            "A informação principal do objetivo aparece em primeiro plano, à primeira vista?",
            "A legenda da figura está alinhada ao objetivo?",
            "Há informação demais? Se sim, dividir em uma sequência de figuras.",
            "Cores suaves, legível para quem não é especialista em mapas?",
            "Rótulos todos visíveis, com buffer, sem cobrir a informação principal?",
            "Imagem de satélite com brilho e contraste adequados, sem ficar escura, apagada ou estourada?",
            "Linhas finas, sem traço grosseiro, mas ainda visíveis sobre a imagem?",
        ],
        "conferido": False,
        "gerada_em": agora(),
    }
    Path(f"{base}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    if a.salvar_layout:
        gerenciador = projeto.layoutManager()
        antigo = gerenciador.layoutByName(nome_layout)
        if antigo:
            gerenciador.removeLayout(antigo)
        gerenciador.addLayout(layout)
        shutil.copy2(arq_projeto, arq_projeto.with_name(f"caso_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.qgz"))
        projeto.write()

    ficha_json = pasta / "00_Ficha" / "ficha.json"
    if ficha_json.exists():
        ficha = json.loads(ficha_json.read_text(encoding="utf-8"))
        figuras = [f for f in ficha.get("figuras", []) if f.get("figura") != meta["figura"]]
        figuras.append({k: meta[k] for k in ("figura", "arquivo", "objetivo", "legenda_figura", "conferido")})
        ficha["figuras"] = sorted(figuras, key=lambda f: int(f["figura"].split()[-1]))
        ficha_json.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
        caso.gravar_ficha_md(pasta, ficha)
        caso.registrar_linha(pasta, "figuras", f"{meta['figura']} gerada ({meta['arquivo']}), escala {meta['escala_aproximada']}, legenda no canto {cantos.get('legenda', {}).get('canto', '—')}.")
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description="Figura de mapa com legenda sobreposta para o corpo do texto.")
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--numero", type=int, required=True, help="Número da figura no texto")
    ap.add_argument("--nome-curto", required=True, help="Parte do nome do arquivo, sem espaços")
    ap.add_argument("--objetivo", required=True, help="O que a figura precisa mostrar, em uma frase")
    ap.add_argument("--legenda-figura", required=True, help="Texto da legenda da figura no documento (sem 'Figura N –')")
    ap.add_argument("--fonte", default="Elaborado pelo autor. Sistema de referência SIRGAS 2000.",
                    help="Fonte, impressa abaixo da figura (ABNT): autoria, imagem (sensor e data) e bases usadas")
    ap.add_argument("--camadas", nargs="+", required=True, help="Camadas do projeto, de cima para baixo")
    ap.add_argument("--foco", nargs="*", help="Camadas que definem o enquadramento (padrão: a primeira)")
    ap.add_argument("--principal", nargs="*", help="Camadas da informação principal, que os rótulos não devem cobrir (padrão: as do foco)")
    ap.add_argument("--nomes", nargs="*", default=[], help='Nome na legenda: "camada=Nome legível"')
    ap.add_argument("--estilos", nargs="*", default=[],
                    help=f'Paleta padrão: "camada=papel" ou "camada=papel:campo_do_rotulo". Papéis: {", ".join(PAPEIS)}')
    ap.add_argument("--margem", type=float, default=0.35, help="Folga em volta do foco (fração do maior lado)")
    ap.add_argument("--largura-mm", type=float, default=160)
    ap.add_argument("--altura-mm", type=float, default=110)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--ajuste-imagem", default="auto", choices=["auto", "so-medir"],
                    help="auto: corrige brilho e contraste se preciso; so-medir: só aponta o problema")
    ap.add_argument("--sem-legenda", action="store_true")
    ap.add_argument("--sem-escala", action="store_true")
    ap.add_argument("--sem-norte", action="store_true")
    ap.add_argument("--sem-grade", action="store_true", help="Sem grade de coordenadas na borda")
    ap.add_argument("--nao-salvar-layout", dest="salvar_layout", action="store_false")
    a = ap.parse_args(argv)

    app = iniciar_qgis()
    projeto = QgsProject()
    try:
        meta = montar_figura(a, projeto)
    finally:
        projeto.clear()
        del projeto
        gc.collect()  # libera layout e legenda antes de encerrar o QGIS
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    if app is not None:
        sys.stdout.flush()
        # fora do QGIS, encerrar a aplicação Qt com layouts criados pode derrubar o processo
        # depois de tudo gravado; sair direto evita o falso erro
        os._exit(0)
    return meta


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
