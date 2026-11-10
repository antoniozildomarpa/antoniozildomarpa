"""Acrescenta um prazo à lista que o painel do escritório mostra (Clientes/_painel/prazos.csv).

Chamado pela skill agenda-prazos depois de lançar o evento no Google Agenda. Só acrescenta:
não apaga nem altera linhas existentes. Se já houver linha com a mesma data, cliente, processo e descrição,
não faz nada.

Uso:
  python scripts/registrar_prazo.py --data 2026-11-20 --tipo Prazo --cliente "Nome" --processo "0000000-00.0000.0.00.0000"
      --descricao "Réplica à contestação" --fonte "intimação de 05/11, pág. 2" [--hora 09:00] [--clientes <pasta>]
"""
import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

CAMPOS = ["data", "hora", "tipo", "cliente", "processo", "descricao", "fonte", "conferido"]
RAIZ = Path(__file__).resolve().parent.parent


def pasta_clientes(arg):
    if arg:
        return Path(arg)
    local = RAIZ / "escritorio.local.md"
    if local.exists():
        m = re.search(r"Pasta Clientes: `(.+?)`", local.read_text(encoding="utf-8"))
        if m:
            return Path(m.group(1))
    sys.exit("Pasta Clientes não encontrada: informe --clientes ou rode o instalador.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="AAAA-MM-DD")
    ap.add_argument("--hora", default="")
    ap.add_argument("--tipo", required=True, help="Prazo, Audiência, Perícia, Exigência INSS, Ação...")
    ap.add_argument("--cliente", required=True)
    ap.add_argument("--processo", default="")
    ap.add_argument("--descricao", required=True)
    ap.add_argument("--fonte", required=True, help="documento e página de onde saiu o prazo")
    ap.add_argument("--clientes", help="pasta Clientes (padrão: a do escritorio.local.md)")
    a = ap.parse_args()

    try:
        date.fromisoformat(a.data)
    except ValueError:
        sys.exit(f"Data '{a.data}' fora do formato AAAA-MM-DD (ex.: 2026-11-25).")
    if a.hora and not re.fullmatch(r"\d{2}:\d{2}", a.hora):
        sys.exit("Hora no formato HH:MM.")

    arq = pasta_clientes(a.clientes) / "_painel" / "prazos.csv"
    arq.parent.mkdir(parents=True, exist_ok=True)
    linhas = []
    if arq.exists():
        with open(arq, encoding="utf-8-sig") as fh:
            linhas = list(csv.DictReader(fh, delimiter=";"))
    chave = lambda l: (l.get("data", ""), l.get("cliente", "").strip().lower(),
                       l.get("processo", "").strip(), l.get("descricao", "").strip().lower())
    nova = {"data": a.data, "hora": a.hora, "tipo": a.tipo, "cliente": a.cliente.strip(), "processo": a.processo.strip(),
            "descricao": a.descricao.strip(), "fonte": a.fonte.strip(), "conferido": ""}
    if any(chave(l) == chave(nova) for l in linhas):
        print("Já estava na lista do painel.")
        return
    novo_arquivo = not arq.exists()
    with open(arq, "a", newline="", encoding="utf-8-sig" if novo_arquivo else "utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS, delimiter=";")
        if novo_arquivo:
            w.writeheader()
        w.writerow(nova)
    print(f"Prazo acrescentado ao painel: {a.data} · {a.descricao} · {a.cliente}")


if __name__ == "__main__":
    main()
