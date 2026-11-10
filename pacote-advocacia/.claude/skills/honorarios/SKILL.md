---
name: honorarios
description: Lê contratos de honorários assinados e lança os valores, parcelas, vencimentos e percentuais de êxito na planilha de controle financeiro do escritório. Use quando um contrato novo for assinado ou quando a advogada pedir para conferir o que está a receber.
---

# Honorários

Pedido da advogada (questão 20, item 6). A base definitiva (Google Sheets ou Excel) e as regras de recebimento dependem do bloco G do questionário, ainda pendente. Até lá, a planilha é `Financeiro/Controle_Honorarios.xlsx`, na pasta definida em `escritorio.local.md`.

## Passos

1. Leia o contrato (Word: `scripts/converter_docs.py`; PDF: `scripts/ler_pdf.py`). Extraia: cliente, caso, tipo (fixo, êxito ou misto), valor total, número de parcelas, primeiro vencimento, percentual de êxito e sobre o que incide.
2. Mostre os dados extraídos à advogada ou à colaboradora e espere a confirmação.
3. Lance:
   `python scripts/lancar_honorario.py --planilha "<Financeiro>/Controle_Honorarios.xlsx" --cliente "..." --area "..." --caso "..." --tipo fixo --valor 3000 --parcelas 3 --primeiro-vencimento AAAA-MM-DD --contrato "<caminho do contrato>"`
4. Registre na `ficha-cliente.md` que o contrato foi lançado, com a data.

## Regras

- Valor que não estiver claro no contrato não é lançado: fica como pendência para a advogada.
- O script só acrescenta linhas. Baixa de pagamento e correções são feitas por uma pessoa na planilha, até o bloco G definir outro fluxo.
- Valores de terceiros (alvarás, RPV, precatórios do cliente) não entram nesta planilha (questão 28, pendente).
- Honorário de êxito é condicional: não somar com o que está a receber.
