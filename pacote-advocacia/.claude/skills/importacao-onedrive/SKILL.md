---
name: importacao-onedrive
description: Conduz a importação das pastas de clientes do OneDrive para a pasta Clientes e a criação da ficha cadastral de cada cliente a partir dos documentos. Quatro etapas com aprovação entre elas - inventário (só nomes), cópia aprovada, extração do conteúdo (PDF, Word, fotos, e-mails, áudios) e ficha-cliente.md com fonte de cada dado, fechando com a planilha geral de clientes. Use quando a advogada pedir para mapear, migrar ou cadastrar os clientes do OneDrive, ou para retomar uma importação parada.
---

# Importação do OneDrive e cadastro dos clientes

Trabalho grande, feito em etapas. Cada etapa termina com algo para a advogada ou uma colaboradora conferir, e a seguinte só começa depois do "pode seguir". Pode levar vários dias: no começo de cada sessão, leia `<Clientes>/_inventario/andamento.md` (crie na primeira vez) para saber onde parou, e atualize-o ao fim de cada etapa ou lote.

Caminhos: a pasta Clientes e o OneDrive estão em `escritorio.local.md`. Os scripts ficam em `scripts/` do pacote.

## Antes de começar (uma vez)

1. **Autorização para ler o conteúdo.** A questão 12 autorizou ler só nomes. As etapas 3 e 4 abrem os documentos. Pergunte à advogada, com estas palavras: "A etapa de ficha cadastral abre e lê os documentos das pastas (RG, CPF, procurações, petições, laudos, áudios), no seu computador e na sua conta. Autoriza?" Registre a resposta, com data, em `andamento.md`. Sem o sim, faça só as etapas 1 e 2.
2. **Processos em segredo de justiça.** Peça que ela crie um arquivo `SIGILOSO.txt` nas pastas desses casos no OneDrive **antes** do inventário. Pasta marcada não é listada, copiada nem lida; ela mesma move essas pastas depois.
3. **OneDrive sincronizado.** O inventário lê o que o Windows mostra da pasta do OneDrive. Arquivos "só na nuvem" aparecem normalmente e não são baixados no inventário, mas são baixados na cópia (etapa 2). Confira o espaço livre em disco.

## Etapa 1: inventário (só nomes e metadados)

```
python scripts/inventario_pastas.py --raiz "<OneDrive>" --saida "<Clientes>/_inventario/inventario-AAAA-MM-DD"
```

Sem `--raiz`, o script acha o OneDrive sozinho. Não use `--anonimo` aqui: o modo anônimo é só para mostrar o relatório fora do escritório, e não grava o caminho de origem que a etapa 2 precisa.

Leia o `resumo.md` e apresente à advogada, em poucas linhas:
- volume total, quanto está só na nuvem e quanto tempo e espaço a cópia vai exigir;
- como ela organiza hoje (primeiro nível), o que parece pasta de cliente e o que não parece;
- problemas: arquivos soltos, caminhos longos, CPF em nome de arquivo, duplicados, processo espalhado em duas pastas.

Depois peça que ela abra `proposta_migracao.csv` no Excel e, linha a linha:
- corrija a `area_sugerida` e a parte da área e do nome em `destino_sugerido` (formato `Clientes/{Área}/{Nome do cliente}/`), principalmente as `[DECIDIR]`;
- quando duas pastas forem do mesmo cliente, ponha o mesmo destino nas duas;
- escreva `sim` em `aprovar` no que deve ser copiado. Pastas paradas há anos podem ficar de fora agora.

Se a estrutura dela não for por área e cliente, a proposta sai torta: não force. Mostre o primeiro nível e combine com ela como ler a estrutura antes de seguir.

## Etapa 2: cópia aprovada

```
python scripts/migrar_pastas.py --csv "<proposta_migracao.csv aprovada>" --clientes "<Clientes>"
```

Isso é simulação. Mostre o total de arquivos, o tamanho, o espaço livre e os avisos (sigilosas, destino sem área). Com o "pode copiar", rode de novo com `--executar`.

- O OneDrive não é alterado. Nada é movido nem apagado.
- Cada cliente recebe `Clientes/{Área}/{Cliente}/_importado-onedrive/` com a estrutura original dentro.
- Se cair no meio, rode o mesmo comando: o que já foi copiado é pulado.
- Registro de cada arquivo em `<Clientes>/_inventario/migracao-*.csv`. Informe as falhas.

## Etapa 3: extração do conteúdo

Só com a autorização do item 1.

```
python scripts/extrair_cliente.py --lote "<Clientes>"               (todos)
python scripts/extrair_cliente.py "<Clientes>/<Área>/<Cliente>"     (um cliente)
```

Opções: `--audio` transcreve os áudios (lento, deixe para o fim ou para os clientes que precisarem), `--max-paginas 40` limita as páginas lidas por PDF (a qualificação está no começo; autos inteiros não precisam ser lidos para a ficha), `--max-mb 60`.

O script grava em `<cliente>/_extracao/`: textos, `indice.csv`, `candidatos.json` e `resumo.md`. Rodar de novo só processa o que mudou. Para centenas de clientes, rode por área ou deixe rodando à noite com o computador ligado.

## Etapa 4: ficha cadastral

Para cada cliente, por lotes de 10 a 20, delegando ao agente `triagem-documentos` quando o lote for grande:

1. Leia `_extracao/resumo.md`. Não abra todos os textos.
2. Abra, na ordem, os textos que trazem a qualificação: procuração, petição inicial, contrato de honorários, declaração de hipossuficiência; depois RG/CNH e comprovante de residência. Use o `indice.csv` para achar o arquivo de texto de cada um.
3. Copie `modelos/ficha-cliente-modelo.md` para `<Clientes>/<Área>/<Cliente>/ficha-cliente.md` e preencha:
   - cada dado com a fonte, no formato `- CPF: 000.000.000-00 (fonte: procuracao.pdf, pág. 1) [CONFIRMAR]`;
   - todo dado de leitura automática leva `[CONFIRMAR]`; dado sem fonte fica só `[CONFIRMAR]`;
   - valores diferentes em documentos diferentes: os dois, com as fontes, e `[DECIDIR]`;
   - em **Casos**, um por processo CNJ ou requerimento, com assunto e situação aparente;
   - em **Documentos de praxe**, `sim (arquivo)` ou `não encontrado`;
   - em **Pendências**, o que não foi lido (foto ilegível, áudio, .zip, vídeo) e o que falta.
4. Se a ficha já existir (criada pela skill `cadastro-clientes` ou à mão), não sobrescreva: complete só os campos `[CONFIRMAR]` e acrescente o que faltar, sem apagar o que alguém escreveu.

Cuidados:
- Os documentos trazem dados de outras pessoas: cônjuge, filhos, parte contrária, testemunhas, médicos. Só entra na ficha o que for do cliente. Na dúvida, `[DECIDIR]`.
- Os dados do próprio escritório (telefone, e-mail, OAB e endereço da advogada) já são descartados pelo script. Ignore-os se aparecerem.
- OCR e Whisper erram números e nomes. Por isso o `[CONFIRMAR]` fica até alguém conferir no documento.
- Não copie dados de um cliente para a ficha, a pasta ou o relatório de outro.
- Prazos encontrados nos documentos (intimação recente, exigência do INSS) vão para a skill `agenda-prazos` e para a lista de alertas da etapa 5. Não deixe passar.

## Etapa 5: planilha geral

```
python scripts/consolidar_cadastro.py --clientes "<Clientes>"
```

Gera `<Clientes>/_cadastro/clientes-AAAA-MM-DD.xlsx` com uma linha por cliente: dados da qualificação, documentos de praxe, processos, quantos `[CONFIRMAR]` e `[DECIDIR]` faltam e a situação da ficha. Nunca sobrescreve uma planilha anterior.

Encerre cada lote com um relatório curto à advogada: fichas criadas, clientes com documentos de praxe faltando, conflitos a decidir, prazos encontrados e arquivos que não foram lidos.

## O que esta skill não faz

- Não apaga, move nem renomeia nada no OneDrive ou na pasta Clientes.
- Não reorganiza `_importado-onedrive/` em casos (`{Caso}/01 Entrada` etc.). Isso é decidido depois, cliente a cliente, com `estrutura/criar_pastas.py`.
- Não abre pasta com `SIGILOSO.txt` (o hook bloqueia de qualquer modo).
- Não envia nada para fora do computador e da conta dela.
