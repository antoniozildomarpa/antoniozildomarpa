"""Hook UserPromptSubmit: avisa quando a sessao esta longa e convem abrir outra.

Conta as mensagens do usuario por sessao (session_id recebido no stdin).
A partir de LIMITE mensagens avisa, e depois repete a cada PASSO mensagens.
Nunca bloqueia: qualquer erro sai com codigo 0 e sem saida.
"""
import json
import os
import re
import sys

LIMITE = 50
PASSO = 25
PASTA_ESTADO = os.path.join(os.path.expanduser("~"), ".claude", "hooks", "state")


def contar(session_id):
    os.makedirs(PASTA_ESTADO, exist_ok=True)
    seguro = re.sub(r"[^A-Za-z0-9_-]", "", session_id) or "sem_sessao"
    caminho = os.path.join(PASTA_ESTADO, seguro + ".count")
    n = 0
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            n = int(f.read().strip() or 0)
    n += 1
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(str(n))
    return n


def main():
    try:
        dados = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except Exception:
        return 0
    n = contar(dados.get("session_id", ""))
    if n < LIMITE or (n - LIMITE) % PASSO != 0:
        return 0

    aviso = (
        f"Esta sessao ja tem {n} mensagens e fica mais lenta e cara a cada resposta. "
        "Se a proxima tarefa for de outro cliente ou outro processo, abra uma sessao nova."
    )
    como_voltar = (
        "Para nao perder o historico: antes de trocar, peca um HANDOFF.md na pasta 03 Analise do caso "
        "(modelo em ~/.claude/templates/HANDOFF_modelo.md). Para voltar depois: 'claude --resume' (lista), "
        "'claude --resume <ID>' ou 'claude --continue' (ultima da pasta). Nao use /clear sem salvar antes."
    )
    saida = {
        "systemMessage": aviso,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "[alerta de sessao] " + aviso + " Avise de forma breve, no inicio da resposta, "
                "e ofereca a troca. " + como_voltar
            ),
        },
    }
    sys.stdout.write(json.dumps(saida, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
