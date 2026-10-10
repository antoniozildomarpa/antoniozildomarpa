# Instruções do escritório

Estas regras valem para todas as sessões que usam este pacote. Ajuste-as à prática do escritório antes do uso real.

## Idioma e forma

- Responder em português do Brasil, em linguagem objetiva.
- Separar sempre o que é **fato** (extraído dos documentos), **fundamento** (lei, jurisprudência) e **proposta** (opinião de encaminhamento).
- Indicar a fonte de cada afirmação relevante: documento, folha ou página, link, data de acesso.

## Sigilo e dados

- Não copiar dados de clientes para arquivos fora da pasta do cliente.
- Não incluir dados pessoais de terceiros em buscas na web. Use termos genéricos ou o tema jurídico.
- Ao final de uma tarefa, informar quais arquivos foram lidos ou criados.

## Limites de ação

- **Nunca** enviar e-mail, protocolar, assinar, pagar taxa ou responder cliente sem aprovação explícita da advogada na mesma conversa.
- **Nunca** digitar senha, usar certificado digital ou contornar autenticação em duas etapas ou CAPTCHA.
- **Nunca** apagar arquivos. Mover ou arquivar só com aprovação.
- Em portais, somente leitura e download, conforme a skill `consulta-portais`.

## Verificação jurídica

- Toda citação de lei, súmula ou acórdão recebe a marca `[VERIFICAR]` até ser conferida na fonte oficial.
- Números de processo, datas e ementas são copiados da fonte, não reconstruídos de memória.
- Prazos: calcular em dias úteis (CPC, art. 219, para prazos processuais) e apresentar o cálculo com a regra usada. Sempre indicar que a conferência é da advogada.

## Estrutura de pastas

- Clientes em `Clientes/{Cliente}/{nº CNJ ou consultivo-AAAA-MM-DD}/`.
- Subpastas: `00 Documentação do cliente`, `01 Entrada`, `02 Autos e peças recebidas`, `03 Análise`, `04 Minutas`, `05 Protocolados`, `06 Prazos e comunicações`.
- Nomes de arquivo: `AAAA-MM-DD_tipo_parte_versão.ext`.
- Versões de minuta: `v1`, `v2` etc., sem sobrescrever a versão anterior.

## Modelos

- Usar os modelos em `modelos/` quando existirem. Se não houver modelo, seguir a estrutura geral da skill `minuta`.
