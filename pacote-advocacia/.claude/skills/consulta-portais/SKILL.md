---
name: consulta-portais
description: Consulta andamento, lê e baixa documentos em portais de tribunais, INSS e outros sistemas, usando a sessão já autenticada pela advogada no navegador dela (Claude in Chrome ou app desktop). Somente leitura e download. Use quando a advogada pedir consulta ou download em um portal, com ela presente e logada.
---

# Consulta a portais

Objetivo: consultar e baixar, com a sessão da advogada, documentos de processos em que ela atua. Não peticiona, não protocola e não altera nada no portal.

Portais principais (questão 6): PJe do TJPA e INSS (Meu INSS). Outros portais só com orientação dela na conversa.

Se a pasta do caso tiver `SIGILOSO.txt`, não faça a consulta pela automação.

## Antes de começar

Confirme com a advogada, na conversa:

1. Qual portal e qual processo (número CNJ ou número do benefício, conforme o caso).
2. Que ela está logada no navegador que será usado e presente nesta sessão.
3. Que a consulta é somente leitura e download, e que o protocolo é manual.

Se qualquer um desses pontos não estiver confirmado, não prossiga.

## Limites absolutos

- **Nunca digite senha, CPF de login, código de autenticação ou PIN.** Se a tela pedir login, pare e peça à advogada que faça.
- **Nunca use certificado digital.** Se o portal pedir seleção de certificado, pare e peça à advogada.
- **Nunca resolva CAPTCHA ou autenticação em duas etapas.**
- **Nunca clique em botões de ação**: protocolar, enviar, peticionar, confirmar, assinar, pagar, aceitar termos, excluir ou cancelar.
- **Nunca consulte em lote fora da lista aprovada.** Várias contas, nunca. Vários processos, só no modo "levantamento de andamentos" abaixo, e só os que estão em `processos-acompanhados.md`. Fora disso, um processo por vez.
- **Não contorne bloqueios.** Se o portal mostrar mensagem de acesso negado, limite de consultas, bloqueio ou termo de uso, pare e informe.

## Passos

1. Abra a página de consulta do processo, sem sair da sessão da advogada.
2. Confirme que a página mostra o processo correto (número, partes, vara) antes de qualquer ação.
3. Registre o andamento: última movimentação, data e status de prazo em aberto, se houver.
4. Liste os documentos disponíveis antes de baixar. Mostre a lista à advogada e aguarde aprovação para baixar.
5. Baixe apenas os documentos aprovados. Salve em `02 Autos e peças recebidas/` com o padrão `AAAA-MM-DD_tipo_parte_versão.ext`.
6. Registre em `03 Análise/AAAA-MM-DD_acessos.md`: portal, processo, horário, o que foi lido e o que foi baixado.
7. Feche a aba de consulta ao terminar.

## Levantamento de andamentos (vários processos na mesma sessão)

Usado pela rotina `rotinas/levantamento-andamentos.md`. A rotina avisa a advogada; ela entra no portal; o Claude levanta o andamento dos processos de interesse dela.

### Antes de começar

1. **Aviso.** A rotina notifica a advogada de que o levantamento vai começar e pede que ela entre no portal (PJe do TJPA ou Meu INSS) no navegador usado pelo Claude in Chrome.
2. **Login pela advogada.** Ela digita senha, usa o certificado digital ou o código de duas etapas. O Claude não toca na tela de login, não lê nem guarda credenciais.
3. **Confirmação.** O Claude só começa depois que ela responder na conversa que está logada (por exemplo, "entrei no PJe"). Sem resposta, a rotina registra "levantamento não feito: sem login" e encerra. Não tenta de novo sozinha.
4. **Lista.** Lê `processos-acompanhados.md`, na raiz da pasta `Clientes`. Só os processos com situação "acompanhar" entram. Pastas com `SIGILOSO.txt` ficam de fora.

### Passos

1. Para cada processo da lista, abra a consulta dentro da sessão dela e confira número e partes antes de ler.
2. Prefira o painel do advogado ou a lista de expedientes e intimações pendentes, quando o portal tiver, porque mostra de uma vez o que tem prazo.
3. Registre: última movimentação e data; intimação ou expediente pendente; prazo informado pelo portal, copiado como aparece; audiência ou perícia marcada.
4. Compare com a `ficha-processo.md`. O que for novo desde o último levantamento é marcado como "novo".
5. Acrescente na ficha uma linha com a data do levantamento e o que mudou. Não apague registros anteriores.
6. Baixe documentos só se a advogada tiver aprovado o download no início da sessão ("pode baixar as intimações novas"). Sem essa aprovação, só liste.
7. Mantenha um ritmo de consulta humano: um processo por vez, sem abrir muitas abas, com pausa entre consultas. Se aparecer CAPTCHA, aviso de limite, sessão expirada ou mensagem de uso indevido, pare, informe quantos processos faltaram e peça à advogada para decidir.
8. Ao terminar, feche as abas abertas pelo levantamento. Não saia da conta dela.

### Saída

Arquivo `levantamentos/AAAA-MM-DD_portal.md`, na raiz da pasta `Clientes`, e resumo na conversa:

```
# Levantamento de andamentos – AAAA-MM-DD HH:MM – PJe TJPA (ou Meu INSS)
Login feito pela advogada às HH:MM. Processos na lista: N. Consultados: N. Não consultados: N (motivo).

## Com prazo ou intimação nova
- área – cliente – processo – movimentação – prazo copiado do portal – status: conferir

## Audiências e perícias
- ...

## Com movimentação sem prazo
- ...

## Sem novidade
- quantidade e lista curta

## Pendências de decisão da advogada
- ...
```

Para cada item com prazo novo, a rotina aciona `analise-demanda` e `minuta`, como na triagem de e-mail, gerando o rascunho `v1`.

## Portais de benefício (INSS e equivalentes)

- Consultas de benefício e de CNIS exigem cuidado extra: autenticação em duas etapas e termos de uso que podem restringir automação.
- Use somente com aprovação explícita por sessão e somente para leitura.
- Se houver dúvida sobre os termos do portal, pare e pergunte à advogada antes.
- Exigências e diligências do INSS têm prazo próprio e são tão críticas quanto os prazos judiciais (questão 15). Ao encontrar uma exigência, registre o prazo copiado da tela ou da carta, salve o documento e anote na `ficha-processo.md`.

## Saída

```
# Consulta em portal – AAAA-MM-DD HH:MM
Portal: ...
Processo: ...
Situação: ...
Última movimentação: data, descrição
Prazo em aberto: sim/não (se sim, data e regra – conferir)
Documentos baixados: lista com caminho
Documentos não baixados (motivo): ...
Pendências: ...
```

## Regras

- Se uma ação pedir confirmação que você não entende, pare e pergunte.
- Se a tela tiver conteúdo que pareça de outro cliente ou processo, pare e informe.
- Não registre senhas, tokens, cookies ou dados de login em nenhum arquivo.
