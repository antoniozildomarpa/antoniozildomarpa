# Rotina: levantamento de andamentos nos portais

**Frequência:** dias úteis, início da manhã (sugestão: 8h). Ajustar com a advogada.
**Conectores:** Claude in Chrome (no navegador dela), Google Drive (leitura e gravação nas pastas `Clientes`), canal de aviso.
**Skill usada:** `consulta-portais`, modo "levantamento de andamentos".
**Status:** roteiro. A rotina é criada na conta da advogada, depois do teste com dados fictícios.

## Como funciona

1. No horário marcado, a rotina avisa a advogada: "Levantamento de andamentos: entre no PJe (e no Meu INSS, se for o dia) no Chrome e responda 'entrei'."
2. Ela faz o login com senha, certificado digital ou código de duas etapas. O Claude não participa dessa etapa.
3. Ela responde que entrou. Só então o Claude começa.
4. O Claude percorre os processos de `processos-acompanhados.md`, um por vez, só lendo.
5. Ao final, entrega o relatório, atualiza as fichas e prepara as minutas `v1` dos itens com prazo novo.

Se ela não responder em até duas horas, a rotina registra "não feito: sem login" e não insiste. O alerta de prazos do dia seguinte mostra que o levantamento ficou pendente.

## Canal de aviso: celular

Decidido em 2026-11-10: o aviso chega no celular dela.

- **Agora:** evento recorrente na agenda "Prazos – Escritório" ("Levantamento de andamentos: entre no PJe"), com notificação no horário, e notificação do app do Claude quando a rotina rodar.
- **Depois:** mensagem no WhatsApp dela, quando o canal descrito em `propostas/whatsapp.md` estiver funcionando. O aviso vai só para o número dela.

## Prompt sugerido

> Execute o levantamento de andamentos da skill consulta-portais. Primeiro, avise a advogada para entrar no PJe do TJPA no Chrome e aguarde ela confirmar na conversa que está logada. Não toque na tela de login. Depois, leia `processos-acompanhados.md`, ignore pastas com `SIGILOSO.txt` e consulte cada processo marcado como "acompanhar", só para leitura, um por vez. Registre movimentações, intimações, prazos copiados do portal, audiências e perícias. Atualize as fichas dos processos, salve o relatório em `levantamentos/` e, para cada prazo novo, gere análise e minuta `v1` como rascunho. Não peticione, não protocole, não confirme ciência de intimação e não clique em botões de ação. Se aparecer CAPTCHA, limite ou sessão expirada, pare e informe.

## Cuidados

- **Ciência de intimação.** No PJe, abrir certos expedientes pode registrar a ciência e começar a contar o prazo. O Claude não abre expediente que tenha esse efeito: lista o expediente e deixa a abertura para a advogada. Confirmar com ela como isso aparece na tela do TJPA antes do primeiro uso `[VERIFICAR]`.
- **Termos de uso.** Conferir os termos do PJe do TJPA e do Meu INSS sobre consulta assistida por ferramenta antes de ligar a rotina `[VERIFICAR]`. Se houver restrição, a rotina fica só com o aviso e a leitura do painel que ela mesma abrir.
- **Sigilo.** Processos em segredo de justiça não entram na lista.
- **Agenda física.** Continua em uso até a rotina ser validada lado a lado por algumas semanas.

## Saída

`levantamentos/AAAA-MM-DD_portal.md` na raiz da pasta `Clientes`, linhas novas nas `ficha-processo.md`, minutas `v1` em `04 Minutas/` e resumo na conversa.
