#!/usr/bin/env python3
"""Copia para a pasta Clientes as pastas aprovadas na proposta_migracao.csv do inventário.

Só copia. Não move, não renomeia e não apaga nada no OneDrive: a origem fica intacta até a advogada
conferir o resultado e decidir o que fazer com ela.

    python migrar_pastas.py --csv "<proposta_migracao.csv aprovada>" --clientes "<pasta Clientes>" [--executar]

Sem --executar é só simulação: mostra o que seria copiado, quanto espaço precisa e os problemas.

Para cada linha com aprovar = sim:
    origem   = caminho_origem (coluna gravada pelo inventário)
    destino  = <Clientes>/<Área>/<Cliente>/_importado-onedrive/<caminho da origem a partir da raiz>/
A área e o nome do cliente vêm da coluna destino_sugerido (que a advogada pode corrigir no Excel).
Guardar o caminho original dentro de _importado-onedrive evita que duas pastas do mesmo cliente
(em áreas diferentes, por exemplo) se misturem. A reorganização em casos é feita depois, caso a caso.

Regras:
- Linhas com sigiloso = sim não são copiadas: a advogada move essas pastas pessoalmente.
- Arquivo que já existe no destino com o mesmo tamanho é pulado (pode rodar de novo depois de uma falha).
- Arquivo que existe com tamanho diferente não é sobrescrito: recebe o sufixo " (onedrive)".
- Arquivos só na nuvem são baixados pelo próprio OneDrive durante a cópia (pode demorar).
- Registro de cada arquivo em <Clientes>/_inventario/migracao-AAAA-MM-DD-HHMM.csv.
"""
import argparse
import csv
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

IMPORT = "_importado-onedrive"
IGNORAR = {"desktop.ini", "thumbs.db", ".ds_store"}


def longo(p: Path) -> str:
    """Prefixo do Windows para caminhos acima de 260 caracteres."""
    s = str(p.resolve()) if not str(p).startswith("\\\\?\\") else str(p)
    if os.name == "nt" and not s.startswith("\\\\?\\"):
        s = "\\\\?\\UNC\\" + s[2:] if s.startswith("\\\\") else "\\\\?\\" + s
    return s


def limpar(nome: str) -> str:
    for c in '<>:"/\\|?*':
        nome = nome.replace(c, "-")
    return nome.strip().rstrip(".") or "sem-nome"


def tem_sigilo(pasta: Path) -> bool:
    for raiz, _, arqs in os.walk(longo(pasta)):
        if any(a.lower() == "sigiloso.txt" for a in arqs):
            return True
    return False


def ler_linhas(caminho: Path):
    with open(caminho, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def destino_da_linha(l, clientes: Path, raiz_comum: Path):
    partes = [p for p in l["destino_sugerido"].replace("\\", "/").split("/") if p]
    if partes and partes[0].lower() == "clientes":
        partes = partes[1:]
    if len(partes) < 2 or "[DECIDIR]" in partes[0]:
        return None, "área ou cliente não definidos em destino_sugerido"
    origem = Path(l["caminho_origem"])
    try:
        relativo = origem.relative_to(raiz_comum)
    except ValueError:
        relativo = Path(origem.name)
    return clientes / limpar(partes[0]) / limpar(partes[1]) / IMPORT / relativo, None


def main() -> int:
    ap = argparse.ArgumentParser(description="Cópia aprovada do OneDrive para a pasta Clientes.")
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--clientes", required=True, type=Path)
    ap.add_argument("--executar", action="store_true", help="sem isto, só simula")
    args = ap.parse_args()

    linhas = ler_linhas(args.csv)
    if not linhas or "caminho_origem" not in linhas[0]:
        print("ERRO: CSV sem a coluna caminho_origem. Gere o inventário sem --anonimo.", file=sys.stderr)
        return 1
    aprovadas = [l for l in linhas if l.get("aprovar", "").strip().lower() in ("sim", "s", "x")]
    if not aprovadas:
        print("Nenhuma linha com 'sim' na coluna aprovar. Nada a fazer.")
        return 0
    origens = [Path(l["caminho_origem"]) for l in aprovadas if l["caminho_origem"]]
    raiz_comum = Path(os.path.commonpath([str(o) for o in origens])) if len(origens) > 1 else origens[0].parent
    clientes = args.clientes.resolve()
    if any(clientes == o or o in clientes.parents for o in origens):
        print("ERRO: a pasta Clientes não pode ficar dentro de uma pasta de origem.", file=sys.stderr)
        return 1

    plano, problemas, total = [], [], 0
    for l in aprovadas:
        origem = Path(l["caminho_origem"])
        if l.get("sigiloso", "").strip().lower() == "sim" or (origem.is_dir() and tem_sigilo(origem)):
            problemas.append(f"sigilosa, não copiada (mover pessoalmente): {origem}")
            continue
        if not origem.is_dir():
            problemas.append(f"origem não encontrada: {origem}")
            continue
        destino, erro = destino_da_linha(l, clientes, raiz_comum)
        if erro:
            problemas.append(f"{erro}: {origem}")
            continue
        for r, dirs, arqs in os.walk(longo(origem)):
            rel = Path(r[len(longo(origem)):].lstrip("\\/"))
            for a in arqs:
                if a.lower() in IGNORAR:
                    continue
                src = Path(r) / a
                try:
                    tam = os.stat(src).st_size
                except OSError as e:
                    problemas.append(f"sem acesso ({type(e).__name__}): {src}")
                    continue
                plano.append((src, destino / rel / a, tam))
                total += tam

    livre = shutil.disk_usage(clientes if clientes.exists() else clientes.anchor).free
    print(f"Pastas aprovadas: {len(aprovadas)} · arquivos a copiar: {len(plano)} · {total / 1024**3:.2f} GB")
    print(f"Espaço livre no destino: {livre / 1024**3:.2f} GB")
    for p in problemas:
        print("  !!", p)
    if not args.executar:
        for src, dst, _ in plano[:15]:
            print(f"  {str(src).replace(chr(92) * 2 + '?' + chr(92), '')}  ->  {dst}")
        if len(plano) > 15:
            print(f"  ... e mais {len(plano) - 15}")
        print("Simulação. Para copiar, rode de novo com --executar.")
        return 0
    if total > livre * 0.9:
        print("ERRO: espaço livre insuficiente (margem de 10%). Libere espaço ou copie em partes.", file=sys.stderr)
        return 1

    log_dir = clientes / "_inventario"
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / f"migracao-{datetime.now():%Y-%m-%d-%H%M}.csv"
    copiados = pulados = falhas = 0
    with open(log, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["situacao", "origem", "destino", "bytes"])
        for i, (src, dst, tam) in enumerate(plano, 1):
            try:
                os.makedirs(longo(dst.parent), exist_ok=True)
                alvo = dst
                if os.path.exists(longo(dst)):
                    if os.stat(longo(dst)).st_size == tam:
                        w.writerow(["já existia", src, dst, tam])
                        pulados += 1
                        continue
                    alvo = dst.with_name(f"{dst.stem} (onedrive){dst.suffix}")
                shutil.copy2(longo(src), longo(alvo))
                ok = os.stat(longo(alvo)).st_size == tam
                w.writerow(["copiado" if ok else "TAMANHO DIFERENTE", src, alvo, tam])
                copiados += ok
                falhas += not ok
            except OSError as e:
                w.writerow([f"FALHA {type(e).__name__}", src, dst, tam])
                falhas += 1
            if i % 200 == 0:
                print(f"  {i}/{len(plano)}")
    print(f"Copiados: {copiados} · já existiam: {pulados} · falhas: {falhas}. Registro: {log}")
    print("O OneDrive não foi alterado.")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
