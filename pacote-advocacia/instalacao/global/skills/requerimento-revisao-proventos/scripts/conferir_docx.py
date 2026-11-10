"""Exporta o .docx para PDF pelo Word e gera PNG de cada página, para conferência visual.

Uso: python conferir_docx.py "minuta.docx" "pasta_saida"
"""
import sys, os, pymupdf, win32com.client

docx, saida = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(saida, exist_ok=True)
pdf = os.path.join(saida, 'minuta.pdf')
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
try:
    d = word.Documents.Open(docx, False, True)
    d.SaveAs(pdf, 17)  # 17 = wdFormatPDF
    d.Close(0)
finally:
    word.Quit()
doc = pymupdf.open(pdf)
for i, p in enumerate(doc):
    p.get_pixmap(dpi=70).save(os.path.join(saida, f'pag{i + 1}.png'))
print(len(doc), 'páginas; PNG em', saida)
