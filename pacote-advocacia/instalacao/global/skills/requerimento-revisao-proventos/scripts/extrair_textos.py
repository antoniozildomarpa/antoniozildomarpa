"""Extrai o texto de todos os PDFs de uma pasta de servidor, com OCR nas páginas escaneadas.

Uso: python -E -P extrair_textos.py "pasta do servidor" [--pular-leis]
Saída: <pasta>/_revisao/textos/<arquivo>.txt e, para PDFs escaneados de até 3 páginas,
<pasta>/_revisao/paginas/<arquivo>_pN.png (holerite, portaria: conferir visualmente).
As leis municipais são as mesmas em todos os casos e já estão resumidas em
references/fundamentos.md; com --pular-leis os PDFs cujo nome começa com "LEI" são ignorados.
"""
import sys, os, pymupdf

pasta = sys.argv[1]
pular_leis = '--pular-leis' in sys.argv
out_txt = os.path.join(pasta, '_revisao', 'textos')
out_png = os.path.join(pasta, '_revisao', 'paginas')
os.makedirs(out_txt, exist_ok=True)
os.makedirs(out_png, exist_ok=True)
ocr = None

for nome in sorted(os.listdir(pasta)):
    if not nome.lower().endswith('.pdf') or (pular_leis and nome.upper().startswith('LEI')):
        continue
    doc = pymupdf.open(os.path.join(pasta, nome))
    base = os.path.splitext(nome)[0]
    partes, escaneadas = [], 0
    for i, pg in enumerate(doc):
        txt = pg.get_text().strip()
        if len(txt) < 50:  # página escaneada
            escaneadas += 1
            if ocr is None:
                from rapidocr_onnxruntime import RapidOCR
                ocr = RapidOCR()
            res, _ = ocr(pg.get_pixmap(dpi=200).tobytes('png'))
            # ordena por linha (y) e depois x
            linhas = sorted(res or [], key=lambda x: (round(x[0][0][1] / 15), x[0][0][0]))
            txt = '[OCR]\n' + '\n'.join(x[1] for x in linhas)
        partes.append(f'\n=== PAG {i + 1} ===\n{txt}\n')
    with open(os.path.join(out_txt, base + '.txt'), 'w', encoding='utf-8') as fh:
        fh.write(''.join(partes))
    if escaneadas and len(doc) <= 3:
        for i, pg in enumerate(doc):
            pg.get_pixmap(dpi=110).save(os.path.join(out_png, f'{base}_p{i + 1}.png'))
    print(f'{nome}: {len(doc)} pág., {escaneadas} com OCR')
print('saída em', out_txt)
