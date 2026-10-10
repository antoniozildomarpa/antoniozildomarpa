# Rotina: triagem de e-mail

**Frequência:** duas vezes ao dia (ex.: 9h e 15h, em dias úteis). Ajuste ao ritmo do escritório.
**Conectores:** Gmail ou Outlook (leitura), Google Drive (gravação em `01 Entrada` e `03 Análise`).
**Skill usada:** `triagem-email`.
**Status:** roteiro. Depende de conector de e-mail na conta da advogada.

## Prompt sugerido

> Execute a skill triagem-email. Liste os e-mails recebidos desde a última triagem registrada em `03 Análise/ultima-triagem.txt`. Classifique, extraia os dados principais, salve anexos relevantes nas pastas corretas e crie a nota de triagem. Não envie, não responda, não arquive e não marque como lido. Ao final, liste as decisões pendentes para a advogada.

## Saída

Nota em `03 Análise/AAAA-MM-DD_triagem.md` e resumo na conversa.

## Limites

- Não envia nem responde e-mails.
- Não cria eventos de calendário sem aprovação.
- Não abre links de portais com login.
