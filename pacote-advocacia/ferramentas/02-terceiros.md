# Ferramentas de terceiros

Avaliar somente depois das ferramentas nativas. Para cada item, testar com dados fictícios antes de qualquer uso real.

Antes de instalar, verifique: quem mantém a ferramenta, onde os dados são processados, se há contrato de tratamento de dados (LGPD) e se o código é público quando se trata de servidor MCP comunitário.

Legenda de status: `[ ]` pendente · `[~]` em teste com dados fictícios · `[x]` aprovado para uso real · `[-]` descartado

---

## Pesquisa jurisprudencial brasileira

### A. Jurídico AI (conector MCP comercial)

- **[ ] Status:** pendente
- **O que agiliza:** busca de jurisprudência com resposta que indica a fonte para conferência. Reduz o tempo de pesquisa inicial da skill `pesquisa-juridica`.
- **Como instalar:** siga a documentação do fornecedor em https://juridico.ai/mcp-da-juridico.md. Normalmente envolve criar conta, gerar uma chave ou URL do servidor e adicioná-la como conector na conta dela. Confirme o procedimento atual no próprio material.
- **Como executar:**
  > Use o conector da Jurídico AI para buscar decisões do STJ sobre [tema genérico]. Para cada decisão, retorne número, relator, data e link. Marque como Não conferido o que não estiver na fonte oficial.
- **Riscos:** é um fornecedor comercial, e as alegações de acervo não foram verificadas de forma independente. Dados de clientes não devem ser enviados. Consultas devem ser genéricas.
- **Critério para aprovar:** comparar 10 decisões retornadas com a fonte oficial. Se mais de uma não existir ou estiver errada, descartar.

### B. Servidores MCP para dados públicos de tribunais (comunitários)

- **[ ] Status:** pendente
- **Exemplos encontrados:** servidor para o TJPR (https://glama.ai/mcp/servers/y8kjqnkx5k) e para o TJTO (https://glama.ai/mcp/servers/forptdvjpm). Há também servidor para o PJe (https://glama.ai/mcp/servers/chapirousIA/pje-mcp-server), que exige certificado digital e, por isso, **não deve ser usado pelo agente**.
- **O que agiliza:** consulta direta de processos públicos e comunicações, sem abrir o portal manualmente.
- **Como instalar:** adicione o servidor como MCP na configuração do Claude Code (arquivo `.mcp.json` na pasta do projeto) ou no app desktop, conforme a documentação atual. Antes, leia o código-fonte e o repositório do servidor. Não instale servidor sem código público verificável.
- **Como executar:** consulta apenas por número de processo público, sem dados de partes. Exemplo:
  > Consulte o processo público de número X no TJPR e liste a última movimentação.
- **Riscos:** cobertura limitada a tribunais específicos. Servidores comunitários podem ser abandonados. Não envie dados sigilosos.
- **Critério para aprovar:** o código é público, a última atualização é recente, e o resultado bate com o portal oficial em cinco processos de teste.

## Plugins e conectores do catálogo oficial

### C. Plugin "Legal" (catálogo Anthropic)

- **[ ] Status:** pendente
- **O que agiliza:** modelos de fluxo para revisão de contratos, triagem de NDA, rascunho de peças, gestão de conhecimento e checagem de compliance. Usa conectores de Gmail, Google Calendar e Drive.
- **Como instalar:** pelo catálogo de plugins da conta dela. Busque "Legal" e instale. Os conectores (Gmail, Calendar, Drive) pedem autorização dela, separadamente.
- **Como executar:** o plugin traz comandos próprios. Use-o como referência de fluxo, e não como substituto das skills do pacote, porque ele é voltado a departamentos jurídicos internos, nos EUA.
- **Riscos:** muitos fluxos são de contratos de empresa, que não se aplicam diretamente à advocacia contenciosa. Avalie o que serve.
- **Critério para aprovar:** usar o fluxo de triagem em dez e-mails fictícios e comparar com a triagem da skill.

### D. Legal Data Hunter (catálogo)

- **[ ] Status:** pendente, antes de tudo, verificar cobertura do Brasil
- **O que agiliza:** busca em mais de 23 milhões de documentos jurídicos, em 160 jurisdições.
- **Como instalar:** pelo catálogo de conectores. Antes de instalar, confirme se o Brasil e os tribunais de interesse estão na lista (`discover_countries` e `discover_sources`, na própria ferramenta).
- **Riscos:** se o Brasil não estiver coberto, descartar.

### E. Stintwell for Law Firms (catálogo)

- **[ ] Status:** pendente
- **O que agiliza:** gestão do escritório, com foco em caixa, captação de clientes, operação e contratação. Complementa o painel financeiro com diagnóstico de gargalos.
- **Como instalar:** pelo catálogo de plugins. Plugin da comunidade, com descrição que diz não ser consultoria jurídica.
- **Como executar:** peça um diagnóstico de caixa com dados fictícios, para ver se as sugestões fazem sentido.
- **Riscos:** conecta a dados financeiros. Só usar com dados fictícios até avaliar o fornecedor e o tratamento de dados.
- **Critério para aprovar:** o diagnóstico com dados fictícios ser útil e coerente com o que ela já sabe do escritório.

### F. LegalizaObra (catálogo)

- **[-] Status:** descartado por enquanto
- **Motivo:** cuida de INSS de obras de construção (eSocial, DARF). Só faz sentido se ela atender clientes de construção. Reavaliar apenas nesse caso.

## Ferramentas de outros países (não recomendadas para o Brasil)

Estas ferramentas são voltadas a direito dos EUA, Espanha, Emirados ou Vietnã. Não servem à advocacia brasileira, e foram descartadas para este pacote:

- **[-] CoCounsel Legal e CoCounsel (plugin):** pesquisa no acervo do Westlaw, dos EUA.
- **[-] Paxton Legal Research, Descrybe, Midpage, CourtListener:** direito dos EUA.
- **[-] realLaw AI:** legislação dos Emirados Árabes.
- **[-] regai (Vietnã) e Contratos laborales/civiles (Espanha):** outras jurisdições.
- **[-] LegalZoom e Rocket Lawyer:** serviços de consultoria jurídica para consumidores nos EUA.
- **[-] Legal Brain Agent:** direito japonês.
- **[-] Reco:** segurança de SaaS, sem aplicação para advocacia.
- **[-] Law-student (plugin):** voltado a estudo para a ordem jurídica dos EUA.

## Fontes

- [Jurídico AI – MCP](https://juridico.ai/mcp-da-juridico.md)
- [Jurídico AI – página principal](https://juridico.ai/?p=14351)
- [Jurídico AI – como pesquisar jurisprudência com Claude](https://juridico.ai/blog/advogados/como-pesquisar-jurisprudencia-claude.md)
- [Servidor MCP para o TJPR](https://glama.ai/mcp/servers/y8kjqnkx5k)
- [Servidor MCP para o TJTO](https://glama.ai/mcp/servers/forptdvjpm)
- [Servidor MCP para o PJe](https://glama.ai/mcp/servers/chapirousIA/pje-mcp-server)
- [Discussão sobre servidor MCP para PJe](https://tecjustica.substack.com/p/claude-desktop-mcp-server-pje-sua/comments)
