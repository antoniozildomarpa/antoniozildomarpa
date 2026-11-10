#!/usr/bin/env python3
"""Inventário das pastas de clientes no OneDrive (ou em qualquer pasta), lendo só nomes e metadados.

O que NÃO faz: não abre nenhum arquivo, não calcula hash, não move, não renomeia, não apaga.
Arquivos do OneDrive que estão só na nuvem continuam só na nuvem: o script lê o atributo do Windows
e o tamanho informado, sem forçar o download.

Uso:
    python inventario_pastas.py [--raiz <pasta>] --saida <pasta_relatorio> [--anonimo]

Sem --raiz, procura o OneDrive do usuário (variáveis OneDrive, OneDriveCommercial, OneDriveConsumer).

Saída em <pasta_relatorio>:
    resumo.md               volume, estrutura, tipos de arquivo, idade, problemas encontrados
    pastas.csv              uma linha por pasta (arquivos, subpastas, tamanho, última alteração)
    arquivos.csv            uma linha por arquivo (categoria, tamanho, data, nuvem/local, sinais)
    proposta_migracao.csv   origem -> destino sugerido em Clientes/{Área}/{Cliente}/, coluna "aprovar"
    mapa_anonimo.csv        (só com --anonimo) tabela código -> nome real. NÃO SAI DO COMPUTADOR.

Com --anonimo, nomes de clientes viram códigos (Cliente-0001), nomes de arquivo viram categoria e
extensão, e números de processo, CPF e requerimentos do INSS são mascarados. É a versão que pode ser
mostrada fora do escritório, depois de conferida pela advogada.
"""
import argparse
import csv
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Atributos de arquivo do Windows (OneDrive "arquivos sob demanda")
ATTR_OFFLINE = 0x1000
ATTR_RECALL_ON_OPEN = 0x40000
ATTR_PINNED = 0x80000
ATTR_UNPINNED = 0x100000
ATTR_RECALL_ON_DATA_ACCESS = 0x400000

CNJ = re.compile(r"\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}")
CPF = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
INSS = re.compile(r"(?:INSS|NB|benef[íi]cio|requerimento|protocolo)[\s_.-]*(?:n[ºo°.]?\s*)?\d{9,10}", re.I)
DATA_NOME = re.compile(r"(19|20)\d{2}[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])|\b(0[1-9]|[12]\d|3[01])[-_.](0[1-9]|1[0-2])[-_.](19|20)?\d{2}\b")
VERSAO = re.compile(r"\b(v\d+|vers[ãa]o|final|novo|nova|corrigid[oa]|c[óo]pia|copy|\(\d+\))\b", re.I)

AREAS = [
    ("Previdenciário RPPS", r"rpps|ipaset|regime\s*pr[óo]prio|servidor|aposentad|pens[ãa]o\s*por\s*morte\s*servidor|proventos"),
    ("Previdenciário RGPS", r"rgps|inss|bpc|loas|aux[íi]lio|sal[áa]rio[- ]maternidade|aposentadoria|benef[íi]cio|previd"),
    ("Família e Sucessões", r"fam[íi]lia|div[óo]rcio|alimentos|guarda|invent[áa]rio|partilha|uni[ãa]o\s*est[áa]vel|sucess|curatela|interdi"),
    ("Direito Público", r"p[úu]blic|prefeitura|munic[íi]pio|estado|concurso|improbidade|licita|administrativ|servidor\s*p[úu]blico"),
    ("Consumidor", r"consumidor|banco|empr[ée]stimo|consignado|cart[ãa]o|celpa|equatorial|energia|telefon|operadora|procon|negativa"),
    ("Ambiental", r"ambiental|ibama|semas|embargo|desmat|auto\s*de\s*infra"),
]
AREAS = [(n, re.compile(r, re.I)) for n, r in AREAS]

CATEGORIAS = [
    ("documento pessoal", r"\brg\b|\bcpf\b|\bcnh\b|identidade|certid|comprovante|resid[êe]ncia|t[íi]tulo\s*eleitor|ctps|carteira\s*de\s*trabalho|nis\b|pis\b"),
    ("procuração/contrato", r"procura[çc]|contrato|honor[áa]rio|declara[çc][ãa]o\s*de\s*hipossu|substabelec"),
    ("peça processual", r"peti[çc]|inicial|contesta|r[ée]plica|recurso|apela|agravo|contrarraz|embargos|memoriais|manifesta"),
    ("decisão judicial", r"senten[çc]a|decis[ãa]o|despacho|ac[óo]rd[ãa]o|intima[çc]|cita[çc]|mandado|alvar[áa]"),
    ("documento médico", r"laudo|atestado|receita|exame|prontu[áa]rio|per[íi]cia|\bcid\b"),
    ("previdenciário", r"cnis|carta\s*de\s*concess|indeferim|exig[êe]ncia|ppp|ltcat|contracheque|holerite|ficha\s*financeira|portaria|planilha\s*de\s*c[áa]lculo"),
]
CATEGORIAS = [(n, re.compile(r, re.I)) for n, r in CATEGORIAS]
EXT_GRUPO = {
    "pdf": "PDF", "doc": "Word", "docx": "Word", "odt": "Word", "rtf": "Word",
    "xls": "Planilha", "xlsx": "Planilha", "csv": "Planilha", "ods": "Planilha",
    "jpg": "Foto", "jpeg": "Foto", "png": "Foto", "heic": "Foto", "webp": "Foto", "bmp": "Foto", "tif": "Foto", "tiff": "Foto",
    "opus": "Áudio", "ogg": "Áudio", "mp3": "Áudio", "m4a": "Áudio", "wav": "Áudio", "aac": "Áudio", "amr": "Áudio",
    "mp4": "Vídeo", "mov": "Vídeo", "avi": "Vídeo", "3gp": "Vídeo",
    "zip": "Compactado", "rar": "Compactado", "7z": "Compactado",
    "txt": "Texto", "md": "Texto", "eml": "E-mail", "msg": "E-mail", "html": "Texto",
}
IGNORAR_NOMES = {"desktop.ini", "thumbs.db", ".ds_store"}
# Palavras que formam nomes de pasta de área ou de organização (não de cliente). Um nome feito só delas
# é tratado como categoria: aparece no relatório e não conta como cliente. Qualquer outra palavra
# (um nome de pessoa, por exemplo) faz a pasta ser tratada como cliente e, no modo anônimo, codificada.
CATEGORIA_PALAVRAS = set("""
previdenciario previdenciaria previdencia rpps rgps inss ipaset aposentadoria aposentadorias revisao revisoes
pensao pensoes bpc loas auxilio auxilios beneficio beneficios salario maternidade doenca acidente incapacidade
familia familias divorcio divorcios alimentos guarda inventario inventarios sucessoes sucessao partilha uniao estavel
curatela interdicao civel civil civeis
publico publica direito administrativo servidor servidores municipio prefeitura estado concurso concursos
consumidor consumidores banco bancos bancario emprestimo emprestimos consignado consignados energia telefonia
ambiental ambientais ibama semas trabalhista trabalhistas criminal penal tributario
clientes cliente processos processo casos caso ativos ativas encerrados encerradas arquivados arquivo arquivos
antigos antigas novos novas nova novo pasta pastas documentos docs modelos modelo diversos geral outros
escritorio juridico administrativos judiciais judicial extrajudicial requerimentos requerimento peticoes
digitalizados scan scans whatsapp downloads fotos e de do da dos das em x
""".split())
_ACENTOS = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC")


def eh_categoria(nome):
    palavras = re.findall(r"[A-Za-zÀ-ÿ]+|\d+", nome.translate(_ACENTOS).lower())
    if not palavras:
        return False
    return all(p in CATEGORIA_PALAVRAS or re.fullmatch(r"(19|20)\d{2}", p) for p in palavras)


def indice_cliente(partes):
    """Posição da pasta de cliente no caminho: a primeira que não é só área/categoria."""
    for i, nome in enumerate(partes):
        if not eh_categoria(nome):
            return i
    return None
LIMITE_CAMINHO = 240  # perto do limite de 260 do Windows


def achar_onedrive():
    """Só escolhe sozinho se houver um único OneDrive. Com pessoal e corporativo, exige --raiz."""
    achados = []
    for var in ("OneDriveCommercial", "OneDriveConsumer", "OneDrive"):
        p = os.environ.get(var)
        if p and os.path.isdir(p) and os.path.normcase(os.path.realpath(p)) not in (
                os.path.normcase(os.path.realpath(a)) for a in achados):
            achados.append(p)
    if len(achados) == 1:
        return Path(achados[0])
    if achados:
        print("Há mais de um OneDrive neste computador. Informe qual varrer com --raiz:", file=sys.stderr)
        for a in achados:
            print(f"  {a}", file=sys.stderr)
    return None


def area_provavel(texto):
    for nome, rx in AREAS:
        if rx.search(texto):
            return nome
    return ""


def categoria(nome, ext):
    for cat, rx in CATEGORIAS:
        if rx.search(nome):
            return cat
    return EXT_GRUPO.get(ext, "outro").lower()


def situacao_nuvem(attrs):
    if attrs is None:
        return "desconhecido"
    if attrs & (ATTR_RECALL_ON_DATA_ACCESS | ATTR_RECALL_ON_OPEN | ATTR_OFFLINE):
        return "só na nuvem"
    if attrs & ATTR_PINNED:
        return "sempre no dispositivo"
    return "local"


def mascarar(texto):
    texto = CNJ.sub("[CNJ]", texto)
    texto = CPF.sub("[CPF]", texto)
    texto = INSS.sub("[INSS]", texto)
    return texto


class Anonimizador:
    def __init__(self, ativo):
        self.ativo = ativo
        self.mapa = {}
        self.contagem = Counter()

    def caminho(self, partes):
        """Caminho exibido. No modo anônimo, só nomes de categoria ficam; o resto vira código."""
        if not self.ativo:
            return "/".join(partes)
        ic = indice_cliente(partes)
        saida = []
        for i, nome in enumerate(partes):
            if ic is None or i < ic:
                saida.append(mascarar(nome) if eh_categoria(nome) else self.codigo("Pasta", partes[:i + 1]))
            elif i == ic:
                saida.append(self.codigo("Cliente", partes[:i + 1]))
            else:
                saida.append(self.codigo("Pasta", partes[:i + 1]))
        return "/".join(saida)

    def codigo(self, tipo, chave):
        if chave not in self.mapa:
            self.contagem[tipo] += 1
            self.mapa[chave] = f"{tipo}-{self.contagem[tipo]:04d}"
        return self.mapa[chave]

    def arquivo(self, nome, cat, ext):
        if not self.ativo:
            return nome
        return f"[{cat}].{ext}" if ext else f"[{cat}]"


def varrer(raiz: Path, anon: Anonimizador):
    arquivos, pastas = [], {}
    inicio = time.time()
    pilha = [(raiz, 0, ())]
    while pilha:
        atual, nivel, partes = pilha.pop()
        info = pastas.setdefault(partes, {"nivel": nivel, "arquivos": 0, "subpastas": 0, "bytes": 0,
                                          "ultima": 0.0, "nuvem": 0, "real": str(atual)})
        try:
            entradas = list(os.scandir(atual))
        except OSError as e:
            info["erro"] = type(e).__name__
            continue
        if any(e.name.lower() == "sigiloso.txt" for e in entradas):
            info["sigiloso"] = True  # registra que existe; não lista o conteúdo
            continue
        for e in entradas:
            try:
                if e.is_dir(follow_symlinks=False):
                    info["subpastas"] += 1
                    pilha.append((Path(e.path), nivel + 1, partes + (e.name,)))
                    continue
                if e.name.lower() in IGNORAR_NOMES:
                    continue
                st = e.stat(follow_symlinks=False)
            except OSError:
                continue
            attrs = getattr(st, "st_file_attributes", None)
            ext = e.name.rsplit(".", 1)[-1].lower() if "." in e.name else ""
            cat = categoria(e.name, ext)
            nuvem = situacao_nuvem(attrs)
            arquivos.append({
                "partes": partes, "nivel": nivel, "nome": e.name, "ext": ext, "categoria": cat,
                "grupo": EXT_GRUPO.get(ext, "Outro"), "bytes": st.st_size, "modificado": st.st_mtime,
                "nuvem": nuvem, "len_caminho": len(e.path),
                "tem_cnj": bool(CNJ.search(e.name)), "tem_cpf": bool(CPF.search(e.name)),
                "tem_inss": bool(INSS.search(e.name)), "tem_data": bool(DATA_NOME.search(e.name)),
                "tem_versao": bool(VERSAO.search(e.name)),
            })
            info["arquivos"] += 1
            info["bytes"] += st.st_size
            info["ultima"] = max(info["ultima"], st.st_mtime)
            info["nuvem"] += nuvem == "só na nuvem"
    # tamanho acumulado das pastas (inclui subpastas)
    acumulado = defaultdict(lambda: [0, 0, 0.0])
    for a in arquivos:
        for i in range(len(a["partes"]) + 1):
            k = a["partes"][:i]
            acumulado[k][0] += 1
            acumulado[k][1] += a["bytes"]
            acumulado[k][2] = max(acumulado[k][2], a["modificado"])
    return arquivos, pastas, acumulado, time.time() - inicio


def mb(b):
    return f"{b / 1024 / 1024:,.1f} MB".replace(",", "X").replace(".", ",").replace("X", ".")


def data(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""


def caminho_exibido(partes, anon):
    return anon.caminho(partes)


def escrever_csv(caminho, campos, linhas):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        w.writeheader()
        w.writerows(linhas)


def main() -> int:
    ap = argparse.ArgumentParser(description="Inventário de pastas (só nomes e metadados).")
    ap.add_argument("--raiz", type=Path)
    ap.add_argument("--saida", required=True, type=Path)
    ap.add_argument("--anonimo", action="store_true")
    args = ap.parse_args()

    raiz = args.raiz or achar_onedrive()
    if not raiz or not raiz.is_dir():
        print("Pasta raiz não encontrada. Informe --raiz.", file=sys.stderr)
        return 1
    raiz = raiz.resolve()
    saida = args.saida.resolve()
    if saida == raiz or raiz in saida.parents:
        print("A pasta do relatório não pode ficar dentro da pasta varrida.", file=sys.stderr)
        return 1
    saida.mkdir(parents=True, exist_ok=True)
    anon = Anonimizador(args.anonimo)

    arquivos, pastas, acum, segundos = varrer(raiz, anon)
    agora = time.time()
    total_bytes = sum(a["bytes"] for a in arquivos)

    # ---- pastas.csv
    linhas_p = []
    for partes, info in sorted(pastas.items()):
        tot = acum.get(partes, [0, 0, 0.0])
        linhas_p.append({
            "pasta": caminho_exibido(partes, anon) or "(raiz)",
            "nivel": info["nivel"], "arquivos_diretos": info["arquivos"], "subpastas": info["subpastas"],
            "arquivos_total": tot[0], "tamanho_total_mb": round(tot[1] / 1024 / 1024, 2),
            "ultima_alteracao": data(tot[2]), "so_na_nuvem": info["nuvem"],
            "area_provavel": area_provavel(" ".join(partes)), "erro": info.get("erro", ""),
        })
    escrever_csv(saida / "pastas.csv", list(linhas_p[0].keys()) if linhas_p else ["pasta"], linhas_p)

    # ---- arquivos.csv
    linhas_a = [{
        "pasta": caminho_exibido(a["partes"], anon) or "(raiz)",
        "arquivo": anon.arquivo(a["nome"], a["categoria"], a["ext"]),
        "nivel": a["nivel"], "extensao": a["ext"], "grupo": a["grupo"], "categoria": a["categoria"],
        "tamanho_kb": round(a["bytes"] / 1024, 1), "modificado": data(a["modificado"]), "nuvem": a["nuvem"],
        "caminho_longo": "sim" if a["len_caminho"] > LIMITE_CAMINHO else "",
        "cnj_no_nome": "sim" if a["tem_cnj"] else "", "cpf_no_nome": "sim" if a["tem_cpf"] else "",
        "data_no_nome": "sim" if a["tem_data"] else "", "versao_no_nome": "sim" if a["tem_versao"] else "",
    } for a in arquivos]
    escrever_csv(saida / "arquivos.csv", list(linhas_a[0].keys()) if linhas_a else ["arquivo"], linhas_a)

    # ---- proposta de migração: uma linha por pasta de cliente (primeira pasta que não é só área/categoria)
    def pasta_cliente(partes):
        ic = indice_cliente(partes)
        return None if ic is None else partes[:ic + 1]

    candidatos = sorted({pasta_cliente(p) for p in pastas if pasta_cliente(p)})
    linhas_m = []
    cnj_por_pasta = defaultdict(set)
    for a in arquivos:
        chave = pasta_cliente(a["partes"])
        if chave:
            for m in CNJ.findall(a["nome"] + " " + " ".join(a["partes"])):
                cnj_por_pasta[chave].add(re.sub(r"\D", "", m))
    for partes in candidatos:
        tot = acum.get(partes, [0, 0, 0.0])
        area = area_provavel(" ".join(partes)) or "[DECIDIR]"
        nome_cliente = caminho_exibido(partes, anon).split("/")[-1]
        linhas_m.append({
            "aprovar": "", "origem": caminho_exibido(partes, anon),
            "destino_sugerido": f"Clientes/{area}/{nome_cliente}/",
            "area_sugerida": area, "arquivos": tot[0], "tamanho_mb": round(tot[1] / 1024 / 1024, 2),
            "ultima_alteracao": data(tot[2]),
            "situacao": "ativo (últimos 12 meses)" if tot[2] and agora - tot[2] < 365 * 86400 else "parado há mais de 1 ano",
            "processos_no_nome": len(cnj_por_pasta.get(partes, ())),
            "sigiloso": "sim" if any(i.get("sigiloso") for p, i in pastas.items() if p[:len(partes)] == partes) else "",
            "observacao": "",
            "caminho_origem": "" if args.anonimo else str(raiz.joinpath(*partes)),
        })
    escrever_csv(saida / "proposta_migracao.csv",
                 list(linhas_m[0].keys()) if linhas_m else ["origem"], linhas_m)

    # ---- problemas
    soltos = [a for a in arquivos if a["nivel"] <= 1]
    longos = [a for a in arquivos if a["len_caminho"] > LIMITE_CAMINHO]
    com_cpf = [a for a in arquivos if a["tem_cpf"]]
    vazias = [p for p, i in pastas.items() if p and acum.get(p, [0])[0] == 0]
    dup = Counter((a["nome"].lower(), a["bytes"]) for a in arquivos if a["bytes"] > 0)
    duplicados = {k: v for k, v in dup.items() if v > 1}
    cnj_global = defaultdict(set)
    for a in arquivos:
        for m in CNJ.findall(a["nome"] + " " + " ".join(a["partes"])):
            cnj_global[re.sub(r"\D", "", m)].add(a["partes"][:2])
    cnj_espalhado = {k: v for k, v in cnj_global.items() if len(v) > 1}
    profundidades = Counter(a["nivel"] for a in arquivos)
    grupos = Counter(a["grupo"] for a in arquivos)
    grupos_bytes = Counter()
    for a in arquivos:
        grupos_bytes[a["grupo"]] += a["bytes"]
    cats = Counter(a["categoria"] for a in arquivos)
    nuvem = Counter(a["nuvem"] for a in arquivos)
    idade = Counter()
    for a in arquivos:
        anos = (agora - a["modificado"]) / (365 * 86400)
        idade["até 1 ano" if anos < 1 else "1 a 3 anos" if anos < 3 else "3 a 5 anos" if anos < 5 else "mais de 5 anos"] += 1
    nivel1 = sorted(((p, acum[p]) for p, i in pastas.items() if i["nivel"] == 1), key=lambda x: -x[1][0])
    padrao_data = sum(a["tem_data"] for a in arquivos)
    padrao_versao = sum(a["tem_versao"] for a in arquivos)
    sem_area = sum(1 for m in linhas_m if m["area_sugerida"] == "[DECIDIR]")

    def pct(n, d):
        return f"{100 * n / d:.0f}%" if d else "0%"

    n = len(arquivos)
    r = []
    r.append(f"# Inventário de pastas – {datetime.now():%Y-%m-%d %H:%M}\n")
    r.append(f"Raiz: `{'[ocultada]' if args.anonimo else raiz}`. Varredura em {segundos:.0f} s, só nomes e metadados; nenhum arquivo foi aberto ou baixado.")
    r.append("Versão anônima: nomes de clientes e de arquivos substituídos; números de processo, CPF e INSS mascarados.\n" if args.anonimo else "")
    r.append("## Volume\n")
    r.append(f"- Arquivos: {n:,}".replace(",", "."))
    r.append(f"- Pastas: {len(pastas) - 1:,}".replace(",", "."))
    r.append(f"- Tamanho total: {mb(total_bytes)}")
    r.append(f"- Só na nuvem (não baixados no computador): {nuvem.get('só na nuvem', 0)} ({pct(nuvem.get('só na nuvem', 0), n)})")
    r.append(f"- Pastas candidatas a pasta de cliente (nível 2): {len([p for p, i in pastas.items() if i['nivel'] == 2])}\n")
    r.append("## Primeiro nível (como ela organiza hoje)\n")
    r.append("| Pasta | Arquivos | Tamanho | Última alteração | Área provável |\n|---|---|---|---|---|")
    for p, (qtd, b, ult) in nivel1[:40]:
        r.append(f"| {caminho_exibido(p, anon)} | {qtd} | {mb(b)} | {data(ult)} | {area_provavel(' '.join(p)) or '–'} |")
    if len(nivel1) > 40:
        r.append(f"| … mais {len(nivel1) - 40} pastas (ver pastas.csv) | | | | |")
    r.append("\n## Profundidade (em que nível os arquivos estão)\n")
    r.append(" · ".join(f"nível {k}: {v}" for k, v in sorted(profundidades.items())))
    r.append("\n## Tipos de arquivo\n")
    r.append("| Tipo | Arquivos | Tamanho |\n|---|---|---|")
    for g, q in grupos.most_common():
        r.append(f"| {g} | {q} | {mb(grupos_bytes[g])} |")
    r.append("\n## Conteúdo provável (pelo nome)\n")
    r.append(" · ".join(f"{c}: {q}" for c, q in cats.most_common()))
    r.append("\n## Idade (última alteração)\n")
    r.append(" · ".join(f"{k}: {idade[k]}" for k in ("até 1 ano", "1 a 3 anos", "3 a 5 anos", "mais de 5 anos")))
    r.append("\n## Padrão de nomes\n")
    r.append(f"- Arquivos com data no nome: {padrao_data} ({pct(padrao_data, n)})")
    r.append(f"- Arquivos com marca de versão no nome (final, v2, cópia, (1)): {padrao_versao} ({pct(padrao_versao, n)})")
    r.append(f"- Pastas de cliente sem área identificável pelo nome: {sem_area} de {len(linhas_m)}\n")
    r.append("## Problemas encontrados\n")
    r.append(f"- Arquivos soltos na raiz ou no 1º nível, fora de pasta de cliente: {len(soltos)}")
    r.append(f"- Caminhos longos (mais de {LIMITE_CAMINHO} caracteres, risco no Windows e na cópia): {len(longos)}")
    r.append(f"- Arquivos com CPF no nome (dado pessoal exposto no nome): {len(com_cpf)}")
    r.append(f"- Pastas vazias: {len(vazias)}")
    r.append(f"- Prováveis duplicados (mesmo nome e mesmo tamanho): {len(duplicados)} grupos, {sum(duplicados.values()) - len(duplicados)} cópias extras")
    r.append(f"- Números de processo que aparecem em mais de uma pasta de cliente: {len(cnj_espalhado)}")
    r.append(f"- Pastas com SIGILOSO.txt (registradas, conteúdo não listado): {sum(1 for i in pastas.values() if i.get('sigiloso'))}")
    r.append("\n## Próximos passos\n")
    r.append("1. Conferir a `proposta_migracao.csv`: área e destino de cada pasta, marcando `sim` em `aprovar`.")
    r.append("2. Decidir o que fazer com pastas paradas há mais de um ano (migrar como arquivo morto ou deixar no OneDrive).")
    r.append("3. A cópia para o Google Drive só começa depois da aprovação, e só copia: o OneDrive fica intacto até a conferência.")
    (saida / "resumo.md").write_text("\n".join(x for x in r if x is not None), encoding="utf-8")

    if args.anonimo:
        escrever_csv(saida / "mapa_anonimo.csv", ["codigo", "nivel", "nome_real"],
                     [{"codigo": c, "nivel": k[0], "nome_real": k[1]} for k, c in anon.mapa.items()])
        print(f"ATENÇÃO: {saida / 'mapa_anonimo.csv'} liga os códigos aos nomes reais. Não envie esse arquivo.")

    print(f"OK: {n} arquivos, {len(pastas) - 1} pastas, {mb(total_bytes)} em {segundos:.0f} s. Relatório: {saida / 'resumo.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
