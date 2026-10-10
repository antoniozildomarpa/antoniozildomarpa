# Checklist de instalação e primeiro uso

Siga na ordem. Cada etapa tem um critério de conclusão.

## 1. Preparação

- [ ] Copiar a pasta `pacote-advocacia/` para a conta ou computador dela (ou clonar o repositório privado).
- [ ] Revisar o `CLAUDE.md` e ajustar as regras à prática do escritório.
- [ ] **Critério:** o `CLAUDE.md` reflete as regras de sigilo, protocolo e verificação do escritório.

## 2. Conectores e acessos (na conta dela)

- [ ] Conectar Google Drive e Google Calendar.
- [ ] Conectar o e-mail (Gmail ou Outlook) para a skill `triagem-email`.
- [ ] Instalar o Claude in Chrome ou usar o app desktop, para a skill `consulta-portais`.
- [ ] **Critério:** cada conector aparece como conectado e cada acesso foi feito por ela, sem compartilhamento de senha ou certificado.

## 3. Estrutura de pastas

- [ ] Rodar uma simulação: `python estrutura/criar_pastas.py --base ~/Clientes --cliente "Cliente Fictício" --dry-run`.
- [ ] Criar de fato, se a simulação estiver correta.
- [ ] **Critério:** a árvore criada tem as sete subpastas padrão.

## 4. Teste com caso fictício

- [ ] Criar um cliente e processo fictícios.
- [ ] Rodar `analise-demanda` com um documento de teste.
- [ ] Rodar `pesquisa-juridica` sobre um tema conhecido e conferir as fontes.
- [ ] Rodar `minuta` e verificar as marcações `[VERIFICAR]`, `[CONFIRMAR]` e `[DECIDIR]`.
- [ ] **Critério:** cada saída segue o formato da skill e nenhuma citação aparece sem status.

## 5. Primeiro caso real (somente leitura)

- [ ] Confirmar que o escritório autoriza tratar dados do cliente nesta ferramenta.
- [ ] Rodar triagem e análise, sem envio e sem protocolo.
- [ ] Conferir cada prazo e cada citação na fonte oficial.
- [ ] **Critério:** a advogada revisou a análise e a minuta, e nada foi enviado pela automação.

## 6. Rotinas recorrentes

- [ ] Criar as rotinas a partir dos arquivos em `rotinas/`, uma por vez, começando pelo alerta de prazos.
- [ ] Revisar a primeira semana de saídas antes de manter a rotina.
- [ ] **Critério:** as saídas são úteis e as ações indevidas ficaram bloqueadas.

## 7. Revisão periódica

- [ ] Revisar mensalmente as skills e as regras do `CLAUDE.md`.
- [ ] Atualizar o pacote conforme a prática mudar.
- [ ] Considerar liberar ações mais amplas (envio, protocolo assistido) só depois de um período de uso sem falhas, e sempre com confirmação explícita.
