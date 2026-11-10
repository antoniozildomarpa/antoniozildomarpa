---
name: triagem-email
description: Lê e filtra e-mails recebidos, identifica intimações do PJe, avisos e exigências do INSS, notificações, prazos e pedidos de clientes, salva o conteúdo e os anexos na pasta do cliente, anota na ficha e, quando há prazo, prepara análise e minuta como rascunho. Use quando a advogada pedir triagem da caixa de entrada ou de um e-mail específico. Não envia nem responde e-mails.
---

# Triagem de e-mail

Objetivo: separar o que é urgente do que é ruído, guardar cada comunicação na pasta certa, anotar na ficha do cliente e deixar a minuta pronta para a advogada revisar (questão 20, item 5, de `respostas/questionario.md`). Hoje os prazos dela ficam em agenda física e já houve perda de prazo, então esta skill é a primeira linha de controle.

## Limites

- **Somente leitura e organização de arquivos.** Não envia, não responde, não arquiva, não apaga e não marca como lido sem aprovação.
- Não abrir links de e-mail que levem a portais com login. Para portais, use a skill `consulta-portais`, com aprovação.
- Não tratar e-mail como fonte oficial de intimação sem conferência no sistema do tribunal ou no Meu INSS.
- Se o e-mail for de processo cuja pasta tem `SIGILOSO.txt`, registre só que chegou e para qual pasta, sem resumir o conteúdo e sem gerar minuta.

## Filtros de classificação

Aplique em ordem. Um e-mail pode ter mais de uma classe.

| Classe | Sinais típicos | Prioridade |
|---|---|---|
| Urgente: prazo judicial ou audiência | Notificações do PJe/TJPA, "intimação", "citação", "prazo", "audiência", "perícia", "sentença", "vista", "publicação" | Alta |
| Urgente: exigência administrativa | Avisos do INSS (Meu INSS), "exigência", "cumprimento de exigência", "carta de exigência", "diligência", comunicações do regime próprio (por exemplo, IPASET) | Alta |
| Cliente com pedido | Remetente cadastrado, pedido de orientação, documento enviado | Média |
| Órgão ou administrativo | Órgãos públicos, cartórios, notificações extrajudiciais | Média |
| Fornecedor e administrativo | Faturas, assinaturas, sistemas | Baixa |
| Ruído | Newsletters, marketing, notificações automáticas sem conteúdo | Ignorar |

A lista de remetentes e domínios cadastrados fica em `remetentes.md`, na raiz da pasta `Clientes`, se a advogada tiver criado. Sem essa lista, use os sinais acima e peça confirmação quando houver dúvida.

## Passos

1. **Coleta.** Liste os e-mails recebidos desde a última triagem (data registrada em `ultima-triagem.txt`, na raiz da pasta `Clientes`, ou últimas 48 horas na primeira execução).
2. **Classificação.** Aplique os filtros e atribua classe e prioridade.
3. **Extração.** Para cada e-mail relevante, extraia: remetente, data, assunto, número do processo ou do requerimento, partes, pedido, prazo mencionado e anexos.
4. **Pasta.** Localize a pasta do caso (`Clientes/{Área}/{Cliente}/{Caso}/`) pelo número do processo, do requerimento ou pelo nome do cliente. Se não houver pasta, não crie; registre na nota e pergunte.
5. **Arquivo.** Salve o conteúdo do e-mail (texto, em `.md` ou `.pdf`) e os anexos em `01 Entrada/`, no padrão `AAAA-MM-DD_tipo_parte_versão.ext`.
6. **Ficha.** Acrescente na `ficha-processo.md` do caso uma linha com a data, a comunicação recebida e o prazo informado. Não apague registros anteriores.
7. **Prazos.** Para cada prazo identificado, liste na nota com o texto copiado do e-mail. Não crie evento no calendário sem aprovação.
8. **Análise e minuta.** Para cada item urgente com prazo em aberto, acione `analise-demanda` e, em seguida, `minuta`, gerando o rascunho `v1` em `04 Minutas/`. A minuta não é enviada nem protocolada; fica para revisão da advogada.
9. **Nota.** Crie a nota de triagem com o resumo (formato abaixo) em `03 Análise/` de cada caso afetado e um resumo geral na conversa.
10. **Registro.** Atualize `ultima-triagem.txt` com a data e hora da execução.

## Saída

```
# Triagem de e-mail – AAAA-MM-DD HH:MM

## Urgentes: prazo judicial ou audiência
- [remetente] assunto – processo – prazo informado – salvo em: caminho – minuta: caminho ou "não gerada (motivo)"

## Urgentes: exigências administrativas (INSS, regime próprio)
- ...

## Clientes e pedidos
- ...

## Órgãos e administrativo
- ...

## Ignorados (resumo: quantidade e motivo)

## Sem pasta de cliente (aguardam decisão)
- ...

## Pendências de decisão da advogada
- ...
```

## Regras

- Ao citar prazo, copie o texto do e-mail. Não converta datas sem indicar a regra usada.
- Se um e-mail parecer golpe, phishing ou comunicação falsa de tribunal ou do INSS, sinalize e não salve anexos.
- Não inclua o conteúdo integral de e-mails na nota. Use resumo e referência ao arquivo salvo.
- O e-mail do escritório (Gmail ou Outlook) ainda não foi definido. A rotina só é criada depois que o conector certo estiver ligado na conta da advogada.
