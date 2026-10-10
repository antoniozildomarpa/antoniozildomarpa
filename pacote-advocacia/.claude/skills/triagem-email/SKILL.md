---
name: triagem-email
description: Lê e filtra e-mails recebidos, identifica intimações, citações, notificações, prazos e pedidos de clientes, salva anexos na pasta correta e registra notas de análise. Use quando a advogada pedir triagem da caixa de entrada ou de um e-mail específico. Não envia nem responde e-mails.
---

# Triagem de e-mail

Objetivo: separar o que é urgente do que é ruído, organizar anexos nas pastas do cliente e deixar um registro para a advogada decidir.

## Limites

- **Somente leitura e organização de arquivos.** Não envia, não responde, não arquiva, não apaga e não marca como lido sem aprovação.
- Não abrir links de e-mail que levem a portais com login. Para portais, use a skill `consulta-portais`, com aprovação.
- Não tratar e-mail como fonte oficial de intimação sem conferência no sistema do tribunal.

## Filtros de classificação

Aplique em ordem. Um e-mail pode ter mais de uma classe.

| Classe | Sinais típicos | Prioridade |
|---|---|---|
| Urgente: prazo ou audiência | "intimação", "citação", "prazo", "audiência", "vista", "publicação", domínios de tribunais | Alta |
| Cliente com pedido | Remetente cadastrado, pedido de orientação, documento enviado | Média |
| Órgão ou administrativo | INSS, órgãos públicos, cartórios, notificações extrajudiciais | Média |
| Fornecedor e administrativo | Faturas, assinaturas, sistemas | Baixa |
| Ruído | Newsletters, marketing, notificações automáticas sem conteúdo | Ignorar |

A lista de remetentes e domínios cadastrados fica em `03 Análise/remetentes.md`, se a advogada tiver criado. Sem essa lista, use os sinais acima e peça confirmação quando houver dúvida.

## Passos

1. **Coleta.** Liste os e-mails recebidos desde a última triagem (data registrada em `03 Análise/ultima-triagem.txt`, ou últimas 48 horas na primeira execução).
2. **Classificação.** Aplique os filtros e atribua classe e prioridade.
3. **Extração.** Para cada e-mail relevante, extraia: remetente, data, assunto, número de processo (se houver), partes, pedido, prazo mencionado e anexos.
4. **Anexos.** Salve os anexos em `01 Entrada/` no padrão `AAAA-MM-DD_tipo_parte_versão.ext`. Se o cliente ainda não tiver pasta, não crie; registre na nota e pergunte.
5. **Nota.** Crie `03 Análise/AAAA-MM-DD_triagem.md` com o resumo.
6. **Prazos.** Para cada prazo identificado, não crie evento no calendário sem aprovação. Liste na nota para a advogada confirmar.
7. **Registro.** Atualize `03 Análise/ultima-triagem.txt` com a data e hora da execução.

## Saída

```
# Triagem de e-mail – AAAA-MM-DD HH:MM

## Urgentes (prazo ou audiência)
- [remetente] assunto – processo – prazo informado – anexo salvo em: caminho

## Clientes e pedidos
- ...

## Órgãos e administrativo
- ...

## Ignorados (resumo: quantidade e motivo)

## Pendências de decisão da advogada
- ...
```

## Regras

- Ao citar prazo, copie o texto do e-mail. Não converta datas sem indicar a regra usada.
- Se um e-mail parecer golpe, phishing ou comunicação falsa de tribunal, sinalize e não salve anexos.
- Não inclua o conteúdo integral de e-mails na nota. Use resumo e referência ao arquivo salvo.
