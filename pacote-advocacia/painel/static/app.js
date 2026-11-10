/* Painel do escritório. JavaScript puro, sem bibliotecas externas: funciona sem internet no escritório. */
"use strict";

// ------------------------------------------------------------------ ícones (traço fino, estilo sóbrio)
const P = {
  inicio: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
  clientes: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.5 3.4-5.5 6.5-5.5s5.7 2 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8"/><path d="M18 14.8c1.8.7 3 2.5 3.5 5.2"/>',
  prazos: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="M8 14h3v3H8z"/>',
  foto: '<path d="M4 8h3l1.6-2.4A1 1 0 0 1 9.4 5h5.2a1 1 0 0 1 .8.4L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13.5" r="3.5"/>',
  microfone: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/>',
  claude: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.7 1.8 1.8.7-1.8.7L19 20l-.7-1.8-1.8-.7 1.8-.7z"/>',
  honorarios: '<path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H18v3"/><rect x="3" y="8" width="18" height="12" rx="2"/><circle cx="16.5" cy="14" r="1.2"/>',
  nuvem: '<path d="M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 8.5a4 4 0 0 1-.5 7.97"/><path d="M12 11v9M9 17l3 3 3-3"/>',
  novo: '<circle cx="10" cy="8" r="3.5"/><path d="M3.5 20c.8-3.5 3.3-5.5 6.5-5.5 1.6 0 3 .5 4.1 1.3M19 14v6M16 17h6"/>',
  tarefas: '<path d="M10 6h10M10 12h10M10 18h10"/><path d="M4 6l1.2 1.2L7.5 5M4 12l1.2 1.2L7.5 11M4 18l1.2 1.2L7.5 17"/>',
  celular: '<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M11 18.5h2"/>',
  busca: '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
  ok: '<path d="M5 12.5l4.5 4.5L19 7"/>',
  alerta: '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17.2v.1"/>',
  relogio: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
  sair: '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 16l-4-4 4-4M6 12h10"/>',
  voltar: '<path d="M15 5l-7 7 7 7"/>',
  arquivo: '<path d="M7 3h7l5 5v12a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14 3v5h5"/>',
  pasta: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  enviar: '<path d="M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/>',
  mais: '<path d="M12 5v14M5 12h14"/>',
  acoes: '<rect x="4" y="4" width="7" height="7" rx="1.6"/><rect x="13" y="4" width="7" height="7" rx="1.6"/><rect x="4" y="13" width="7" height="7" rx="1.6"/><rect x="13" y="13" width="7" height="7" rx="1.6"/>',
  fechar: '<path d="M6 6l12 12M18 6 6 18"/>',
  parar: '<rect x="7" y="7" width="10" height="10" rx="1.5"/>',
  girar: '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v4.5h-4.5"/>',
  escudo: '<path d="M12 3l7 3v5.5c0 4.4-3 8-7 9.5-4-1.5-7-5.1-7-9.5V6z"/><path d="M9 12l2 2 4-4"/>',
  balanca: '<path d="M12 4v16M7 20h10M5 7h14"/><path d="M5 7l-2.5 6a2.8 2.8 0 0 0 5 0zM19 7l-2.5 6a2.8 2.8 0 0 0 5 0z"/>',
};
const ic = (n, t = 22) => `<svg width="${t}" height="${t}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${P[n] || ""}</svg>`;

// ------------------------------------------------------------------ utilidades
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const iniciais = (n) => (n || "?").replace(/^(Dra?\.|Sr\.?|Sra\.?)\s*/i, "").split(/\s+/).filter((p) => p.length > 2 || /^[A-ZÀ-Ú]/.test(p)).slice(0, 2).map((p) => p[0]).join("").toUpperCase();

let EU = null, DEMO = false, AREAS = [], CACHE_CLIENTES = null;

async function api(caminho, dados) {
  const op = { headers: { "X-Painel": "1" }, credentials: "same-origin" };
  if (dados !== undefined) {
    op.method = "POST";
    op.headers["Content-Type"] = "application/json";
    op.body = JSON.stringify(dados);
  }
  const r = await fetch("/api/" + caminho, op);
  let j = {};
  try { j = await r.json(); } catch (_) { /* resposta vazia */ }
  if (r.status === 401 && caminho !== "entrar" && caminho !== "eu") { EU = null; telaEntrada(); throw new Error(j.erro || "Entre de novo."); }
  if (!r.ok) throw new Error(j.erro || "Algo deu errado.");
  return j;
}

let avisoTimer;
function aviso(msg, erro = false) {
  const a = $("#aviso");
  a.textContent = msg;
  a.className = erro ? "erro" : "";
  a.hidden = false;
  clearTimeout(avisoTimer);
  avisoTimer = setTimeout(() => (a.hidden = true), erro ? 6000 : 3500);
}

function enviarArquivo(arquivo, lote, aoProgresso) {
  return new Promise((ok, falha) => {
    const x = new XMLHttpRequest();
    x.open("POST", `/api/upload?lote=${encodeURIComponent(lote || "")}&nome=${encodeURIComponent(arquivo.name || "arquivo")}`);
    x.setRequestHeader("X-Painel", "1");
    x.upload.onprogress = (e) => e.lengthComputable && aoProgresso && aoProgresso(e.loaded / e.total);
    x.onload = () => {
      let j = {};
      try { j = JSON.parse(x.responseText); } catch (_) { /* nada */ }
      x.status === 200 ? ok(j) : falha(new Error(j.erro || "Falha no envio."));
    };
    x.onerror = () => falha(new Error("Sem conexão com o computador do escritório."));
    x.send(arquivo);
  });
}

async function enviarVarios(arquivos, barra) {
  let lote = "";
  for (let i = 0; i < arquivos.length; i++) {
    const r = await enviarArquivo(arquivos[i], lote, (p) => barra && (barra.style.width = `${((i + p) / arquivos.length) * 100}%`));
    lote = r.lote;
  }
  return lote;
}

function acompanharTarefa(t, alvo, aoTerminar) {
  const desenhar = (t) => {
    const cls = t.estado === "rodando" ? "rodando" : t.estado === "concluída" ? "feita" : "erro";
    const icone = t.estado === "rodando" ? "girar" : t.estado === "concluída" ? "ok" : "alerta";
    alvo.innerHTML = `<div class="cartao tarefa ${cls}"><div class="bolha">${ic(icone, 20)}</div><div class="meio">
      <strong>${esc(t.titulo)}</strong><br><small class="sub">${t.estado === "rodando" ? "Trabalhando… pode sair desta tela, a tarefa continua." : esc(t.estado)}</small>
      ${t.saida && t.estado !== "rodando" ? `<pre>${esc(t.saida)}</pre>` : ""}
      <div class="resultado"></div></div></div>`;
  };
  desenhar(t);
  const passo = async () => {
    try {
      const n = await api("tarefa?id=" + t.id);
      desenhar(n);
      if (n.estado === "rodando") return setTimeout(passo, 1500);
      if (aoTerminar) aoTerminar(n, $(".resultado", alvo));
    } catch (e) { aviso(e.message, true); }
  };
  setTimeout(passo, 1200);
}

function dataLonga(d = new Date()) {
  return d.toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}

function blocoDia(p) {
  const [a, m, d] = (p.data || "").split("-");
  const cls = p.dias === null ? "" : p.dias < 0 ? (p.conferido ? "passado" : "urgente") : p.dias <= 2 ? "urgente" : p.dias <= 7 ? "atencao" : "";
  return `<div class="dia ${cls}"><b>${esc(+d || "?")}</b><small>${esc(MESES[(+m || 1) - 1])}</small></div>`;
}

function quando(p) {
  if (p.dias === null) return "";
  if (p.dias < 0) return `<span class="selo urgente">vencido há ${-p.dias} dia${p.dias < -1 ? "s" : ""}</span>`;
  if (p.dias === 0) return '<span class="selo urgente">hoje</span>';
  if (p.dias === 1) return '<span class="selo urgente">amanhã</span>';
  if (p.dias <= 7) return `<span class="selo atencao">em ${p.dias} dias</span>`;
  return `<span class="selo neutro">em ${p.dias} dias</span>`;
}

async function clientes(forcar) {
  if (!CACHE_CLIENTES || forcar) CACHE_CLIENTES = await api("clientes");
  return CACHE_CLIENTES;
}

async function seletorCliente(id = "cliente", obrigatorio = false, valor = "") {
  const cs = await clientes();
  return `<div class="campo"><label for="${id}">Cliente${obrigatorio ? "" : " (opcional)"}</label>
    <select id="${id}">${obrigatorio ? '<option value="">Escolha…</option>' : '<option value="">Sem cliente: só gerar o arquivo</option>'}
    ${cs.map((c) => `<option value="${esc(c.id)}" ${c.id === valor ? "selected" : ""}>${esc(c.nome)} · ${esc(c.area)}</option>`).join("")}</select></div>`;
}

// ------------------------------------------------------------------ entrada
async function telaEntrada() {
  const info = await api("inicio");
  DEMO = info.demo;
  if (!info.configurado) return telaConfigurar(info);
  let escolhido = info.perfis.length === 1 ? info.perfis[0].id : null;
  let pin = "";
  $("#app").innerHTML = `<main class="entrada textura">
    <img class="logo" src="/img/logo.png" alt="Leulla Mendanha, Advogada">
    <div class="filete"></div>
    <h1>Quem está usando?</h1>
    <div class="perfis">${info.perfis.map((p) => `<button class="perfil" data-id="${esc(p.id)}">
      <div class="avatar">${esc(p.iniciais || iniciais(p.nome))}</div><span>${esc(p.nome)}</span><small>${p.papel === "advogada" ? "advogada" : "colaboradora"}</small></button>`).join("")}</div>
    <div class="pin" hidden><p>Digite seu PIN de 6 números</p><div class="pontos">${"<i></i>".repeat(6)}</div>
      <div class="teclado">${[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => `<button data-n="${n}">${n}</button>`).join("")}
      <button class="sem-borda" data-n="limpar">Limpar</button><button data-n="0">0</button><button class="sem-borda" data-n="apagar">Apagar</button></div>
      <div class="erro-pin"></div></div>
    ${DEMO ? '<p class="selo-demo">Demonstração com dados fictícios. PINs de treino: Dra. Leulla 111111 · Colaboradora 1 222222 · Colaboradora 2 333333</p>' : ""}
  </main>`;
  const pontos = () => $$(".pontos i").forEach((i, k) => i.classList.toggle("cheio", k < pin.length));
  const escolher = (id) => {
    escolhido = id;
    $$(".perfil").forEach((b) => b.classList.toggle("ativo", b.dataset.id === id));
    $(".pin").hidden = false;
    pin = ""; pontos(); $(".erro-pin").textContent = "";
  };
  const tentar = async () => {
    try {
      const r = await api("entrar", { usuario: escolhido, pin });
      EU = r.usuario;
      iniciarApp();
    } catch (e) {
      $(".erro-pin").textContent = e.message;
      pin = ""; pontos();
    }
  };
  const tecla = (n) => {
    if (!escolhido) return;
    if (n === "limpar") pin = "";
    else if (n === "apagar") pin = pin.slice(0, -1);
    else if (pin.length < 6) pin += n;
    pontos();
    if (pin.length === 6) tentar();
  };
  $$(".perfil").forEach((b) => b.addEventListener("click", () => escolher(b.dataset.id)));
  $$(".teclado button").forEach((b) => b.addEventListener("click", () => tecla(b.dataset.n)));
  document.onkeydown = (e) => {
    if (EU) return;
    if (/^\d$/.test(e.key)) tecla(e.key);
    if (e.key === "Backspace") tecla("apagar");
  };
  if (escolhido) escolher(escolhido);
}

function telaConfigurar(info) {
  $("#app").innerHTML = `<main class="entrada textura"><img class="logo" src="/img/logo.png" alt="Leulla Mendanha, Advogada"><div class="filete"></div>
    <div class="cartao pad" style="max-width:520px;width:100%;color:var(--texto)">
      <h2 class="secao">Primeira configuração</h2>
      ${info.local ? `<p class="nota">Crie um perfil para cada pessoa. Cada uma escolhe um PIN de 6 números, que fica guardado só neste computador, em forma cifrada. Ninguém mais vê o PIN, nem o Claude.</p>
      <form id="cfg">
        ${[["Dra. Leulla", "advogada"], ["", "colaboradora"], ["", "colaboradora"]].map(([n, p], i) => `
        <div class="grade-2"><div class="campo"><label>${p === "advogada" ? "Advogada" : "Colaboradora " + i} </label><input name="nome${i}" value="${esc(n)}" ${i ? 'placeholder="Nome (opcional)"' : "required"}></div>
        <div class="campo"><label>PIN de 6 números</label><input name="pin${i}" inputmode="numeric" pattern="\\d{6}" maxlength="6" type="password" autocomplete="new-password" ${i ? "" : "required"}></div></div>
        <input type="hidden" name="papel${i}" value="${p}">`).join("")}
        <button class="botao dourado grande" type="submit">Criar perfis</button></form>` :
        '<p class="nota dourada">A primeira configuração é feita no computador do escritório, abrindo o painel nele.</p>'}
    </div></main>`;
  const f = $("#cfg");
  if (f) f.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(f);
    const perfis = [0, 1, 2].map((i) => ({ nome: fd.get("nome" + i), pin: fd.get("pin" + i), papel: fd.get("papel" + i) })).filter((p) => p.nome && p.pin);
    try { await api("configurar", { perfis }); aviso("Perfis criados."); telaEntrada(); } catch (er) { aviso(er.message, true); }
  });
}

// ------------------------------------------------------------------ casca
const MENU = [
  ["Dia a dia"],
  ["inicio", "Início", "inicio"], ["prazos", "Prazos", "prazos"], ["clientes", "Clientes", "clientes"],
  ["Fazer"],
  ["fotos", "Fotos para PDF", "foto"], ["atendimento", "Atendimento", "microfone"], ["claude", "Pedir ao Claude", "claude"],
  ["novo-cliente", "Novo cliente", "novo"], ["honorarios", "Honorários", "honorarios"],
  ["Escritório"],
  ["importacao", "Importar do OneDrive", "nuvem"], ["tarefas", "Tarefas", "tarefas"], ["celular", "Usar no celular", "celular"],
];
const TITULOS = Object.fromEntries(MENU.filter((m) => m.length > 1).map((m) => [m[0], m[1]]));

async function iniciarApp() {
  const eu = await api("eu");
  EU = eu.usuario; DEMO = eu.demo; AREAS = eu.areas;
  $("#app").innerHTML = `<div class="casca">
    <aside class="lateral textura">
      <div class="marca"><img src="/img/logo.png" alt="Leulla Mendanha, Advogada"></div><div class="filete"></div>
      <nav class="menu">${MENU.map((m) => m.length === 1 ? `<div class="grupo">${m[0]}</div>` :
        `<a href="#/${m[0]}" data-rota="${m[0]}">${ic(m[2], 20)}<span>${m[1]}</span>${m[0] === "tarefas" ? '<span class="contagem" id="n-tarefas" hidden></span>' : ""}</a>`).join("")}</nav>
      <div class="quem"><div class="avatar">${esc(EU.iniciais || iniciais(EU.nome))}</div><div><strong>${esc(EU.nome)}</strong><small>${EU.papel}</small></div>
        <button class="icone-botao" id="sair" title="Sair">${ic("sair", 20)}</button></div>
    </aside>
    <div class="principal">
      <header class="topo-movel textura"><img src="/img/monograma.png" alt=""><span class="titulo" id="titulo-movel"></span>
        <button class="icone-botao" id="sair-movel" title="Sair">${ic("sair", 21)}</button></header>
      <header class="topo"><button class="voltar" id="voltar" hidden title="Voltar">${ic("voltar", 18)}</button>
        <div><h1 id="titulo"></h1><div class="sub" id="subtitulo"></div></div><div class="direita" id="topo-direita"></div></header>
      ${DEMO ? '<div class="faixa-demo">Demonstração com dados fictícios. Nada aqui é de cliente real.</div>' : ""}
      <main class="conteudo" id="conteudo"></main>
    </div>
    <nav class="barra-movel">
      <a href="#/inicio" data-rota="inicio">${ic("inicio", 22)}Início</a>
      <a href="#/prazos" data-rota="prazos">${ic("prazos", 22)}Prazos</a>
      <a href="#/acoes" data-rota="acoes" class="central"><span class="c">${ic("mais", 24)}</span></a>
      <a href="#/clientes" data-rota="clientes">${ic("clientes", 22)}Clientes</a>
      <a href="#/tarefas" data-rota="tarefas">${ic("tarefas", 22)}Tarefas<span class="contagem" id="n-tarefas-m" hidden></span></a>
    </nav></div>`;
  const sair = async () => { try { await api("sair", {}); } catch (_) { /* nada */ } EU = null; telaEntrada(); };
  $("#sair").addEventListener("click", sair);
  $("#sair-movel").addEventListener("click", sair);
  $("#voltar").addEventListener("click", () => history.back());
  window.onhashchange = rotear;
  if (!location.hash || location.hash === "#/") location.hash = "#/inicio";
  rotear();
  contarTarefas();
}

async function contarTarefas() {
  if (!EU) return;
  try {
    const ts = await api("tarefas");
    const n = ts.filter((t) => t.estado === "rodando").length;
    ["#n-tarefas", "#n-tarefas-m"].forEach((s) => { const e = $(s); if (e) { e.hidden = !n; e.textContent = n; } });
  } catch (_) { /* nada */ }
  setTimeout(contarTarefas, 8000);
}

function cabecalho(titulo, sub = "", voltar = false, direita = "") {
  $("#titulo").textContent = titulo;
  $("#titulo-movel").textContent = titulo;
  $("#subtitulo").textContent = sub;
  $("#voltar").hidden = !voltar;
  $("#topo-direita").innerHTML = direita;
  document.title = `${titulo} · Escritório`;
}

async function rotear() {
  const [rota, arg] = location.hash.replace(/^#\/?/, "").split("/");
  $$("[data-rota]").forEach((a) => a.classList.toggle("ativo", a.dataset.rota === rota || (rota === "cliente" && a.dataset.rota === "clientes")));
  const c = $("#conteudo");
  c.innerHTML = '<div class="vazio">Carregando…</div>';
  window.scrollTo(0, 0);
  const telas = { inicio: telaInicio, prazos: telaPrazos, clientes: telaClientes, cliente: telaCliente, fotos: telaFotos,
    atendimento: telaAtendimento, claude: telaClaude, "novo-cliente": telaNovoCliente, honorarios: telaHonorarios,
    importacao: telaImportacao, tarefas: telaTarefas, celular: telaCelular, acoes: telaAcoes };
  try { await (telas[rota] || telaInicio)(c, arg); } catch (e) { c.innerHTML = `<div class="cartao pad"><p>${esc(e.message)}</p></div>`; }
}

// ------------------------------------------------------------------ telas
const ACOES = [
  ["fotos", "foto", "Fotos para PDF", "Foto de documento vira PDF legível e leve"],
  ["atendimento", "microfone", "Gravar atendimento", "Grava ou envia o áudio e transcreve"],
  ["claude", "claude", "Pedir ao Claude", "Ficha, análise, minuta ou pedido livre"],
  ["novo-cliente", "novo", "Novo cliente", "Cria a pasta e a ficha no padrão"],
  ["honorarios", "honorarios", "Lançar honorário", "Contrato fixo, êxito ou misto"],
  ["importacao", "nuvem", "Importar OneDrive", "Pastas antigas para o padrão novo"],
];
const blocoAcoes = () => `<div class="acoes">${ACOES.map(([r, i, t, s]) => `<a class="cartao acao" href="#/${r}"><div class="bolha">${ic(i, 24)}</div><div><strong>${t}</strong><br><span>${s}</span></div></a>`).join("")}</div>`;

async function telaInicio(c) {
  cabecalho("Início");
  const r = await api("resumo");
  const h = new Date().getHours();
  const ola = h < 12 ? "Bom dia" : h < 18 ? "Boa tarde" : "Boa noite";
  c.innerHTML = `
    <p class="saudacao">${ola}, ${esc(EU.nome.split(" ")[0] === "Dra." ? EU.nome : EU.nome.split(" ")[0])}.</p>
    <p class="data-hoje">${esc(dataLonga())}</p>
    <div class="indicadores">
      <a class="cartao indicador ${r.prazos_vencidos ? "urgente" : "atencao"}" href="#/prazos"><div class="bolha">${ic("prazos")}</div><div><strong>${r.prazos_7}</strong><span>prazos em 7 dias${r.prazos_vencidos ? ` · <b style="color:var(--urgente)">${r.prazos_vencidos} vencido${r.prazos_vencidos > 1 ? "s" : ""}</b>` : ""}</span></div></a>
      <a class="cartao indicador dourado" href="#/clientes"><div class="bolha">${ic("ok")}</div><div><strong>${r.a_conferir}</strong><span>dados a conferir</span></div></a>
      <a class="cartao indicador ${r.a_decidir ? "urgente" : ""}" href="#/clientes"><div class="bolha">${ic("balanca")}</div><div><strong>${r.a_decidir}</strong><span>dados a decidir</span></div></a>
      <a class="cartao indicador" href="#/clientes"><div class="bolha">${ic("clientes")}</div><div><strong>${r.clientes}</strong><span>clientes</span></div></a>
    </div>
    <h2 class="secao">O que você quer fazer?</h2>
    ${blocoAcoes()}
    <h2 class="secao">Próximos prazos <a href="#/prazos">ver todos</a></h2>
    <div class="cartao"><ul class="lista">${r.proximos.length ? r.proximos.map((p) => `<li>${blocoDia(p)}<div class="meio"><strong>${esc(p.descricao)}</strong>
      <small>${esc(p.tipo)} · ${esc(p.cliente)} · ${esc(p.processo)}${p.hora ? " · " + esc(p.hora) : ""}</small></div>${quando(p)}</li>`).join("") : '<li class="vazio">Nenhum prazo lançado.</li>'}</ul></div>
    <h2 class="secao">Fichas a conferir <a href="#/clientes">ver clientes</a></h2>
    <div class="cartao"><ul class="lista">${r.fichas_pendentes.length ? r.fichas_pendentes.map((f) => `<li class="clicavel"><a class="linha" href="#/cliente/${esc(f.id)}">
      <div class="avatar" style="width:40px;height:40px;font-size:14px;margin:0">${esc(iniciais(f.nome))}</div>
      <div class="meio"><strong>${esc(f.nome)}</strong><small>${esc(f.area)}</small></div>
      ${f.decidir ? `<span class="selo urgente">${f.decidir} a decidir</span>` : ""}<span class="selo atencao">${f.confirmar} a conferir</span></a></li>`).join("") : '<li class="vazio">Tudo conferido.</li>'}</ul></div>`;
}

function telaAcoes(c) {
  cabecalho("O que você quer fazer?");
  c.innerHTML = blocoAcoes() + `<h2 class="secao">Mais</h2><div class="cartao"><ul class="lista">
    ${[["tarefas", "tarefas", "Tarefas em andamento"], ["celular", "celular", "Usar no celular"]].map(([r, i, t]) => `<li class="clicavel"><a class="linha" href="#/${r}">${ic(i)}<div class="meio"><strong>${t}</strong></div></a></li>`).join("")}</ul></div>`;
}

async function telaPrazos(c) {
  cabecalho("Prazos", "Também lançados na agenda “Prazos – Escritório”");
  let prazos = await api("prazos");
  let filtro = "todos";
  const tipos = [...new Set(prazos.map((p) => p.tipo).filter(Boolean))];
  const grupo = (p) => p.dias === null ? "Sem data" : p.dias < 0 ? "Vencidos" : p.dias === 0 ? "Hoje" : p.dias <= 7 ? "Próximos 7 dias" : "Depois";
  const desenhar = () => {
    const lista = prazos.filter((p) => filtro === "todos" || p.tipo === filtro).filter((p) => !(p.dias < 0 && p.conferido));
    const grupos = {};
    lista.forEach((p) => (grupos[grupo(p)] = grupos[grupo(p)] || []).push(p));
    c.innerHTML = `<p class="nota">Cada prazo vem do documento indicado em “fonte”. A conferência final é da advogada: ao conferir, o prazo sai do aviso de pendência.</p>
      <div class="opcoes" style="margin-bottom:8px"><button class="opcao ${filtro === "todos" ? "ativa" : ""}" data-f="todos">Todos</button>
      ${tipos.map((t) => `<button class="opcao ${filtro === t ? "ativa" : ""}" data-f="${esc(t)}">${esc(t)}</button>`).join("")}</div>
      ${["Vencidos", "Hoje", "Próximos 7 dias", "Depois", "Sem data"].filter((g) => grupos[g]).map((g) => `<h2 class="secao">${g} <small>${grupos[g].length}</small></h2>
      <div class="cartao"><ul class="lista">${grupos[g].map((p) => `<li>${blocoDia(p)}<div class="meio"><strong>${esc(p.descricao)}</strong>
        <small>${esc(p.tipo)} · ${esc(p.cliente)} · ${esc(p.processo)}${p.hora ? " · " + esc(p.hora) : ""}</small>
        <small>Fonte: ${esc(p.fonte || "não informada")}${p.conferido ? " · conferido por " + esc(p.conferido) : ""}</small></div>
        ${quando(p)}${p.conferido ? `<span class="selo ok">${ic("ok", 14)} conferido</span>` :
          EU.papel === "advogada" ? `<button class="botao pequeno claro" data-conferir="${p.id}">${ic("ok", 16)} Conferir</button>` : '<span class="selo neutro">a conferir</span>'}</li>`).join("")}</ul></div>`).join("") || '<div class="cartao vazio">Nenhum prazo.</div>'}`;
    $$("[data-f]", c).forEach((b) => b.addEventListener("click", () => { filtro = b.dataset.f; desenhar(); }));
    $$("[data-conferir]", c).forEach((b) => b.addEventListener("click", async () => {
      try { await api("conferir-prazo", { id: +b.dataset.conferir }); aviso("Prazo conferido."); prazos = await api("prazos"); desenhar(); } catch (e) { aviso(e.message, true); }
    }));
  };
  desenhar();
}

async function telaClientes(c) {
  cabecalho("Clientes", "Fichas criadas a partir das pastas e dos documentos");
  const cs = await clientes(true);
  let area = "todas", termo = "";
  c.innerHTML = `<div class="botoes" style="margin-bottom:14px;align-items:center"><label class="busca">${ic("busca", 18)}<input id="busca" placeholder="Buscar por nome" autocomplete="off"></label>
    <a class="botao dourado" href="#/novo-cliente">${ic("mais", 18)} Novo cliente</a></div>
    <div class="opcoes" id="areas" style="margin-bottom:16px"></div><div class="cartao"><ul class="lista" id="lista"></ul></div>`;
  const desenhar = () => {
    const areas = [...new Set(cs.map((x) => x.area))];
    $("#areas").innerHTML = `<button class="opcao ${area === "todas" ? "ativa" : ""}" data-a="todas">Todas · ${cs.length}</button>` +
      areas.map((a) => `<button class="opcao ${area === a ? "ativa" : ""}" data-a="${esc(a)}">${esc(a)} · ${cs.filter((x) => x.area === a).length}</button>`).join("");
    const t = termo.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
    const lista = cs.filter((x) => (area === "todas" || x.area === area) && x.nome.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().includes(t));
    $("#lista").innerHTML = lista.length ? lista.map((x) => `<li class="clicavel"><a class="linha" href="#/cliente/${esc(x.id)}">
      <div class="avatar" style="width:42px;height:42px;font-size:15px;margin:0">${esc(iniciais(x.nome))}</div>
      <div class="meio"><strong>${esc(x.nome)}</strong><small>${esc(x.area)}${x.casos ? ` · ${x.casos} caso${x.casos > 1 ? "s" : ""}` : ""}</small></div>
      ${!x.ficha ? '<span class="selo neutro">sem ficha</span>' : ""}${x.decidir ? `<span class="selo urgente">${x.decidir} a decidir</span>` : ""}
      ${x.confirmar ? `<span class="selo atencao">${x.confirmar} a conferir</span>` : x.ficha && !x.decidir ? `<span class="selo ok">${ic("ok", 14)} conferida</span>` : ""}</a></li>`).join("") : '<li class="vazio">Nenhum cliente encontrado.</li>';
    $$("[data-a]").forEach((b) => b.addEventListener("click", () => { area = b.dataset.a; desenhar(); }));
  };
  $("#busca").addEventListener("input", (e) => { termo = e.target.value; desenhar(); });
  desenhar();
}

async function telaCliente(c, id) {
  const d = await api("cliente?id=" + encodeURIComponent(id));
  const r = d.resumo;
  cabecalho(r.nome, r.area, true);
  let aba = sessionStorage.getItem("aba-cliente") || "ficha";
  const f = d.ficha;
  c.innerHTML = `<div class="cartao cabeca-cliente"><div class="avatar">${esc(iniciais(r.nome))}</div>
    <div><h2>${esc(r.nome)}</h2><div class="sub">${esc(r.area)} · ${esc(r.situacao || "sem ficha")}</div>
    <div class="botoes" style="margin-top:8px">${r.decidir ? `<span class="selo urgente">${r.decidir} a decidir</span>` : ""}${r.confirmar ? `<span class="selo atencao">${r.confirmar} a conferir</span>` : ""}</div></div>
    <div class="botoes"><a class="botao claro" href="#/fotos" data-cli>${ic("foto", 18)} Fotos</a><a class="botao claro" href="#/atendimento" data-cli>${ic("microfone", 18)} Atendimento</a>
    <a class="botao dourado" href="#/claude" data-cli>${ic("claude", 18)} Pedir ao Claude</a></div></div>
    <div class="abas"><button data-aba="ficha">Ficha</button><button data-aba="docs">Documentos · ${d.arquivos.length}</button></div><div id="aba"></div>`;
  $$("[data-cli]", c).forEach((a) => a.addEventListener("click", () => sessionStorage.setItem("cliente-escolhido", id)));
  const desenhar = () => {
    $$("[data-aba]").forEach((b) => b.classList.toggle("ativa", b.dataset.aba === aba));
    const alvo = $("#aba");
    if (aba === "docs") {
      const grupos = {};
      d.arquivos.forEach((a) => (grupos[a.pasta || "Pasta do cliente"] = grupos[a.pasta || "Pasta do cliente"] || []).push(a));
      alvo.innerHTML = Object.keys(grupos).length ? Object.entries(grupos).map(([g, as]) => `<h2 class="secao" style="font-size:17px">${ic("pasta", 18)} ${esc(g)}</h2>
        <div class="cartao"><ul class="lista">${as.map((a) => `<li class="clicavel"><a class="linha" target="_blank" rel="noopener" href="/api/arquivo?id=${encodeURIComponent(id)}&caminho=${encodeURIComponent(a.caminho)}">
        ${ic("arquivo", 20)}<div class="meio"><strong style="font-weight:500">${esc(a.nome)}</strong><small>${esc(a.data)} · ${a.kb} KB</small></div></a></li>`).join("")}</ul></div>`).join("") : '<div class="cartao vazio">Pasta vazia.</div>';
      return;
    }
    if (!f) {
      alvo.innerHTML = `<div class="cartao pad"><p>Este cliente ainda não tem ficha.</p><div class="botoes">
        <button class="botao dourado" id="fazer-ficha">${ic("claude", 18)} Pedir a ficha ao Claude</button></div><div id="t-ficha" style="margin-top:14px"></div></div>`;
      $("#fazer-ficha").addEventListener("click", async () => {
        try { acompanharTarefa(await api("pedir-claude", { modelo: "ficha", cliente: id }), $("#t-ficha")); } catch (e) { aviso(e.message, true); }
      });
      return;
    }
    alvo.innerHTML = (r.confirmar || r.decidir ? `<p class="nota dourada">Os campos em amarelo saíram da leitura automática: confira no documento indicado e toque em “Conferido”. Os em vermelho têm dois valores; quem decide é a advogada.</p>` : "") +
      f.secoes.filter((s) => s.titulo !== "Conferências").map((s) => `<div class="cartao ficha-sec"><h3>${esc(s.titulo)}</h3>
      ${s.itens.length ? s.itens.map((it) => `<div class="dado ${it.estado}">
        <div class="rotulo">${esc(it.campo || "•")}</div>
        <div class="valor">${esc(it.valor || "—")}${it.fontes.length && it.estado !== "decidir" ? `<span class="fonte">fonte: ${esc(it.fontes.join("; "))}</span>` : ""}</div>
        <div>${it.estado === "confirmar" ? `<button class="botao pequeno claro" data-conf="${it.linha}">${ic("ok", 16)} Conferido</button>` :
          it.estado === "decidir" ? '<span class="selo urgente">decidir</span>' : ""}</div>
        ${it.estado === "decidir" ? `<div class="escolhas">${it.opcoes.map((o, k) => EU.papel === "advogada" ? `<button class="botao pequeno claro" data-dec="${it.linha}" data-op="${k}">Usar: ${esc(o)}</button>` : `<span class="selo neutro">${esc(o)}</span>`).join("")}
          ${EU.papel !== "advogada" ? '<small class="sub">aguarda decisão da advogada</small>' : ""}</div>` : ""}
      </div>`).join("") : '<div class="vazio">—</div>'}</div>`).join("");
    const item = (linha) => f.secoes.flatMap((s) => s.itens).find((x) => x.linha === +linha);
    $$("[data-conf]", alvo).forEach((b) => b.addEventListener("click", async () => {
      const it = item(b.dataset.conf);
      try { await api("conferir", { id, linha: it.linha, original: it.original }); aviso("Conferido."); telaCliente(c, id); } catch (e) { aviso(e.message, true); }
    }));
    $$("[data-dec]", alvo).forEach((b) => b.addEventListener("click", async () => {
      const it = item(b.dataset.dec);
      try { await api("decidir", { id, linha: it.linha, original: it.original, escolha: it.opcoes[+b.dataset.op] }); aviso("Decisão registrada."); telaCliente(c, id); } catch (e) { aviso(e.message, true); }
    }));
  };
  $$("[data-aba]").forEach((b) => b.addEventListener("click", () => { aba = b.dataset.aba; sessionStorage.setItem("aba-cliente", aba); desenhar(); }));
  desenhar();
}

function clienteEscolhido() {
  const v = sessionStorage.getItem("cliente-escolhido") || "";
  sessionStorage.removeItem("cliente-escolhido");
  return v;
}

async function telaFotos(c) {
  cabecalho("Fotos para PDF", "Corrige rotação e brilho, monta o PDF e respeita o limite de tamanho");
  const pre = clienteEscolhido();
  let fotos = [];
  c.innerHTML = `<div class="grade-2" style="align-items:start;gap:16px">
    <div class="cartao pad">${await seletorCliente("cliente", false, pre)}
      <div class="campo"><label for="nome">Que documento é?</label><select id="nome">
        ${["RG", "CPF", "CNH", "Comprovante de residência", "Certidão", "CNIS", "Laudo médico", "Contracheque", "Documento"].map((n) => `<option>${n}</option>`).join("")}</select></div>
      <div class="campo"><label>Tamanho máximo do PDF</label><div class="opcoes" id="limite">
        ${[[3, "3 MB"], [5, "5 MB"], [10, "10 MB"]].map(([v, t]) => `<button class="opcao ${v === 5 ? "ativa" : ""}" data-v="${v}" type="button">${t}</button>`).join("")}</div>
        <span class="ajuda">Confira o limite do PJe e do INSS [VERIFICAR]. Na dúvida, 5 MB.</span></div>
      <label style="display:flex;gap:10px;align-items:center;margin-bottom:18px"><input type="checkbox" id="cinza"> Preto e branco (arquivo menor)</label>
      <button class="botao dourado grande" id="gerar" disabled>${ic("arquivo", 20)} Gerar PDF</button>
      <div class="progresso" hidden><i></i></div><div id="t" style="margin-top:14px"></div></div>
    <div><div class="solta" id="solta"><div class="bolha">${ic("foto", 26)}</div><strong>Arraste as fotos aqui</strong><br>
      <span class="sub">ou</span><div class="botoes" style="justify-content:center;margin-top:10px">
      <label class="botao">${ic("foto", 18)} Tirar foto<input type="file" accept="image/*" capture="environment" hidden id="camera"></label>
      <label class="botao claro">${ic("enviar", 18)} Escolher arquivos<input type="file" accept="image/*,.heic,.heif" multiple hidden id="arquivos"></label></div>
      <p class="sub" style="font-size:12.5px;margin:12px 0 0">A ordem das fotos é a ordem das páginas.</p></div>
      <div class="miniaturas" id="minis"></div></div></div>`;
  let limite = 5;
  $$("#limite .opcao").forEach((b) => b.addEventListener("click", () => { limite = +b.dataset.v; $$("#limite .opcao").forEach((x) => x.classList.toggle("ativa", x === b)); }));
  const minis = () => {
    $("#minis").innerHTML = fotos.map((f, i) => `<div class="miniatura"><img src="${f.url}" alt=""><b>${i + 1}</b><button data-rm="${i}" title="Tirar">${ic("fechar", 14)}</button></div>`).join("");
    $$("[data-rm]").forEach((b) => b.addEventListener("click", () => { URL.revokeObjectURL(fotos[+b.dataset.rm].url); fotos.splice(+b.dataset.rm, 1); minis(); }));
    $("#gerar").disabled = !fotos.length;
  };
  const somar = (lista) => { [...lista].filter((f) => f.type.startsWith("image/") || /\.hei[cf]$/i.test(f.name)).forEach((f) => fotos.push({ f, url: URL.createObjectURL(f) })); minis(); };
  $("#camera").addEventListener("change", (e) => somar(e.target.files));
  $("#arquivos").addEventListener("change", (e) => somar(e.target.files));
  const s = $("#solta");
  s.addEventListener("dragover", (e) => { e.preventDefault(); s.classList.add("sobre"); });
  s.addEventListener("dragleave", () => s.classList.remove("sobre"));
  s.addEventListener("drop", (e) => { e.preventDefault(); s.classList.remove("sobre"); somar(e.dataTransfer.files); });
  $("#gerar").addEventListener("click", async () => {
    const b = $("#gerar"); b.disabled = true;
    const barra = $(".progresso"); barra.hidden = false;
    try {
      const lote = await enviarVarios(fotos.map((x) => x.f), $("i", barra));
      const cli = $("#cliente").value;
      const t = await api("fotos-pdf", { lote, cliente: cli, nome: $("#nome").value, cinza: $("#cinza").checked, limite_mb: limite });
      acompanharTarefa(t, $("#t"), (n, alvo) => {
        if (n.resultado && n.resultado.caminho) {
          alvo.innerHTML = `<p style="margin:10px 0 0">PDF de ${n.resultado.kb} KB salvo na pasta do cliente, em “00 Documentação do cliente”.</p>
            <div class="botoes" style="margin-top:10px"><a class="botao claro" target="_blank" rel="noopener" href="/api/arquivo?id=${encodeURIComponent(n.resultado.cliente)}&caminho=${encodeURIComponent(n.resultado.caminho)}">${ic("arquivo", 18)} Abrir PDF</a></div>`;
        } else if (n.resultado) {
          alvo.innerHTML = `<p style="margin:10px 0 0">PDF gerado (${n.resultado.kb} KB). Sem cliente escolhido, ele fica na pasta temporária do computador do escritório.</p>`;
        }
        b.disabled = false;
      });
    } catch (e) { aviso(e.message, true); b.disabled = false; }
  });
}

async function telaAtendimento(c) {
  cabecalho("Atendimento", "Grave a conversa (com o consentimento do cliente) ou envie um áudio");
  const pre = clienteEscolhido();
  c.innerHTML = `<div class="grade-2" style="align-items:start;gap:16px">
    <div class="cartao gravador"><button class="gravar" id="gravar" title="Gravar">${ic("microfone", 34)}</button>
      <div class="cronometro" id="cron">00:00</div><p class="sub" id="estado-grav">Toque para gravar</p>
      <audio id="ouvir" controls hidden style="width:100%;margin-top:10px"></audio>
      <p class="sub" style="font-size:13px">ou <label style="color:var(--azul);cursor:pointer;text-decoration:underline">envie um áudio do WhatsApp<input type="file" accept="audio/*,.opus,.ogg,.m4a" hidden id="audio"></label></p></div>
    <div class="cartao pad">${await seletorCliente("cliente", true, pre)}
      <p class="nota">O áudio e o texto ficam na pasta do cliente, em “Atendimentos”. A transcrição roda no computador do escritório (Whisper) e pode errar nomes e números.</p>
      <button class="botao dourado grande" id="transcrever" disabled>${ic("arquivo", 20)} Transcrever</button>
      <div class="progresso" hidden><i></i></div><div id="t" style="margin-top:14px"></div></div></div>`;
  let gravador = null, partes = [], blob = null, inicio = 0, relogio = null;
  const pronto = () => ($("#transcrever").disabled = !blob);
  $("#gravar").addEventListener("click", async () => {
    if (gravador && gravador.state === "recording") { gravador.stop(); return; }
    if (!navigator.mediaDevices || !window.MediaRecorder) return aviso("Este navegador não grava áudio aqui. Envie um arquivo de áudio.", true);
    try {
      const fluxo = await navigator.mediaDevices.getUserMedia({ audio: true });
      gravador = new MediaRecorder(fluxo); partes = [];
      gravador.ondataavailable = (e) => partes.push(e.data);
      gravador.onstop = () => {
        fluxo.getTracks().forEach((t) => t.stop());
        clearInterval(relogio);
        const tipo = gravador.mimeType || "audio/webm";
        blob = new File(partes, `atendimento.${tipo.includes("mp4") ? "m4a" : tipo.includes("ogg") ? "ogg" : "webm"}`, { type: tipo });
        $("#ouvir").src = URL.createObjectURL(blob); $("#ouvir").hidden = false;
        $("#gravar").classList.remove("ativo"); $("#gravar").innerHTML = ic("microfone", 34);
        $("#estado-grav").textContent = "Gravação pronta. Ouça e toque em Transcrever.";
        pronto();
      };
      gravador.start(1000); inicio = Date.now();
      $("#gravar").classList.add("ativo"); $("#gravar").innerHTML = ic("parar", 34);
      $("#estado-grav").textContent = "Gravando… toque para parar";
      relogio = setInterval(() => { const s = Math.floor((Date.now() - inicio) / 1000); $("#cron").textContent = `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`; }, 500);
    } catch (e) { aviso("Sem acesso ao microfone. Permita o microfone no navegador.", true); }
  });
  $("#audio").addEventListener("change", (e) => {
    blob = e.target.files[0] || null;
    if (blob) { $("#ouvir").src = URL.createObjectURL(blob); $("#ouvir").hidden = false; $("#estado-grav").textContent = blob.name; }
    pronto();
  });
  $("#transcrever").addEventListener("click", async () => {
    const cli = $("#cliente").value;
    if (!cli) return aviso("Escolha o cliente.", true);
    const b = $("#transcrever"); b.disabled = true;
    const barra = $(".progresso"); barra.hidden = false;
    try {
      const lote = await enviarVarios([blob], $("i", barra));
      const t = await api("transcrever", { lote, cliente: cli });
      acompanharTarefa(t, $("#t"), (n, alvo) => {
        if (!n.resultado) return;
        alvo.innerHTML = `<div class="saida">${esc(n.resultado.texto || "(sem texto)")}</div>
          <div class="botoes" style="margin-top:12px"><button class="botao dourado" id="ficha-at">${ic("claude", 18)} Fazer a ficha do atendimento</button></div><div id="t2" style="margin-top:12px"></div>`;
        $("#ficha-at").addEventListener("click", async () => {
          try { acompanharTarefa(await api("pedir-claude", { modelo: "atendimento", cliente: cli, arquivo: n.resultado.caminho || "" }), $("#t2")); } catch (e) { aviso(e.message, true); }
        });
      });
    } catch (e) { aviso(e.message, true); b.disabled = false; }
  });
}

async function telaClaude(c) {
  cabecalho("Pedir ao Claude", "O pedido roda no computador do escritório, com as regras do escritório");
  const pre = clienteEscolhido();
  const tipos = [["ficha", "pasta", "Ficha do cliente", "Lê os documentos e preenche a ficha"], ["analise", "arquivo", "Analisar documento", "Resumo, prazos e providências"],
    ["minuta", "balanca", "Minuta", "Rascunho no papel timbrado, para revisão"], ["livre", "claude", "Pedido livre", "Qualquer outra tarefa"]];
  let modelo = "analise";
  c.innerHTML = `<div class="acoes" id="tipos" style="margin-bottom:18px">${tipos.map(([m, i, t, s]) => `<button class="cartao acao" data-m="${m}" type="button"><div class="bolha">${ic(i, 24)}</div><div><strong>${t}</strong><br><span>${s}</span></div></button>`).join("")}</div>
    <div class="cartao pad">${await seletorCliente("cliente", false, pre)}
      <div class="campo"><label for="texto">O que você precisa?</label><textarea id="texto" placeholder="Ex.: Prepare a réplica à contestação do banco, com base nos documentos da pasta."></textarea>
      <span class="ajuda">Nada é enviado, protocolado ou apagado sem a aprovação da advogada. Citações jurídicas vêm marcadas [VERIFICAR].</span></div>
      <button class="botao dourado grande" id="enviar">${ic("claude", 20)} Enviar pedido</button><div id="t" style="margin-top:14px"></div></div>
    <h2 class="secao">Pedidos recentes</h2><div id="recentes"></div>`;
  const marcar = () => $$("[data-m]").forEach((b) => { b.style.borderColor = b.dataset.m === modelo ? "var(--dourado-escuro)" : ""; b.style.boxShadow = b.dataset.m === modelo ? "0 0 0 3px rgba(224,188,122,.3)" : ""; });
  $$("[data-m]").forEach((b) => b.addEventListener("click", () => { modelo = b.dataset.m; marcar(); }));
  marcar();
  $("#enviar").addEventListener("click", async () => {
    const cli = $("#cliente").value, texto = $("#texto").value.trim();
    if ((modelo === "ficha" || modelo === "analise") && !cli) return aviso("Escolha o cliente.", true);
    try { acompanharTarefa(await api("pedir-claude", { modelo, cliente: cli, texto }), $("#t"), () => recentes()); } catch (e) { aviso(e.message, true); }
  });
  const recentes = async () => {
    const ts = (await api("tarefas")).filter((t) => /Claude|Ficha|Minuta|Análise/.test(t.titulo)).slice(0, 8);
    $("#recentes").innerHTML = ts.length ? ts.map((t) => blocoTarefa(t)).join("") : '<div class="cartao vazio">Nenhum pedido ainda.</div>';
    ligarTarefas($("#recentes"));
  };
  recentes();
}

async function telaNovoCliente(c) {
  cabecalho("Novo cliente", "Cria a pasta no padrão do escritório e a ficha em branco");
  c.innerHTML = `<div class="cartao pad" style="max-width:640px"><form id="f">
    <div class="campo"><label for="nomec">Nome completo do cliente</label><input id="nomec" required minlength="3" autocomplete="off"></div>
    <div class="campo"><label for="area">Área</label><select id="area" required>${AREAS.map((a) => `<option>${esc(a)}</option>`).join("")}</select></div>
    <div class="campo"><label>Tipo de caso</label><div class="opcoes" id="tipo">
      <button type="button" class="opcao ativa" data-t="nenhum">Ainda não sei</button><button type="button" class="opcao" data-t="processo">Processo judicial</button><button type="button" class="opcao" data-t="inss">Requerimento no INSS</button></div></div>
    <div class="campo" id="num" hidden><label for="numero" id="rotulo-num">Número</label><input id="numero" autocomplete="off"></div>
    <button class="botao dourado grande" type="submit">${ic("pasta", 20)} Criar pasta e ficha</button></form><div id="r" style="margin-top:14px"></div></div>`;
  let tipo = "nenhum";
  $$("#tipo .opcao").forEach((b) => b.addEventListener("click", () => {
    tipo = b.dataset.t; $$("#tipo .opcao").forEach((x) => x.classList.toggle("ativa", x === b));
    $("#num").hidden = tipo === "nenhum";
    $("#rotulo-num").textContent = tipo === "processo" ? "Número do processo (CNJ)" : "Número do requerimento no INSS";
  }));
  $("#f").addEventListener("submit", async (e) => {
    e.preventDefault();
    const dados = { cliente: $("#nomec").value, area: $("#area").value };
    if (tipo !== "nenhum") dados[tipo] = $("#numero").value;
    try {
      const r = await api("novo-cliente", dados);
      CACHE_CLIENTES = null;
      $("#r").innerHTML = `<p class="nota">Pasta criada.</p>${r.id ? `<a class="botao claro" href="#/cliente/${esc(r.id)}">Abrir cliente</a>` : ""}`;
    } catch (er) { aviso(er.message, true); }
  });
}

async function telaHonorarios(c) {
  cabecalho("Honorários", "Lançamento na planilha de controle");
  const h = await api("honorarios");
  const cs = await clientes();
  c.innerHTML = `<div class="grade-2" style="align-items:start;gap:16px"><div class="cartao pad"><form id="f">
    <div class="campo"><label for="cli">Cliente</label><input id="cli" list="lista-cli" required autocomplete="off"><datalist id="lista-cli">${cs.map((x) => `<option value="${esc(x.nome)}">`).join("")}</datalist></div>
    <div class="campo"><label>Tipo de contrato</label><div class="opcoes" id="tipo">${[["fixo", "Valor fixo"], ["exito", "Êxito"], ["misto", "Misto"]].map(([v, t], i) => `<button type="button" class="opcao ${i ? "" : "ativa"}" data-t="${v}">${t}</button>`).join("")}</div></div>
    <div class="grade-2"><div class="campo" id="c-valor"><label for="valor">Valor total (R$)</label><input id="valor" inputmode="decimal" placeholder="3.000,00"></div>
    <div class="campo" id="c-perc" hidden><label for="perc">Percentual de êxito (%)</label><input id="perc" inputmode="decimal" placeholder="30"></div></div>
    <div class="grade-2"><div class="campo"><label for="parc">Parcelas</label><input id="parc" type="number" min="1" max="60" value="1"></div>
    <div class="campo"><label for="venc">1º vencimento</label><input id="venc" type="date"></div></div>
    <button class="botao dourado grande" type="submit">${ic("honorarios", 20)} Lançar</button></form></div>
    <div class="cartao"><h2 class="secao" style="padding:18px 20px 0;margin:0 0 8px">Últimos lançamentos</h2>
    ${h.linhas.length ? (() => {
      const pref = ["Cliente", "Tipo", "Parcela", "Valor da parcela (R$)", "Percentual de êxito (%)", "Vencimento", "Status"];
      let cols = pref.filter((k) => k in h.linhas[0]);
      if (!cols.length) cols = Object.keys(h.linhas[0]).slice(0, 6);
      const rot = (k) => k.replace(" (R$)", "").replace("Percentual de êxito (%)", "Êxito %");
      return `<div class="rolagem"><table class="tabela"><thead><tr>${cols.map((k) => `<th>${esc(rot(k))}</th>`).join("")}</tr></thead>
      <tbody>${h.linhas.slice(0, 12).map((l) => `<tr>${cols.map((k) => `<td>${esc(l[k] ?? "")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
    })() : '<div class="vazio">Nenhum lançamento.</div>'}</div></div>`;
  let tipo = "fixo";
  $$("#tipo .opcao").forEach((b) => b.addEventListener("click", () => {
    tipo = b.dataset.t; $$("#tipo .opcao").forEach((x) => x.classList.toggle("ativa", x === b));
    $("#c-valor").hidden = tipo === "exito"; $("#c-perc").hidden = tipo === "fixo";
  }));
  $("#f").addEventListener("submit", async (e) => {
    e.preventDefault();
    const cli = cs.find((x) => x.nome === $("#cli").value);
    try {
      await api("honorario", { cliente: $("#cli").value, area: cli ? cli.area : "", tipo, valor: $("#valor").value, percentual: $("#perc").value, parcelas: $("#parc").value, vencimento: $("#venc").value });
      aviso("Honorário lançado na planilha."); telaHonorarios(c);
    } catch (er) { aviso(er.message, true); }
  });
}

async function telaImportacao(c) {
  cabecalho("Importar do OneDrive", "Das pastas antigas para o padrão novo, com a sua aprovação em cada etapa");
  const e = await api("importacao");
  const adv = EU.papel === "advogada";
  const passos = [
    ["Inventário", "Lista nomes, tamanhos e datas das pastas do OneDrive. Não abre nenhum arquivo.", !!e.inventario,
      `<button class="botao" data-p="inventario">${ic("busca", 18)} Fazer inventário</button>`, e.inventario ? `Último: ${e.inventario}` : ""],
    ["Aprovar a proposta", "Na planilha, confira área e nome de cada cliente e escreva “sim” no que deve ser copiado.", e.aprovadas > 0,
      `<button class="botao claro" data-p="abrir_proposta" ${e.proposta ? "" : "disabled"}>${ic("arquivo", 18)} Abrir planilha no Excel</button>`, e.proposta ? `${e.aprovadas} pasta(s) aprovada(s)` : ""],
    ["Copiar", "Copia as pastas aprovadas para a pasta Clientes. O OneDrive fica como está.", e.copias > 0,
      `<button class="botao claro" data-p="simular" ${e.aprovadas ? "" : "disabled"}>Simular</button><button class="botao" data-p="copiar" ${e.aprovadas && adv ? "" : "disabled"}>${ic("nuvem", 18)} Copiar</button>`,
      adv ? "" : "A cópia é aprovada pela advogada."],
    ["Ler os documentos", "Lê PDFs, fotos, Word e e-mails de cada cliente, no computador do escritório.", e.extraidos > 0,
      e.autorizado ? `<button class="botao" data-p="extrair">${ic("arquivo", 18)} Ler documentos</button>` :
        `<button class="botao dourado" data-p="autorizar" ${adv ? "" : "disabled"}>${ic("escudo", 18)} Autorizo a leitura dos documentos</button>`,
      e.autorizado ? `${e.extraidos} de ${e.clientes} clientes lidos` : "A leitura do conteúdo depende da autorização da advogada."],
    ["Fichas e planilha", "O Claude preenche as fichas (10 por vez) e o painel monta a planilha geral.", !!e.planilha,
      `<button class="botao" data-p="fichas" ${e.autorizado ? "" : "disabled"}>${ic("claude", 18)} Próximas 10 fichas</button><button class="botao claro" data-p="planilha">Planilha geral</button>`,
      `${e.fichas} ficha(s)${e.planilha ? " · " + e.planilha : ""}`],
  ];
  const atual = passos.findIndex((p) => !p[2]);
  c.innerHTML = `<p class="nota">Processos em segredo de justiça: crie um arquivo SIGILOSO.txt na pasta deles, ainda no OneDrive, antes do inventário. Essas pastas não são listadas, copiadas nem lidas.</p>
    <div class="cartao passos">${passos.map(([t, d, feito, botoes, info], i) => `<div class="passo ${feito ? "feito" : i === atual ? "atual" : ""}">
      <div class="num">${feito ? ic("ok", 20) : i + 1}</div><div><h3>${t}</h3><p>${d}</p><div class="botoes">${botoes}</div>
      ${info ? `<p class="sub" style="margin:10px 0 0;font-size:13px">${esc(info)}</p>` : ""}</div></div>`).join("")}</div>
    <div id="t" style="margin-top:16px"></div>
    ${e.resumo_inventario ? `<h2 class="secao">Resumo do último inventário</h2><div class="cartao pad"><div class="saida" style="max-height:480px">${esc(e.resumo_inventario)}</div></div>` : ""}`;
  $$("[data-p]", c).forEach((b) => b.addEventListener("click", async () => {
    try {
      const r = await api("importacao", { passo: b.dataset.p });
      if (r.id) acompanharTarefa(r, $("#t"), () => setTimeout(() => telaImportacao(c), 800));
      else { aviso(r.aviso || "Feito."); telaImportacao(c); }
    } catch (er) { aviso(er.message, true); }
  }));
}

function blocoTarefa(t) {
  const cls = t.estado === "rodando" ? "rodando" : t.estado === "concluída" ? "feita" : "erro";
  const icone = t.estado === "rodando" ? "girar" : t.estado === "concluída" ? "ok" : "alerta";
  return `<div class="cartao tarefa ${cls}" style="margin-bottom:10px"><div class="bolha">${ic(icone, 20)}</div><div class="meio">
    <strong>${esc(t.titulo)}</strong><br><small class="sub">${esc(t.quem)} · ${esc(t.inicio)}${t.fim ? " até " + esc(t.fim) : ""} · ${esc(t.estado)}</small>
    ${t.saida ? `<details><summary class="sub" style="cursor:pointer;font-size:13px;margin-top:6px">ver detalhes</summary><pre>${esc(t.saida)}</pre></details>` : ""}</div></div>`;
}
const ligarTarefas = () => {};

async function telaTarefas(c) {
  cabecalho("Tarefas", "O que o computador do escritório está fazendo ou já fez");
  const ts = await api("tarefas");
  c.innerHTML = ts.length ? ts.map(blocoTarefa).join("") : '<div class="cartao vazio">Nenhuma tarefa desde que o painel foi aberto.</div>';
  if (ts.some((t) => t.estado === "rodando")) setTimeout(() => location.hash === "#/tarefas" && telaTarefas(c), 3000);
}

function telaCelular(c) {
  cabecalho("Usar no celular", "Dentro e fora do escritório, sem abrir o computador para a internet");
  c.innerHTML = `<div class="cartao pad" style="max-width:760px">
    <p>O painel mora no computador do escritório. O celular chega até ele por uma rede particular (Tailscale), que só aceita os aparelhos de vocês. Nada fica aberto na internet.</p>
    <div class="passos">${[
      ["Uma vez, no computador", "Instalar o Tailscale e entrar com a conta do escritório. Depois, dois cliques em <b>PAINEL-NO-CELULAR.cmd</b> (pasta do painel)."],
      ["Uma vez, em cada celular", "Instalar o app Tailscale (Play Store ou App Store) e entrar com a mesma conta."],
      ["Abrir o painel", "No navegador do celular, abrir o endereço que o PAINEL-NO-CELULAR.cmd mostrou (termina em <b>.ts.net</b>)."],
      ["Ícone na tela inicial", "No Android (Chrome): menu ⋮ › Adicionar à tela inicial. No iPhone (Safari): Compartilhar › Adicionar à Tela de Início."],
    ].map(([t, d], i) => `<div class="passo"><div class="num">${i + 1}</div><div><h3>${t}</h3><p>${d}</p></div></div>`).join("")}</div>
    <p class="nota dourada">O computador do escritório precisa estar ligado e com o painel aberto. Se o celular for perdido, remova-o da rede no site do Tailscale e troque o PIN de quem o usava.</p></div>`;
}

// ------------------------------------------------------------------ partida
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
(async () => {
  try { await iniciarApp(); } catch (_) { telaEntrada().catch((e) => { $("#app").innerHTML = `<div class="entrada textura"><p>${esc(e.message)}</p></div>`; }); }
})();
