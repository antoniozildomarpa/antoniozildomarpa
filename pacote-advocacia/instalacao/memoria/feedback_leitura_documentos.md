---
name: feedback-leitura-documentos
description: Ler PDFs e documentos Office primeiro com os scripts locais do pacote, que economizam e não enviam nada para fora
metadata:
  type: feedback
---

Para PDF, usar `scripts/ler_pdf.py` (texto e OCR locais, gera índice por página). Para Word, Excel e PowerPoint, usar `scripts/converter_docs.py` (MarkItDown local). Depois ler só o `indice.json` e as páginas ou trechos necessários, não o arquivo inteiro.

**Why:** processos têm centenas de páginas; ler tudo de uma vez gasta muito do limite do plano e é mais lento. Os scripts rodam no computador, sem custo e sem mandar o documento a terceiros.
**How to apply:** exceção para PDF de 1 ou 2 páginas, que pode ser lido direto. Fotos e escaneados ruins passam antes pelo `scripts/tratar_imagens.py`.
