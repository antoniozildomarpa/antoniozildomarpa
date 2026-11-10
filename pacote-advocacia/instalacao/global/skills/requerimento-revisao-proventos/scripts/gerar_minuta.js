// Gera a minuta Word do requerimento de revisão de proventos a partir do caso.json.
// Uso: node gerar_minuta.js caminho/caso.json "saida.docx" [--forcar]
// O caso.json precisa ter passado antes pelo calc_retroativos.py (bloco "calculo").
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell, WidthType,
        BorderStyle, ShadingType, Footer, PageNumber } = require('docx');

const [, , arqCaso, saida, flag] = process.argv;
const caso = JSON.parse(fs.readFileSync(arqCaso, 'utf8'));
const { requerente: R, beneficio: B, planilha: P, gratificacao: G, calculo: K } = caso;
if (!K) { console.error('ERRO: rode antes o calc_retroativos.py'); process.exit(1); }
if (!B.integral && flag !== '--forcar') {
  console.error('ERRO: aposentadoria sem integralidade; a tese do item 8 não se aplica. Revise o texto ou use --forcar.');
  process.exit(1);
}

const fem = R.genero !== 'M';
const a = fem ? 'a' : 'o';                 // artigo: a/o requerente
const da = fem ? 'da' : 'do', aA = fem ? 'à' : 'ao';
const br = v => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pct = `${Math.round(G.percentual * 100)}%`;
const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
const [mf, af] = K.mes_final.split('/');
const mesFinal = `${MESES[+mf - 1]} de ${af}`;
const dib = B.dib.split('-').reverse().join('/');
const lista = l => l.length > 1 ? `${l.slice(0, -1).join(', ')} e ${l[l.length - 1]}` : l[0];
// gratificação também sobre as horas normais (Lei 11.920/2023), quando a planilha as inclui
const hn = !!G.sobre_horas_normais;
const baseTxt = hn ? 'sobre o vencimento base e sobre as horas normais' : 'sobre o vencimento base';
const citInt = B.citacao_integralidade || 'totalidade da remuneração do cargo efetivo em que se der a aposentadoria';

const F = 'Times New Roman', SZ = 24;
// espaço inquebrável após "R$" para o valor não ficar na linha seguinte
const r = (t, o = {}) => new TextRun({ text: t.replace(/R\$ /g, 'R$ '), font: F, size: SZ, ...o });
// parágrafo de corpo: justificado, recuo de primeira linha, entrelinha 1,5
const p = (runs, o = {}) => new Paragraph({
  children: typeof runs === 'string' ? [r(runs)] : runs,
  alignment: AlignmentType.JUSTIFIED, spacing: { line: 336, after: 100 },
  indent: { firstLine: 1134 }, ...o });
const c = (runs, o = {}) => p(runs, { alignment: AlignmentType.CENTER, indent: {}, ...o });
const sec = t => p([r(t, { bold: true })], { indent: {}, spacing: { before: 240, after: 120, line: 360 } });
const num = (n, titulo, texto) => p([r(`${n}. `), r(titulo, { bold: true }), r(' ' + texto)]);

const qualif = [R.nacionalidade, R.estado_civil].filter(Boolean).join(', ');
const corpo = [
  p([r('ILUSTRÍSSIMA SENHORA SUPERINTENDENTE DO INSTITUTO DE PREVIDÊNCIA DOS SERVIDORES MUNICIPAIS DE TUCURUÍ – IPASET', { bold: true })], { indent: {} }),
  p([r(`Processo de Benefício nº ${B.processo}`, { bold: true })], { indent: {}, spacing: { before: 360, after: 360, line: 360 } }),
  p([r(R.nome, { bold: true }), r(`, ${qualif}, ${fem ? 'aposentada' : 'aposentado'} no cargo de ${R.cargo}, matrícula nº ${R.matricula}, RG nº ${R.rg}, CPF nº ${R.cpf}${R.pis ? `, PIS/PASEP nº ${R.pis}` : ''}, ${fem ? 'residente e domiciliada' : 'residente e domiciliado'} em ${R.residencia}, vem, respeitosamente, com fundamento no art. 40, §§ 1º e 8º, da Constituição Federal, no art. 7º da EC nº 41/2003, no ${B.fundamentacao}, no art. 64, I, “i”, da Lei Municipal nº 9.757/2013 e nos arts. 27, I, “c”, e 31 da Lei Municipal nº 9.860/2016, requerer a`)]),
  c([r('REVISÃO DO CÁLCULO DOS PROVENTOS DE APOSENTADORIA', { bold: true })], { spacing: { before: 240, after: 240, line: 360 } }),
  p('pelos fatos e fundamentos a seguir.', { indent: {} }),

  sec('I – DOS FATOS'),
  p(`1. Pela Portaria nº ${B.portaria}-IPASET, de ${B.data_portaria}, foi concedida ${aA} requerente ${B.descricao}, nos termos do Parecer de Benefício nº ${B.parecer}.`),
  p(`2. A planilha de cálculo de ${P.data} fixou os proventos em R$ ${br(P.total)}, composta apenas por ${lista(P.parcelas)}.`),
  p(`3. Na atividade, ${a} requerente percebia, de forma regular e contínua, a Gratificação de Ensino Especial (gratificação de atendimento educacional especializado), no percentual de ${pct} ${baseTxt}${hn ? ' (rubricas “Gratificação Ensino Especial” e “Gratificação 20% Horas Normais”)' : ''}, conforme contracheques e fichas financeiras anexos. Essa parcela não constou da planilha de proventos, e o Parecer nº ${B.parecer} não apresentou fundamento para sua exclusão.`),

  sec('II – DO DIREITO'),
  num(4, 'Da natureza legal e permanente da gratificação.', 'A Lei Municipal nº 9.860/2016, que dispõe sobre o Plano de Cargos, Carreira e Remuneração do Magistério, estabelece no art. 27, I, “c”, a “gratificação de atendimento educacional especializado (classe especial)”, e no art. 31 a fixa em 20% sobre o vencimento base. Trata-se de vantagem de carreira, criada por lei, com percentual fixo, inerente à docência exercida no próprio cargo efetivo, e não de gratificação por função de confiança ou de caráter eventual.'),
  num(5, 'Da integração à base de contribuição.', 'O art. 64, I, “i”, da Lei Municipal nº 9.757/2013 determina que constitui base de contribuição “qualquer outra vantagem pecuniária legalmente estabelecida, não excluída pelo § 2º deste artigo”. A gratificação em questão não figura entre as exclusões taxativas do § 2º e não tem natureza temporária ou pro labore, pois era paga de forma continuada. Esse mesmo dispositivo fundamentou, na planilha deste IPASET, a inclusão das parcelas de Nível Superior e Pós-Graduação.'),
  num(6, 'Da isonomia de critério.', 'O Adicional por Tempo de Serviço, incluído nos proventos, está previsto no mesmo art. 27 da Lei nº 9.860/2016 (inciso II, “a”). Não há razão jurídica para tratar de modo diverso vantagens do mesmo rol legal, calculadas por percentual fixo sobre a mesma base.'),
  num(7, 'Da Lei Municipal nº 11.920/2023.', 'Ao dar nova redação ao art. 20, § 2º, da Lei nº 9.860/2016, com efeitos desde abril de 2004, o legislador municipal estabeleceu que sobre as horas normais da jornada do professor “incidirão todas as gratificações e os adicionais concedidos aos servidores integrantes do Magistério Público Municipal, previstos no artigo 27”. Reconheceu, assim, que as gratificações do art. 27 compõem a remuneração ordinária do cargo de professor.'
    + (hn ? ` O Parecer nº ${B.parecer} aplicou essa regra ao reconhecer que o Adicional por Tempo de Serviço e o Nível Superior incidem sobre o salário-base somado às horas normais, e assim foram calculados na planilha de proventos. Pelo mesmo critério, a gratificação de atendimento educacional especializado, prevista no mesmo art. 27, deve incidir sobre o vencimento base e sobre as horas normais, como era paga na atividade.` : '')),
  num(8, 'Da integralidade.', `Nos termos do ${B.fundamentacao}, reconhecido no Parecer nº ${B.parecer}, os proventos correspondem à “${citInt}”. Como a gratificação integrava a remuneração ${da} requerente no cargo efetivo, deve integrar os proventos.`),
  num(9, 'Das contribuições.', `Sendo a parcela integrante da base de contribuição por força de lei, eventual ausência de retenção na fonte decorre de falha do ente pagador e não pode ser oposta ${aA} ${fem ? 'segurada' : 'segurado'}. Ainda assim, em respeito ao caráter contributivo do regime (art. 40, caput, da CF), ${a} requerente manifesta concordância com o recolhimento das contribuições eventualmente devidas, na forma do art. 64, § 1º, da Lei nº 9.757/2013, inclusive mediante compensação com os valores retroativos.`),
  // precedente administrativo do próprio IPASET (opcional: bloco "precedente" no caso.json)
  ...(caso.precedente ? [num(10, 'Do precedente administrativo.', `Este próprio Instituto já reconheceu a incorporação da gratificação aos proventos em caso análogo. No Processo de Benefício nº ${caso.precedente.processo} (Portaria nº ${caso.precedente.portaria}-IPASET, de ${caso.precedente.data_portaria}, aposentadoria voluntária de professora, com integralidade e paridade), o Parecer de Benefício nº ${caso.precedente.parecer} e a planilha de cálculo de ${caso.precedente.planilha_data} incluíram nos proventos a Gratificação de Ensino Especial, no valor de R$ ${br(caso.precedente.valor)}, com o mesmo fundamento aqui invocado (art. 64, I, “i”, da Lei nº 9.757/2013 c/c art. 27, I, “c”, da Lei nº 9.860/2016), embora a parcela também não integrasse a base de contribuição na atividade. Portanto, a ausência de desconto previdenciário não foi óbice à inclusão. Negar ${aA} requerente o mesmo tratamento, em situação análoga, violaria os princípios da isonomia, da legalidade e da segurança jurídica (art. 37, caput, da CF). Os documentos do precedente constam dos arquivos deste Instituto, para consulta de ofício.`)] : []),

  sec('III – DOS PEDIDOS'),
  p('Ante o exposto, requer:'),
  p(`a) a revisão da planilha de cálculo dos proventos, com a inclusão da Gratificação de Atendimento Educacional Especializado (Ensino Especial), à razão de ${pct} ${baseTxt}, atualmente R$ ${br(K.diferenca_mensal)}, elevando os proventos para R$ ${br(K.proventos_revistos)}, com a consequente retificação da Portaria nº ${B.portaria};`),
  p(`b) o pagamento das diferenças retroativas desde a data de início do benefício (${dib}), inclusive sobre o 13º salário, que até ${mesFinal} somam R$ ${br(K.total_nominal)} nominais, ${K.selic ? 'corrigidas pela taxa SELIC (art. 3º da EC nº 113/2021)' : 'a serem corrigidas pela taxa SELIC (art. 3º da EC nº 113/2021)'}, conforme memória de cálculo anexa, sem prejuízo das parcelas que se vencerem no curso do processo.`),
  p('Termos em que pede deferimento.', { spacing: { before: 120, after: 120, line: 336 } }),
  p(`${caso.cidade_data || 'Tucuruí/PA'}, ____ de ________________ de ${caso.ano_requerimento || af}.`, { alignment: AlignmentType.RIGHT, indent: {} }),
  c('______________________________________', { spacing: { before: 200, after: 0 } }),
  c([r(R.nome, { bold: true })], { spacing: { after: 0 } }),
  c('Requerente', { spacing: { after: 120 } }),
  p([r('Anexos:', { bold: true })], { indent: {} }),
  ...caso.anexos.map(t => t.replace('{portaria}', B.portaria).replace('{planilha_data}', P.data).replace('{parecer}', B.parecer))
    .map((t, i) => p(`${i + 1}. ${t}`, { indent: { left: 567 }, spacing: { after: 0, line: 264 } })),
];

// Anexo: memória de cálculo
const W = [1200, 2306, 1400, 1300, 1400, 1400]; // soma 9006 = largura útil (A4, margens 3 cm e 2 cm)
const bd = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
const longa = K.linhas.length > 20; // tabela compacta para caber o anexo numa página
const cell = (t, i, { bold = false, head = false } = {}) => new TableCell({
  width: { size: W[i], type: WidthType.DXA }, borders,
  shading: head ? { type: ShadingType.CLEAR, fill: 'D9D9D9', color: 'auto' } : undefined,
  margins: { top: longa ? 10 : 40, bottom: longa ? 10 : 40, left: 80, right: 80 },
  children: [new Paragraph({ alignment: i >= 2 ? AlignmentType.RIGHT : AlignmentType.LEFT,
    children: [new TextRun({ text: t, font: F, size: longa ? 18 : 20, bold: bold || head })] })] });
const row = (v, o) => new TableRow({ children: v.map((t, i) => cell(t, i, o)) });
const tabela = new Table({ width: { size: 9006, type: WidthType.DXA }, columnWidths: W, rows: [
  row(['Competência', 'Parcela', 'Nominal (R$)', 'SELIC acum. (%)', 'Correção (R$)', 'Total (R$)'], { head: true }),
  ...K.linhas.map(l => row([l.competencia, l.parcela, br(l.nominal), br(l.selic_pct), br(l.correcao), br(l.total)])),
  row(['Total', '', br(K.total_nominal), '', br(K.total_correcao), br(K.total_geral)], { bold: true }) ] });

const decimo = K.linhas.find(l => l.parcela.startsWith('13º'));
const [ac, mc, dc] = K.data_calculo.split('-');
const mesAnterior = +mc === 1 ? `dez/${+ac - 1}` : `${MESES[+mc - 2].slice(0, 3)}/${ac}`;
const peq = t => p(t, { indent: {}, spacing: { after: 60, line: 276 } });
const anexo = [
  c([r('ANEXO – MEMÓRIA DE CÁLCULO DOS RETROATIVOS', { bold: true })], { pageBreakBefore: true }),
  c(`Gratificação de Atendimento Educacional Especializado (${pct}) – Processo nº ${B.processo}`, { spacing: { after: 240 } }),
  peq((hn
      ? `Diferença mensal: ${pct} × (R$ ${br(P.vencimento_base)} de vencimento base + R$ ${br(P.horas_normais)} de horas normais, conforme a planilha de ${P.data}) = R$ ${br(Math.round(G.percentual * (P.vencimento_base + P.horas_normais) * 100) / 100)}.`
      : `Diferença mensal: ${pct} × R$ ${br(P.vencimento_base)} (vencimento base da planilha de ${P.data}) = R$ ${br(Math.round(G.percentual * P.vencimento_base * 100) / 100)}.`)
      + ((caso.reajustes || []).length ? ` Reajustes do vencimento base considerados: ${caso.reajustes.map(x => `R$ ${br(x.vencimento_base)} a partir de ${x.a_partir.split('-').reverse().join('/')}`).join('; ')}.` : '')),
  peq(`Termo inicial: ${dib}.` + (K.linhas[0].parcela.includes('dias') ? ` Primeiro mês proporcional (${K.linhas[0].parcela.match(/\d+\/\d+ dias/)[0]}).` : '') + (decimo ? ` 13º salário de ${decimo.competencia.slice(3)} ${decimo.parcela.includes('/') ? 'proporcional a ' + decimo.parcela.match(/\d+\/12/)[0] : 'integral'}.` : '')),
  peq(K.selic
    ? `Correção e juros: taxa SELIC (art. 3º da EC nº 113/2021), somadas as taxas mensais do mês seguinte ao vencimento até ${mesAnterior}, mais 1% no mês do pagamento (${MESES[+mc - 1].slice(0, 3)}/${ac}). Fonte: Banco Central do Brasil, série SGS 4390, consulta em ${dc}/${mc}/${ac}.`
    : 'Valores nominais, sem correção; a correção pela taxa SELIC (art. 3º da EC nº 113/2021) será apurada na liquidação.'),
  new Paragraph({ spacing: { after: 120 }, children: [] }),
  tabela,
  new Paragraph({ spacing: { before: 200 }, children: [] }),
  peq('Valores brutos, sujeitos à contribuição previdenciária de inativo e ao imposto de renda. Havendo reajuste do vencimento base no período (paridade), as diferenças serão recalculadas pelo valor vigente em cada competência.'),
];

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: SZ } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1701, left: 1701, right: 1134, bottom: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18 })] })] }) },
    children: [...corpo, ...anexo] }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(saida, b); console.log('ok', saida); });
