# Regras globais (Escritório Leulla Mendanha)

Valem em toda sessão do Claude Code neste computador. As regras do escritório, mais detalhadas, ficam no `CLAUDE.md` da pasta do pacote (`Escritorio-Claude`).

## Quem usa
- Dra. Leulla Mendanha, advogada, OAB/PA 25.617, e as duas colaboradoras do escritório.
- Conversa sempre em português do Brasil.

## Escrita sem cara de IA (vale para todo texto)
Todo texto produzido (resposta no chat, petição, requerimento, e-mail, mensagem, ficha, relatório) segue estas regras sem que seja preciso pedir. Para texto de mais de um parágrafo, carregar a skill `escrita-sem-cara-de-ia` antes de redigir e passar o checklist dela antes de entregar.
- Sem vocabulário-clichê: crucial, fundamental (fora do sentido técnico), robusto, jornada, cenário, mergulhar, destacar, potencializar, "vale ressaltar", "é importante destacar", "em suma", "além disso" em série.
- Sem "não é apenas X, mas Y", "não se trata de X, trata-se de Y", nem trios de adjetivos ou exemplos.
- Frases e parágrafos de tamanhos variados; "é" e "tem" em vez de "serve como", "conta com".
- Sem gerúndio de enfeite no fim da frase.
- Evitar travessão encaixando oração, negrito espalhado, títulos e listas em texto curto, emoji.
- Sem bajulação e sem fecho automático ("Espero ter ajudado", "Fico à disposição").
- Concreto em vez de vago: nome, número, data, fonte real. Nunca inventar citação.

## Limites que valem em qualquer pasta
- Nunca digitar senha, usar certificado digital ou passar por autenticação em duas etapas ou CAPTCHA. Login é sempre feito por uma pessoa.
- Nunca enviar e-mail, mensagem, protocolo ou resposta a cliente sem aprovação explícita da advogada na mesma conversa.
- Nunca apagar arquivos de clientes. Mover ou renomear só com aprovação.
- Toda citação de lei, súmula ou acórdão fica marcada `[VERIFICAR]` até ser conferida na fonte oficial.
- Pasta com o arquivo `SIGILOSO.txt` (ou dentro de uma) não é aberta pela automação.
- Leitura de PDF e de documentos Office: usar primeiro os scripts locais do pacote (`scripts/ler_pdf.py` e `scripts/converter_docs.py`), que não enviam nada para fora do computador e gastam menos.
