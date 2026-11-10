#!/usr/bin/env python3
"""Painel do escritório: servidor local que dá botões às tarefas do pacote.

    python painel/servidor.py            (usa as pastas de escritorio.local.md)
    python painel/servidor.py --demo     (dados fictícios em painel/_demo, para mostrar e treinar)

Abre em http://127.0.0.1:8765. Só escuta no próprio computador. O acesso pelo celular, dentro ou fora do
escritório, passa pela rede privada do Tailscale (`tailscale serve`), que leva até este endereço local
com HTTPS; nada fica aberto na internet. Ver painel/LEIA-ME.md.

Segurança:
- Perfis com PIN (guardado só como hash PBKDF2, em painel/usuarios.json, que não vai para o GitHub).
- Sessão em cookie HttpOnly, SameSite=Strict; toda ação exige o cabeçalho X-Painel (barra pedidos de
  outros sites). Cinco PINs errados bloqueiam o perfil por 5 minutos.
- Pastas com SIGILOSO.txt não aparecem nem são abertas. Nenhum caminho sai da pasta Clientes.
- Nenhum botão apaga arquivo. Aprovar cópia, decidir dado em conflito e conferir prazo: só a advogada.
"""
import argparse
import base64
import csv
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import uuid
from datetime import date, datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PAINEL = Path(__file__).resolve().parent
PACOTE = PAINEL.parent
SCRIPTS = PACOTE / "scripts"
ESTATICO = PAINEL / "static"
# Fora da pasta do pacote: o Claude Code (que trabalha na pasta do pacote) não alcança os perfis.
USUARIOS = Path(os.environ.get("APPDATA", Path.home())) / "PainelEscritorio" / "usuarios.json"
UPLOADS = Path(os.environ.get("TEMP", "/tmp")) / "painel-escritorio-uploads"
PY = sys.executable
AREAS = ["Previdenciário RPPS", "Previdenciário RGPS", "Família e Sucessões", "Direito Público",
         "Consumidor", "Ambiental"]
MAX_UPLOAD = 150 * 1024 * 1024
SESSAO_HORAS = 12

CFG = {"demo": False, "clientes": None, "financeiro": None}
SESSOES = {}          # token -> {"usuario": id, "expira": ts}
TENTATIVAS = {}       # usuario -> [erros, bloqueado_ate]
TAREFAS = {}          # id -> dict
TRAVA = threading.Lock()


# ------------------------------------------------------------------ configuração
def ler_local():
    f = PACOTE / "escritorio.local.md"
    if not f.exists():
        return None, None
    t = f.read_text(encoding="utf-8")
    m1 = re.search(r"Pasta Clientes:\s*`([^`]+)`", t)
    m2 = re.search(r"Pasta Financeiro:\s*`([^`]+)`", t)
    return (Path(m1.group(1)) if m1 else None), (Path(m2.group(1)) if m2 else None)


def clientes_dir() -> Path:
    return CFG["clientes"]


def planilha_honorarios() -> Path:
    return CFG["financeiro"] / "Controle_Honorarios.xlsx"


# ------------------------------------------------------------------ usuários e sessões
def hash_pin(pin, sal=None):
    sal = sal or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(sal), 200_000).hex()
    return sal, h


def carregar_usuarios():
    if not USUARIOS.exists():
        return []
    return json.loads(USUARIOS.read_text(encoding="utf-8"))


def salvar_usuarios(us):
    USUARIOS.parent.mkdir(parents=True, exist_ok=True)
    USUARIOS.write_text(json.dumps(us, ensure_ascii=False, indent=1), encoding="utf-8")


def usuario_por_id(uid):
    return next((u for u in carregar_usuarios() if u["id"] == uid), None)


def publico(u):
    return {"id": u["id"], "nome": u["nome"], "papel": u["papel"], "iniciais": u.get("iniciais", "")}


# ------------------------------------------------------------------ pastas de clientes
def tem_sigilo(p: Path) -> bool:
    try:
        return any(n.lower() == "sigiloso.txt" for n in os.listdir(p))
    except OSError:
        return False


def id_cliente(p: Path) -> str:
    rel = p.relative_to(clientes_dir()).as_posix()
    return base64.urlsafe_b64encode(rel.encode()).decode().rstrip("=")


def pasta_do_id(cid: str) -> Path:
    rel = base64.urlsafe_b64decode(cid + "=" * (-len(cid) % 4)).decode()
    p = (clientes_dir() / rel).resolve()
    base = clientes_dir().resolve()
    if base not in p.parents or len(p.relative_to(base).parts) != 2 or not p.is_dir() or tem_sigilo(p):
        raise PermissionError("pasta inválida")
    return p


def pastas_clientes():
    raiz = clientes_dir()
    if not raiz or not raiz.is_dir():
        return
    for area in sorted(p for p in raiz.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        for cli in sorted(p for p in area.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
            if tem_sigilo(cli):
                continue  # segredo de justiça: não aparece nem conta
            yield area, cli


LINHA = re.compile(r"^-\s+([^:]{2,40}):\s*(.*)$")


def ler_ficha(cli: Path):
    f = cli / "ficha-cliente.md"
    if not f.exists():
        return None
    texto = f.read_text(encoding="utf-8")
    limpo = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), texto, flags=re.S)
    secoes, atual = [], None
    cab = {}
    for i, l in enumerate(limpo.splitlines()):
        if l.startswith("## "):
            atual = {"titulo": l[3:].strip(), "itens": []}
            secoes.append(atual)
            continue
        if atual is None:
            m = re.match(r"^(Área|Situação da ficha|Criada em):\s*(.+)", l)
            if m:
                cab[m.group(1)] = m.group(2).strip()
            continue
        s = l.strip()
        if not s.startswith("- "):
            continue
        m = LINHA.match(s)
        campo, valor = (m.group(1).strip(), m.group(2).strip()) if m else ("", s[2:].strip())
        estado = "decidir" if "[DECIDIR]" in valor else "confirmar" if "[CONFIRMAR]" in valor else "ok"
        fontes = re.findall(r"\(fonte:\s*([^)]*)\)", valor)
        exibido = re.sub(r"\s*\(fonte:[^)]*\)", "", valor).replace("[CONFIRMAR]", "").replace("[DECIDIR]", "").strip()
        opcoes = [re.sub(r"\s*\(fonte:[^)]*\)?", "", o).strip() for o in re.split(r"\)\s+ou\s+", valor)] if estado == "decidir" else []
        opcoes = [o.replace("[DECIDIR]", "").strip(" )") for o in opcoes if o.strip()]
        atual["itens"].append({"linha": i, "campo": campo, "valor": exibido, "estado": estado,
                               "fontes": fontes, "opcoes": opcoes, "original": l})
    return {"cabecalho": cab, "secoes": secoes, "confirmar": texto.count("[CONFIRMAR]"),
            "decidir": texto.count("[DECIDIR]")}


def resumo_cliente(area: Path, cli: Path):
    f = ler_ficha(cli)
    nome = cli.name
    if f:
        for s in f["secoes"]:
            for it in s["itens"]:
                if it["campo"] == "Nome completo" and it["valor"]:
                    nome = it["valor"]
    casos = sum(1 for s in f["secoes"] if s["titulo"] == "Casos" for it in s["itens"] if it["valor"]) if f else 0
    return {"id": id_cliente(cli), "pasta": cli.name, "nome": nome, "area": area.name,
            "ficha": bool(f), "confirmar": f["confirmar"] if f else 0, "decidir": f["decidir"] if f else 0,
            "situacao": (f or {}).get("cabecalho", {}).get("Situação da ficha", "sem ficha" if not f else ""),
            "casos": casos, "alterado": datetime.fromtimestamp(cli.stat().st_mtime).strftime("%Y-%m-%d")}


def editar_ficha(cli: Path, linha: int, original: str, nova: str | None, registro: str):
    """Troca uma linha da ficha (conferindo que ela não mudou) e registra a conferência. Guarda cópia antes."""
    f = cli / "ficha-cliente.md"
    linhas = f.read_text(encoding="utf-8").splitlines()
    if linha >= len(linhas) or linhas[linha] != original:
        raise ValueError("A ficha mudou desde que foi aberta. Recarregue a página.")
    hist = cli / "_historico-ficha"
    hist.mkdir(exist_ok=True)
    shutil.copy2(f, hist / f"ficha-{datetime.now():%Y%m%d-%H%M%S}.md")
    if nova is not None:
        linhas[linha] = nova
    if not any(l.strip() == "## Conferências" for l in linhas):
        linhas += ["", "## Conferências"]
    linhas.append(f"- {datetime.now():%Y-%m-%d, %Hh%M} · {registro}")
    f.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def listar_arquivos(cli: Path, limite=400):
    out = []
    for r, dirs, arqs in os.walk(cli):
        rp = Path(r)
        if tem_sigilo(rp):
            dirs[:] = []
            continue
        dirs[:] = sorted(d for d in dirs if not d.startswith(("_extracao", "_historico", ".")))
        for a in sorted(arqs):
            if a.lower() in ("desktop.ini", "thumbs.db"):
                continue
            p = rp / a
            try:
                st = p.stat()
            except OSError:
                continue
            out.append({"caminho": p.relative_to(cli).as_posix(), "nome": a,
                        "pasta": rp.relative_to(cli).as_posix() if rp != cli else "",
                        "kb": round(st.st_size / 1024), "data": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")})
            if len(out) >= limite:
                return out
    return out


# ------------------------------------------------------------------ prazos
CAMPOS_PRAZO = ["data", "hora", "tipo", "cliente", "processo", "descricao", "fonte", "conferido"]


def arquivo_prazos():
    return clientes_dir() / "_painel" / "prazos.csv"


def ler_prazos():
    f = arquivo_prazos()
    if not f.exists():
        return []
    with open(f, encoding="utf-8-sig") as fh:
        linhas = list(csv.DictReader(fh, delimiter=";"))
    hoje = date.today()
    for i, l in enumerate(linhas):
        l["id"] = i
        try:
            d = date.fromisoformat(l["data"])
            l["dias"] = (d - hoje).days
        except ValueError:
            l["dias"] = None
    return sorted(linhas, key=lambda x: (x["dias"] is None, x["dias"] if x["dias"] is not None else 0, x.get("hora", "")))


def marcar_prazo(idx, quem):
    f = arquivo_prazos()
    with open(f, encoding="utf-8-sig") as fh:
        linhas = list(csv.DictReader(fh, delimiter=";"))
    linhas[idx]["conferido"] = f"{quem} em {date.today().isoformat()}"
    with open(f, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS_PRAZO, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


# ------------------------------------------------------------------ tarefas em segundo plano
def nova_tarefa(titulo, quem, cmd=None, cwd=None, depois=None, simulacao=None):
    tid = uuid.uuid4().hex[:10]
    t = {"id": tid, "titulo": titulo, "quem": quem, "inicio": datetime.now().strftime("%Y-%m-%d %H:%M"),
         "estado": "rodando", "saida": "", "resultado": None}
    with TRAVA:
        TAREFAS[tid] = t

    def rodar():
        try:
            if simulacao is not None:
                time.sleep(2.5)
                t["saida"] = simulacao
                t["estado"] = "concluída"
            else:
                env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
                p = subprocess.run(cmd, cwd=cwd or PACOTE, capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", env=env, timeout=6 * 3600,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                t["saida"] = (p.stdout + ("\n" + p.stderr if p.stderr.strip() else "")).strip()[-20000:]
                t["estado"] = "concluída" if p.returncode == 0 else "com erro"
            if depois and t["estado"] == "concluída":
                t["resultado"] = depois(t)
        except Exception as e:  # registra e segue
            t["estado"] = "com erro"
            t["saida"] += f"\n{type(e).__name__}: {e}"
        t["fim"] = datetime.now().strftime("%H:%M")
        try:
            log = clientes_dir() / "_painel" / "tarefas.log"
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(f"{t['inicio']} · {t['quem']} · {t['titulo']} · {t['estado']}\n")
        except OSError:
            pass

    threading.Thread(target=rodar, daemon=True).start()
    return t


def claude_cmd(prompt, papel="advogada"):
    """Claude Code sem interação. As proibições de .claude/settings.json (envio de e-mail, exclusão, edição
    dos arquivos do pacote) e o hook de sigilo continuam valendo. Pedidos das colaboradoras rodam também
    sem terminal, para que um pedido livre não execute comandos no computador."""
    exe = shutil.which("claude")
    if not exe:
        return None
    cmd = [exe, "-p", prompt, "--permission-mode", "acceptEdits", "--output-format", "text"]
    if papel != "advogada":
        cmd += ["--disallowedTools", "Bash", "PowerShell"]
    return cmd


MODELOS_PEDIDO = {
    "ficha": "Use a skill importacao-onedrive, etapa 4, para preencher ou completar a ficha-cliente.md da pasta {pasta}. Leia primeiro _extracao/resumo.md. No fim, diga em poucas linhas o que preencheu e o que ficou [CONFIRMAR] ou [DECIDIR].",
    "analise": "Use a skill analise-demanda no documento mais recente da pasta {pasta}. Responda com o resumo, os prazos encontrados e as providências sugeridas.",
    "atendimento": "Use a skill ficha-atendimento com a transcrição {arquivo}, do cliente da pasta {pasta}.",
    "minuta": "Use a skill minuta para o pedido a seguir, cliente da pasta {pasta}: {texto}",
    "livre": "{texto}",
}


# ------------------------------------------------------------------ importação do OneDrive
def estado_importacao():
    c = clientes_dir()
    inv = c / "_inventario"
    andamento = inv / "andamento.md"
    invs = sorted(inv.glob("inventario-*")) if inv.exists() else []
    migr = sorted(inv.glob("migracao-*.csv")) if inv.exists() else []
    proposta = invs[-1] / "proposta_migracao.csv" if invs else None
    aprovadas = 0
    if proposta and proposta.exists():
        with open(proposta, encoding="utf-8-sig") as fh:
            aprovadas = sum(1 for l in csv.DictReader(fh, delimiter=";") if l.get("aprovar", "").strip().lower() == "sim")
    autorizado = andamento.exists() and "Autorização para ler o conteúdo: SIM" in andamento.read_text(encoding="utf-8")
    clis = list(pastas_clientes())
    extraidos = sum(1 for _, cl in clis if (cl / "_extracao" / "resumo.md").exists())
    fichas = sum(1 for _, cl in clis if (cl / "ficha-cliente.md").exists())
    cad = sorted((c / "_cadastro").glob("clientes-*.xlsx")) if (c / "_cadastro").exists() else []
    resumo_inv = ""
    if invs and (invs[-1] / "resumo.md").exists():
        resumo_inv = (invs[-1] / "resumo.md").read_text(encoding="utf-8")[:6000]
    return {"inventario": invs[-1].name if invs else "", "resumo_inventario": resumo_inv,
            "proposta": str(proposta) if proposta and proposta.exists() else "", "aprovadas": aprovadas,
            "copias": len(migr), "autorizado": autorizado, "clientes": len(clis), "extraidos": extraidos,
            "fichas": fichas, "planilha": cad[-1].name if cad else ""}


# ------------------------------------------------------------------ servidor HTTP
class Painel(BaseHTTPRequestHandler):
    server_version = "PainelEscritorio/1.0"

    def log_message(self, fmt, *args):
        pass

    # ---------- utilitários
    def enviar(self, codigo, corpo=b"", tipo="application/json; charset=utf-8", extra=None):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; "
                         "style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def json(self, obj, codigo=200, extra=None):
        self.enviar(codigo, json.dumps(obj, ensure_ascii=False).encode("utf-8"), extra=extra)

    def erro(self, msg, codigo=400):
        self.json({"erro": msg}, codigo)

    def corpo_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 2_000_000:
            raise ValueError("pedido grande demais")
        return json.loads(self.rfile.read(n) or b"{}")

    def sessao(self):
        ck = self.headers.get("Cookie", "")
        m = re.search(r"(?:^|;\s*)sessao=([A-Za-z0-9_-]+)", ck)
        if not m:
            return None
        s = SESSOES.get(m.group(1))
        if not s or s["expira"] < time.time():
            return None
        return usuario_por_id(s["usuario"])

    def https(self):
        return self.headers.get("X-Forwarded-Proto", "") == "https"

    # ---------- GET
    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        if not url.path.startswith("/api/"):
            return self.estatico(url.path)
        if url.path == "/api/inicio":
            us = carregar_usuarios()
            return self.json({"configurado": bool(us), "perfis": [publico(u) for u in us], "demo": CFG["demo"],
                              "local": self.client_address[0] in ("127.0.0.1", "::1") and not self.headers.get("X-Forwarded-For")})
        u = self.sessao()
        if not u:
            return self.erro("Entre com seu PIN.", 401)
        try:
            rota = getattr(self, "get_" + url.path[5:].replace("-", "_").replace("/", "_"), None)
            if not rota:
                return self.erro("não encontrado", 404)
            return rota(u, q)
        except PermissionError as e:
            return self.erro(str(e) or "sem permissão", 403)
        except Exception as e:
            return self.erro(f"{type(e).__name__}: {e}", 500)

    def estatico(self, caminho):
        if caminho in ("", "/"):
            caminho = "/index.html"
        alvo = (ESTATICO / caminho.lstrip("/")).resolve()
        if ESTATICO.resolve() not in alvo.parents or not alvo.is_file():
            alvo = ESTATICO / "index.html"  # rotas do app
        tipo = mimetypes.guess_type(alvo.name)[0] or "application/octet-stream"
        if alvo.suffix == ".webmanifest":
            tipo = "application/manifest+json"
        extra = {"Cache-Control": "no-cache"}
        if alvo.name == "sw.js":
            extra["Service-Worker-Allowed"] = "/"
        self.enviar(200, alvo.read_bytes(), tipo + ("; charset=utf-8" if tipo.startswith(("text/", "application/javascript")) else ""), extra)

    def get_eu(self, u, q):
        return self.json({"usuario": publico(u), "demo": CFG["demo"], "areas": AREAS,
                          "clientes_dir": str(clientes_dir())})

    def get_resumo(self, u, q):
        prazos = [p for p in ler_prazos() if p["dias"] is not None and p["dias"] >= -3]
        clis = [resumo_cliente(a, c) for a, c in pastas_clientes()]
        rodando = [t for t in TAREFAS.values() if t["estado"] == "rodando"]
        return self.json({
            "prazos_7": sum(1 for p in prazos if 0 <= p["dias"] <= 7),
            "prazos_vencidos": sum(1 for p in prazos if p["dias"] < 0 and not p.get("conferido")),
            "proximos": prazos[:6],
            "clientes": len(clis), "a_conferir": sum(c["confirmar"] for c in clis),
            "a_decidir": sum(c["decidir"] for c in clis),
            "fichas_pendentes": sorted([c for c in clis if c["confirmar"] or c["decidir"]],
                                       key=lambda c: -(c["decidir"] * 10 + c["confirmar"]))[:5],
            "tarefas": len(rodando)})

    def get_clientes(self, u, q):
        return self.json([resumo_cliente(a, c) for a, c in pastas_clientes()])

    def get_cliente(self, u, q):
        cli = pasta_do_id(q.get("id", ""))
        area = cli.parent.name
        return self.json({"resumo": resumo_cliente(cli.parent, cli), "ficha": ler_ficha(cli),
                          "arquivos": listar_arquivos(cli), "area": area,
                          "extracao": (cli / "_extracao" / "resumo.md").exists()})

    def get_arquivo(self, u, q):
        cli = pasta_do_id(q.get("id", ""))
        alvo = (cli / q.get("caminho", "")).resolve()
        if cli.resolve() not in alvo.parents or not alvo.is_file() or tem_sigilo(alvo.parent):
            raise PermissionError("arquivo inválido")
        tipo = mimetypes.guess_type(alvo.name)[0] or "application/octet-stream"
        nome = alvo.name.encode("ascii", "replace").decode().replace('"', "")
        self.enviar(200, alvo.read_bytes(), tipo, {"Content-Disposition": f'inline; filename="{nome}"',
                                                   "Cache-Control": "no-store"})

    def get_prazos(self, u, q):
        return self.json(ler_prazos())

    def get_tarefas(self, u, q):
        return self.json(sorted(TAREFAS.values(), key=lambda t: t["inicio"], reverse=True)[:40])

    def get_tarefa(self, u, q):
        t = TAREFAS.get(q.get("id", ""))
        return self.json(t) if t else self.erro("tarefa não encontrada", 404)

    def get_honorarios(self, u, q):
        f = planilha_honorarios()
        linhas = []
        if f.exists():
            from openpyxl import load_workbook
            wb = load_workbook(f, read_only=True, data_only=True)
            ws = wb["Honorários"] if "Honorários" in wb.sheetnames else wb.active
            rows = list(ws.iter_rows(values_only=True))
            cab = [str(c or "") for c in rows[0]] if rows else []
            for r in rows[1:]:
                if any(r):
                    linhas.append({cab[i]: (v.isoformat()[:10] if hasattr(v, "isoformat") else v) for i, v in enumerate(r) if i < len(cab)})
            wb.close()
        return self.json({"planilha": f.name, "existe": f.exists(), "linhas": linhas[-30:][::-1]})

    def get_importacao(self, u, q):
        return self.json(estado_importacao())

    # ---------- POST
    def do_POST(self):
        url = urlparse(self.path)
        if self.headers.get("X-Painel") != "1":
            return self.erro("pedido recusado", 403)
        try:
            if url.path == "/api/entrar":
                return self.post_entrar(self.corpo_json())
            if url.path == "/api/configurar":
                return self.post_configurar(self.corpo_json())
            u = self.sessao()
            if not u:
                return self.erro("Entre com seu PIN.", 401)
            if url.path == "/api/upload":
                return self.post_upload(u, {k: v[0] for k, v in parse_qs(url.query).items()})
            rota = getattr(self, "post_" + url.path[5:].replace("-", "_").replace("/", "_"), None)
            if not rota:
                return self.erro("não encontrado", 404)
            return rota(u, self.corpo_json())
        except PermissionError as e:
            return self.erro(str(e) or "sem permissão", 403)
        except ValueError as e:
            return self.erro(str(e), 400)
        except Exception as e:
            return self.erro(f"{type(e).__name__}: {e}", 500)

    def post_configurar(self, d):
        """Primeira configuração dos perfis. Só no próprio computador e só se ainda não houver perfis."""
        if carregar_usuarios():
            raise PermissionError("Os perfis já existem.")
        if self.client_address[0] not in ("127.0.0.1", "::1") or self.headers.get("X-Forwarded-For"):
            raise PermissionError("A configuração inicial é feita no computador do escritório.")
        perfis = d.get("perfis") or []
        if not perfis or not any(p.get("papel") == "advogada" for p in perfis):
            raise ValueError("Crie pelo menos o perfil da advogada.")
        us = []
        for p in perfis:
            pin = str(p.get("pin", ""))
            if not re.fullmatch(r"\d{6}", pin):
                raise ValueError("O PIN tem 6 números.")
            sal, h = hash_pin(pin)
            nome = p["nome"].strip()[:40]
            us.append({"id": secrets.token_hex(4), "nome": nome, "papel": p["papel"],
                       "iniciais": "".join(w[0] for w in nome.replace("Dra.", "").split()[:2]).upper(),
                       "sal": sal, "hash": h})
        salvar_usuarios(us)
        return self.json({"ok": True})

    def post_entrar(self, d):
        u = usuario_por_id(d.get("usuario", ""))
        if not u:
            return self.erro("Perfil não encontrado.", 404)
        erros, ate = TENTATIVAS.get(u["id"], [0, 0])
        if ate > time.time():
            return self.erro(f"Muitas tentativas. Aguarde {int((ate - time.time()) / 60) + 1} min.", 429)
        _, h = hash_pin(str(d.get("pin", "")), u["sal"])
        if not hmac.compare_digest(h, u["hash"]):
            erros += 1
            TENTATIVAS[u["id"]] = [0, time.time() + 300] if erros >= 5 else [erros, 0]
            return self.erro("PIN incorreto.", 401)
        TENTATIVAS.pop(u["id"], None)
        tok = secrets.token_urlsafe(32)
        SESSOES[tok] = {"usuario": u["id"], "expira": time.time() + SESSAO_HORAS * 3600}
        ck = f"sessao={tok}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSAO_HORAS * 3600}"
        if self.https():
            ck += "; Secure"
        return self.json({"usuario": publico(u)}, extra={"Set-Cookie": ck})

    def post_sair(self, u, d):
        ck = self.headers.get("Cookie", "")
        m = re.search(r"sessao=([A-Za-z0-9_-]+)", ck)
        if m:
            SESSOES.pop(m.group(1), None)
        return self.json({"ok": True}, extra={"Set-Cookie": "sessao=; Max-Age=0; Path=/"})

    def post_upload(self, u, q):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_UPLOAD:
            raise ValueError("Arquivo vazio ou maior que 150 MB.")
        lote = re.sub(r"[^a-f0-9]", "", q.get("lote", "")) or secrets.token_hex(8)
        nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", q.get("nome", "arquivo"))[:120] or "arquivo"
        pasta = UPLOADS / lote
        pasta.mkdir(parents=True, exist_ok=True)
        ordem = len(list(pasta.iterdir()))
        destino = pasta / f"{ordem:03d}_{nome}"
        restante = n
        with open(destino, "wb") as fh:
            while restante:
                bloco = self.rfile.read(min(1 << 20, restante))
                if not bloco:
                    break
                fh.write(bloco)
                restante -= len(bloco)
        return self.json({"lote": lote, "arquivo": destino.name})

    def _lote(self, lote):
        p = UPLOADS / re.sub(r"[^a-f0-9]", "", lote or "")
        if not p.is_dir() or p == UPLOADS:
            raise ValueError("Envie os arquivos primeiro.")
        return sorted(p.iterdir())

    def post_conferir(self, u, d):
        cli = pasta_do_id(d["id"])
        linha, original = int(d["linha"]), d["original"]
        if "[CONFIRMAR]" not in original:
            raise ValueError("Esta linha já está conferida.")
        nova = re.sub(r"\s*\[CONFIRMAR\]", "", original)
        campo = (LINHA.match(original.strip()) or [None, original.strip()[2:40]])[1]
        editar_ficha(cli, linha, original, nova, f"{u['nome']} conferiu: {campo}")
        return self.json({"ok": True})

    def post_decidir(self, u, d):
        if u["papel"] != "advogada":
            raise PermissionError("Só a advogada decide dados em conflito.")
        cli = pasta_do_id(d["id"])
        linha, original, escolha = int(d["linha"]), d["original"], d["escolha"].strip()
        m = LINHA.match(original.strip())
        if not m or not escolha:
            raise ValueError("Escolha um valor.")
        fonte = ""
        for parte in re.split(r"\)\s+ou\s+", m.group(2)):
            if parte.strip().startswith(escolha[:12]):
                f = re.search(r"\(fonte:\s*([^)]*)", parte)
                fonte = f" (fonte: {f.group(1).strip()})" if f else ""
        nova = f"- {m.group(1)}: {escolha}{fonte}"
        editar_ficha(cli, linha, original, nova, f"{u['nome']} decidiu {m.group(1)}: {escolha}")
        return self.json({"ok": True})

    def post_conferir_prazo(self, u, d):
        if u["papel"] != "advogada":
            raise PermissionError("A conferência final do prazo é da advogada.")
        marcar_prazo(int(d["id"]), u["nome"])
        return self.json({"ok": True})

    def post_novo_cliente(self, u, d):
        area, nome = d.get("area", ""), d.get("cliente", "").strip()
        if area not in AREAS or len(nome) < 3:
            raise ValueError("Informe a área e o nome completo.")
        cmd = [PY, str(PACOTE / "estrutura" / "criar_pastas.py"), "--base", str(clientes_dir()),
               "--area", area, "--cliente", nome]
        if d.get("processo"):
            cmd += ["--processo", d["processo"].strip()]
        elif d.get("inss"):
            cmd += ["--inss", d["inss"].strip()]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if p.returncode:
            raise ValueError((p.stderr or p.stdout).strip()[-500:])
        cli = clientes_dir() / area / nome
        return self.json({"ok": True, "id": id_cliente(cli) if cli.is_dir() else None, "saida": p.stdout[-1500:]})

    def post_fotos_pdf(self, u, d):
        arquivos = self._lote(d.get("lote"))
        nome = re.sub(r'[<>:"/\\|?*]', "-", d.get("nome") or "documento").strip()[:60] or "documento"
        if d.get("cliente"):
            cli = pasta_do_id(d["cliente"])
            pasta = cli / "00 Documentação do cliente"
        else:
            pasta = UPLOADS / "pdfs"
        pasta.mkdir(parents=True, exist_ok=True)
        saida = pasta / f"{date.today().isoformat()}_{nome}.pdf"
        k = 2
        while saida.exists():
            saida = pasta / f"{date.today().isoformat()}_{nome}-{k}.pdf"
            k += 1
        cmd = [PY, str(SCRIPTS / "tratar_imagens.py"), *map(str, arquivos), "--saida", str(saida),
               "--limite-mb", str(float(d.get("limite_mb") or 5))]
        if d.get("cinza"):
            cmd.append("--cinza")

        def depois(t):
            r = {"pdf": saida.name, "kb": round(saida.stat().st_size / 1024)}
            if d.get("cliente"):
                r.update(cliente=d["cliente"], caminho=saida.relative_to(pasta_do_id(d["cliente"])).as_posix())
            return r
        t = nova_tarefa(f"Fotos para PDF: {saida.name}", u["nome"], cmd, depois=depois)
        return self.json(t)

    def post_transcrever(self, u, d):
        arquivos = self._lote(d.get("lote"))
        audio = arquivos[0]
        destino_dir = None
        if d.get("cliente"):
            destino_dir = pasta_do_id(d["cliente"]) / "Atendimentos"
            destino_dir.mkdir(exist_ok=True)
            base = f"{datetime.now():%Y-%m-%d_%H%M}_atendimento"
            novo = destino_dir / (base + audio.suffix)
            shutil.copy2(audio, novo)
            audio = novo
        cmd = [PY, str(SCRIPTS / "transcrever.py"), str(audio)]

        def depois(t):
            txt = audio.with_suffix(".txt")
            texto = txt.read_text(encoding="utf-8") if txt.exists() else ""
            r = {"texto": texto[:20000], "arquivo": txt.name}
            if d.get("cliente"):
                r.update(cliente=d["cliente"], caminho=txt.relative_to(pasta_do_id(d["cliente"])).as_posix())
            return r
        sim = None
        if CFG["demo"] and not d.get("real"):
            sim = "Simulação (modo demonstração): a transcrição real usa o Whisper no computador do escritório."

            def depois(t, audio=audio):  # noqa: F811
                return {"texto": "Cliente relata que recebeu carta do INSS pedindo documentos em até 30 dias. "
                                 "Diz que trabalhou na roça desde 1990 com o marido. Traz CNIS e carteira do "
                                 "sindicato. (texto de exemplo, modo demonstração)", "arquivo": audio.name}
        t = nova_tarefa("Transcrição de atendimento", u["nome"], cmd, depois=depois, simulacao=sim)
        return self.json(t)

    def post_honorario(self, u, d):
        tipo = d.get("tipo")
        if tipo not in ("fixo", "exito", "misto") or not d.get("cliente"):
            raise ValueError("Informe cliente e tipo.")
        cmd = [PY, str(SCRIPTS / "lancar_honorario.py"), "--planilha", str(planilha_honorarios()),
               "--cliente", d["cliente"], "--tipo", tipo, "--area", d.get("area", ""), "--caso", d.get("caso", ""),
               "--parcelas", str(int(d.get("parcelas") or 1)), "--obs", f"lançado pelo painel por {u['nome']}"]
        if d.get("valor"):
            cmd += ["--valor", str(float(str(d["valor"]).replace(".", "").replace(",", ".")))]
        if d.get("percentual"):
            cmd += ["--percentual", str(float(str(d["percentual"]).replace(",", ".")))]
        if d.get("vencimento"):
            cmd += ["--primeiro-vencimento", d["vencimento"]]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if p.returncode:
            raise ValueError((p.stderr or p.stdout).strip()[-500:])
        return self.json({"ok": True, "saida": p.stdout[-800:]})

    def post_pedir_claude(self, u, d):
        modelo = d.get("modelo", "livre")
        if modelo not in MODELOS_PEDIDO:
            raise ValueError("Tipo de pedido desconhecido.")
        pasta = ""
        if d.get("cliente"):
            pasta = str(pasta_do_id(d["cliente"]))
        texto = (d.get("texto") or "").strip()[:4000]
        if modelo in ("livre", "minuta") and not texto:
            raise ValueError("Escreva o pedido.")
        arquivo = ""
        if modelo == "atendimento":
            if not pasta or not d.get("arquivo"):
                raise ValueError("Falta a transcrição do atendimento.")
            alvo = (Path(pasta) / d["arquivo"]).resolve()
            if Path(pasta).resolve() not in alvo.parents or not alvo.is_file():
                raise PermissionError("arquivo inválido")
            arquivo = str(alvo)
        prompt = MODELOS_PEDIDO[modelo].format(pasta=pasta, texto=texto, arquivo=arquivo)
        prompt += (f"\n\nPedido feito pelo painel do escritório por {u['nome']} ({u['papel']}). "
                   "Siga o CLAUDE.md. Não envie nada para fora, não protocole e não apague arquivos.")
        titulos = {"ficha": "Ficha do cliente", "analise": "Análise de documento", "atendimento": "Ficha de atendimento",
                   "minuta": "Minuta", "livre": "Pedido ao Claude"}
        cmd = claude_cmd(prompt, u["papel"])
        sim = None
        if CFG["demo"] or not cmd:
            sim = ("Modo demonstração: no computador do escritório, este pedido é enviado ao Claude Code com a "
                   f"skill certa e a resposta aparece aqui.\n\nPedido que seria enviado:\n{prompt}")
        t = nova_tarefa(titulos[modelo], u["nome"], cmd, simulacao=sim)
        return self.json(t)

    def post_importacao(self, u, d):
        passo = d.get("passo")
        c = clientes_dir()
        inv = c / "_inventario"
        inv.mkdir(parents=True, exist_ok=True)
        est = estado_importacao()
        if passo == "autorizar":
            if u["papel"] != "advogada":
                raise PermissionError("Só a advogada autoriza a leitura dos documentos.")
            with open(inv / "andamento.md", "a", encoding="utf-8") as fh:
                fh.write(f"\n- {datetime.now():%Y-%m-%d %H:%M} · Autorização para ler o conteúdo: SIM · {u['nome']}, pelo painel\n")
            return self.json({"ok": True})
        if passo == "inventario":
            cmd = [PY, str(SCRIPTS / "inventario_pastas.py"), "--saida", str(inv / f"inventario-{date.today().isoformat()}")]
            if d.get("raiz"):
                cmd += ["--raiz", d["raiz"]]
            return self.json(nova_tarefa("Inventário do OneDrive", u["nome"], cmd))
        if passo == "abrir_proposta":
            if not est["proposta"]:
                raise ValueError("Rode o inventário primeiro.")
            if hasattr(os, "startfile"):
                os.startfile(est["proposta"])  # abre no Excel do computador
            return self.json({"ok": True, "aviso": "A planilha abre no Excel do computador do escritório."})
        if passo in ("simular", "copiar"):
            if passo == "copiar" and u["papel"] != "advogada":
                raise PermissionError("Só a advogada aprova a cópia.")
            if not est["proposta"] or not est["aprovadas"]:
                raise ValueError("Nenhuma pasta marcada com 'sim' na planilha de proposta.")
            cmd = [PY, str(SCRIPTS / "migrar_pastas.py"), "--csv", est["proposta"], "--clientes", str(c)]
            if passo == "copiar":
                cmd.append("--executar")
            return self.json(nova_tarefa("Cópia do OneDrive" + (" (simulação)" if passo == "simular" else ""), u["nome"], cmd))
        if passo == "extrair":
            if not est["autorizado"]:
                raise PermissionError("Falta a autorização da advogada para ler os documentos.")
            cmd = [PY, str(SCRIPTS / "extrair_cliente.py"), "--lote", str(c)]
            return self.json(nova_tarefa("Leitura dos documentos", u["nome"], cmd))
        if passo == "fichas":
            if not est["autorizado"]:
                raise PermissionError("Falta a autorização da advogada para ler os documentos.")
            prompt = ("Use a skill importacao-onedrive, etapa 4: crie ou complete a ficha-cliente.md dos próximos 10 "
                      "clientes que já têm _extracao/resumo.md e ainda não têm ficha. Registre em _inventario/andamento.md.")
            cmd = claude_cmd(prompt, u["papel"])
            sim = "Modo demonstração: aqui o Claude Code faria as próximas 10 fichas." if CFG["demo"] or not cmd else None
            return self.json(nova_tarefa("Fichas cadastrais (lote de 10)", u["nome"], cmd, simulacao=sim))
        if passo == "planilha":
            cmd = [PY, str(SCRIPTS / "consolidar_cadastro.py"), "--clientes", str(c)]
            return self.json(nova_tarefa("Planilha geral de clientes", u["nome"], cmd))
        raise ValueError("Passo desconhecido.")


class ServidorExclusivo(ThreadingHTTPServer):
    """No Windows, o padrão do Python deixa dois painéis ocuparem a mesma porta. Aqui a porta é exclusiva."""
    allow_reuse_address = False
    daemon_threads = True

    def server_bind(self):
        import socket
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def main():
    ap = argparse.ArgumentParser(description="Painel do escritório (servidor local).")
    ap.add_argument("--demo", action="store_true", help="usa dados fictícios em painel/_demo")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--abrir", action="store_true", help="abre o navegador")
    args = ap.parse_args()
    if args.demo:
        demo = PAINEL / "_demo"
        if not (demo / "Clientes").exists():
            subprocess.run([PY, str(PAINEL / "gerar_demo.py"), str(demo)], check=True)
        CFG.update(demo=True, clientes=demo / "Clientes", financeiro=demo / "Financeiro")
        global USUARIOS
        USUARIOS = demo / "usuarios-demo.json"
    else:
        cl, fi = ler_local()
        if not cl:
            sys.exit("escritorio.local.md não encontrado: rode o instalador ou use --demo.")
        CFG.update(clientes=cl, financeiro=fi or cl.parent / "Financeiro")
    (clientes_dir() / "_painel").mkdir(parents=True, exist_ok=True)
    UPLOADS.mkdir(parents=True, exist_ok=True)
    url = f"http://127.0.0.1:{args.porta}"
    try:
        srv = ServidorExclusivo(("127.0.0.1", args.porta), Painel)
    except OSError:
        # Já há um painel ligado (por exemplo, o da inicialização do Windows): só abre o navegador nele.
        print(f"O painel já estava ligado em {url}.")
        if args.abrir:
            import webbrowser
            webbrowser.open(url)
        sys.exit(3)
    print(f"Painel do escritório em {url}" + ("  (demonstração, dados fictícios)" if args.demo else ""))
    print("Para fechar, feche esta janela.")
    if args.abrir:
        import webbrowser
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
