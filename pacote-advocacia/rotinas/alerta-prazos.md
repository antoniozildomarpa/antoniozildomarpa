# Rotina: alerta de prazos

**Frequência:** diária, início da manhã (dias úteis).
**Conectores:** Google Calendar (leitura), Google Drive (leitura das pastas `06 Prazos e comunicações`).
**Status:** roteiro. A rotina deve ser criada na conta da advogada, a partir deste texto.

## Prompt sugerido

> Liste os prazos processuais e pendências dos próximos cinco dias úteis, lendo as notas em `06 Prazos e comunicações` de cada processo ativo e os eventos de prazo do calendário. Para cada item: processo, descrição, data de vencimento, regra usada no cálculo e status (ok ou conferir). Não crie, altere nem exclua eventos. Não envie mensagens. Ao final, liste os prazos sem regra de cálculo registrada.

## Saída

Resumo na conversa e, opcionalmente, arquivo `03 Análise/AAAA-MM-DD_prazos.md`.

## Limites

- Somente leitura.
- O cálculo automático é ponto de partida. A conferência é da advogada.
