#!/usr/bin/env python3
"""Mapeia só os NOMES das pastas e arquivos de clientes e propõe um cadastro para aprovação.

Não abre nenhum documento (a advogada autorizou ler apenas nomes, questão 12). Não move,
não renomeia e não apaga nada.

Etapa 1, propor:
    python mapear_pastas.py propor --raiz "<pasta com as áreas>" --saida cadastro-proposto.csv

    Gera uma linha por pasta de cliente (segundo nível: Área/Cliente), com os números de processo
    (CNJ) e de requerimento do INSS encontrados nos nomes das subpastas e arquivos. A coluna
    "aprovar" fica em branco para a advogada ou uma colaboradora marcar "sim".

Etapa 2, aplicar o que foi aprovado:
    python mapear_pastas.py aplicar --csv cadastro-proposto.csv

    Para cada linha com aprovar = sim, cria a ficha-cliente.md na pasta do cliente, se ainda não
    existir, e gera clientes.csv (cadastro geral) ao lado do CSV.
"""
import argparse
import csv
import os
import re
import sys
from datetime import date
from pathlib import Path

CNJ = re.compile(r"\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}")
INSS = re.compile(r"(?:INSS|NB|benef[íi]cio|requerimento)[\s_-]*(?:n[ºo°.]?\s*)?(\d{9,10})", re.I)
CAMPOS = ["aprovar", "area", "cliente", "caminho", "n_subpastas", "n_arquivos",
          "processos_cnj", "requerimentos_inss", "tem_ficha", "sigiloso", "observacao"]


def nomes(pasta: Path, limite=2000):
    """Nomes de tudo abaixo da pasta, até 'limite' itens. Só nomes, sem abrir arquivos."""
    saida, n_dir, n_arq = [], 0, 0
    for raiz, dirs, arqs in os.walk(pasta):
        n_dir += len(dirs)
        n_arq += len(arqs)
        saida += dirs + arqs
        if len(saida) > limite:
            break
    return saida, n_dir, n_arq


def normaliza_cnj(s):
    d = re.sub(r"\D", "", s)
    return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:20]}" if len(d) == 20 else s


def propor(raiz: Path, saida: Path):
    linhas = []
    for area in sorted(p for p in raiz.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
        for cliente in sorted(p for p in area.iterdir() if p.is_dir()):
            sigiloso = any(Path(r, "SIGILOSO.txt").exists() for r, _, _ in os.walk(cliente))
            itens, n_dir, n_arq = nomes(cliente)
            texto = " ".join(itens)
            linhas.append({
                "aprovar": "",
                "area": area.name,
                "cliente": cliente.name,
                "caminho": str(cliente),
                "n_subpastas": n_dir,
                "n_arquivos": n_arq,
                "processos_cnj": "; ".join(sorted({normaliza_cnj(x) for x in CNJ.findall(texto)})),
                "requerimentos_inss": "; ".join(sorted(set(INSS.findall(texto)))),
                "tem_ficha": "sim" if (cliente / "ficha-cliente.md").exists() else "não",
                "sigiloso": "sim" if sigiloso else "não",
                "observacao": "",
            })
    with open(saida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        w.writeheader()
        w.writerows(linhas)
    print(f"{len(linhas)} cliente(s) propostos em {saida}. Marque 'sim' na coluna aprovar e rode a etapa aplicar.")


FICHA = """# Ficha do cliente: {cliente}

Área: {area}
Criada em: {hoje} (cadastro a partir dos nomes das pastas)

## Dados pessoais
- Nome completo: [CONFIRMAR]
- CPF: [CONFIRMAR]
- Contato: [CONFIRMAR]

## Casos
{casos}

## Atendimentos
"""


def aplicar(caminho_csv: Path):
    with open(caminho_csv, encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    aprovadas = [l for l in linhas if l["aprovar"].strip().lower() in ("sim", "s", "x")]
    criadas = 0
    for l in aprovadas:
        pasta = Path(l["caminho"])
        if l["sigiloso"] == "sim":
            print(f"ignorado (sigiloso): {l['cliente']}")
            continue
        ficha = pasta / "ficha-cliente.md"
        if ficha.exists() or not pasta.is_dir():
            continue
        casos = [c for c in (l["processos_cnj"] + "; " + l["requerimentos_inss"]).split("; ") if c.strip()]
        ficha.write_text(FICHA.format(cliente=l["cliente"], area=l["area"], hoje=date.today().isoformat(),
                                      casos="\n".join(f"- {c}" for c in casos) or "- [CONFIRMAR]"),
                         encoding="utf-8")
        criadas += 1
    cadastro = caminho_csv.with_name("clientes.csv")
    with open(cadastro, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS[1:], delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(aprovadas)
    print(f"{len(aprovadas)} aprovado(s), {criadas} ficha(s) criada(s). Cadastro geral: {cadastro}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Cadastro de clientes a partir dos nomes das pastas.")
    sub = ap.add_subparsers(dest="etapa", required=True)
    p1 = sub.add_parser("propor")
    p1.add_argument("--raiz", required=True, type=Path)
    p1.add_argument("--saida", required=True, type=Path)
    p2 = sub.add_parser("aplicar")
    p2.add_argument("--csv", required=True, type=Path)
    args = ap.parse_args()
    if args.etapa == "propor":
        if args.saida.exists():
            print(f"ERRO: {args.saida} já existe; escolha outro nome.", file=sys.stderr)
            return 1
        propor(args.raiz, args.saida)
    else:
        aplicar(args.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
