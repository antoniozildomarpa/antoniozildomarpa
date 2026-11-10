"""Hook PreToolUse: bloqueia leitura e escrita em pastas marcadas com SIGILOSO.txt.

Processos em segredo de justiça ficam fora da automação (CLAUDE.md, seção Sigilo). Basta criar um
arquivo SIGILOSO.txt na pasta do caso ou do cliente: tudo o que estiver dentro dela fica bloqueado
para Read, Edit, Write, Glob, Grep e NotebookEdit. Comandos de terminal que citem o caminho também
são barrados.

Em caso de erro do próprio hook, a ferramenta segue normalmente (código 0, sem saída).
"""
import json
import os
import re
import sys

MARCA = "SIGILOSO.txt"
SUBIDA_MAXIMA = 8  # quantas pastas acima conferir


def pasta_sigilosa(caminho):
    if not caminho:
        return None
    p = os.path.abspath(os.path.expanduser(caminho))
    if os.path.basename(p).lower() == MARCA.lower():
        return os.path.dirname(p)  # ler o próprio marcador é permitido
    atual = p if os.path.isdir(p) else os.path.dirname(p)
    for _ in range(SUBIDA_MAXIMA):
        if os.path.isfile(os.path.join(atual, MARCA)):
            return atual
        pai = os.path.dirname(atual)
        if pai == atual:
            break
        atual = pai
    return None


def caminhos_no_comando(cmd):
    """Trechos entre aspas ou com barra no comando de terminal."""
    achados = re.findall(r'"([^"]+)"|\'([^\']+)\'', cmd)
    trechos = [a or b for a, b in achados]
    trechos += [t for t in cmd.split() if ("\\" in t or "/" in t) and not t.startswith("-")]
    return trechos


def negar(motivo):
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": motivo,
        }
    }, ensure_ascii=False))


def main():
    dados = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    ferramenta = dados.get("tool_name", "")
    entrada = dados.get("tool_input", {}) or {}
    candidatos = []
    if ferramenta in ("Bash", "PowerShell"):
        candidatos = caminhos_no_comando(entrada.get("command", ""))
    else:
        for chave in ("file_path", "path", "notebook_path"):
            if entrada.get(chave):
                candidatos.append(entrada[chave])
    for c in candidatos:
        pasta = pasta_sigilosa(c)
        if pasta and os.path.basename(c).lower() != MARCA.lower():
            negar(f"Pasta em segredo de justiça ({pasta} tem {MARCA}). A automação não abre esta pasta. "
                  "Registre só que ela existe e foi ignorada.")
            return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
