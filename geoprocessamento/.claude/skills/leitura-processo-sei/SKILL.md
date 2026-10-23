---
name: leitura-processo-sei
description: Lê um processo no SEI aberto no Chrome do usuário (somente leitura) - identifica a demanda, o setor demandante, o prazo e os documentos úteis da árvore, baixa o que importa para a pasta do caso e cria a ficha. Use quando o usuário pedir para iniciar um caso a partir do processo aberto no SEI.
---

# Leitura do processo no SEI (somente leitura)

Usa o Claude in Chrome na sessão que o usuário já abriu no SEI. Leia antes a skill do navegador (`anthropic-skills:chrome-browser`).

## Regras de segurança (sempre)

- **Somente leitura.** Nenhum clique que altere o processo: nada de incluir, editar, assinar, enviar, concluir, atribuir, anotar ou dar ciência.
- Login, senha, certificado digital e CAPTCHA são sempre do usuário.
- Se o SEI pedir senha ou confirmação, pare e avise.
- Trabalhe numa aba nova; não feche nem altere as abas do usuário.

## 1. Situar o processo

1. Confirme com o usuário qual processo está aberto (número no topo da árvore).
2. Leia o cabeçalho: NUP, tipo do processo, interessados.
3. Leia a árvore de documentos (painel da esquerda): número SEI, tipo, data e unidade de cada documento.

## 2. Encontrar a demanda

1. Normalmente é o documento mais recente endereçado à unidade do usuário: despacho, ofício, memorando, solicitação.
2. Abra e leia. Extraia:
   - **setor demandante** (quem pediu);
   - **número SEI** do documento da demanda;
   - **pedido em uma frase**;
   - **prazo**, se houver;
   - **tipo de documento esperado** (Relatório Técnico, Informação Técnica, Parecer Técnico ou Manifestação Técnica). Se não estiver claro, pergunte.
3. Releia os documentos citados pela demanda: eles costumam ser os insumos da análise.

## 3. Escolher e baixar documentos

Baixe só o que serve à análise:
- autos de infração, termos de embargo, relatórios de fiscalização;
- mapas, croquis, imagens e tabelas de coordenadas;
- documentos do imóvel (CAR, matrícula, memorial descritivo);
- manifestações anteriores sobre o mesmo assunto.

Como baixar:
- documento PDF ou externo: abra e use a opção de download do próprio SEI ou do visualizador;
- vários documentos: a opção **Gerar PDF** do processo, escolhendo só os documentos necessários, gera um único arquivo.

Salve em `01_Processo_SEI/` com o nome `SEI_<número>_<descrição-curta>.pdf`. Se o download cair na pasta Downloads, mova para a pasta do caso.

## 4. Criar a pasta e a ficha

Com os dados da demanda, siga a skill `estrutura-caso`:

```
python geoprocessamento/automacao-sei/scripts/caso.py criar --nup "<NUP>" --apelido "<apelido>" --tipo <tipo> \
  --demandante "<setor>" --documento-sei "<nº SEI>" --pedido "<pedido>" --prazo AAAA-MM-DD
```

Depois, liste em `documentos_baixados` da ficha cada arquivo baixado (número SEI, tipo, data) e registre a etapa `triagem`.

## 5. Entregar à coordenadora

Devolva:
- o resumo da demanda (quem, o quê, prazo, tipo de documento);
- a lista de documentos baixados e o que cada um traz para a análise;
- dúvidas que só o usuário resolve.

A **Conferência 1** acontece depois da leitura dos documentos (agente-leitor): o usuário confirma o entendimento da demanda e o plano de análise.
