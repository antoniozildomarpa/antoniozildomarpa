"""Lê tabelas de coordenadas (GMS, grau decimal ou UTM), valida e gera vértices e polígono.

Uso:
    python coordenadas.py <tabela.csv> [--tipo poligono|pontos|linha] [--formato auto|gms|decimal|utm]
                          [--zona 22] [--hemisferio S] [--datum SIRGAS2000] [--saida <pasta>] [--casas 3]

Entrada: CSV com cabeçalho (separador , ou ; detectado sozinho; vírgula decimal aceita).
Colunas reconhecidas (sem diferenciar maiúsculas e acentos):
    vértice: vertice, ponto, id, nome, marco
    geográficas: latitude/lat/y e longitude/lon/long/x
    UTM: e/este/easting/x e n/norte/northing/y, e opcionalmente zona/fuso

Saídas, na pasta de saída (padrão: a pasta da tabela):
    <nome>_normalizado.csv   vértices em grau decimal e GMS, com o datum
    <nome>.geojson           vértices e polígono (ou linha), com área e perímetro
    <nome>_validacao.md      o que foi conferido, alertas e erros

Código de saída: 0 sem erros, 2 com erros (os arquivos não são gerados).
Só usa a biblioteca padrão do Python: roda no Python do QGIS ou em qualquer outro.
"""

import argparse
import csv
import io
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

ELIPSOIDES = {
    # datum: (semieixo maior, achatamento, EPSG geográfico, base EPSG UTM sul por zona 18..25)
    "SIRGAS2000": (6378137.0, 1 / 298.257222101, 4674),
    "WGS84": (6378137.0, 1 / 298.257223563, 4326),
    "SAD69": (6378160.0, 1 / 298.25, 4618),
    "CORREGO_ALEGRE": (6378388.0, 1 / 297.0, 4225),
}

BRASIL = {"lat": (-34.0, 5.5), "lon": (-74.5, -28.5)}


def sem_acento(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower().strip()


# ---------- leitura de números e GMS ----------

def numero(txt):
    """'12,345' ou '12.345' ou '1.234,5' -> float."""
    t = txt.strip().replace(" ", "")
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") else t.replace(",", "")
    else:
        t = t.replace(",", ".")
    return float(t)




def ler_angulo(txt, eixo):
    """Converte GMS, graus-minutos decimais ou grau decimal em grau decimal.

    Retorna (valor, tinha_hemisferio, formato). Lança ValueError com o motivo.
    """
    bruto = txt.strip()
    if not bruto:
        raise ValueError("vazio")
    t = bruto.upper().replace("º", "°").replace("’", "'").replace("′", "'").replace("″", '"').replace("”", '"').replace("''", '"')
    hemi = None
    m = re.search(r"([NSEWLO])\s*$", t) or re.match(r"^\s*([NSEWLO])", t)
    if m:
        hemi = m.group(1)
        t = (t[: m.start()] + t[m.end():]).strip()
    negativo = t.startswith("-")
    t = t.lstrip("+-").strip()

    partes = [p for p in re.split(r"[°'\":\s]+", t) if p]
    if not partes:
        raise ValueError("sem números")
    try:
        nums = [numero(p) for p in partes]
    except ValueError:
        raise ValueError(f"não reconheci '{bruto}'")
    if len(nums) == 1:
        valor, formato = nums[0], "decimal"
    elif len(nums) == 2:
        g, mi = nums
        if mi >= 60:
            raise ValueError(f"minutos ≥ 60 em '{bruto}'")
        valor, formato = g + mi / 60, "graus e minutos"
    elif len(nums) == 3:
        g, mi, s = nums
        if mi >= 60 or s >= 60:
            raise ValueError(f"minutos ou segundos ≥ 60 em '{bruto}'")
        if mi != int(mi):
            raise ValueError(f"minutos com decimais e segundos ao mesmo tempo em '{bruto}'")
        valor, formato = g + mi / 60 + s / 3600, "GMS"
    else:
        raise ValueError(f"números demais em '{bruto}'")

    if hemi:
        if eixo == "lat" and hemi not in "NS":
            raise ValueError(f"hemisfério '{hemi}' inválido para latitude")
        if eixo == "lon" and hemi not in "EWLO":
            raise ValueError(f"hemisfério '{hemi}' inválido para longitude")
        if hemi in "SWO":
            valor = -abs(valor)
    elif negativo:
        valor = -valor
    return valor, bool(hemi or negativo), formato


def para_gms(valor, eixo, casas=3):
    hemi = ("N" if valor >= 0 else "S") if eixo == "lat" else ("L" if valor >= 0 else "O")
    v = abs(valor)
    g = int(v)
    m = int((v - g) * 60)
    s = round(((v - g) * 60 - m) * 60, casas)
    if s >= 60:
        s -= 60
        m += 1
    if m >= 60:
        m -= 60
        g += 1
    largura = 2 if eixo == "lat" else 3
    seg = f"{s:0{3 + casas}.{casas}f}".replace(".", ",")
    return f"{g:0{largura}d}°{m:02d}'{seg}\" {hemi}"


# ---------- UTM -> geográficas (Snyder, série de Krüger) ----------

def utm_para_geo(e, n, zona, hemisferio, datum):
    a, f, _ = ELIPSOIDES[datum]
    k0 = 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    x = e - 500000.0
    y = n - (10000000.0 if hemisferio == "S" else 0.0)
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (mu + (3 * e1 / 2 - 27 * e1**3 / 32) * math.sin(2 * mu)
            + (21 * e1**2 / 16 - 55 * e1**4 / 32) * math.sin(4 * mu)
            + (151 * e1**3 / 96) * math.sin(6 * mu)
            + (1097 * e1**4 / 512) * math.sin(8 * mu))
    s1, c1 = math.sin(phi1), math.cos(phi1)
    t1 = math.tan(phi1) ** 2
    cc = ep2 * c1**2
    n1 = a / math.sqrt(1 - e2 * s1**2)
    r1 = a * (1 - e2) / (1 - e2 * s1**2) ** 1.5
    d = x / (n1 * k0)
    lat = phi1 - (n1 * math.tan(phi1) / r1) * (
        d**2 / 2 - (5 + 3 * t1 + 10 * cc - 4 * cc**2 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * cc + 45 * t1**2 - 252 * ep2 - 3 * cc**2) * d**6 / 720)
    lon0 = math.radians((zona - 1) * 6 - 180 + 3)
    lon = lon0 + (d - (1 + 2 * t1 + cc) * d**3 / 6
                  + (5 - 2 * cc + 28 * t1 - 3 * cc**2 + 8 * ep2 + 24 * t1**2) * d**5 / 120) / c1
    return math.degrees(lat), math.degrees(lon)


# ---------- área e perímetro no elipsoide ----------

def area_elipsoidal(pontos, datum):
    """Área (m²) por projeção cilíndrica de áreas iguais sobre a esfera autálica (exata para áreas)."""
    a, f, _ = ELIPSOIDES[datum]
    e2 = f * (2 - f)
    e = math.sqrt(e2)

    def q(phi):
        s = math.sin(phi)
        return (1 - e2) * (s / (1 - e2 * s * s) - (1 / (2 * e)) * math.log((1 - e * s) / (1 + e * s)))

    qp = q(math.pi / 2)
    rq = a * math.sqrt(qp / 2)
    betas = [math.asin(max(-1.0, min(1.0, q(math.radians(la)) / qp))) for la, _ in pontos]
    b0 = sum(betas) / len(betas)
    lon0 = sum(lo for _, lo in pontos) / len(pontos)
    xy = [(rq * math.cos(b0) * math.radians(lo - lon0), rq * math.sin(b) / math.cos(b0)) for b, (_, lo) in zip(betas, pontos)]
    soma = 0.0
    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]
        soma += x1 * y2 - x2 * y1
    return abs(soma) / 2


def distancia(p1, p2, datum):
    """Distância geodésica (m), fórmula de Vincenty."""
    a, f, _ = ELIPSOIDES[datum]
    b = a * (1 - f)
    (la1, lo1), (la2, lo2) = p1, p2
    if la1 == la2 and lo1 == lo2:
        return 0.0
    L = math.radians(lo2 - lo1)
    U1 = math.atan((1 - f) * math.tan(math.radians(la1)))
    U2 = math.atan((1 - f) * math.tan(math.radians(la2)))
    sU1, cU1, sU2, cU2 = math.sin(U1), math.cos(U1), math.sin(U2), math.cos(U2)
    lam = L
    for _ in range(200):
        sl, cl = math.sin(lam), math.cos(lam)
        ss = math.sqrt((cU2 * sl) ** 2 + (cU1 * sU2 - sU1 * cU2 * cl) ** 2)
        cs = sU1 * sU2 + cU1 * cU2 * cl
        sig = math.atan2(ss, cs)
        sa = cU1 * cU2 * sl / ss
        c2a = 1 - sa * sa
        c2sm = cs - 2 * sU1 * sU2 / c2a if c2a else 0.0
        C = f / 16 * c2a * (4 + f * (4 - 3 * c2a))
        prev = lam
        lam = L + (1 - C) * f * sa * (sig + C * ss * (c2sm + C * cs * (-1 + 2 * c2sm * c2sm)))
        if abs(lam - prev) < 1e-12:
            break
    u2 = c2a * (a * a - b * b) / (b * b)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    ds = B * ss * (c2sm + B / 4 * (cs * (-1 + 2 * c2sm * c2sm) - B / 6 * c2sm * (-3 + 4 * ss * ss) * (-3 + 4 * c2sm * c2sm)))
    return b * A * (sig - ds)


def segmentos_se_cruzam(pontos):
    """Lista de pares de lados (i, j) que se cruzam, num polígono fechado."""
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])

    def cruza(p1, p2, p3, p4):
        d1, d2, d3, d4 = ccw(p3, p4, p1), ccw(p3, p4, p2), ccw(p1, p2, p3), ccw(p1, p2, p4)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    n = len(pontos)
    xy = [(lo, la) for la, lo in pontos]
    achados = []
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if cruza(xy[i], xy[(i + 1) % n], xy[j], xy[(j + 1) % n]):
                achados.append((i + 1, j + 1))
    return achados


# ---------- leitura da tabela ----------

NOMES = {
    "vertice": ["vertice", "ponto", "id", "nome", "marco", "pt"],
    "lat": ["latitude", "lat"],
    "lon": ["longitude", "lon", "long", "lng"],
    "e": ["e", "este", "easting", "coord e", "coordenada e", "x"],
    "n": ["n", "norte", "northing", "coord n", "coordenada n", "y"],
    "zona": ["zona", "fuso", "zone"],
}


def achar_colunas(cabecalho):
    norm = [sem_acento(c) for c in cabecalho]
    col = {}
    for chave, nomes in NOMES.items():
        for nome in nomes:
            if nome in norm:
                col[chave] = norm.index(nome)
                break
    return col


def ler_tabela(caminho):
    texto = Path(caminho).read_text(encoding="utf-8-sig")
    try:
        dialeto = csv.Sniffer().sniff(texto[:4096], delimiters=";,\t")
    except csv.Error:
        dialeto = csv.excel
        dialeto.delimiter = ";" if texto.count(";") > texto.count(",") else ","
    linhas = [l for l in csv.reader(io.StringIO(texto), dialeto) if any(c.strip() for c in l)]
    return linhas[0], linhas[1:]


def processar(a):
    cab, linhas = ler_tabela(a.tabela)
    col = achar_colunas(cab)
    erros, alertas = [], []

    formato = a.formato
    if formato == "auto":
        if "lat" in col and "lon" in col:
            formato = "geo"
        elif "e" in col and "n" in col:
            formato = "utm"
        else:
            sys.exit(f"Não encontrei colunas de coordenadas no cabeçalho: {cab}. Use --formato e nomes de coluna reconhecidos.")
    elif formato in ("gms", "decimal"):
        formato = "geo"
    if formato == "geo" and not ("lat" in col and "lon" in col):
        # x/y como longitude/latitude
        if "e" in col and "n" in col:
            col["lon"], col["lat"] = col["e"], col["n"]
        else:
            sys.exit("Para coordenadas geográficas, preciso de colunas de latitude e longitude.")

    vertices = []
    formatos_vistos = set()
    for i, l in enumerate(linhas, start=2):
        nome = l[col["vertice"]].strip() if "vertice" in col and col["vertice"] < len(l) else f"V{len(vertices) + 1}"
        try:
            if formato == "geo":
                lat, lat_h, f1 = ler_angulo(l[col["lat"]], "lat")
                lon, lon_h, f2 = ler_angulo(l[col["lon"]], "lon")
                formatos_vistos.update([f1, f2])
                if lon > 0 and not lon_h:
                    lon = -lon
                    alertas.append(f"Linha {i} ({nome}): longitude positiva sem hemisfério; assumida Oeste.")
                if lat > 0 and not lat_h:
                    alertas.append(f"Linha {i} ({nome}): latitude positiva sem hemisfério; assumida Norte. Confira.")
            else:
                e = numero(l[col["e"]])
                n = numero(l[col["n"]])
                zona = int(numero(l[col["zona"]])) if "zona" in col and col["zona"] < len(l) and l[col["zona"]].strip() else a.zona
                if not zona:
                    raise ValueError("zona UTM não informada (use --zona)")
                if not (100000 <= e <= 900000):
                    raise ValueError(f"E = {e} fora da faixa UTM (100.000 a 900.000)")
                if not (0 <= n <= 10000000):
                    raise ValueError(f"N = {n} fora da faixa UTM")
                lat, lon = utm_para_geo(e, n, zona, a.hemisferio, a.datum)
                formatos_vistos.add(f"UTM zona {zona}{a.hemisferio}")
        except (ValueError, IndexError) as ex:
            erros.append(f"Linha {i} ({nome}): {ex}")
            continue
        if not (BRASIL["lat"][0] <= lat <= BRASIL["lat"][1] and BRASIL["lon"][0] <= lon <= BRASIL["lon"][1]):
            erros.append(f"Linha {i} ({nome}): {lat:.6f}, {lon:.6f} fica fora do Brasil.")
            continue
        vertices.append({"vertice": nome, "lat": lat, "lon": lon, "linha": i})

    pontos = [(v["lat"], v["lon"]) for v in vertices]
    resultado = {"datum": a.datum, "epsg": ELIPSOIDES[a.datum][2], "tipo": a.tipo, "formatos": sorted(formatos_vistos)}

    # vértices repetidos
    for k in range(1, len(pontos)):
        if pontos[k] == pontos[k - 1]:
            alertas.append(f"Vértice {vertices[k]['vertice']} repete o anterior.")
    if a.tipo == "poligono" and len(pontos) > 1 and pontos[0] == pontos[-1]:
        vertices.pop()
        pontos.pop()
        alertas.append("Último vértice igual ao primeiro: o polígono já vinha fechado; a repetição foi removida.")

    if a.tipo == "poligono":
        if len(pontos) < 3:
            erros.append(f"Polígono precisa de pelo menos 3 vértices válidos (encontrei {len(pontos)}).")
        else:
            cruz = segmentos_se_cruzam(pontos)
            for i, j in cruz:
                erros.append(f"Lados {i} e {j} se cruzam: o polígono tem autointerseção (ordem dos vértices ou erro de digitação).")
    if len(pontos) >= 2:
        n_lados = len(pontos) if a.tipo == "poligono" else len(pontos) - 1
        lados = [distancia(pontos[k], pontos[(k + 1) % len(pontos)], a.datum) for k in range(n_lados)]
        med = sorted(lados)[len(lados) // 2] if lados else 0
        for k, d in enumerate(lados):
            if med > 0 and d > 5 * med and d > 200:
                alertas.append(f"Lado {k + 1} ({vertices[k]['vertice']} → {vertices[(k + 1) % len(vertices)]['vertice']}) mede {d:,.0f} m, "
                               f"mais de 5 vezes a mediana ({med:,.0f} m). Pode ser erro de digitação.".replace(",", "."))
        resultado["perimetro_m"] = round(sum(lados), 2)
    if a.tipo == "poligono" and len(pontos) >= 3 and not erros:
        area = area_elipsoidal(pontos, a.datum)
        resultado["area_m2"] = round(area, 2)
        resultado["area_ha"] = round(area / 10000, 4)
    resultado["n_vertices"] = len(pontos)
    return vertices, resultado, erros, alertas


def gravar(a, vertices, resultado, erros, alertas):
    tabela = Path(a.tabela)
    saida = Path(a.saida) if a.saida else tabela.parent
    saida.mkdir(parents=True, exist_ok=True)
    base = saida / tabela.stem
    rel = [f"# Validação de coordenadas – {tabela.name}", "",
           f"- Datum declarado: {resultado['datum']} (EPSG:{resultado['epsg']})",
           f"- Formato lido: {', '.join(resultado['formatos']) or '—'}",
           f"- Tipo: {resultado['tipo']}",
           f"- Vértices válidos: {resultado['n_vertices']}"]
    if "area_ha" in resultado:
        rel.append(f"- Área (elipsoidal, cálculo próprio): {resultado['area_ha']:.4f} ha".replace(".", ","))
    if "perimetro_m" in resultado:
        rel.append(f"- Perímetro: {resultado['perimetro_m']:.2f} m".replace(".", ","))
    rel += ["", "## Erros", ""] + ([f"- {e}" for e in erros] or ["- Nenhum."])
    rel += ["", "## Alertas", ""] + ([f"- {x}" for x in alertas] or ["- Nenhum."])
    rel += ["", "A área oficial é a calculada pelo QGIS no projeto do caso. As duas devem coincidir; diferença acima de 0,1% indica problema."]
    Path(f"{base}_validacao.md").write_text("\n".join(rel) + "\n", encoding="utf-8")
    if erros:
        return

    with open(f"{base}_normalizado.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["vertice", "lat_dec", "lon_dec", "lat_gms", "lon_gms", "datum", "epsg", "linha_origem"])
        for v in vertices:
            w.writerow([v["vertice"], f"{v['lat']:.9f}", f"{v['lon']:.9f}", para_gms(v["lat"], "lat", a.casas),
                        para_gms(v["lon"], "lon", a.casas), resultado["datum"], resultado["epsg"], v["linha"]])

    feats = [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [v["lon"], v["lat"]]},
              "properties": {"vertice": v["vertice"], "lat_gms": para_gms(v["lat"], "lat", a.casas), "lon_gms": para_gms(v["lon"], "lon", a.casas)}}
             for v in vertices]
    coords = [[v["lon"], v["lat"]] for v in vertices]
    if resultado["tipo"] == "poligono":
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [coords + [coords[0]]]},
                      "properties": {k: resultado[k] for k in ("area_ha", "perimetro_m", "n_vertices") if k in resultado}})
    elif resultado["tipo"] == "linha":
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": coords},
                      "properties": {k: resultado[k] for k in ("perimetro_m", "n_vertices") if k in resultado}})
    gj = {"type": "FeatureCollection", "name": tabela.stem, "datum": resultado["datum"], "epsg": resultado["epsg"], "features": feats}
    Path(f"{base}.geojson").write_text(json.dumps(gj, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="Valida tabelas de coordenadas e gera vértices e polígono.")
    p.add_argument("tabela")
    p.add_argument("--tipo", default="poligono", choices=["poligono", "pontos", "linha"])
    p.add_argument("--formato", default="auto", choices=["auto", "gms", "decimal", "utm"])
    p.add_argument("--zona", type=int, help="Zona UTM, se a tabela não tiver a coluna (Pará: 21, 22 ou 23)")
    p.add_argument("--hemisferio", default="S", choices=["N", "S"])
    p.add_argument("--datum", default="SIRGAS2000", choices=list(ELIPSOIDES))
    p.add_argument("--saida")
    p.add_argument("--casas", type=int, default=3, help="Casas decimais dos segundos no GMS")
    a = p.parse_args()
    vertices, resultado, erros, alertas = processar(a)
    gravar(a, vertices, resultado, erros, alertas)
    print(json.dumps({"resultado": resultado, "erros": erros, "alertas": alertas}, ensure_ascii=False, indent=1))
    sys.exit(2 if erros else 0)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
