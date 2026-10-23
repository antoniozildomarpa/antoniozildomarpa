"""Gancho de segurança: impede o Claude de assinar ou enviar processo no SEI e de digitar senhas.

Recebe a chamada de ferramenta de navegador ou de controle do computador (JSON na entrada padrão) e
nega a ação quando ela menciona assinatura, envio de processo ou campo de senha. Assinar e enviar são
sempre do usuário. Ferramentas só de leitura (ler página, localizar, captura de tela) passam.
"""

import json
import sys
import unicodedata

SO_LEITURA = ("read", "get_page", "find", "screenshot", "tabs_context", "list", "console", "network", "zoom")
PROIBIDO = {
    "assinar": "assinatura de documento",
    "assinatura": "assinatura de documento",
    "documento_assinar": "assinatura de documento",
    "enviar processo": "envio de processo",
    "enviarprocesso": "envio de processo",
    "procedimento_enviar": "envio de processo",
    "pwdsenha": "campo de senha",
    "senha": "campo de senha",
    "password": "campo de senha",
}


def normal(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def main():
    try:
        dados = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    ferramenta = dados.get("tool_name", "")
    nome_acao = normal(ferramenta.split("__")[-1])
    if any(p in nome_acao for p in SO_LEITURA):
        return
    texto = normal(json.dumps(dados.get("tool_input", {}), ensure_ascii=False))
    for termo, motivo in PROIBIDO.items():
        if termo in texto:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Bloqueado pelo gancho de segurança do SEI ({motivo}). Assinar documentos, enviar processos "
                        "e digitar senhas são ações exclusivas do usuário. Pare aqui e avise o usuário do que falta ele fazer."
                    ),
                }
            }, ensure_ascii=False))
            return


if __name__ == "__main__":
    main()
