---
name: leitura-documentos
description: Lê PDFs de processo, cartas do INSS, contracheques e documentos Word ou Excel de forma econômica, gerando primeiro um índice local por página (tipo provável, nº CNJ, datas, prazos citados) e só depois abrindo as páginas que importam. Use sempre que precisar ler documentos de um caso com mais de duas páginas.
---

# Leitura de documentos

Objetivo: gastar pouco do limite do plano e não mandar o documento para fora do computador. Os scripts rodam localmente (PyMuPDF, OCR RapidOCR e MarkItDown).

## Passos

1. Confira se a pasta não tem `SIGILOSO.txt`. Se tiver, pare.
2. PDF: `python scripts/ler_pdf.py "<arquivo.pdf ou pasta>" --out "<pasta do caso>/03 Análise/textos"`.
   - Use `--paginas 1-30` em processos grandes, para começar pelo início.
   - Páginas escaneadas passam por OCR automaticamente. Números lidos por OCR (valores, datas, CPF) devem ser conferidos na imagem antes de entrar em peça.
3. Word, Excel e PowerPoint: `python scripts/converter_docs.py <arquivos> --out "<pasta do caso>/03 Análise/textos"`.
4. Leia o `indice.json`: contagem por tipo, `paginas_com_prazo`, `numeros_cnj`. Depois abra só os `pNNN.txt` necessários.
5. Fotos de documento ruins de ler: trate antes com a skill `tratamento-documentos`.

## Regras

- PDF de uma ou duas páginas pode ser lido direto.
- Ao citar um trecho, informe arquivo e página.
- O tipo no índice é só uma pista (palavras-chave). Confirme lendo a página.
- A pasta `textos` é material de trabalho: não vai para o processo nem para o cliente.
