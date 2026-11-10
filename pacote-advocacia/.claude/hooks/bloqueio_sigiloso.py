"""Hook PreToolUse: bloqueia leitura e escrita em pastas marcadas com SIGILOSO.txt.

Processos em segredo de justiça ficam fora da automação (CLAUDE.md, seção Sigilo). Basta criar um
arquivo SIGILOSO.txt na pasta do caso ou do cliente.

Regras:
- Arquivo ou pasta dentro de uma pasta marcada: bloqueado (procura o marcador nas pastas acima).
- Busca ou listagem (Glob, Grep, ou comando de terminal que cite uma pasta) a partir de uma pasta que
  CONTENHA uma pasta marcada em qualquer nível abaixo: bloqueada. Fazer a busca numa pasta mais específica.
- Sem caminho informado, vale a pasta atual da sessão.
- Na dúvida (erro ao conferir, árvore grande demais), bloqueia. Ler o próprio SIGILOSO.txt é permitido.
"""
import json
import os
import re
import sys

MARCA = "sigiloso.txt"
SUBIDA_MAXIMA = 10
LIMITE_PASTAS = 20000  # descida: acima disso, bloqueia e pede uma pasta mais específica
IGNORAR = {".git", "node_modules", "__pycache__", ".venv", "venv"}
RECURSIVAS = {"Glob", "Grep"}


class ArvoreGrande(Exception):
    pass


def resolver(caminho, cwd):
    p = os.path.expanduser(caminho)
    if not os.path.isabs(p):
        p = os.path.join(cwd or os.getcwd(), p)
    return os.path.realpath(p)


def tem_marca(pasta):
    try:
        return any(n.lower() == MARCA for n in os.listdir(pasta))
    except OSError:
        return False


def marcada_acima(p):
    atual = p if os.path.isdir(p) else os.path.dirname(p)
    for _ in range(SUBIDA_MAXIMA):
        if tem_marca(atual):
            return atual
        pai = os.path.dirname(atual)
        if pai == atual:
            break
        atual = pai
    return None


def marcada_abaixo(p):
    if not os.path.isdir(p):
        return None
    vistas = 0
    for raiz, dirs, arqs in os.walk(p):
        dirs[:] = [d for d in dirs if d not in IGNORAR]
        vistas += 1
        if vistas > LIMITE_PASTAS:
            raise ArvoreGrande(p)
        if any(a.lower() == MARCA for a in arqs):
            return raiz
    return None


def caminhos_no_comando(cmd):
    achados = re.findall(r'"([^"]+)"|\'([^\']+)\'', cmd)
    trechos = [a or b for a, b in achados]
    trechos += [t.strip("\"'") for t in cmd.split() if ("\\" in t or "/" in t or t in (".", "..")) and not t.startswith("-")]
    return trechos


def decidir(dados):
    ferramenta = dados.get("tool_name", "")
    entrada = dados.get("tool_input", {}) or {}
    cwd = dados.get("cwd") or os.getcwd()

    if ferramenta in ("Bash", "PowerShell"):
        alvos, descer = caminhos_no_comando(entrada.get("command", "")), True
    else:
        alvos = [entrada[k] for k in ("file_path", "path", "notebook_path") if entrada.get(k)]
        descer = ferramenta in RECURSIVAS
        if not alvos and descer:
            alvos = [cwd]

    for alvo in alvos:
        p = resolver(alvo, cwd)
        if os.path.basename(p).lower() == MARCA:
            continue
        pasta = marcada_acima(p)
        if pasta:
            return (f"Pasta em segredo de justiça ({pasta} tem SIGILOSO.txt). A automação não abre esta pasta. "
                    "Registre só que ela existe e foi ignorada.")
        if descer:
            try:
                pasta = marcada_abaixo(p)
            except ArvoreGrande:
                return (f"A pasta {p} é grande demais para conferir o sigilo. Faça a busca numa pasta mais "
                        "específica (a do cliente ou a do caso).")
            if pasta:
                return (f"A busca em {p} alcançaria uma pasta em segredo de justiça ({pasta}). "
                        "Faça a busca numa pasta mais específica, que não contenha processos sigilosos.")
    return None


def negar(motivo):
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": motivo,
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        motivo = decidir(json.loads(sys.stdin.buffer.read().decode("utf-8-sig")))
    except Exception as e:  # falha fechada: na dúvida, não abre
        motivo = (f"O hook de sigilo não conseguiu conferir esta ação ({type(e).__name__}) e a bloqueou por "
                  "precaução. Verifique .claude/hooks/bloqueio_sigiloso.py.")
    if motivo:
        negar(motivo)
    sys.exit(0)
