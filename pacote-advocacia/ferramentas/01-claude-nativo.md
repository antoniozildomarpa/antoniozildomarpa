# Ferramentas nativas do Claude

Ferramentas do próprio Claude, sem fornecedor externo. Avaliar nesta ordem.

Antes de instalar qualquer item, confirme na conta dela os menus atuais (Configurações, Conectores, Skills, Extensões). Os caminhos mudam com frequência, e este arquivo não substitui a documentação oficial.

Legenda de status: `[ ]` pendente · `[~]` em teste com dados fictícios · `[x]` aprovado para uso real

---

## 1. Skill de Word (docx)

- **[ ] Status:** pendente
- **O que agiliza:** gera minutas em Word a partir dos modelos do escritório, preenche campos (cliente, processo, pedidos) e cria novas versões sem apagar a anterior. Lê e aplica comentários e controle de alterações.
- **Como instalar:** já aparece como skill disponível nesta sessão. Na conta dela, confirme em Configurações > Skills se a skill de Word está ativa. Se não estiver, ative-a. Em Claude Code, a skill também pode ser colocada em `.claude/skills/`.
- **Como executar:**
  > Preencha o modelo `modelos/contestacao.docx` com os dados da pasta `03 Análise/`. Salve em `04 Minutas/` como `v1`, sem sobrescrever versões anteriores. Marque com `[VERIFICAR]` cada citação não conferida.
- **Limites:** o texto final é sempre revisado por ela. Formatação complexa de modelos antigos pode precisar de ajuste manual.

## 2. Skill de PDF

- **[ ] Status:** pendente
- **O que agiliza:** extrai texto de autos digitalizados (OCR), gera índice de peças com número de página, extrai tabelas (cálculos, planilhas de valores), junta e separa PDFs para anexar a petições.
- **Como instalar:** mesmo caminho da skill de Word. Confirme que a skill de PDF está ativa.
- **Como executar:**
  > Leia os PDFs da pasta `02 Autos e peças recebidas/`. Gere um índice com nome da peça, data e páginas. Para digitalizações ilegíveis, marque `[OCR INCERTO]`.
- **Limites:** OCR em digitalizações ruins pode trocar números e datas. Qualquer número extraído deve ser conferido no original antes de entrar em peça.

## 3. Skill de planilha (xlsx)

- **[ ] Status:** pendente
- **O que agiliza:** conciliação entre extrato e recebimentos, fechamento mensal, exportação para o contador, fórmulas de saldo e inadimplência.
- **Como instalar:** mesma verificação de skills. Não precisa de instalação adicional.
- **Como executar:**
  > Compare o extrato em `financeiro/extrato-AAAA-MM.csv` com a aba `Recebimentos`. Liste os lançamentos sem correspondência, com valor e data, e não altere a aba original.
- **Limites:** conciliação automática sugere pares, mas a decisão de baixa é dela.

## 4. Claude Docs (docs)

- **[ ] Status:** pendente
- **O que agiliza:** minutas e pareceres compartilháveis, em que ela comenta trechos e o Claude responde nos comentários. Boa forma de revisão sem sair do fluxo.
- **Como instalar:** verifique se o conector de documentos está disponível na conta dela. Nesta sessão ele aparece como conector de Docs.
- **Como executar:** peça um documento novo ou a edição de um existente. Para revisão, peça que o Claude responda aos comentários dela.
- **Limites:** documentos com dados de clientes ficam no ambiente do Docs. Antes de usar com dados reais, verifique onde ficam armazenados e quem tem acesso.

## 5. Skill de visualização (dataviz)

- **[ ] Status:** pendente
- **O que agiliza:** gráficos e indicadores do painel financeiro: receita mensal, parcelas em atraso por faixa de dias, alvarás pendentes.
- **Como instalar:** mesma verificação de skills.
- **Como executar:**
  > A partir do CSV exportado do painel, gere um gráfico de receita por mês e um indicador de parcelas vencidas há mais de 30 dias.
- **Limites:** o painel precisa exportar dados em formato limpo. Dados mal estruturados geram gráficos enganosos.

## 6. Claude Code

- **[ ] Status:** pendente
- **O que agiliza:** é o ambiente de trabalho principal do pacote. Permite rodar skills, subagentes para tarefas paralelas (ex.: triagem e pesquisa ao mesmo tempo), hooks para bloquear ações indevidas e rotinas agendadas.
- **Como instalar:** siga a documentação oficial atual do Claude Code para o sistema operacional dela. Não coloquei comandos de instalação aqui, porque mudam entre versões. Depois de instalado, abra a pasta do pacote e confirme que as skills em `.claude/skills/` aparecem.
- **Como executar:** no terminal, dentro da pasta do pacote, inicie o Claude Code e peça a tarefa em linguagem natural. Exemplo:
  > Use a skill triagem-email para a caixa de entrada de hoje.
- **Hooks úteis para este caso:** um hook pode bloquear automaticamente qualquer tentativa de envio de e-mail ou protocolo. É uma camada extra de segurança, além do `CLAUDE.md`. Configurar hooks é tarefa para o skill de configuração (`update-config`).
- **Limites:** o uso no terminal exige algum conforto com linha de comando. Se isso for um obstáculo, o app desktop cobre boa parte do mesmo fluxo.

## 7. Rotinas agendadas

- **[ ] Status:** pendente
- **O que agiliza:** triagem de e-mail, alerta de prazos e relatórios sem intervenção manual. Já estão roteirizadas em `rotinas/`.
- **Como instalar:** são criadas na conta dela, pelo Claude Code ou pela interface de rotinas, a partir dos arquivos em `rotinas/`. Não são transferidas como arquivo.
- **Como executar:** cada rotina tem frequência, conectores necessários e o prompt. Crie uma por vez e revise a primeira semana de saídas antes de manter.
- **Limites:** rotinas que dependem de e-mail só funcionam depois de o conector de e-mail estar conectado na conta dela.

## 8. Claude in Chrome

- **[ ] Status:** pendente
- **O que agiliza:** consultas e downloads em portais de tribunais e de órgãos, com a sessão já logada por ela. Evita trocar dados manualmente.
- **Como instalar:** instale a extensão Claude in Chrome a partir da loja de extensões do Chrome, buscando pelo nome oficial. Confirme que é a extensão do fornecedor oficial. Faça login com a conta do Claude e aprove o acesso aos sites necessários.
- **Como executar:** ela abre o portal e faz o login. Depois, pede a consulta:
  > Consulte o processo de número X no portal, leia a última movimentação e liste os documentos disponíveis. Não baixe nada até eu aprovar.
- **Limites:** segue a skill `consulta-portais`. Login, certificado e CAPTCHA continuam com ela. Portais podem restringir automação, então confira os termos.

## 9. App desktop do Claude (com controle de computador)

- **[ ] Status:** pendente
- **O que agiliza:** operar programas locais que não têm API, como leitor de PDF, programa de contabilidade ou sistema de gestão instalado no computador. Útil para tarefas repetitivas de lançamento.
- **Como instalar:** baixe o app oficial do Claude para o sistema dela. Ative o controle de computador em Configurações. No macOS, o sistema vai pedir permissões de acessibilidade e de gravação de tela, que devem ser concedidas por ela.
- **Como executar:** a partir do app, peça a tarefa e acompanhe. Antes de ações em programas com dados financeiros, confirme com ela, porque a skill de controle de computador tem regras de cautela para apps sensíveis.
- **Limites:** cada ação passa por tela. É mais lento que uma API e exige que ela esteja presente. Nenhuma ação de pagamento ou envio deve ser delegada sem confirmação.
