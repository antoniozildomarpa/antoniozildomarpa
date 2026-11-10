#!/usr/bin/env python3
"""Converte Word, Excel, PowerPoint e HTML para Markdown, localmente (MarkItDown).

Nada é enviado a serviço externo. O texto convertido não é impresso; o script só informa
o caminho e o tamanho de cada arquivo gerado.

Uso:
    python converter_docs.py <arquivo> [<arquivo> ...] --out <pasta>
"""
import argparse
import sys
from pathlib import Path

from markitdown import MarkItDown


def main() -> int:
    ap = argparse.ArgumentParser(description="Converter documentos para Markdown (local).")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    saida = Path(args.out)
    saida.mkdir(parents=True, exist_ok=True)
    conversor = MarkItDown()
    erros = 0
    for caminho in args.arquivos:
        origem = Path(caminho)
        if not origem.is_file():
            print(f"ERRO não encontrado: {origem}", file=sys.stderr)
            erros += 1
            continue
        try:
            texto = conversor.convert(str(origem)).text_content
        except Exception as e:
            print(f"ERRO {origem.name}: {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
            erros += 1
            continue
        destino = saida / (origem.name + ".md")
        destino.write_text(texto, encoding="utf-8")
        print(f"OK {origem.name} -> {destino} ({len(texto)} caracteres)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
