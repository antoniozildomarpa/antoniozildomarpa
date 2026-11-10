---
name: cadastro-clientes
description: Monta o cadastro de clientes por área a partir só dos nomes das pastas existentes (sem abrir documentos), gera uma lista proposta para aprovação e, depois de aprovada, cria a ficha-cliente.md de cada cliente e o clientes.csv geral. Use no primeiro mapeamento das pastas ou quando a advogada pedir para atualizar o cadastro.
---

# Cadastro de clientes

Esta skill trabalha só com nomes de pastas, sem abrir documentos. Para importar as pastas do OneDrive e montar a ficha completa a partir do conteúdo dos documentos, use a skill `importacao-onedrive`.

Pedido da advogada (questão 20, item 1): cadastro de clientes por área. Ela autorizou a leitura apenas dos nomes de pastas e arquivos (questão 12).

## Etapa 1: proposta

`python scripts/mapear_pastas.py propor --raiz "<pasta Clientes>" --saida "<pasta Clientes>/cadastro-proposto-AAAA-MM-DD.csv"`

O script lê só nomes. Para cada pasta `Área/Cliente`, lista nº de subpastas e arquivos, números CNJ e de requerimento do INSS que aparecem nos nomes, se já existe ficha e se há `SIGILOSO.txt`.

Se as pastas atuais não estiverem no formato `Área/Cliente` (questão 8: sem padrão), não force: mostre a estrutura encontrada à advogada e combine com ela como mapear antes de seguir.

## Etapa 2: aprovação

A advogada ou uma colaboradora abre o CSV no Excel, confere área e nome, corrige o que precisar e escreve `sim` na coluna `aprovar`. Nada é criado sem essa marca.

## Etapa 3: aplicação

`python scripts/mapear_pastas.py aplicar --csv "<o CSV aprovado>"`

Cria `ficha-cliente.md` onde não existir (dados pessoais ficam `[CONFIRMAR]`) e gera `clientes.csv` ao lado. Pastas sigilosas são puladas.

## Regras

- Não move, não renomeia e não apaga pastas. A migração para o padrão novo (`Clientes/{Área}/{Cliente}/{Caso}/`) é outra decisão, caso a caso.
- Dados pessoais (CPF, contato) só entram na ficha a partir de documento ou da transcrição do atendimento, nunca de suposição.
