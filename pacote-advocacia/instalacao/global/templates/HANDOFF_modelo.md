# Modelo de HANDOFF.md

Modelo para fechar uma sessão do Claude Code e continuar em outra sem perder o fio.
Gerar na pasta do caso (`03 Análise/`) antes de trocar de sessão. Preencher todas as seções; se uma não se aplicar, escrever "nenhum".

Primeira mensagem da sessão nova: "leia o HANDOFF.md em <caminho> e continue pela pendência 1".

---

```markdown
# HANDOFF – <cliente> – <nº do processo ou requerimento> – <data>

## 1. Caso e objetivo
- Cliente e área: <nome> – <área>
- Pasta do caso: <caminho completo> (conferir se o Google Drive está sincronizado antes de listar)
- O que falta entregar: <frase curta: minuta, análise, cálculo, conferência de prazo>

## 2. Decisões tomadas
- <decisão> – motivo: <regra ou fato> – decidido por: <advogada | colaboradora | Claude>

## 3. Arquivos
- Documentos de origem: <caminhos>
- Textos extraídos: <pasta>
- Minutas e versões: <caminhos, com v1, v2>

## 4. Prazos
- <prazo> – vencimento <data> – regra usada – na agenda: sim/não – conferido pela advogada: sim/não

## 5. Pendências (em ordem)
1. <tarefa> – depende de: <nada | item N> – comando: `<comando completo, se houver>`
2. <tarefa> – depende de: <item N>

## 6. Dúvidas em aberto
- <ponto> – aguarda: <decisão da advogada | documento do cliente | conferência na fonte>

## 7. Sessão
- ID da sessão que está sendo fechada: <ID>
- Para consulta pontual: `claude --resume <ID>`
```

---

## Regras de uso
- Pendência com comando traz o comando completo.
- Não copiar no handoff dados pessoais além do necessário para achar o caso (nome e número bastam).
- Não gravar senhas, tokens nem códigos de acesso.
