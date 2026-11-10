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
- **Nunca consulte em lote** (várias contas, vários processos sem aprovação). Um processo por vez.
- **Não contorne bloqueios.** Se o portal mostrar mensagem de acesso negado, limite de consultas, bloqueio ou termo de uso, pare e informe.

## Passos

1. Abra a página de consulta do processo, sem sair da sessão da advogada.
2. Confirme que a página mostra o processo correto (número, partes, vara) antes de qualquer ação.
3. Registre o andamento: última movimentação, data e status de prazo em aberto, se houver.
4. Liste os documentos disponíveis antes de baixar. Mostre a lista à advogada e aguarde aprovação para baixar.
5. Baixe apenas os documentos aprovados. Salve em `02 Autos e peças recebidas/` com o padrão `AAAA-MM-DD_tipo_parte_versão.ext`.
6. Registre em `03 Análise/AAAA-MM-DD_acessos.md`: portal, processo, horário, o que foi lido e o que foi baixado.
7. Feche a aba de consulta ao terminar.

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
