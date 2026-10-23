"""Georreferencia um mapa ou croqui escaneado a partir de pontos de controle, com controle de erro.

Roda com o Python do QGIS (precisa do GDAL). Exemplo:
    python-qgis.bat georreferenciar.py --pasta "<caso>" --imagem "<caso>/02_Insumos/mapas_scan/croqui.jpg" \
        --pontos "<caso>/02_Insumos/mapas_scan/croqui_pontos.csv" --limite-m 10 --fonte "Croqui do auto de infração, escala 1:50.000"

Pontos de controle (CSV, separador , ou ;), uma linha por ponto, com:
    pixel:  coluna/x_pixel e linha/y_pixel (a partir do canto superior esquerdo da imagem)
    terreno: latitude e longitude (GMS ou decimal) OU e, n (UTM) com zona
    opcional: id e uso ("controle" ou "verificacao"; os de verificação não entram no ajuste)
Também aceita o arquivo .points do georreferenciador do QGIS (mapX, mapY, sourceX, sourceY, enable).

Saídas em 03_Geo/georreferenciados/:
    <nome>_georref.tif    GeoTIFF em SIRGAS 2000 (EPSG:4674), compactado, com transparência fora do mapa
    <nome>_georref.json   transformação, erro de cada ponto, RMS, limite e o uso permitido
    <nome>_georref.md     o mesmo relatório para leitura
Código 2 quando o RMS passa do limite (o raster é gerado, mas marcado como "somente ilustrativo").
"""

import argparse
import csv
import io
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from osgeo import gdal, osr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caso  # noqa: E402
from coordenadas import ELIPSOIDES, achar_colunas, ler_angulo, numero, sem_acento, utm_para_geo  # noqa: E402

gdal.UseExceptions()
TERMOS = {1: 3, 2: 6, 3: 10}


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def srs(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return s


def epsg_utm(lon, lat):
    zona = int(math.floor((lon + 180) / 6)) + 1
    return (31954 + zona) if (lat >= 0 and 18 <= zona <= 22) else (31960 + zona)


def ler_pontos(caminho, datum, zona_padrao, hemisferio):
    texto = Path(caminho).read_text(encoding="utf-8-sig")
    linhas = [l for l in texto.splitlines() if l.strip() and not l.startswith("#")]
    if linhas and linhas[0].lower().startswith("mapx"):  # formato .points do QGIS
        pontos = []
        for i, l in enumerate(csv.DictReader(io.StringIO("\n".join(linhas))), start=1):
            if str(l.get("enable", "1")).strip() in ("0", "false"):
                continue
            pontos.append({"id": f"P{i}", "col": float(l["sourceX"]), "lin": -float(l["sourceY"]),
                           "lon": float(l["mapX"]), "lat": float(l["mapY"]), "uso": "controle"})
        return pontos, "QGIS .points (coordenadas do mapa assumidas em graus no datum informado)"
    try:
        dialeto = csv.Sniffer().sniff("\n".join(linhas[:20]), delimiters=";,\t")
    except csv.Error:
        dialeto = csv.excel
        dialeto.delimiter = ";" if linhas[0].count(";") >= linhas[0].count(",") else ","
    tabela = list(csv.reader(io.StringIO("\n".join(linhas)), dialeto))
    cab = tabela[0]
    norm = [sem_acento(c) for c in cab]
    col = achar_colunas(cab)

    def idx(*nomes):
        for n in nomes:
            if n in norm:
                return norm.index(n)
        return None

    ic, il = idx("coluna", "x_pixel", "pixel_x", "col", "px"), idx("linha", "y_pixel", "pixel_y", "lin", "py")
    iu = idx("uso", "tipo")
    if ic is None or il is None:
        sys.exit("A tabela de pontos precisa das colunas de pixel: coluna (ou x_pixel) e linha (ou y_pixel).")
    pontos, formato = [], ""
    for k, l in enumerate(tabela[1:], start=2):
        pid = l[col["vertice"]].strip() if "vertice" in col else f"P{k - 1}"
        if "lat" in col and "lon" in col and col["lat"] not in (ic, il):
            lat, _, f1 = ler_angulo(l[col["lat"]], "lat")
            lon, tem_h, f2 = ler_angulo(l[col["lon"]], "lon")
            if lon > 0 and not tem_h:
                lon = -lon
            formato = f"geográficas ({f1})"
        else:
            e, n = numero(l[col["e"]]), numero(l[col["n"]])
            zona = int(numero(l[col["zona"]])) if "zona" in col and l[col["zona"]].strip() else zona_padrao
            if not zona:
                sys.exit("Pontos em UTM sem zona: informe --zona.")
            lat, lon = utm_para_geo(e, n, zona, hemisferio, datum)
            formato = f"UTM zona {zona}{hemisferio}"
        uso = sem_acento(l[iu]).strip() if iu is not None and iu < len(l) and l[iu].strip() else "controle"
        pontos.append({"id": pid, "col": numero(l[ic]), "lin": numero(l[il]), "lat": lat, "lon": lon,
                       "uso": "verificacao" if uso.startswith("verif") else "controle"})
    return pontos, formato


def desenho(x, y, ordem):
    termos = [np.ones_like(x), x, y]
    if ordem >= 2:
        termos += [x * x, x * y, y * y]
    if ordem >= 3:
        termos += [x ** 3, x * x * y, x * y * y, y ** 3]
    return np.column_stack(termos)


def ajustar(pts, ordem):
    """Ajuste por mínimos quadrados pixel -> metros (UTM); devolve coeficientes e função de previsão."""
    x = np.array([p["col"] for p in pts], float)
    y = np.array([p["lin"] for p in pts], float)
    # normaliza os pixels para estabilidade numérica
    mx, my, s = x.mean(), y.mean(), max(x.std(), y.std(), 1.0)
    A = desenho((x - mx) / s, (y - my) / s, ordem)
    ce, *_ = np.linalg.lstsq(A, np.array([p["e"] for p in pts]), rcond=None)
    cn, *_ = np.linalg.lstsq(A, np.array([p["n"] for p in pts]), rcond=None)

    def prever(px, py):
        B = desenho((np.asarray(px, float) - mx) / s, (np.asarray(py, float) - my) / s, ordem)
        return B @ ce, B @ cn
    return prever


def avaliar(pontos, ordem):
    ctrl = [p for p in pontos if p["uso"] == "controle"]
    verif = [p for p in pontos if p["uso"] == "verificacao"]
    prever = ajustar(ctrl, ordem)
    for p in ctrl + verif:
        e, n = prever([p["col"]], [p["lin"]])
        p["residuo_m"] = float(math.hypot(e[0] - p["e"], n[0] - p["n"]))
    # resíduo com o ponto fora do ajuste (aponta ponto suspeito melhor que o resíduo comum)
    if len(ctrl) > TERMOS[ordem] + 1:
        for i, p in enumerate(ctrl):
            outros = ctrl[:i] + ctrl[i + 1:]
            e, n = ajustar(outros, ordem)([p["col"]], [p["lin"]])
            p["residuo_sem_o_ponto_m"] = float(math.hypot(e[0] - p["e"], n[0] - p["n"]))
    rms = math.sqrt(sum(p["residuo_m"] ** 2 for p in ctrl) / len(ctrl))
    rms_verif = math.sqrt(sum(p["residuo_m"] ** 2 for p in verif) / len(verif)) if verif else None
    # tamanho do pixel no terreno
    e0, n0 = prever([0, 1, 0], [0, 0, 1])
    pixel_m = math.sqrt(abs((e0[1] - e0[0]) * (n0[2] - n0[0]) - (e0[2] - e0[0]) * (n0[1] - n0[0])))
    return ctrl, verif, rms, rms_verif, pixel_m


def main(argv=None):
    ap = argparse.ArgumentParser(description="Georreferenciamento com controle de erro.")
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--imagem", required=True)
    ap.add_argument("--pontos", required=True)
    ap.add_argument("--datum", default="SIRGAS2000", choices=list(ELIPSOIDES), help="Datum das coordenadas dos pontos")
    ap.add_argument("--zona", type=int)
    ap.add_argument("--hemisferio", default="S", choices=["N", "S"])
    ap.add_argument("--ordem", type=int, default=0, choices=[0, 1, 2, 3], help="Polinômio; 0 = escolher sozinho")
    ap.add_argument("--limite-m", type=float, help="RMS máximo aceito, em metros (definido caso a caso)")
    ap.add_argument("--escala-mapa", type=float, help="Denominador da escala do mapa original, para sugerir o limite")
    ap.add_argument("--reamostragem", default="cubic", choices=["near", "bilinear", "cubic", "lanczos"])
    ap.add_argument("--fonte", default="", help="De onde vem o mapa (documento, página, escala)")
    a = ap.parse_args(argv)

    pasta = Path(a.pasta)
    imagem = Path(a.imagem)
    pontos, formato = ler_pontos(a.pontos, a.datum, a.zona, a.hemisferio)
    ctrl_n = sum(1 for p in pontos if p["uso"] == "controle")
    if ctrl_n < 3:
        sys.exit(f"São necessários pelo menos 3 pontos de controle (há {ctrl_n}).")

    # coordenadas dos pontos: datum de origem -> SIRGAS 2000 -> UTM da zona (metros)
    epsg_origem = ELIPSOIDES[a.datum][2]
    lon_c = sum(p["lon"] for p in pontos) / len(pontos)
    lat_c = sum(p["lat"] for p in pontos) / len(pontos)
    epsg_m = epsg_utm(lon_c, lat_c)
    para_sirgas = osr.CoordinateTransformation(srs(epsg_origem), srs(4674))
    para_utm = osr.CoordinateTransformation(srs(4674), srs(epsg_m))
    for p in pontos:
        lon, lat, _ = para_sirgas.TransformPoint(p["lon"], p["lat"])
        p["lon"], p["lat"] = lon, lat
        p["e"], p["n"], _ = para_utm.TransformPoint(lon, lat)

    # ordem do polinômio: a mais simples que não deixa erro sistemático
    ordens = [a.ordem] if a.ordem else [o for o in (1, 2) if ctrl_n >= TERMOS[o] + 2] or [1]
    melhor = None
    for o in ordens:
        ctrl, verif, rms, rms_v, pixel_m = avaliar([dict(p) for p in pontos], o)
        if melhor is None or rms < 0.7 * melhor[2]:  # só sobe a ordem se reduzir o erro com folga
            melhor = (o, ctrl, rms, rms_v, pixel_m, verif)
    ordem, ctrl, rms, rms_v, pixel_m, verif = melhor

    sugestao = round(0.0002 * a.escala_mapa, 1) if a.escala_mapa else round(2 * pixel_m, 1)
    limite = a.limite_m if a.limite_m else sugestao
    # ponto suspeito: aquele cuja retirada derruba o RMS com folga (até 2 pontos, um de cada vez)
    suspeitos, sugestoes, restantes, rms_atual = [], [], [dict(p) for p in pontos], rms
    for _ in range(2):
        ctrl_r = [p for p in restantes if p["uso"] == "controle"]
        if len(ctrl_r) < TERMOS[ordem] + 3:
            break
        testes = []
        for p in ctrl_r:
            sem = [q for q in restantes if q is not p]
            testes.append((avaliar([dict(q) for q in sem], ordem)[2], p))
        rms_sem, pior = min(testes, key=lambda x: x[0])
        if rms_sem < 0.6 * rms_atual and rms_atual > limite * 0.5:
            suspeitos.append(pior["id"])
            sugestoes.append(f"sem o ponto {pior['id']}, o RMS cai de {rms_atual:.2f} m para {rms_sem:.2f} m".replace(".", ","))
            restantes = [q for q in restantes if q is not pior]
            rms_atual = rms_sem
        else:
            break
    aprovado = rms <= limite and (rms_v is None or rms_v <= limite * 1.5)

    # GeoTIFF: GCPs em UTM, transformação polinomial, saída em SIRGAS 2000 geográficas
    destino_dir = pasta / "03_Geo" / "georreferenciados"
    destino_dir.mkdir(parents=True, exist_ok=True)
    nome = imagem.stem
    tif = destino_dir / f"{nome}_georref.tif"
    gcps = [gdal.GCP(p["e"], p["n"], 0, p["col"], p["lin"], "", p["id"]) for p in ctrl]
    temp = destino_dir / f"_{nome}_gcps.vrt"
    gdal.Translate(str(temp), str(imagem), format="VRT", GCPs=gcps, outputSRS=f"EPSG:{epsg_m}")
    gdal.Warp(str(tif), str(temp), dstSRS="EPSG:4674", polynomialOrder=ordem, resampleAlg=a.reamostragem,
              dstAlpha=True, creationOptions=["COMPRESS=DEFLATE", "TILED=YES"])
    temp.unlink(missing_ok=True)

    uso = "medição e análise" if aprovado else "somente ilustrativo (não usar para medir áreas ou distâncias)"
    rel = {
        "imagem": str(imagem), "saida": str(tif), "fonte": a.fonte, "pontos_formato": formato,
        "datum_dos_pontos": a.datum, "sistema_de_calculo": f"EPSG:{epsg_m}", "sistema_de_saida": "EPSG:4674",
        "transformacao": f"polinomial de ordem {ordem}", "pontos_controle": len(ctrl), "pontos_verificacao": len(verif),
        "rms_m": round(rms, 2), "rms_verificacao_m": round(rms_v, 2) if rms_v is not None else None,
        "pixel_no_terreno_m": round(pixel_m, 2), "limite_m": limite,
        "limite_origem": "informado pelo usuário" if a.limite_m else
                         ("sugerido: 0,2 mm na escala 1:" + f"{int(a.escala_mapa):,}".replace(",", ".") if a.escala_mapa else "sugerido: 2 pixels no terreno"),
        "aprovado": aprovado, "uso_permitido": uso, "pontos_suspeitos": suspeitos, "sugestoes": sugestoes,
        "pontos": [{k: (round(v, 2) if isinstance(v, float) and k not in ("lat", "lon") else v) for k, v in p.items()} for p in ctrl + verif],
        "em": agora(),
    }
    (destino_dir / f"{nome}_georref.json").write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [f"# Georreferenciamento – {imagem.name}", "",
          f"- Fonte: {a.fonte or '—'}",
          f"- Transformação: {rel['transformacao']}, {len(ctrl)} pontos de controle" + (f" e {len(verif)} de verificação" if verif else ""),
          f"- **RMS: {rel['rms_m']:.2f} m** (limite {limite:.1f} m, {rel['limite_origem']})".replace(".", ","),
          f"- Pixel no terreno: {rel['pixel_no_terreno_m']:.2f} m".replace(".", ","),
          f"- **Uso permitido: {uso}**", ""]
    if rel["rms_verificacao_m"] is not None:
        md.insert(5, f"- RMS nos pontos de verificação (independentes): {rel['rms_verificacao_m']:.2f} m".replace(".", ","))
    if suspeitos:
        md += [f"**Pontos suspeitos: {', '.join(suspeitos)}** ({'; '.join(sugestoes)}). Confira a posição do ponto no mapa e a coordenada; "
               "se estiver errado, corrija ou retire da tabela e rode de novo. O script não retira pontos sozinho.", ""]
    md += ["| Ponto | Uso | Erro (m) | Erro sem o ponto no ajuste (m) |", "| --- | --- | --- | --- |"]
    for p in ctrl + verif:
        sem = p.get("residuo_sem_o_ponto_m")
        md.append(f"| {p['id']} | {p['uso']} | {p['residuo_m']:.2f} | {sem:.2f} |".replace(".", ",") if sem is not None
                  else f"| {p['id']} | {p['uso']} | {p['residuo_m']:.2f} | — |".replace(".", ","))
    (destino_dir / f"{nome}_georref.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    ficha_json = pasta / "00_Ficha" / "ficha.json"
    if ficha_json.exists():
        ficha = json.loads(ficha_json.read_text(encoding="utf-8"))
        lista = [g for g in ficha.get("georreferenciados", []) if g.get("arquivo") != tif.name]
        lista.append({"arquivo": tif.name, "fonte": a.fonte, "rms_m": rel["rms_m"], "limite_m": limite, "uso": uso})
        ficha["georreferenciados"] = lista
        ficha_json.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
        caso.gravar_ficha_md(pasta, ficha)
        caso.registrar_linha(pasta, "geo", f"Georreferenciado {imagem.name}: RMS {rel['rms_m']} m (limite {limite} m), {uso}.")

    print(json.dumps({k: rel[k] for k in ("saida", "transformacao", "rms_m", "rms_verificacao_m", "pixel_no_terreno_m",
                                          "limite_m", "limite_origem", "aprovado", "uso_permitido", "pontos_suspeitos", "sugestoes")},
                     ensure_ascii=False, indent=2))
    sys.exit(0 if aprovado else 2)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
