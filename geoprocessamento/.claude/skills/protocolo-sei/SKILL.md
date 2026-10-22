---
name: protocolo-sei
description: Lança no SEI, pelo Chrome do usuário, o documento técnico aprovado de um caso - cria o documento principal em branco, inclui os anexos como documentos externos, cola o texto da minuta final, insere os links para os anexos e cria o despacho ao setor demandante. Nunca assina e nunca envia. Use só depois da Conferência 4 (autorização do usuário).
---

# Lançamento no SEI

Usa o Claude in Chrome na sessão do usuário. Leia antes a skill do navegador (`anthropic-skills:chrome-browser`).

## Antes de começar (obrigatório)

1. **Conferência 4 registrada**: o usuário autorizou o lançamento deste caso, nesta conversa.
2. Minuta final aprovada em `05_Documento/` (a versão indicada pelo usuário) e anexos prontos (`06_Anexos/manifesto.json` sem pendência).
3. Pergunte e anote na ficha:
   - **nível de acesso** dos documentos (Público, Restrito ou Sigiloso) e a hipótese legal, se restrito;
   - **tipo do documento externo** usado para os anexos no SEI do órgão (ex.: "Anexo", "Mapa");
   - **unidade de destino** do despacho (normalmente o setor demandante).
4. Confirme o processo aberto no SEI (NUP igual ao da ficha).

## Regras de segurança (sempre)

- **Nunca clique em "Assinar Documento" nem em "Enviar Processo"**, nem confirme assinatura. Um gancho do Claude Code bloqueia essas ações, mas a regra vale de qualquer forma.
- Nunca digite senha.
- Um passo de cada vez, com print de confirmação salvo em `07_SEI/`.
- Se algo inesperado aparecer (erro, tela diferente, pedido de confirmação), pare e mostre ao usuário.
- Registre cada número SEI gerado em `07_SEI/numeros_sei.json` e na ficha.

## Passos

### 1. Documento principal em branco
1. No processo, **Incluir Documento** → escolha o tipo (Relatório Técnico, Informação Técnica, Parecer Técnico ou Manifestação Técnica).
2. Texto inicial: nenhum. Descrição: o assunto curto. Nível de acesso: o combinado.
3. Confirme os dados. Anote o **número SEI** do documento criado. Feche o editor sem escrever.

### 2. Anexos (documentos externos)
Para cada anexo do manifesto, na ordem dos números:
1. **Incluir Documento** → **Externo**.
2. Tipo do documento: o combinado. Data: a da preparação. Nome na árvore: a descrição do anexo (ex.: "Anexo 2 – Carta imagem da área embargada"). Formato: nato-digital. Nível de acesso: o combinado.
3. Anexe o arquivo `06_Anexos/Anexo_N_...`. Confirme.
4. Anote o **número SEI** do anexo.

### 3. Texto do documento principal
1. Abra a minuta final no Word, selecione todo o conteúdo (texto, figuras e tabelas) e copie.
2. Abra o documento principal no editor do SEI (**Editar Conteúdo**) e cole no corpo.
3. Confira se figuras e tabelas vieram inteiras e se a formatação está legível.
4. Salve (botão **Salvar** do editor). Não assine.

### 4. Links para os anexos
1. No editor, em cada menção "Anexo N" do texto (e na Relação de Anexos), selecione o texto e use o botão de **link para documento do SEI**, informando o número SEI do anexo N.
2. Confira que todos os anexos citados têm link e que cada link aponta para o anexo certo.
3. Salve.

### 5. Despacho
1. **Incluir Documento** → **Despacho**.
2. Texto: encaminha ao setor demandante o documento principal (com link pelo número SEI) e os anexos (com links), em resposta ao documento da demanda (número SEI da ficha).
   Modelo: "Encaminho o Relatório Técnico nº SEI XXXXXXXX, com os Anexos 1 a 3 (SEI XXXXXXXX a XXXXXXXX), em atendimento ao Despacho SEI XXXXXXXX."
3. Salve. Não assine e não envie.

### 6. Parar e avisar
Mostre ao usuário: os números SEI de tudo o que foi criado, os prints e o que falta fazer por ele:
1. conferir no SEI;
2. **assinar** o documento principal e o despacho;
3. **enviar** o processo à unidade de destino.

Registre a etapa `sei` como concluída e `assinatura_envio` como pendente (do usuário).
