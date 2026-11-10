---
name: requerimento-revisao-proventos
description: Elabora, a partir da pasta de documentos de um servidor aposentado do município de Tucuruí-PA (IPASET), a análise e a minuta Word do requerimento de revisão de proventos para incluir a Gratificação de Ensino Especial (atendimento educacional especializado, 20%), com o cálculo dos retroativos corrigidos pela SELIC. Usar quando o usuário apontar uma ou várias pastas de servidores e pedir o requerimento, a revisão de aposentadoria, a gratificação de ensino especial ou o cálculo dos retroativos.
---

# Requerimento de revisão de proventos: Gratificação de Ensino Especial

Estrutura do caso: `caso.exemplo.json`, com dados fictícios (o modelo foi validado num caso real em 2026,
cujos dados não acompanham o pacote). Teses, textos legais e pontos fracos estão em
`references/fundamentos.md`; leia esse arquivo antes de analisar o primeiro caso. Os trechos de lei vieram
do OCR dos PDFs: confira-os no texto oficial antes do primeiro uso `[VERIFICAR]`.

Argumento: uma pasta de servidor ou uma pasta-mãe com várias pastas de servidores. Na pasta-mãe,
processe cada subpasta que tenha PDFs e, no fim, faça um quadro-resumo de todas.

`SK` abaixo é `%USERPROFILE%\.claude\skills\requerimento-revisao-proventos` (no Bash, `~/.claude/skills/requerimento-revisao-proventos`).

## Passo a passo (por servidor)

1. **Extrair textos.** `python -E -P SK/scripts/extrair_textos.py "<pasta>" --pular-leis`
   (`-E -P`, não `-I`: o OCR precisa do pyyaml instalado na pasta de pacotes do usuário).
   Gera `<pasta>/_revisao/textos/*.txt` e PNG das páginas escaneadas curtas em `_revisao/paginas/`.
   Leia os .txt. Para holerite e portaria escaneados, olhe também os PNG: o OCR erra números.
   Se faltarem leis que não estão na referência, rode sem `--pular-leis`.

2. **Montar `<pasta>/_revisao/caso.json`** copiando `SK/caso.exemplo.json` e trocando os dados:
   - requerente: nome, gênero (F/M), qualificação, cargo, matrícula, RG, CPF, PIS (do parecer,
     da portaria, do holerite ou do requerimento original). Dado que não estiver nos documentos fica
     como `"[PREENCHER]"`; nunca invente.
   - beneficio: processo, portaria e data, DIB, descrição, parecer, fundamentação legal (da planilha)
     e `integral` (true só se a planilha/parecer indicar integralidade).
   - planilha: data de emissão, vencimento base, `horas_normais` (se a planilha tiver a parcela
     Horas Normais da Lei 11.920/2023), total e a lista das parcelas que entraram.
   - gratificacao: percentual (20%, art. 31), `sobre_horas_normais`, `no_holerite` e
     `na_base_contribuicao` (houve desconto previdenciário sobre ela?).
     **Critério do escritório (26/10/2026):** quando a planilha inclui Horas Normais e o holerite traz
     as rubricas "Gratificação Ensino Especial" e "Gratificação 20% Horas Normais", use
     `sobre_horas_normais: true` (base = vencimento + horas normais). O gerador acrescenta ao item 7
     que o parecer calculou ATS e Nível Superior sobre salário-base + horas normais; confira se o
     parecer do caso diz isso (grep "Salário-base + Horas Normais").
   - beneficio.citacao_integralidade: use quando a regra não for o art. 50, § 2º, I (ex.: pontuação,
     art. 49, § 6º, I: "integralidade da remuneração e paridade do servidor público no cargo
     efetivo em que se der a aposentadoria"). DIB = data da portaria, salvo indicação diferente.
   - reajustes: vencimentos base posteriores à DIB, se os documentos mostrarem.
   - anexos: ajuste à documentação real.

3. **Triagem antes de gerar** (pare e informe o usuário em vez de gerar a minuta se):
   - a gratificação não aparece no holerite/ficha financeira da atividade;
   - a aposentadoria não tem integralidade (a tese do item 8 cai; o gerador recusa sem `--forcar`);
   - a gratificação já consta da planilha de proventos.

4. **Calcular.** `python SK/scripts/calc_retroativos.py "<pasta>/_revisao/caso.json"`
   (padrão: data de hoje; use `--data-calculo AAAA-MM-DD` para fixar outra data e `--sem-selic` se a
   API do BCB estiver fora). Grava o bloco `calculo` no caso.json e imprime a tabela.

5. **Gerar a minuta.**
   `node SK/scripts/gerar_minuta.js "<pasta>/_revisao/caso.json" "<pasta>/MINUTA - REQUERIMENTO REVISAO PROVENTOS - <PRIMEIRO NOME>.docx"`
   O texto jurídico é fixo no gerador (itens 1 a 9, mais o item 10 "Do precedente administrativo" quando o caso.json tiver o bloco `precedente` {processo, portaria, data_portaria, parecer, planilha_data, valor}, preenchido com um precedente favorável do próprio IPASET, se houver; pedidos somente "a" e "b"). Se o caso exigir
   texto diferente, ajuste uma cópia do script no scratchpad, nunca o original sem pedido do usuário.

6. **Conferir.** `python SK/scripts/conferir_docx.py "<docx>" "<scratchpad>/conf_<nome>"` e veja
   os PNG. O esperado são 3 páginas de requerimento e a página 4 com o anexo. Corrija página com
   uma linha só ou em branco.

7. **Registrar** em `<pasta>/_revisao/analise.md`: dados extraídos (com o documento de origem),
   resultado da triagem, pontos fracos do caso (ver referência), totais nominal/corrigido, pendências
   (`[PREENCHER]`, data do requerimento, documentos a juntar).

## Ao final

Responda com uma linha por servidor: nome, proventos atuais → revistos, retroativos nominal e
corrigido, situação (gerado / gerado com pendências / não gerado e motivo). Não protocole, não envie
e não publique nada; o usuário revisa e assina.
