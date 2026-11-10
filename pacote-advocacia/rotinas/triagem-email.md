# Rotina: triagem de e-mail

**Frequência:** duas vezes ao dia (ex.: 9h e 15h, em dias úteis). Ajuste ao ritmo do escritório.
**Conectores:** Gmail ou Outlook (leitura), Google Drive (gravação em `01 Entrada` e `03 Análise`).
**Skill usada:** `triagem-email`.
**Status:** roteiro. Depende de conector de e-mail na conta da advogada. O e-mail do escritório (Gmail ou Outlook) ainda não foi definido.

## Prompt sugerido

> Execute a skill triagem-email. Liste os e-mails recebidos desde a última triagem registrada em `ultima-triagem.txt`, na raiz da pasta `Clientes`. Classifique, dando prioridade às notificações do PJe e aos avisos e exigências do INSS. Salve o conteúdo e os anexos nas pastas dos casos, anote nas fichas, e para cada item urgente com prazo gere a análise e a minuta `v1` como rascunho. Não envie, não responda, não arquive e não marque como lido. Ao final, liste as decisões pendentes para a advogada.

## Saída

Nota de triagem em `03 Análise/` de cada caso afetado, minutas `v1` em `04 Minutas/` e resumo na conversa.

## Limites

- Não envia nem responde e-mails.
- Não cria eventos de calendário sem aprovação.
- Não abre links de portais com login.
