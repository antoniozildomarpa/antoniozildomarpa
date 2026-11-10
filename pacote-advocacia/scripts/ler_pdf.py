#!/usr/bin/env python3
"""Lê PDFs de processo localmente e gera um índice por página, para o Claude ler só o necessário.

Tudo roda no computador: texto nativo pelo PyMuPDF e OCR (RapidOCR) nas páginas escaneadas.
Nada é enviado a serviço externo.

Uso:
    python ler_pdf.py <arquivo.pdf | pasta> --out <pasta_saida> [--paginas 1-20] [--sem-ocr]

Saída, por PDF:
    <saida>/<nome>/indice.json    um registro por página (tipo provável, nº CNJ, datas, prazos)
    <saida>/<nome>/pNNN.txt       texto de cada página
O texto não é impresso na tela; só o resumo.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pymupdf

MIN_CHARS = 40

# A primeira regra que bater define o tipo provável da página.
TIPOS = [
    ("intimacao", r"\bINTIMA[ÇC][AÃ]O\b|\bFICA\s+INTIMAD"),
    ("citacao", r"\bCITA[ÇC][AÃ]O\b|\bMANDADO\s+DE\s+CITA"),
    ("sentenca", r"\bSENTEN[ÇC]A\b|JULGO\s+(PROCEDENTE|IMPROCEDENTE|EXTINTO)"),
    ("acordao", r"\bAC[ÓO]RD[ÃA]O\b|\bEMENTA\b"),
    ("decisao", r"\bDECIS[ÃA]O\b|\bDEFIRO\b|\bINDEFIRO\b"),
    ("despacho", r"\bDESPACHO\b|\bINTIME-SE\b|\bCUMPRA-SE\b"),
    ("audiencia_pericia", r"\bAUDI[ÊE]NCIA\b|\bPER[ÍI]CIA\b"),
    ("exigencia_inss", r"EXIG[ÊE]NCIA|CARTA\s+DE\s+EXIG|MEU\s*INSS|INSTITUTO\s+NACIONAL\s+DO\s+SEGURO"),
    ("regime_proprio", r"IPASET|INSTITUTO\s+DE\s+PREVID[ÊE]NCIA\s+DOS\s+SERVIDORES|PORTARIA\s+N"),
    ("cnis_contracheque", r"\bCNIS\b|CONTRACHEQUE|HOLERITE|FICHA\s+FINANCEIRA|REMUNERA[ÇC][ÕO]ES"),
    ("laudo_medico", r"\bLAUDO\b|\bATESTADO\b|\bCID\b"),
    ("procuracao_contrato", r"\bPROCURA[ÇC][ÃA]O\b|HONOR[ÁA]RIOS|CONTRATO\s+DE\s+PRESTA"),
    ("peticao", r"EXCELENT[ÍI]SSIM|MERIT[ÍI]SSIM|ILUSTR[ÍI]SSIM|REQUER\s+(A\s+)?V"),
    ("documento_pessoal", r"REGISTRO\s+GERAL|CARTEIRA\s+DE\s+IDENTIDADE|\bCPF\b|CERTID[ÃA]O\s+DE"),
]
TIPOS = [(t, re.compile(r, re.I)) for t, r in TIPOS]
CNJ = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")
DATA = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
PRAZO = re.compile(r"prazo\s+(?:legal\s+)?de\s+(\d{1,3})\s*(?:\([^)]*\)\s*)?(dias?\s+[úu]teis|dias?\s+corridos|dias?|horas?)", re.I)


def faixa(spec, total):
    if not spec:
        return list(range(1, total + 1))
    paginas = set()
    for parte in spec.split(","):
        if "-" in parte:
            a, b = parte.split("-")
            paginas.update(range(int(a), int(b) + 1))
        else:
            paginas.add(int(parte))
    return sorted(p for p in paginas if 1 <= p <= total)


_ocr = None


def ocr_pagina(pg):
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    res, _ = _ocr(pg.get_pixmap(dpi=200).tobytes("png"))
    if not res:
        return ""
    linhas = sorted(res, key=lambda x: (round(x[0][0][1] / 15), x[0][0][0]))
    return "\n".join(x[1] for x in linhas)


def processar(pdf: Path, saida: Path, paginas_spec, usar_ocr):
    destino = saida / pdf.stem
    destino.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    registros = []
    for n in faixa(paginas_spec, doc.page_count):
        pg = doc[n - 1]
        texto = pg.get_text()
        metodo = "texto"
        if len(texto.strip()) < MIN_CHARS and usar_ocr:
            try:
                texto = ocr_pagina(pg)
                metodo = "ocr"
            except Exception as e:  # OCR indisponível não impede o resto
                metodo = f"sem_ocr ({type(e).__name__})"
        (destino / f"p{n:03d}.txt").write_text(texto, encoding="utf-8")
        tipo = "sem_texto" if len(texto.strip()) < MIN_CHARS else "outro"
        for nome, rx in TIPOS:
            if rx.search(texto):
                tipo = nome
                break
        registros.append({
            "pagina": n,
            "tipo_provavel": tipo,
            "metodo": metodo,
            "caracteres": len(texto.strip()),
            "numeros_cnj": sorted(set(CNJ.findall(texto))),
            "datas": sorted(set(DATA.findall(texto)))[:10],
            "prazos_citados": [" ".join(m) for m in PRAZO.findall(texto)],
        })
    contagem = {}
    for r in registros:
        contagem[r["tipo_provavel"]] = contagem.get(r["tipo_provavel"], 0) + 1
    indice = {
        "pdf": str(pdf),
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "paginas_total": doc.page_count,
        "paginas_lidas": len(registros),
        "contagem_por_tipo": contagem,
        "paginas_com_prazo": [r["pagina"] for r in registros if r["prazos_citados"]],
        "numeros_cnj": sorted({c for r in registros for c in r["numeros_cnj"]}),
        "paginas": registros,
    }
    (destino / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {pdf.name}: {len(registros)} pág. | tipos: {contagem} | "
          f"com prazo: {indice['paginas_com_prazo'] or 'nenhuma'} | índice: {destino / 'indice.json'}")


def main():
    ap = argparse.ArgumentParser(description="Índice local de PDFs de processo.")
    ap.add_argument("entrada", help="arquivo PDF ou pasta com PDFs")
    ap.add_argument("--out", required=True, help="pasta de saída")
    ap.add_argument("--paginas", help="ex.: 1-20,35")
    ap.add_argument("--sem-ocr", action="store_true", help="não fazer OCR nas páginas escaneadas")
    args = ap.parse_args()

    entrada = Path(args.entrada)
    pdfs = sorted(entrada.glob("*.pdf")) if entrada.is_dir() else [entrada]
    if not pdfs:
        print("Nenhum PDF encontrado.", file=sys.stderr)
        return 1
    erros = 0
    for pdf in pdfs:
        try:
            processar(pdf, Path(args.out), args.paginas, not args.sem_ocr)
        except Exception as e:
            print(f"ERRO {pdf.name}: {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
            erros += 1
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
