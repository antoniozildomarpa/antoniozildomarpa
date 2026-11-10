#!/usr/bin/env python3
"""Junta todas as ficha-cliente.md da pasta Clientes numa planilha única (cadastro geral).

    python consolidar_cadastro.py --clientes "<pasta Clientes>" [--saida "<arquivo.xlsx>"]

Lê as linhas "- Campo: valor" das seções Qualificação, Contato e Documentos de praxe, conta os casos
e quantos [CONFIRMAR] e [DECIDIR] ainda estão abertos em cada ficha. Não altera nenhuma ficha.
Padrão de saída: <Clientes>/_cadastro/clientes-AAAA-MM-DD.xlsx (e .csv), sem sobrescrever.
Pastas com SIGILOSO.txt entram só com o nome e a marca "sigiloso".
"""
import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

CAMPOS = ["Nome completo", "Nacionalidade", "Estado civil", "Profissão", "Data de nascimento", "Filiação",
          "RG e órgão emissor", "CPF", "NIS/PIS/NIT", "Matrícula (servidor)",
          "Endereço", "CEP", "Município/UF", "Telefone", "E-mail"]
PRAXE = ["Procuração", "Contrato de honorários", "Declaração de hipossuficiência", "RG/CNH",
         "Comprovante de residência"]
LINHA = re.compile(r"^-\s+([^:]{2,40}):\s*(.*)$")
FONTE = re.compile(r"\s*\(fonte:[^)]*\)")


def secoes(texto):
    atual, out = "", {}
    for l in texto.splitlines():
        if l.startswith("## "):
            atual = l[3:].strip()
            out[atual] = []
        elif atual:
            out[atual].append(l)
    return out


def limpar(v):
    v = FONTE.sub("", v).strip()
    return "" if v in ("[CONFIRMAR]", "") else v


def ler_ficha(f: Path, raiz: Path):
    t = re.sub(r"<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S)
    s = secoes(t)
    rel = f.parent.relative_to(raiz).parts
    linha = {"Área": rel[0] if rel else "", "Pasta": f.parent.name}
    valores = {}
    for sec in ("Qualificação", "Contato", "Documentos de praxe"):
        for l in s.get(sec, []):
            m = LINHA.match(l.strip())
            if m:
                chave = m.group(1).strip()
                if sec == "Documentos de praxe":
                    chave = "Doc: " + chave
                valores.setdefault(chave, m.group(2).strip())
    for c in CAMPOS:
        linha[c] = limpar(valores.get(c, ""))
    for c in PRAXE:
        linha["Doc: " + c] = limpar(valores.get("Doc: " + c, ""))
    casos = [l for l in s.get("Casos", []) if l.strip().startswith("- ") and "[CONFIRMAR]" != l.strip()[2:].strip()]
    linha["Casos"] = len(casos)
    linha["Processos"] = "; ".join(sorted(set(re.findall(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", "\n".join(casos)))))
    linha["A confirmar"] = t.count("[CONFIRMAR]")
    linha["A decidir"] = t.count("[DECIDIR]")
    m = re.search(r"Situação da ficha:\s*(.+)", t)
    linha["Situação da ficha"] = m.group(1).strip() if m else ""
    linha["Ficha"] = str(f)
    return linha


def main() -> int:
    ap = argparse.ArgumentParser(description="Cadastro geral a partir das fichas.")
    ap.add_argument("--clientes", required=True, type=Path)
    ap.add_argument("--saida", type=Path)
    args = ap.parse_args()
    raiz = args.clientes.resolve()
    linhas = []
    for area in sorted(p for p in raiz.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        for cli in sorted(p for p in area.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
            if any(n.lower() == "sigiloso.txt" for n in (x.name for x in cli.iterdir())):
                linhas.append({"Área": area.name, "Pasta": cli.name, "Situação da ficha": "sigiloso"})
                continue
            f = cli / "ficha-cliente.md"
            linhas.append(ler_ficha(f, raiz) if f.exists() else
                          {"Área": area.name, "Pasta": cli.name, "Situação da ficha": "sem ficha"})
    if not linhas:
        print("Nenhuma pasta Área/Cliente encontrada.")
        return 1
    cols = ["Área", "Pasta"] + CAMPOS + ["Doc: " + c for c in PRAXE] + \
           ["Casos", "Processos", "A confirmar", "A decidir", "Situação da ficha", "Ficha"]
    saida = args.saida or raiz / "_cadastro" / f"clientes-{date.today().isoformat()}.xlsx"
    saida.parent.mkdir(parents=True, exist_ok=True)
    base, k = saida, 2
    while saida.exists():
        saida = base.with_name(f"{base.stem}-{k}{base.suffix}")
        k += 1
    with open(saida.with_suffix(".csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        wb = Workbook()
        ws = wb.active
        ws.title = "Clientes"
        ws.append(cols)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="171E44")
        for l in linhas:
            ws.append([l.get(c, "") for c in cols])
        ws.freeze_panes = "C2"
        ws.auto_filter.ref = ws.dimensions
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = min(40, max(10, *(len(str(c.value or "")) for c in col[:50])))
        wb.save(saida)
    except ImportError:
        print("openpyxl ausente: só o CSV foi gerado.")
    com = sum(1 for l in linhas if l.get("Situação da ficha") not in ("sem ficha", "sigiloso"))
    print(f"{len(linhas)} pastas de cliente · {com} com ficha · planilha: {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
