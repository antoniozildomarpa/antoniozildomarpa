# Rotina: alerta de prazos

**Frequência:** diária, início da manhã (dias úteis).
**Conectores:** Google Calendar (leitura), Google Drive (leitura das pastas `06 Prazos e comunicações` e das `ficha-processo.md`).
**Status:** roteiro. A rotina deve ser criada na conta da advogada, a partir deste texto.

Hoje os prazos ficam em agenda física e já houve perda e quase perda de prazo (questões 13 e 14). A agenda física continua em uso até esta rotina ser validada por algumas semanas lado a lado com ela.

## Prompt sugerido

> Liste os prazos e pendências dos próximos cinco dias úteis, lendo as notas em `06 Prazos e comunicações` e a `ficha-processo.md` de cada caso ativo, e os eventos de prazo do calendário. Inclua os prazos judiciais e as exigências e diligências do INSS e do regime próprio, com a mesma prioridade. Inclua também audiências e perícias. Para cada item: área, cliente, caso, descrição, data de vencimento, regra usada no cálculo e status (ok ou conferir). Ignore pastas com `SIGILOSO.txt`, apenas informando quantas foram ignoradas. Não crie, altere nem exclua eventos. Não envie mensagens. Ao final, liste os prazos sem regra de cálculo registrada.

## Saída

Resumo na conversa e, opcionalmente, arquivo `03 Análise/AAAA-MM-DD_prazos.md`.

## Limites

- Somente leitura.
- O cálculo automático é ponto de partida. A conferência é da advogada.
