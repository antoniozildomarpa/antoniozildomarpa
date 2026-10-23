"""Cria e mantém a pasta padronizada de um caso técnico (demanda do SEI).

Uso:
    python caso.py criar --nup "02001.012345/2026-11" --apelido "embargo fazenda x" \
        --tipo relatorio --demandante "DITEC/PA" --prazo 2026-11-05
    python caso.py registrar --pasta "<pasta do caso>" --etapa triagem --texto "Árvore lida, 4 documentos baixados"
    python caso.py situacao --pasta "<pasta do caso>"

A raiz padrão é H:\\Meu Drive\\_GEO\\_DEMANDAS_EMI\\<ano>. Use --raiz para outra pasta.
O script nunca apaga nem sobrescreve arquivos: se a pasta já existir, só cria o que faltar.
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

RAIZ_PADRAO = r"H:\Meu Drive\_GEO\_DEMANDAS_EMI"

SUBPASTAS = [
    "00_Ficha",
    "01_Processo_SEI",
    "02_Insumos/imagens",
    "02_Insumos/vetores_baixados",
    "02_Insumos/consultas_online",
    "02_Insumos/tabelas",
    "02_Insumos/mapas_scan",
    "02_Insumos/documentos_imovel",
    "03_Geo/vetores_produzidos",
    "03_Geo/raster",
    "03_Geo/georreferenciados",
    "04_Figuras",
    "05_Documento",
    "06_Anexos",
    "07_SEI",
]

TIPOS = {
    "relatorio": "Relatório Técnico",
    "informacao": "Informação Técnica",
    "parecer": "Parecer Técnico",
    "manifestacao": "Manifestação Técnica",
}

ETAPAS = [
    "triagem",
    "leitura",
    "conferencia_1",
    "geo",
    "conferencia_2",
    "figuras",
    "redacao",
    "revisao",
    "conferencia_3",
    "anexos",
    "conferencia_4",
    "sei",
    "assinatura_envio",
]


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def slug(texto):
    """Texto sem acentos, minúsculo, com hífens, seguro para nome de pasta no Windows."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t[:40].rstrip("-")


def nup_para_pasta(nup):
    """02001.012345/2026-11 -> 02001.012345-2026-11 (barras e caracteres proibidos viram hífen)."""
    t = re.sub(r'[\\/:*?"<>|\s]+', "-", nup.strip())
    return t.strip("-")


def ler_ficha(pasta):
    caminho = pasta / "00_Ficha" / "ficha.json"
    if not caminho.exists():
        sys.exit(f"Ficha não encontrada: {caminho}")
    return json.loads(caminho.read_text(encoding="utf-8")), caminho


def descrever(item):
    """Uma linha legível para itens da ficha (texto simples ou dicionário)."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict) and "camada" in item and "area_ha" in item:
        ha = f"{item['area_ha']:.4f}".replace(".", ",") if item.get("area_ha") is not None else "—"
        per = f"{item['perimetro_m']:.2f}".replace(".", ",") if item.get("perimetro_m") is not None else "—"
        extra = f", datum de origem {item['datum_origem']}" if item.get("datum_origem") not in (None, "SIRGAS2000") else ""
        return f"{item['camada']}: {ha} ha, perímetro {per} m ({item.get('calculo', '')}{extra}; {item.get('em', '')})"
    return json.dumps(item, ensure_ascii=False)


def gravar_ficha_md(pasta, ficha):
    linhas = [
        f"# Ficha do caso – {ficha['nup']}",
        "",
        "Gerada a partir de `ficha.json`. Edite o JSON ou peça ao Claude para atualizar; este arquivo é refeito a cada atualização.",
        "",
        "## Demanda",
        "",
        "| Campo | Valor |",
        "| --- | --- |",
    ]
    campos = [
        ("NUP", "nup"),
        ("Apelido", "apelido"),
        ("Documento a produzir", "tipo_documento"),
        ("Setor demandante", "setor_demandante"),
        ("Documento da demanda (nº SEI)", "documento_demanda_sei"),
        ("Pedido", "pedido"),
        ("Prazo", "prazo"),
        ("Interessado", "interessado"),
        ("Município/UF", "municipio_uf"),
        ("Bioma", "bioma"),
        ("Criado em", "criado_em"),
    ]
    for rotulo, chave in campos:
        linhas.append(f"| {rotulo} | {ficha.get(chave) or '—'} |")

    linhas += ["", "## Situação das etapas", "", "| Etapa | Situação | Atualizado em |", "| --- | --- | --- |"]
    for etapa in ETAPAS:
        e = ficha["etapas"].get(etapa, {})
        linhas.append(f"| {etapa} | {e.get('situacao', 'pendente')} | {e.get('em', '—')} |")

    for titulo, chave in [
        ("Documentos baixados do SEI", "documentos_baixados"),
        ("Camadas usadas", "camadas"),
        ("Consultas online (fonte, data e hora)", "consultas_online"),
        ("Áreas calculadas", "areas"),
        ("Anexos previstos", "anexos"),
    ]:
        linhas += ["", f"## {titulo}", ""]
        itens = ficha.get(chave) or []
        linhas += [f"- {descrever(i)}" for i in itens] or ["- (nenhum ainda)"]

    (pasta / "00_Ficha" / "ficha.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def registrar_linha(pasta, etapa, texto):
    caminho = pasta / "00_Ficha" / "registro.md"
    if not caminho.exists():
        caminho.write_text("# Registro do caso\n\n| Data e hora | Etapa | O que foi feito |\n| --- | --- | --- |\n", encoding="utf-8")
    with caminho.open("a", encoding="utf-8") as f:
        f.write(f"| {agora()} | {etapa} | {texto.replace('|', '/')} |\n")


def cmd_criar(a):
    if a.tipo not in TIPOS:
        sys.exit(f"Tipo inválido: {a.tipo}. Use um de: {', '.join(TIPOS)}")
    ano = a.ano or str(datetime.now().year)
    raiz = Path(a.raiz) / ano
    nome = nup_para_pasta(a.nup) + (f"_{slug(a.apelido)}" if a.apelido else "")
    pasta = raiz / nome

    existentes = [s for s in SUBPASTAS if (pasta / s).exists()]
    if a.simular:
        print(f"[simulação] Pasta do caso: {pasta}")
        for s in SUBPASTAS:
            print(f"  {'(já existe) ' if s in existentes else ''}{s}")
        return

    for s in SUBPASTAS:
        (pasta / s).mkdir(parents=True, exist_ok=True)

    caminho_json = pasta / "00_Ficha" / "ficha.json"
    if caminho_json.exists():
        ficha = json.loads(caminho_json.read_text(encoding="utf-8"))
        registrar_linha(pasta, "estrutura", "Pasta já existia; subpastas que faltavam foram criadas. Ficha mantida.")
        print(f"Pasta já existia, ficha mantida: {pasta}")
    else:
        ficha = {
            "nup": a.nup,
            "apelido": a.apelido or "",
            "tipo_documento": TIPOS[a.tipo],
            "setor_demandante": a.demandante or "",
            "documento_demanda_sei": a.documento_sei or "",
            "pedido": a.pedido or "",
            "prazo": a.prazo or "",
            "interessado": "",
            "municipio_uf": "",
            "bioma": "",
            "criado_em": agora(),
            "pasta": str(pasta),
            "etapas": {e: {"situacao": "pendente"} for e in ETAPAS},
            "documentos_baixados": [],
            "camadas": [],
            "consultas_online": [],
            "areas": [],
            "anexos": [],
        }
        caminho_json.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
        registrar_linha(pasta, "estrutura", f"Pasta e ficha criadas ({TIPOS[a.tipo]}).")
        print(f"Caso criado: {pasta}")

    gravar_ficha_md(pasta, ficha)


def cmd_registrar(a):
    pasta = Path(a.pasta)
    ficha, caminho = ler_ficha(pasta)
    if a.etapa in ETAPAS:
        ficha["etapas"][a.etapa] = {"situacao": a.situacao, "em": agora()}
        caminho.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
        gravar_ficha_md(pasta, ficha)
    registrar_linha(pasta, a.etapa, a.texto)
    print(f"Registrado em {pasta / '00_Ficha' / 'registro.md'}")


def cmd_situacao(a):
    ficha, _ = ler_ficha(Path(a.pasta))
    print(f"{ficha['nup']} – {ficha['tipo_documento']} – prazo {ficha.get('prazo') or '—'}")
    for etapa in ETAPAS:
        e = ficha["etapas"].get(etapa, {})
        print(f"  {etapa:<18} {e.get('situacao', 'pendente'):<12} {e.get('em', '')}")
    proxima = next((e for e in ETAPAS if ficha["etapas"].get(e, {}).get("situacao") != "concluida"), None)
    print(f"Próxima etapa: {proxima or 'nenhuma, caso concluído'}")


def main():
    p = argparse.ArgumentParser(description="Pasta padronizada de casos técnicos do SEI.")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("criar", help="Cria a pasta e a ficha do caso")
    c.add_argument("--nup", required=True, help="Número do processo no SEI")
    c.add_argument("--apelido", help="Nome curto para identificar o caso")
    c.add_argument("--tipo", required=True, help="relatorio, informacao, parecer ou manifestacao")
    c.add_argument("--demandante", help="Setor que pediu o documento")
    c.add_argument("--documento-sei", help="Número SEI do documento da demanda")
    c.add_argument("--pedido", help="O que foi pedido, em uma frase")
    c.add_argument("--prazo", help="AAAA-MM-DD")
    c.add_argument("--raiz", default=RAIZ_PADRAO, help="Pasta-raiz das demandas (sem o ano)")
    c.add_argument("--ano", help="Subpasta do ano (padrão: ano atual)")
    c.add_argument("--simular", action="store_true", help="Mostra o que seria criado, sem criar")
    c.set_defaults(func=cmd_criar)

    r = sub.add_parser("registrar", help="Registra uma etapa no registro e na ficha")
    r.add_argument("--pasta", required=True)
    r.add_argument("--etapa", required=True, help=f"Uma de: {', '.join(ETAPAS)} (ou outro nome, só para o registro)")
    r.add_argument("--situacao", default="concluida", help="pendente, em_andamento ou concluida")
    r.add_argument("--texto", required=True)
    r.set_defaults(func=cmd_registrar)

    s = sub.add_parser("situacao", help="Mostra a situação das etapas e a próxima")
    s.add_argument("--pasta", required=True)
    s.set_defaults(func=cmd_situacao)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
