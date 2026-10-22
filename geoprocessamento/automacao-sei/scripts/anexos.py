"""Prepara o pacote de anexos do caso para o SEI, com os nomes e a numeração da minuta.

Uso:
    python anexos.py --pasta "<pasta do caso>" \
        --fonte carta_imagem="<caminho>/carta.pdf" --fonte demonstrativo_car="<caminho>/car.pdf"

    - A lista e a numeração vêm de 05_Documento/anexos.json (gerado por minuta.py).
    - O anexo de chave "geoinformacao" é montado sozinho: zip com todas as camadas (produzidas, bases
      e consultas usadas) em GPKG, SHP e KML, mais um LEIA-ME. Usa o ogr2ogr (vem com o QGIS).
    - Para os demais, informe o arquivo de origem com --fonte chave=caminho. Sem --fonte, o script
      procura em 06_Anexos/fontes/ um arquivo cujo nome comece pela chave (ex.: carta_imagem.pdf).

Saídas em 06_Anexos/:
    Anexo_N_<Chave>.<ext>   cada anexo com o nome final (a versão anterior vai para _anteriores/)
    manifesto.json          lista conferida: número, descrição, arquivo, tamanho, verificação
Código 2 se faltar anexo, se algum arquivo estiver corrompido ou acima do limite do SEI.
"""

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caso  # noqa: E402

LIMITE_MB_PADRAO = 50  # confira o limite de upload configurado no SEI do órgão
EXTENSOES_SEI = {".pdf", ".zip", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".kml", ".kmz", ".odt", ".docx", ".xlsx", ".ods", ".csv", ".txt"}
CHAVE_GEO = "geoinformacao"
SRS_NOMES = {4674: "SIRGAS 2000 (geográficas)", 4326: "WGS 84 (geográficas)", 4618: "SAD69 (geográficas)"}


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def camadas_gpkg(gpkg):
    con = sqlite3.connect(gpkg)
    try:
        linhas = con.execute("SELECT table_name, data_type, srs_id FROM gpkg_contents ORDER BY table_name").fetchall()
        saida = []
        for nome, tipo, srs in linhas:
            n = con.execute(f'SELECT COUNT(*) FROM "{nome}"').fetchone()[0]
            saida.append({"camada": nome, "tipo": tipo, "srs": srs, "feicoes": n})
        return saida
    finally:
        con.close()


def achar_ogr2ogr(indicado):
    if indicado:
        return indicado
    return shutil.which("ogr2ogr")


FORMATOS_VETOR = {".shp", ".gpkg", ".kml", ".geojson", ".json", ".kmz", ".gml", ".tab", ".csv"}


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()[:160]


def montar_geoinformacao(pasta, destino, ficha, ogr2ogr):
    """Zip de Geoinformação nos três formatos (GPKG, SHP e KML) e LEIA-ME. Devolve arquivos e camadas."""
    tmp = pasta / "06_Anexos" / "_montagem_geo"
    if tmp.exists():
        shutil.rmtree(tmp)
    (tmp / "gpkg").mkdir(parents=True)
    incluidos, avisos = [], []
    gpkg_caso = pasta / "03_Geo" / "vetores_produzidos" / "caso.gpkg"
    gpkg_final = tmp / "gpkg" / "geoinformacao.gpkg"

    # bases e consultas usadas (vetores), para entrarem no mesmo pacote
    bases = []
    for sub in ("02_Insumos/vetores_baixados", "02_Insumos/consultas_online"):
        origem = pasta / sub
        if origem.exists():
            bases += [f for f in sorted(origem.rglob("*")) if f.is_file() and f.suffix.lower() in FORMATOS_VETOR]

    if ogr2ogr:
        if gpkg_caso.exists():
            shutil.copy2(gpkg_caso, gpkg_final)
        for f in bases:
            if f.suffix.lower() == ".gpkg":
                ok, msg = rodar([ogr2ogr, "-f", "GPKG", "-update", "-append", "-t_srs", "EPSG:4674", str(gpkg_final), str(f)])
            else:
                ok, msg = rodar([ogr2ogr, "-f", "GPKG", "-update", "-append", "-t_srs", "EPSG:4674",
                                 "-nln", re.sub(r"\W+", "_", f.stem).lower(), str(gpkg_final), str(f)])
            if not ok:
                avisos.append(f"Base {f.name} não entrou no GeoPackage: {msg}")
    elif gpkg_caso.exists():
        shutil.copy2(gpkg_caso, gpkg_final)
        avisos.append("Sem ogr2ogr: só o GeoPackage das camadas produzidas foi incluído; faltam SHP, KML e as bases no GPKG.")

    camadas = camadas_gpkg(gpkg_final) if gpkg_final.exists() else []
    if gpkg_final.exists():
        incluidos.append("gpkg/geoinformacao.gpkg")
    if ogr2ogr:
        (tmp / "shp").mkdir()
        (tmp / "kml").mkdir()
        for c in (c for c in camadas if c["tipo"] == "features"):
            nome = c["camada"]
            ok, msg = rodar([ogr2ogr, "-f", "ESRI Shapefile", str(tmp / "shp" / f"{nome}.shp"), str(gpkg_final), nome, "-lco", "ENCODING=UTF-8"])
            if ok:
                incluidos += [f"shp/{f.name}" for f in sorted((tmp / "shp").glob(f"{nome}.*"))]
            else:
                avisos.append(f"{nome} não convertida para SHP: {msg}")
            ok, msg = rodar([ogr2ogr, "-f", "KML", "-t_srs", "EPSG:4326", str(tmp / "kml" / f"{nome}.kml"), str(gpkg_final), nome])
            if ok:
                incluidos.append(f"kml/{nome}.kml")
            else:
                avisos.append(f"{nome} não convertida para KML: {msg}")
    if not ogr2ogr:
        for f in bases:  # sem conversão, ao menos as bases originais vão no pacote
            alvo = tmp / "bases_originais" / f.name
            alvo.parent.mkdir(exist_ok=True)
            shutil.copy2(f, alvo)
            incluidos.append(f"bases_originais/{f.name}")

    georref = pasta / "03_Geo" / "georreferenciados"
    for f in (sorted(georref.rglob("*")) if georref.exists() else []):
        if f.is_file():
            alvo = tmp / "georreferenciados" / f.relative_to(georref)
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, alvo)
            incluidos.append(f"georreferenciados/{f.relative_to(georref).as_posix()}")

    linhas = [
        f"GEOINFORMAÇÃO – Processo {ficha['nup']}",
        f"Documento: {ficha.get('tipo_documento', '')}",
        f"Preparado em: {agora()}",
        "",
        "FORMATOS",
        "  - gpkg/: GeoPackage com todas as camadas (SIRGAS 2000, EPSG:4674)",
        "  - shp/: cada camada em Shapefile (SIRGAS 2000, EPSG:4674)",
        "  - kml/: cada camada em KML (WGS 84, EPSG:4326, padrão do formato; abre no Google Earth)",
        "",
        "CAMADAS",
    ]
    produzidas = {c["camada"] for c in (camadas_gpkg(gpkg_caso) if gpkg_caso.exists() else [])}
    for c in camadas:
        if c["tipo"] == "features":
            origem = "produzida na análise" if c["camada"] in produzidas else "base ou consulta usada"
            linhas.append(f"  - {c['camada']}: {c['feicoes']} feição(ões), {origem}")
    areas = [a for a in ficha.get("areas", []) if isinstance(a, dict)]
    if areas:
        linhas += ["", "ÁREAS CALCULADAS (QGIS, elipsoide GRS80)"]
        for a in areas:
            ha = f"{a['area_ha']:.4f}".replace(".", ",") if a.get("area_ha") is not None else "—"
            linhas.append(f"  - {a['camada']}: {ha} ha")
    if ficha.get("consultas_online"):
        linhas += ["", "CONSULTAS ONLINE (fonte, data e hora)"] + [f"  - {c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)}" for c in ficha["consultas_online"]]
    if avisos:
        linhas += ["", "AVISOS"] + [f"  - {x}" for x in avisos]
    linhas += ["", "ARQUIVOS"] + [f"  - {x}" for x in incluidos]
    linhas += ["", "Como abrir: QGIS (gratuito) abre os três formatos; o Google Earth abre os arquivos KML."]
    (tmp / "LEIA-ME.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(tmp.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(tmp).as_posix())
    shutil.rmtree(tmp)
    return ["LEIA-ME.txt"] + incluidos, camadas, avisos


def verificar(arquivo, limite_mb):
    problemas = []
    tam = arquivo.stat().st_size / 1024 / 1024
    if tam > limite_mb:
        problemas.append(f"{tam:.1f} MB, acima do limite de {limite_mb} MB")
    if arquivo.suffix.lower() not in EXTENSOES_SEI:
        problemas.append(f"extensão {arquivo.suffix} pode não ser aceita no SEI (prefira PDF ou ZIP)")
    if arquivo.suffix.lower() == ".pdf" and not arquivo.read_bytes()[:5] == b"%PDF-":
        problemas.append("não é um PDF válido")
    if arquivo.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(arquivo) as z:
                ruim = z.testzip()
                if ruim:
                    problemas.append(f"zip corrompido em {ruim}")
        except zipfile.BadZipFile:
            problemas.append("zip corrompido")
    if tam == 0:
        problemas.append("arquivo vazio")
    return round(tam, 2), problemas


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pacote de anexos do caso para o SEI.")
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--fonte", action="append", default=[], help="chave=caminho do arquivo de origem")
    ap.add_argument("--limite-mb", type=float, default=LIMITE_MB_PADRAO)
    ap.add_argument("--ogr2ogr", help="Caminho do ogr2ogr (padrão: o do PATH; no Windows, o da pasta bin do QGIS)")
    a = ap.parse_args(argv)

    pasta = Path(a.pasta)
    anexos_json = pasta / "05_Documento" / "anexos.json"
    if not anexos_json.exists():
        sys.exit("05_Documento/anexos.json não existe. Gere a minuta antes (minuta.py).")
    anexos = json.loads(anexos_json.read_text(encoding="utf-8"))
    ficha_json = pasta / "00_Ficha" / "ficha.json"
    ficha = json.loads(ficha_json.read_text(encoding="utf-8"))
    fontes = dict(f.split("=", 1) for f in a.fonte)
    pasta_anexos = pasta / "06_Anexos"
    pasta_fontes = pasta_anexos / "fontes"
    pasta_fontes.mkdir(parents=True, exist_ok=True)
    anteriores = pasta_anexos / "_anteriores" / datetime.now().strftime("%Y%m%d_%H%M%S")
    ogr2ogr = achar_ogr2ogr(a.ogr2ogr)

    manifesto, faltando, com_problema = [], [], []
    for an in anexos:
        chave, n = an["chave"], an["numero"]
        base = an["arquivo_sugerido"]

        def guardar_anterior(numero=n):
            # a versão anterior do anexo vai para _anteriores/, só quando a nova vai ser gravada
            for velho in pasta_anexos.glob(f"Anexo_{numero}_*"):
                if velho.is_file():
                    anteriores.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(velho), anteriores / velho.name)

        item = {"numero": n, "chave": chave, "descricao": an["descricao"]}
        if chave == CHAVE_GEO:
            destino = pasta_anexos / f"{base}.zip"
            guardar_anterior()
            conteudo, camadas, avisos = montar_geoinformacao(pasta, destino, ficha, ogr2ogr)
            item["conteudo_zip"] = conteudo
            item["formatos"] = ["gpkg", "shp", "kml"] if ogr2ogr else ["gpkg"]
            item["avisos"] = avisos
        else:
            origem = fontes.get(chave)
            if not origem:
                candidatos = sorted(pasta_fontes.glob(f"{chave}*"))
                origem = str(candidatos[0]) if candidatos else None
            if not origem or not Path(origem).exists():
                faltando.append(f"Anexo {n} ({an['descricao']}): informe --fonte {chave}=<arquivo> ou coloque o arquivo em 06_Anexos/fontes/{chave}.pdf")
                manifesto.append(item | {"arquivo": None, "situacao": "faltando"})
                continue
            destino = pasta_anexos / f"{base}{Path(origem).suffix.lower()}"
            guardar_anterior()
            shutil.copy2(origem, destino)
            item["origem"] = str(origem)
        tam, problemas = verificar(destino, a.limite_mb)
        item |= {"arquivo": destino.name, "tamanho_mb": tam, "problemas": problemas, "situacao": "pronto" if not problemas else "com problema"}
        if problemas:
            com_problema.append(f"Anexo {n} ({destino.name}): {'; '.join(problemas)}")
        manifesto.append(item)

    extras = [f.name for f in pasta_anexos.glob("Anexo_*") if f.is_file() and not any(m.get("arquivo") == f.name for m in manifesto)]
    resultado = {"pasta": str(pasta_anexos), "em": agora(), "anexos": manifesto, "faltando": faltando,
                 "com_problema": com_problema, "arquivos_sem_citacao": extras,
                 "total_mb": round(sum(m.get("tamanho_mb", 0) for m in manifesto), 2)}
    (pasta_anexos / "manifesto.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    situacao = "concluida" if not faltando and not com_problema else "em_andamento"
    ficha = json.loads(ficha_json.read_text(encoding="utf-8"))
    ficha["anexos"] = [f"Anexo {m['numero']} – {m['descricao']} ({m.get('arquivo') or 'FALTANDO'})" for m in manifesto]
    ficha["etapas"]["anexos"] = {"situacao": situacao, "em": agora()}
    ficha_json.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
    caso.gravar_ficha_md(pasta, ficha)
    caso.registrar_linha(pasta, "anexos", f"{len(manifesto) - len(faltando)} de {len(manifesto)} anexos prontos ({resultado['total_mb']} MB); "
                                          f"{len(faltando)} faltando, {len(com_problema)} com problema.")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    sys.exit(2 if faltando or com_problema else 0)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
