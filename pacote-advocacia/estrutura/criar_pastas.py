#!/usr/bin/env python3
"""Cria a árvore padrão de pastas de um cliente e de um caso.

Estrutura (ver CLAUDE.md, seção "Estrutura de pastas"):

    Clientes/{Área}/{Cliente}/
        00 Documentação do cliente/
        ficha-cliente.md
        {Caso}/
            01 Entrada/ ... 06 Prazos e comunicações/
            ficha-processo.md

Exemplos (sempre com dados fictícios nos testes):
    python criar_pastas.py --base ~/Clientes --area "Previdenciário RGPS" --cliente "Cliente Fictício" --inss 000000000 --dry-run
    python criar_pastas.py --base ~/Clientes --area "Consumidor" --cliente "Cliente Fictício" --processo 0000000-00.0000.8.14.0000
    python criar_pastas.py --base ~/Clientes --area "Direito Público" --cliente "Cliente Fictício"

Nunca apaga nem renomeia nada. Fichas já existentes não são sobrescritas.
"""
import argparse
import re
from datetime import date
from pathlib import Path

AREAS = [
    "Previdenciário RPPS",
    "Previdenciário RGPS",
    "Família e Sucessões",
    "Direito Público",
    "Consumidor",
    "Ambiental",
]

PASTA_CLIENTE = "00 Documentação do cliente"

SUBPASTAS_CASO = [
    "01 Entrada",
    "02 Autos e peças recebidas",
    "03 Análise",
    "04 Minutas",
    "05 Protocolados",
    "06 Prazos e comunicações",
]

FICHA_CLIENTE = """# Ficha do cliente: {cliente}

Área: {area}
Criada em: {hoje}

## Dados pessoais
- Nome completo: [CONFIRMAR]
- CPF: [CONFIRMAR]
- Contato: [CONFIRMAR]

## Casos
- {caso}

## Atendimentos
"""

FICHA_PROCESSO = """# Ficha do caso: {caso}

Cliente: {cliente}
Área: {area}
Criada em: {hoje}

- Tribunal ou órgão: [CONFIRMAR]
- Instância: [CONFIRMAR]
- Sistema: [CONFIRMAR]
- Fase: [CONFIRMAR]
- Próximo prazo: [CONFIRMAR]
- Status: ativo

## Registro (acrescentar com data, sem apagar)
- {hoje}: pasta criada.
"""


def nome_seguro(texto: str) -> str:
    """Remove caracteres proibidos em nomes de pasta no Windows e no macOS/Linux."""
    return re.sub(r'[\\/:*?"<>|]+', " ", texto).strip()


def escrever_se_nao_existe(caminho: Path, conteudo: str, simular: bool) -> None:
    if caminho.exists():
        print(f"já existe, mantido: {caminho}")
        return
    if simular:
        print(caminho)
    else:
        caminho.write_text(conteudo, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria a estrutura padrão de pastas do escritório.")
    parser.add_argument("--base", required=True, type=Path, help="Pasta raiz 'Clientes'")
    parser.add_argument("--area", required=True, help="Área de atuação: " + ", ".join(AREAS))
    parser.add_argument("--cliente", required=True, help="Nome do cliente")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--processo", help="Número CNJ do processo")
    grupo.add_argument("--inss", help="Número do requerimento no INSS")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que seria criado, sem criar")
    args = parser.parse_args()

    if args.area not in AREAS:
        print(f"Aviso: a área '{args.area}' não está na lista padrão. Confira o nome com a advogada.")

    hoje = date.today().isoformat()
    if args.processo:
        caso = args.processo
    elif args.inss:
        caso = f"INSS-{args.inss}"
    else:
        caso = f"consultivo-{hoje}"

    pasta_cliente = args.base.expanduser() / nome_seguro(args.area) / nome_seguro(args.cliente)
    pasta_caso = pasta_cliente / nome_seguro(caso)
    pastas = [pasta_cliente / PASTA_CLIENTE] + [pasta_caso / sub for sub in SUBPASTAS_CASO]

    for caminho in pastas:
        if args.dry_run:
            print(caminho)
        else:
            caminho.mkdir(parents=True, exist_ok=True)

    dados = {"cliente": args.cliente, "area": args.area, "caso": caso, "hoje": hoje}
    ficha_cliente = pasta_cliente / "ficha-cliente.md"
    if ficha_cliente.exists() and not args.dry_run:
        texto = ficha_cliente.read_text(encoding="utf-8")
        linha = f"- {caso}"
        if linha not in texto.splitlines() and "## Casos\n" in texto:
            texto = texto.replace("## Casos\n", f"## Casos\n{linha}\n", 1)
            ficha_cliente.write_text(texto, encoding="utf-8")
            print(f"caso acrescentado na ficha do cliente: {caso}")
    escrever_se_nao_existe(ficha_cliente, FICHA_CLIENTE.format(**dados), args.dry_run)
    escrever_se_nao_existe(pasta_caso / "ficha-processo.md", FICHA_PROCESSO.format(**dados), args.dry_run)

    acao = "Simulação, nada criado" if args.dry_run else "Estrutura criada"
    print(f"{acao}: {pasta_caso}")


if __name__ == "__main__":
    main()
