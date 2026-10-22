---
name: estrutura-caso
description: Cria a pasta padronizada e a ficha de um caso técnico vindo do SEI (relatório, informação, parecer ou manifestação técnica), registra cada etapa e mostra onde o caso parou. Use ao iniciar uma demanda nova, ao concluir qualquer etapa do fluxo e ao retomar um caso.
---

# Estrutura do caso

Toda demanda técnica tem uma pasta própria, com subpastas fixas, uma ficha e um registro. O script `geoprocessamento/automacao-sei/scripts/caso.py` faz tudo isso e nunca apaga nem sobrescreve arquivos.

## Onde fica

- Raiz: `H:\Meu Drive\_GEO\_DEMANDAS_EMI\<ano>\`
- Nome da pasta: NUP sem barras + apelido curto, por exemplo `02001.012345-2026-11_embargo-fazenda-x`.

## Criar um caso

1. Reúna, da triagem no SEI: NUP, tipo de documento, setor demandante, número SEI do documento da demanda, pedido em uma frase e prazo.
2. Se faltar o tipo de documento, pergunte. Tipos: `relatorio` (Relatório Técnico), `informacao` (Informação Técnica), `parecer` (Parecer Técnico), `manifestacao` (Manifestação Técnica).
3. Rode primeiro com `--simular` e mostre ao usuário onde a pasta será criada.
4. Rode de verdade:

```
python geoprocessamento/automacao-sei/scripts/caso.py criar --nup "<NUP>" --apelido "<apelido>" --tipo <tipo> --demandante "<setor>" --documento-sei "<nº SEI>" --pedido "<pedido>" --prazo AAAA-MM-DD
```

## Subpastas e o que vai em cada uma

| Pasta | Conteúdo |
| --- | --- |
| `00_Ficha` | `ficha.json` (fonte), `ficha.md` (leitura), `registro.md` (log) |
| `01_Processo_SEI` | Documentos baixados da árvore, nomeados `SEI_<número>_<descrição>.pdf` |
| `02_Insumos/imagens` | Imagens de satélite, fotos, prints |
| `02_Insumos/vetores_baixados` | Cópias das camadas de `H:\Meu Drive\_GEO\_VETORES` usadas no caso |
| `02_Insumos/consultas_online` | Recortes exportados das consultas ao SISCOM (IBAMA) e à SEMAS-PA, com data e hora no nome |
| `02_Insumos/tabelas` | Coordenadas extraídas dos documentos (CSV) |
| `02_Insumos/mapas_scan` | Mapas e croquis a georreferenciar |
| `02_Insumos/documentos_imovel` | Demonstrativos do CAR e outros documentos do imóvel |
| `03_Geo` | Projeto `caso.qgz`, vetores produzidos, rasters, georreferenciados |
| `04_Figuras` | Recortes de mapa com legenda para o corpo do texto |
| `05_Documento` | Minutas em versões (`minuta_v1.docx`, `minuta_v2.docx`, ...) e `final.docx` |
| `06_Anexos` | Anexos com o nome final (`Anexo_1_...`, `Anexo_2_Geoinformacao.zip`) |
| `07_SEI` | Números SEI gerados e prints de confirmação |

## Registrar cada etapa

Ao concluir qualquer etapa, registre:

```
python geoprocessamento/automacao-sei/scripts/caso.py registrar --pasta "<pasta do caso>" --etapa <etapa> --texto "<o que foi feito, com os arquivos>"
```

Etapas: `triagem`, `leitura`, `conferencia_1`, `geo`, `conferencia_2`, `figuras`, `redacao`, `revisao`, `conferencia_3`, `anexos`, `conferencia_4`, `sei`, `assinatura_envio`. Use `--situacao em_andamento` para uma etapa começada e não terminada.

## Retomar um caso

```
python geoprocessamento/automacao-sei/scripts/caso.py situacao --pasta "<pasta do caso>"
```

Mostra a situação de cada etapa e a próxima. Leia também `00_Ficha/registro.md` antes de continuar.

## Regras

- Dados do caso ficam só na pasta do caso, nunca no repositório.
- Dados de consulta online mudam com o tempo: sempre exporte o recorte usado para `02_Insumos/consultas_online` e anote fonte, data e hora em `consultas_online` na ficha.
- Para atualizar campos da ficha (interessado, município, bioma, documentos, camadas, áreas, anexos), edite `ficha.json` e rode `registrar` em seguida, para refazer o `ficha.md`.
