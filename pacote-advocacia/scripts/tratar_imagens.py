#!/usr/bin/env python3
"""Transforma fotos e digitalizações de documentos num PDF legível e leve, para juntar no PJe ou no INSS.

Para cada imagem: corrige a rotação da foto, ajusta brilho e contraste, opcionalmente passa para
tons de cinza, reduz a resolução para o tamanho de uma folha A4 a 200 dpi e junta tudo num PDF.
Se o PDF passar do limite, reduz a qualidade e a resolução até caber. Tudo local.

Uso:
    python tratar_imagens.py <imagem|pasta> [<imagem> ...] --saida <arquivo.pdf> [--limite-mb 5] [--cinza]

Os originais nunca são alterados. Os limites de tamanho do PJe do TJPA e do Meu INSS devem ser
conferidos no portal antes do primeiro uso [VERIFICAR]; o padrão aqui é 5 MB por arquivo.
"""
import argparse
import io
import sys
from pathlib import Path

import img2pdf
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat

try:  # fotos de iPhone (HEIC)
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
LADO_MAIOR_A4_200DPI = 2339


def coletar(entradas):
    arquivos = []
    for e in entradas:
        p = Path(e)
        if p.is_dir():
            arquivos += sorted(x for x in p.iterdir() if x.suffix.lower() in EXTENSOES)
        elif p.suffix.lower() in EXTENSOES:
            arquivos.append(p)
    return arquivos


def tratar(caminho: Path, cinza: bool) -> Image.Image:
    im = Image.open(caminho)
    im = ImageOps.exif_transpose(im)
    im = im.convert("L" if cinza else "RGB")
    im = ImageOps.autocontrast(im, cutoff=1)
    media = ImageStat.Stat(im.convert("L")).mean[0]
    if media < 120:  # foto escura: clareia
        im = ImageEnhance.Brightness(im).enhance(min(1.6, 140 / max(media, 1)))
    im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=60, threshold=3))
    return im


def redimensionar(im: Image.Image, lado_maior: int) -> Image.Image:
    escala = lado_maior / max(im.size)
    if escala < 1:
        im = im.resize((round(im.width * escala), round(im.height * escala)), Image.LANCZOS)
    return im


def montar_pdf(imagens, qualidade, lado_maior):
    paginas = []
    for im in imagens:
        buf = io.BytesIO()
        redimensionar(im, lado_maior).save(buf, "JPEG", quality=qualidade, optimize=True, dpi=(200, 200))
        paginas.append(buf.getvalue())
    a4 = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
    layout = img2pdf.get_layout_fun(a4, fit=img2pdf.FitMode.into)
    return img2pdf.convert(paginas, layout_fun=layout)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fotos de documentos -> PDF legível e leve.")
    ap.add_argument("entradas", nargs="+", help="imagens ou pastas (a ordem define a ordem das páginas)")
    ap.add_argument("--saida", required=True, help="arquivo PDF a gerar")
    ap.add_argument("--limite-mb", type=float, default=5.0)
    ap.add_argument("--cinza", action="store_true", help="tons de cinza (arquivo menor)")
    args = ap.parse_args()

    arquivos = coletar(args.entradas)
    if not arquivos:
        print("Nenhuma imagem encontrada.", file=sys.stderr)
        return 1
    saida = Path(args.saida)
    if saida.exists():
        print(f"ERRO: {saida} já existe. Escolha outro nome (os arquivos não são sobrescritos).", file=sys.stderr)
        return 1

    imagens = [tratar(a, args.cinza) for a in arquivos]
    limite = args.limite_mb * 1024 * 1024
    qualidade, lado = 85, LADO_MAIOR_A4_200DPI
    while True:
        pdf = montar_pdf(imagens, qualidade, lado)
        if len(pdf) <= limite or (qualidade <= 40 and lado <= 1200):
            break
        if qualidade > 40:
            qualidade = max(40, qualidade - 10)
        else:
            lado = int(lado * 0.85)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_bytes(pdf)
    mb = len(pdf) / 1024 / 1024
    situacao = "OK" if len(pdf) <= limite else "ACIMA DO LIMITE (dividir em mais de um arquivo)"
    print(f"{situacao}: {saida} | {len(arquivos)} página(s) | {mb:.2f} MB | qualidade {qualidade} | lado maior {lado}px")
    return 0 if len(pdf) <= limite else 2


if __name__ == "__main__":
    sys.exit(main())
