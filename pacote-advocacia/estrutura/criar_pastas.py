#!/usr/bin/env python3
"""Cria a árvore padrão de pastas de um cliente ou processo.

Exemplos:
    python criar_pastas.py --base ~/Clientes --cliente "Cliente Fictício" --processo 0000000-00.0000.0.00.0000 --dry-run
    python criar_pastas.py --base ~/Clientes --cliente "Cliente Fictício"
"""
import argparse
import re
from datetime import date
from pathlib import Path

SUBPASTAS = [
    "00 Documentação do cliente",
    "01 Entrada",
    "02 Autos e peças recebidas",
    "03 Análise",
    "04 Minutas",
    "05 Protocolados",
    "06 Prazos e comunicações",
]


def nome_seguro(texto: str) -> str:
    """Remove caracteres proibidos em nomes de pasta no Windows e no macOS/Linux."""
    return re.sub(r'[\\/:*?"<>|]+', " ", texto).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria a estrutura padrão de pastas do escritório.")
    parser.add_argument("--base", required=True, type=Path, help="Pasta raiz 'Clientes'")
    parser.add_argument("--cliente", required=True, help="Nome do cliente")
    parser.add_argument("--processo", help="Número CNJ. Se omitido, usa 'consultivo-AAAA-MM-DD'")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que seria criado, sem criar")
    args = parser.parse_args()

    processo = args.processo or f"consultivo-{date.today().isoformat()}"
    destino = args.base.expanduser() / nome_seguro(args.cliente) / nome_seguro(processo)

    for sub in SUBPASTAS:
        caminho = destino / sub
        if args.dry_run:
            print(caminho)
        else:
            caminho.mkdir(parents=True, exist_ok=True)

    acao = "Simulação, nada criado" if args.dry_run else "Estrutura criada"
    print(f"{acao}: {destino}")


if __name__ == "__main__":
    main()
