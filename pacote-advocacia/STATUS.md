# Status do pacote de advocacia

Este arquivo é o ponto de partida para retomar o trabalho, em qualquer sessão. Atualize-o a cada etapa concluída.

Última atualização: 2026-10-10

## Onde estamos

- **Fase atual:** coleta de respostas da advogada (questionário de 23 perguntas, entregue por você a ela).
- **Pacote inicial:** criado e commitado (commit `e333d19`), em rascunho. Não foi testado com caso real.
- **Estrutura de pastas:** o padrão atual é só uma proposta. A advogada já tem pastas organizadas por cliente e processo, então o pacote deve se adaptar ao que existe, não o contrário.

## Decisões já tomadas

1. Ela usará Claude in Chrome, app desktop do Claude e Claude code, conforme a necessidade de cada ação.
2. Consultas em portais serão somente leitura e download, com a sessão dela. Peticionamento fica manual nas primeiras fases.
3. Credenciais, senhas, certificado digital e autenticação em duas etapas nunca são tratados pelo agente.
4. Nenhum envio de e-mail, protocolo ou resposta a cliente sem aprovação explícita dela.
5. Toda citação jurídica é marcada `[VERIFICAR]` até conferência na fonte oficial.
6. Dados de clientes ficam só na conta dela. O pacote não contém dados reais.
7. O pacote é portável: skills, instruções, modelos e roteiros são transferidos. Conexões, rotinas agendadas e acessos são recriados na conta dela.

## Pendências

- [ ] Respostas ao questionário (blocos A a F), a serem salvas em `respostas/questionario.md`.
- [ ] Confirmar se ela autoriza a leitura apenas dos **nomes** de pastas e arquivos, para mapear a organização atual.
- [ ] Definir área de atuação e tribunais principais (questões A e B).
- [ ] Verificar se há processos em **segredo de justiça** e se precisam de regras separadas (questão 22).
- [ ] Confirmar quais dados podem sair do computador dela (questão 23).
- [ ] Revisar `CLAUDE.md` e skills com base nas respostas.
- [ ] Substituir o `criar_pastas.py` por um mapeamento da organização existente, se for o caso.
- [ ] Criar a ficha de processo (tribunal, instância, sistema, fase, próximo prazo, status), por causa dos muitos processos em andamento.
- [ ] Teste com caso fictício, conforme `checklist-instalacao.md`.
- [ ] Criar as rotinas na conta dela, uma por vez.

## Premissas em aberto

- E-mail: Gmail ou Outlook ainda não definido. Só o Outlook (Microsoft 365) aparece como conector, com conexão incompleta.
- Local das pastas: Drive, OneDrive/SharePoint ou outro, ainda não confirmado.
- Sistema de gestão de processos: não definido.

## Para retomar

1. Ler este arquivo.
2. Ler `respostas/` (quando existir).
3. Ler `README.md` e `CLAUDE.md`.
4. Continuar pela primeira pendência não marcada.
