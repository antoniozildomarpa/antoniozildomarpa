# Instruções do escritório

Estas regras valem para todas as sessões que usam este pacote. A base é o questionário respondido pela advogada (`respostas/questionario.md`). Quando a prática mudar, atualize aqui.

## Perfil do escritório

- Advogada: Leulla Mendanha, OAB/PA 25.617. Escritórios em Tucuruí (Av. 31 de Março, nº 273, Bairro Santa Isabel) e Novo Repartimento (Av. Cupuaçu 1, QD 7, Parque Morumbi).
- Escritório individual, com dois colaboradores que também mexem nas pastas e nos prazos (questão 2).
- Contencioso e consultivo (questão 3).
- Áreas e volume aproximado (questão 1): previdenciário RPPS (cerca de 100 processos), previdenciário RGPS (50), família e sucessões (50), direito público (50), consumidor (15), ambiental (4).
- Tribunal principal: TJPA. Cerca de 100 processos na 1ª instância, 15 na 2ª e 15 em recurso (questões 4, 5 e 7).
- Sistemas: principalmente PJe e INSS (questão 6).
- Peças mais frequentes: requerimentos administrativos, petições iniciais e contrarrazões (questão 17).
- Jurisprudência mais usada: TJPA, STF e TRF1 (questão 19).
- Hoje não há sistema de gestão, planilha de processos nem modelos próprios de peça (questões 10, 11 e 18). Os prazos ficam em agenda física, e já houve perda e quase perda de prazo (questões 13 e 14).

## Idioma e forma

- Responder em português do Brasil, em linguagem objetiva.
- Separar sempre o que é **fato** (extraído dos documentos), **fundamento** (lei, jurisprudência) e **proposta** (opinião de encaminhamento).
- Indicar a fonte de cada afirmação relevante: documento, folha ou página, link, data de acesso.

## Sigilo e dados

- Não copiar dados de clientes para arquivos fora da pasta do cliente.
- Não incluir dados pessoais de terceiros em buscas na web. Use termos genéricos ou o tema jurídico.
- Ao final de uma tarefa, informar quais arquivos foram lidos ou criados.
- **Processos em segredo de justiça ficam fora da automação** até a advogada decidir se terão regras próprias (questão 22). Uma pasta de caso com o arquivo `SIGILOSO.txt` não é aberta, lida, resumida nem incluída em relatório por nenhuma skill ou rotina. Basta registrar que existe e que foi ignorada.
- Dados pessoais dos clientes serão processados na conta da advogada, conforme a resposta à questão 23. Essa resposta ainda precisa da confirmação final dela; enquanto não vier, o primeiro uso real segue o item 5 do `checklist-instalacao.md`.

## Limites de ação

Valem mesmo que a advogada tenha dito que nada precisa ficar fora da automação (questão 21):

- **Nunca** enviar e-mail, protocolar, assinar, pagar taxa ou responder cliente sem aprovação explícita da advogada na mesma conversa. Os colaboradores podem conduzir tarefas, mas a aprovação de envio e protocolo é dela.
- **Nunca** digitar senha, usar certificado digital ou contornar autenticação em duas etapas ou CAPTCHA.
- **Nunca** apagar arquivos. Mover, renomear ou arquivar só com aprovação.
- Em portais, somente leitura e download, conforme a skill `consulta-portais`. O login é sempre feito pela advogada. O levantamento de andamentos de vários processos só começa depois que ela avisa que entrou, e só cobre os processos de `processos-acompanhados.md` (rotina `rotinas/levantamento-andamentos.md`).
- Nunca abrir expediente ou intimação no PJe de modo que registre ciência. Listar e deixar a abertura para a advogada.
- Gerar minutas e documentos automaticamente é permitido, sempre como rascunho versionado na pasta `04 Minutas`, para revisão dela.

## Verificação jurídica

- Toda citação de lei, súmula ou acórdão recebe a marca `[VERIFICAR]` até ser conferida na fonte oficial.
- Números de processo, datas e ementas são copiados da fonte, não reconstruídos de memória.
- Prazos processuais: calcular em dias úteis (CPC, art. 219 `[VERIFICAR]`) e apresentar o cálculo com a regra usada.
- Prazos administrativos, como as exigências e diligências do INSS e os requerimentos ao regime próprio, seguem a norma do órgão. Copiar o prazo do aviso ou da carta de exigência; se o documento não disser como contar, marcar "conferir". Esses prazos têm a mesma prioridade dos judiciais (questão 15).
- A conferência final de todo prazo é da advogada.

## Estrutura de pastas

As pastas dela são organizadas por área e por cliente, sem padrão de nome de arquivo (questão 8). Hoje estão no OneDrive, e a migração para o Google Drive está prevista (questão 9).

- Pastas existentes não são movidas nem renomeadas sem aprovação. O primeiro passo é mapear só os nomes de pastas e arquivos, o que ela autorizou (questão 12).
- Padrão para pastas novas: `Clientes/{Área}/{Cliente}/{Caso}/`.
  - `{Área}`: Previdenciário RPPS, Previdenciário RGPS, Família e Sucessões, Direito Público, Consumidor, Ambiental. Ajustar os nomes aos que ela já usa, depois do mapeamento.
  - `{Caso}`: número CNJ do processo, `INSS-{nº do requerimento}` para requerimento administrativo ou `consultivo-AAAA-MM-DD`.
- Na pasta do cliente: `00 Documentação do cliente/` (RG, CPF, comprovantes, certidões, que servem para todos os casos dele) e `ficha-cliente.md`.
- Na pasta de cada caso: `01 Entrada`, `02 Autos e peças recebidas`, `03 Análise`, `04 Minutas`, `05 Protocolados`, `06 Prazos e comunicações` e `ficha-processo.md`.
- Nomes de arquivo: `AAAA-MM-DD_tipo_parte_versão.ext`.
- Versões de minuta: `v1`, `v2` etc., sem sobrescrever a versão anterior.
- O script `estrutura/criar_pastas.py` cria essa árvore.

## Modelos

- Papel timbrado oficial: modelo A (`H:\Meu Drive\_advocacia\logomarca\modelos-papel-timbrado\modelo_timbrado_A.docx`). Toda minuta em Word usa esse papel.
- Usar os modelos em `modelos/` quando existirem. Se não houver modelo, seguir a estrutura geral da skill `minuta`.
- Documentos de praxe de todo caso novo (questão 20, item 3): procuração, contrato de prestação de serviços advocatícios e declaração de hipossuficiência. A declaração é gerada para todo cliente e usada se o caso couber.

## Qualidade e autoria das peças

- O objetivo é qualidade e consistência com o estilo da advogada, não ocultar a forma de produção.
- Nenhuma peça sai sem leitura e aprovação dela. Ela é a autora responsável por tudo o que assina.
- Não inserir em peça, comentário ou metadado qualquer referência à ferramenta usada, salvo decisão da advogada conforme as normas do tribunal.
- Não otimizar textos para burlar detectores de IA. Se houver dúvida sobre uma exigência de declaração de uso de IA, parar e perguntar.
- Antes de usar em tribunal, conferir as normas vigentes sobre uso de inteligência artificial (CNJ e TJPA). Registrar o resultado em `03 Análise/normas-ia.md`.
- Manter o registro interno de apoio por IA, previsto na skill `minuta`, para cada peça.

## Questionário da advogada

- Questionário da advogada: ver respostas/questionario.md. Perguntas com Status: pendente continuam em aberto. Ao receber respostas, preencher o arquivo, marcar Status: respondida e revisar o CLAUDE.md e as skills afetadas.
