---
name: tratamento-documentos
description: Transforma fotos e digitalizações de documentos enviadas por clientes (celular, WhatsApp, scanner) num PDF legível e leve, com rotação, brilho e contraste corrigidos e tamanho dentro do limite do PJe ou do INSS. Use quando a advogada ou uma colaboradora pedir para preparar documentos para juntar ou protocolar.
---

# Tratamento de fotos e digitalizações

Pedido da advogada (questão 20, item 2): documentos com tamanho, formato, brilho e contraste aceitos pelos sistemas.

## Passos

1. Junte as imagens do documento numa pasta, na ordem das páginas (nomeie `01.jpg`, `02.jpg`... se precisar).
2. Rode:
   `python scripts/tratar_imagens.py "<pasta ou imagens>" --saida "<pasta do caso>/01 Entrada/AAAA-MM-DD_tipo_cliente.pdf"`
   - `--cinza` deixa o arquivo menor e costuma melhorar a leitura de documento só com texto. Não use em foto colorida que precise de cor (por exemplo, laudo com carimbo colorido).
   - `--limite-mb` define o tamanho máximo. Padrão: 5 MB. Os limites do PJe do TJPA e do Meu INSS devem ser conferidos no portal antes do primeiro uso `[VERIFICAR]`.
3. Confira o resultado abrindo o PDF. Se o script avisar "ACIMA DO LIMITE", divida as imagens em dois arquivos.
4. Para documento de identidade, gere frente e verso no mesmo PDF.

## Regras

- Os originais nunca são alterados nem apagados. O script recusa sobrescrever um PDF existente.
- Um documento por arquivo (RG, comprovante de residência, laudo), com nome no padrão `AAAA-MM-DD_tipo_cliente.pdf`.
- Se a foto estiver ilegível mesmo após o tratamento, registre na ficha do cliente que é preciso pedir nova foto. Não tente "adivinhar" o conteúdo.
