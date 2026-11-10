#!/usr/bin/env python3
"""Lança honorários de um contrato numa planilha Excel de controle (cria a planilha se não existir).

A planilha definitiva (Google Sheets ou Excel) depende do bloco G do questionário. Até lá,
este script usa um .xlsx local, que pode ser importado depois.

Uso:
    python lancar_honorario.py --planilha "<Financeiro>/Controle_Honorarios.xlsx" \
        --cliente "Cliente Fictício" --area "Consumidor" --caso "0000000-00.0000.8.14.0000" \
        --tipo fixo --valor 3000 --parcelas 3 --primeiro-vencimento 2026-12-10 \
        --contrato "caminho/do/contrato.docx"

Tipos: fixo, exito, misto. Para êxito, informe --percentual (ex.: 30) e deixe --valor vazio.
Nunca apaga nem altera linhas existentes: só acrescenta.
"""
import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

CABECALHO = ["Lançado em", "Cliente", "Área", "Caso", "Tipo", "Valor total (R$)", "Percentual de êxito (%)",
             "Parcela", "Valor da parcela (R$)", "Vencimento", "Status", "Contrato", "Observação"]


def somar_meses(d: date, n: int) -> date:
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    from calendar import monthrange
    return date(a, m, min(d.day, monthrange(a, m)[1]))


def main() -> int:
    ap = argparse.ArgumentParser(description="Lançar honorários na planilha de controle.")
    ap.add_argument("--planilha", required=True, type=Path)
    ap.add_argument("--cliente", required=True)
    ap.add_argument("--area", default="")
    ap.add_argument("--caso", default="")
    ap.add_argument("--tipo", required=True, choices=["fixo", "exito", "misto"])
    ap.add_argument("--valor", type=float, help="valor fixo total")
    ap.add_argument("--percentual", type=float, help="percentual de êxito")
    ap.add_argument("--parcelas", type=int, default=1)
    ap.add_argument("--primeiro-vencimento", help="AAAA-MM-DD")
    ap.add_argument("--contrato", default="")
    ap.add_argument("--obs", default="")
    args = ap.parse_args()

    if args.tipo in ("fixo", "misto") and args.valor is None:
        ap.error("informe --valor para honorários fixos ou mistos")
    if args.tipo in ("exito", "misto") and args.percentual is None:
        ap.error("informe --percentual para honorários de êxito ou mistos")

    if args.planilha.exists():
        wb = load_workbook(args.planilha)
        ws = wb["Honorários"] if "Honorários" in wb.sheetnames else wb.active
    else:
        args.planilha.parent.mkdir(parents=True, exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.title = "Honorários"
        ws.append(CABECALHO)
        for c in ws[1]:
            c.font = Font(bold=True)
        ws.freeze_panes = "A2"

    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    venc0 = date.fromisoformat(args.primeiro_vencimento) if args.primeiro_vencimento else None
    novas = 0
    if args.valor is not None:
        parcela = round(args.valor / args.parcelas, 2)
        for i in range(args.parcelas):
            valor_i = parcela if i < args.parcelas - 1 else round(args.valor - parcela * (args.parcelas - 1), 2)
            venc = somar_meses(venc0, i).isoformat() if venc0 else "[CONFIRMAR]"
            ws.append([agora, args.cliente, args.area, args.caso, args.tipo, args.valor, args.percentual,
                       f"{i + 1}/{args.parcelas}", valor_i, venc, "a receber", args.contrato, args.obs])
            novas += 1
    if args.tipo in ("exito", "misto"):
        ws.append([agora, args.cliente, args.area, args.caso, "êxito", None, args.percentual,
                   "êxito", None, "ao final do caso", "condicional", args.contrato, args.obs])
        novas += 1
    wb.save(args.planilha)
    print(f"OK: {novas} linha(s) acrescentada(s) em {args.planilha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
