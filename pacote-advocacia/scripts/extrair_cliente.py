#!/usr/bin/env python3
"""Extrai o texto de todos os documentos da pasta de um cliente e separa os dados candidatos à ficha.

Roda no computador, sem enviar nada para fora. Tudo o que gera fica DENTRO da pasta do cliente,
em <cliente>/_extracao/ (regra do CLAUDE.md: dados de cliente não saem da pasta dele).

    python extrair_cliente.py "<pasta do cliente>" [--audio] [--max-paginas 40] [--max-mb 60] [--refazer]
    python extrair_cliente.py --lote "<pasta Clientes>" [mesmas opções]     (todas as pastas Área/Cliente)

O que lê:
    PDF (texto; OCR nas páginas escaneadas, até --max-paginas por arquivo)
    Word .docx, Excel, PowerPoint (MarkItDown) e Word .doc antigo (pelo próprio Word, se instalado)
    Fotos e imagens (OCR), inclusive HEIC do iPhone
    E-mails .eml, textos .txt/.md/.csv/.html
    Áudios (Whisper), só com --audio, porque é lento
O que só registra, sem abrir: vídeos, compactados (.zip/.rar), .msg do Outlook e formatos desconhecidos.

Saída em <cliente>/_extracao/:
    textos/<código>.txt texto de cada arquivo (com o caminho de origem na 1ª linha)
    indice.csv          arquivo, tipo de documento, método, páginas, caracteres, situação
    candidatos.json     CPF, RG, NIS, nascimento, estado civil, endereço, CEP, telefone, e-mail, filiação,
                        qualificação completa, processos, benefícios do INSS, matrícula; cada um com o
                        arquivo e o trecho de onde saiu
    resumo.md           documentos encontrados, o que faltou ler, dados com mais de um valor (conflitos)

Não altera, move nem apaga nenhum documento. Pastas com SIGILOSO.txt são puladas inteiras.
Rodar de novo só processa arquivos novos ou alterados (use --refazer para tudo).
"""
import argparse
import csv
import email
import email.policy
import hashlib
import io
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

SAIDA = "_extracao"
PULAR_PASTAS = {SAIDA, ".git", "__pycache__"}
IGNORAR = {"desktop.ini", "thumbs.db", ".ds_store", "ficha-cliente.md", "ficha-processo.md"}
EXT_TEXTO = {"txt", "md", "csv", "html", "htm", "xml", "json", "rtf"}
EXT_OFFICE = {"docx", "xlsx", "xls", "pptx", "odt", "ods"}
EXT_IMAGEM = {"jpg", "jpeg", "png", "bmp", "tif", "tiff", "webp", "heic", "heif"}
EXT_AUDIO = {"opus", "ogg", "mp3", "m4a", "wav", "aac", "amr", "wma"}
EXT_SO_REGISTRO = {"mp4", "mov", "avi", "3gp", "mkv", "zip", "rar", "7z", "msg", "exe", "lnk"}

# Dados do próprio escritório aparecem em toda procuração e contrato: não são do cliente.
DADOS_ESCRITORIO = [r"98117[-\s]?3173", r"leullamen", r"25[.\s]?617", r"Leulla", r"Mendanha",
                    r"31 de Mar[çc]o,?\s*n?[ºo°]?\s*273", r"Cupua[çc]u"]
ESCRITORIO = re.compile("|".join(DADOS_ESCRITORIO), re.I)

TIPOS_DOC = [
    ("RG / identidade", r"registro\s+geral|carteira\s+de\s+identidade|\bRG\b|c[ée]dula\s+de\s+identidade"),
    ("CPF", r"cadastro\s+de\s+pessoas?\s+f[íi]sicas?|\bCPF\b"),
    ("CNH", r"carteira\s+nacional\s+de\s+habilita|\bCNH\b"),
    ("Comprovante de residência", r"comprovante\s+de\s+(resid|endere)|conta\s+de\s+(luz|energia|[áa]gua)|equatorial|celpa|cosanpa"),
    ("Certidão (nascimento, casamento, óbito)", r"certid[ãa]o\s+de\s+(nascimento|casamento|[óo]bito)"),
    ("Procuração", r"procura[çc][ãa]o|outorgante|outorgad[oa]"),
    ("Contrato de honorários", r"contrato\s+de\s+(presta|honor)|honor[áa]rios\s+advocat"),
    ("Declaração de hipossuficiência", r"hipossufici|declara[çc][ãa]o\s+de\s+pobreza|n[ãa]o\s+possu[io]\s+condi[çc][õo]es"),
    ("CNIS / extrato previdenciário", r"\bCNIS\b|extrato\s+previdenci"),
    ("Carta do INSS (concessão, indeferimento, exigência)", r"carta\s+de\s+(concess|indeferim|exig)|comunica[çc][ãa]o\s+de\s+decis"),
    ("Contracheque / ficha financeira", r"contracheque|holerite|ficha\s+financeira|demonstrativo\s+de\s+pagamento"),
    ("Portaria / ato de aposentadoria", r"\bportaria\b|ato\s+de\s+aposentadoria|ipaset"),
    ("Laudo / atestado médico", r"\blaudo\b|atestado\s+m[ée]dico|\bCID[\s-]?\d|\bCRM\b"),
    ("Petição", r"excelent[íi]ssim|merit[íi]ssim|vem\s+(respeitosamente\s+)?(à|a)\s+presen"),
    ("Decisão / sentença", r"\bsenten[çc]a\b|\bdecis[ãa]o\b|julgo\s+(procedente|improcedente)|\bac[óo]rd[ãa]o\b"),
    ("Intimação / citação", r"\bintima[çc][ãa]o\b|\bcita[çc][ãa]o\b|fica\s+intimad"),
    ("Extrato bancário / empréstimo", r"extrato\s+banc|empr[ée]stimo|consignad|contrato\s+de\s+m[úu]tuo"),
    ("CTPS / vínculo de trabalho", r"carteira\s+de\s+trabalho|\bCTPS\b|\bPPP\b|perfil\s+profissiogr"),
]
TIPOS_DOC = [(n, re.compile(r, re.I)) for n, r in TIPOS_DOC]

DATA = r"(\d{1,2}[/.-]\d{1,2}[/.-](?:19|20)\d{2})"
PADROES = {
    "cpf": re.compile(r"(?<!\d)(\d{3}\.?\d{3}\.?\d{3}-?\d{2})(?!\d)"),
    "rg": re.compile(r"(?:\bRG|registro\s*geral|identidade)[^\dA-Za-z]{0,6}(?:n[ºo°.]?\s*)?([\d.\-]{5,14}[\dXx])"
                     r"(?:\s*[-/,]?\s*(SSP|PC|SEGUP|SESP|DETRAN|IFP)\s*[-/]?\s*([A-Z]{2}))?", re.I),
    "nis_pis_nit": re.compile(r"(?:\bNIS\b|\bPIS\b|\bPASEP\b|\bNIT\b)[^\d]{0,12}(\d{3}\.?\d{5}\.?\d{2}-?\d)", re.I),
    "nascimento": re.compile(r"(?:nascid[oa]\s+em|data\s+de\s+nascimento|nascimento|\bnasc\.?)\s*[:\-]?\s*" + DATA, re.I),
    "estado_civil": re.compile(r"\b(solteir[oa]|casad[oa]|divorciad[oa]|separad[oa]|vi[úu]v[oa]|em\s+uni[ãa]o\s+est[áa]vel|convivente)\b", re.I),
    "endereco": re.compile(r"(?:residente\s+e\s+domiciliad[oa]|resid[êe]ncia|endere[çc]o|domic[íi]lio)\s*(?:na|no|em|à|a|:)?\s*"
                           r"((?:rua|av\.?|avenida|travessa|tv\.?|passagem|estrada|rodovia|vila|alameda|quadra|qd\.?)[^;]{5,160}?)"
                           r"(?=,?\s*(?:telefone|tel\.|celular|fone|e-?mail|vem\b|neste\s+ato|por\s+seu|onde)|;|$)", re.I),
    "cep": re.compile(r"\bCEP[:\s]*(\d{2}\.?\d{3}-?\d{3})\b", re.I),
    "telefone": re.compile(r"(?<!\d)(\(?\d{2}\)?\s?9\s?\d{4}[-\s]?\d{4})(?!\d)"),
    "email": re.compile(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"),
    "filiacao": re.compile(r"(?:filh[oa]\s+de|filia[çc][ãa]o\s*:?|nome\s+da\s+m[ãa]e\s*:?|m[ãa]e\s*:)\s*"
                           r"([A-ZÀ-Ú][A-Za-zÀ-ú' ]{4,70}?(?:\s+e\s+(?:de\s+)?[A-ZÀ-Ú][A-Za-zÀ-ú' ]{4,70}?)?)(?=\s*[,;.]|\s*$)"),
    # roda no texto original: o nome começa no início da linha ou depois de OUTORGANTE:, REQUERENTE: etc.
    "qualificacao": re.compile(r"(?:^|(?:OUTORGANTE|REQUERENTE|AUTORA?|CONTRATANTE|DECLARANTE)\s*:)[ \t]*"
                               r"([A-ZÀ-Ú][A-ZÀ-Ú' ]{6,80},\s*brasileir[oa][\s\S]{20,700}?"
                               r"(?:CEP[:\s]*\d{2}\.?\d{3}-?\d{3}|domiciliad[oa][^.;]{10,200}))", re.M),
    "processo_cnj": re.compile(r"(?<!\d)(\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4})(?!\d)"),
    "beneficio_inss": re.compile(r"(?:\bNB\b|benef[íi]cio\s*(?:n[ºo°.]?)?)\s*[:\-]?\s*(\d{3}\.?\d{3}\.?\d{3}-?\d)", re.I),
    "requerimento_inss": re.compile(r"(?:requerimento|protocolo)\s*(?:n[ºo°.]?)?\s*[:\-]?\s*(\d{9,10})", re.I),
    "matricula": re.compile(r"matr[íi]cula\s*(?:funcional)?\s*(?:n[ºo°.]?)?\s*[:\-]?\s*([\d.\-/]{3,15})", re.I),
    "profissao": re.compile(r"brasileir[oa],\s*[^,]{3,40},\s*([a-zà-ú][a-zà-ú\s()]{3,40}),\s*(?:portador|inscrit|residente|RG|CPF)", re.I),
}


def cpf_valido(s):
    d = [int(c) for c in re.sub(r"\D", "", s)]
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for n in (9, 10):
        soma = sum(d[i] * (n + 1 - i) for i in range(n))
        if (soma * 10 % 11) % 10 != d[n]:
            return False
    return True


def normalizar(campo, v):
    v = re.sub(r"\s+", " ", v).strip(" .,;:-")
    if campo == "cpf":
        d = re.sub(r"\D", "", v)
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    if campo == "processo_cnj":
        d = re.sub(r"\D", "", v)
        return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:]}"
    if campo in ("telefone", "cep", "nis_pis_nit", "beneficio_inss"):
        return re.sub(r"\D", "", v)
    if campo == "estado_civil":
        return v.lower()
    return v


# ---------------------------------------------------------------- leitura por tipo
_ocr = None
_whisper = None


def ocr_bytes(png):
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    res, _ = _ocr(png)
    if not res:
        return ""
    linhas = sorted(res, key=lambda x: (round(x[0][0][1] / 15), x[0][0][0]))
    return "\n".join(x[1] for x in linhas)


def ler_pdf(p, max_pag):
    import pymupdf
    partes, ocr_usado = [], 0
    with pymupdf.open(p) as doc:
        total = doc.page_count
        for i, pg in enumerate(doc):
            if i >= max_pag:
                break
            t = pg.get_text()
            if len(t.strip()) < 40:
                t = ocr_bytes(pg.get_pixmap(dpi=200).tobytes("png"))
                ocr_usado += 1
            partes.append(f"--- página {i + 1} ---\n{t}")
    metodo = "pdf texto" + (f" + OCR em {ocr_usado} pág." if ocr_usado else "")
    if total > max_pag:
        metodo += f" (lidas {max_pag} de {total} pág.)"
    return "\n".join(partes), metodo, total


def ler_imagem(p):
    ext = p.suffix.lower().lstrip(".")
    if ext in ("heic", "heif") or ext in ("webp", "tif", "tiff", "bmp"):
        from PIL import Image, ImageOps
        if ext in ("heic", "heif"):
            import pillow_heif
            pillow_heif.register_heif_opener()
        with Image.open(p) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            buf = io.BytesIO()
            im.save(buf, "PNG")
            dados = buf.getvalue()
    else:
        from PIL import Image, ImageOps
        with Image.open(p) as im:
            im2 = ImageOps.exif_transpose(im)
            if im2 is not im:
                buf = io.BytesIO()
                im2.convert("RGB").save(buf, "PNG")
                dados = buf.getvalue()
            else:
                dados = p.read_bytes()
    return ocr_bytes(dados), "OCR de imagem", 1


def ler_office(p):
    from markitdown import MarkItDown
    return MarkItDown().convert(str(p)).text_content, "MarkItDown", None


def ler_doc_antigo(p):
    import win32com.client  # Word instalado no computador
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    # Documento de terceiro: macros desligadas à força ANTES de abrir (o padrão da automação é habilitar),
    # sem alertas, sem atualizar vínculos e sem travar em arquivo com senha (a senha falsa faz falhar).
    word.AutomationSecurity = 3  # msoAutomationSecurityForceDisable
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(str(p), ConfirmConversions=False, ReadOnly=True, AddToRecentFiles=False,
                                PasswordDocument="senha-invalida", Revert=False, Visible=False,
                                OpenAndRepair=False, NoEncodingDialog=True)
        try:
            return d.Content.Text, "Word (.doc antigo)", None
        finally:
            d.Close(False)
    finally:
        word.Quit()


def ler_eml(p):
    with open(p, "rb") as f:
        m = email.message_from_binary_file(f, policy=email.policy.default)
    corpo = m.get_body(preferencelist=("plain", "html"))
    texto = corpo.get_content() if corpo else ""
    anexos = [a.get_filename() for a in m.iter_attachments()]
    cab = f"De: {m['from']}\nPara: {m['to']}\nData: {m['date']}\nAssunto: {m['subject']}\nAnexos: {anexos}\n\n"
    return cab + texto, "e-mail", None


def ler_texto(p):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return p.read_text(encoding=enc), "texto", None
        except UnicodeDecodeError:
            continue
    return "", "texto (codificação desconhecida)", None


def ler_audio(p):
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = _whisper.transcribe(str(p), language="pt", vad_filter=True)
    return "\n".join(s.text.strip() for s in segs), "Whisper (transcrição, conferir nomes e números)", None


def ler(p, args):
    ext = p.suffix.lower().lstrip(".")
    if ext == "pdf":
        return ler_pdf(p, args.max_paginas)
    if ext in EXT_IMAGEM:
        return ler_imagem(p)
    if ext in EXT_OFFICE:
        return ler_office(p)
    if ext == "doc":
        return ler_doc_antigo(p)
    if ext == "eml":
        return ler_eml(p)
    if ext in EXT_TEXTO:
        return ler_texto(p)
    if ext in EXT_AUDIO:
        if not args.audio:
            return None, "áudio não transcrito (rode com --audio)", None
        return ler_audio(p)
    return None, "só registrado (formato não lido)", None


# ---------------------------------------------------------------- análise
def tipo_documento(nome, texto):
    amostra = nome + "\n" + (texto or "")[:3000]
    return [n for n, rx in TIPOS_DOC if rx.search(amostra)]


def candidatos_do_texto(texto_original, arquivo):
    achados = []
    corrido = re.sub(r"\s+", " ", texto_original)  # junta quebras de linha do PDF e do OCR
    for campo, rx in PADROES.items():
        texto = texto_original if campo == "qualificacao" else corrido
        for m in rx.finditer(texto):
            bruto = m.group(1)
            ini, fim = max(0, m.start() - 70), min(len(texto), m.end() + 70)
            trecho = re.sub(r"\s+", " ", texto[ini:fim]).strip()
            if ESCRITORIO.search(bruto) or (campo in ("telefone", "email", "endereco") and ESCRITORIO.search(trecho)):
                continue
            if campo == "cpf" and not cpf_valido(bruto):
                continue
            valor = normalizar(campo, bruto)
            if campo == "rg" and m.lastindex and m.lastindex >= 3 and m.group(2):
                valor += f" {m.group(2).upper()}/{m.group(3).upper()}"
            achados.append({"campo": campo, "valor": valor, "arquivo": arquivo, "trecho": trecho[:260]})
    return achados


def pastas_cliente(raiz: Path):
    """Pastas Área/Cliente dentro da pasta Clientes (ignora as que começam com _ ou .)."""
    for area in sorted(p for p in raiz.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        for cli in sorted(p for p in area.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
            yield cli


def processar_cliente(cli: Path, args):
    if any(n.lower() == "sigiloso.txt" for n in os.listdir(cli)):
        print(f"[sigiloso] {cli.name}: pasta do cliente marcada, não lida.")
        return
    saida = cli / SAIDA
    (saida / "textos").mkdir(parents=True, exist_ok=True)
    cache_p = saida / "cache.json"
    cache = {} if args.refazer or not cache_p.exists() else json.loads(cache_p.read_text(encoding="utf-8"))
    indice, todos, sigilosas = [], [], []
    inicio = time.time()
    n = 0
    for raiz, dirs, arqs in os.walk(cli):
        r = Path(raiz)
        if any(a.lower() == "sigiloso.txt" for a in arqs):
            sigilosas.append(str(r.relative_to(cli)))
            dirs[:] = []
            continue
        dirs[:] = sorted(d for d in dirs if d not in PULAR_PASTAS)
        for a in sorted(arqs):
            if a.lower() in IGNORAR:
                continue
            p = r / a
            rel = str(p.relative_to(cli))
            try:
                st = p.stat()
            except OSError as e:
                indice.append({"arquivo": rel, "situacao": f"sem acesso ({type(e).__name__})"})
                continue
            chave = f"{st.st_size}-{int(st.st_mtime)}"
            n += 1
            txt_p = saida / "textos" / (hashlib.md5(rel.encode("utf-8")).hexdigest()[:12] + ".txt")
            if rel in cache and cache[rel]["chave"] == chave and Path(saida / cache[rel]["txt"]).exists():
                item = cache[rel]
            else:
                item = {"chave": chave, "txt": "", "metodo": "", "paginas": "", "chars": 0, "situacao": "lido"}
                if st.st_size > args.max_mb * 1024 * 1024 and p.suffix.lower().lstrip(".") not in EXT_AUDIO:
                    item.update(metodo=f"maior que {args.max_mb} MB", situacao="não lido (tamanho)")
                else:
                    try:
                        texto, metodo, pags = ler(p, args)
                        item.update(metodo=metodo, paginas=pags or "")
                        if texto is None:
                            item["situacao"] = "não lido"
                        else:
                            texto = texto.strip()
                            item["chars"] = len(texto)
                            item["situacao"] = "lido" if len(texto) >= 20 else "lido, sem texto legível"
                            txt_p.write_text(f"# origem: {rel}\n# método: {metodo}\n\n{texto}\n", encoding="utf-8")
                            item["txt"] = str(txt_p.relative_to(saida))
                    except Exception as e:  # um arquivo ruim não para o lote
                        item.update(metodo=f"erro: {type(e).__name__}", situacao="falha na leitura")
                cache[rel] = item
            texto = ""
            if item.get("txt"):
                texto = (saida / item["txt"]).read_text(encoding="utf-8")
                todos += candidatos_do_texto(texto, rel)
            todos += [dict(c, trecho="(nome do arquivo)") for c in candidatos_do_texto(a, rel)
                      if c["campo"] in ("processo_cnj", "cpf", "beneficio_inss", "requerimento_inss")]
            indice.append({"arquivo": rel, "tipo_documento": "; ".join(tipo_documento(a, texto)),
                           "metodo": item["metodo"], "paginas": item["paginas"], "caracteres": item["chars"],
                           "texto_extraido": item.get("txt", ""), "situacao": item["situacao"]})
            if n % 25 == 0:
                print(f"  {cli.name}: {n} arquivos...")

    cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(saida / "indice.csv", "w", newline="", encoding="utf-8-sig") as f:
        campos = ["arquivo", "tipo_documento", "metodo", "paginas", "caracteres", "texto_extraido", "situacao"]
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(indice)

    # agrupa candidatos: valor -> fontes
    agrupado = defaultdict(lambda: defaultdict(list))
    for c in todos:
        agrupado[c["campo"]][c["valor"]].append({"arquivo": c["arquivo"], "trecho": c["trecho"]})
    cand = {campo: sorted(({"valor": v, "ocorrencias": len(f), "fontes": f[:6]} for v, f in vals.items()),
                          key=lambda x: -x["ocorrencias"])
            for campo, vals in agrupado.items()}
    (saida / "candidatos.json").write_text(json.dumps(cand, ensure_ascii=False, indent=1), encoding="utf-8")

    tipos = Counter(t for i in indice for t in (i.get("tipo_documento") or "").split("; ") if t)
    nao_lidos = [i for i in indice if i.get("situacao") != "lido"]
    essenciais = ["RG / identidade", "CPF", "Comprovante de residência", "Procuração", "Contrato de honorários",
                  "Declaração de hipossuficiência"]
    r = [f"# Extração: {cli.name}", "",
         f"Gerado em {datetime.now():%Y-%m-%d %H:%M}, em {time.time() - inicio:.0f} s. "
         f"Arquivos: {len(indice)}; lidos: {len(indice) - len(nao_lidos)}; não lidos: {len(nao_lidos)}.",
         "Dados abaixo saíram de leitura automática (OCR e padrões de texto). Tudo vai para a ficha como "
         "[CONFIRMAR] até alguém conferir no documento.", "",
         "## Documentos encontrados (pelo nome e pelo início do texto)", ""]
    r += [f"- {t}: {q}" for t, q in tipos.most_common()] or ["- nenhum tipo reconhecido"]
    faltam = [e for e in essenciais if e not in tipos]
    r += ["", "## Documentos de praxe não encontrados", ""] + ([f"- {e}" for e in faltam] or ["- nenhum"])
    r += ["", "## Dados candidatos (valor · ocorrências · primeira fonte)", ""]
    for campo in PADROES:
        vals = cand.get(campo, [])
        if not vals:
            continue
        marca = "  ← MAIS DE UM VALOR, conferir" if len(vals) > 1 and campo in (
            "cpf", "rg", "nascimento", "nis_pis_nit", "estado_civil") else ""
        r.append(f"**{campo}**{marca}")
        for v in vals[:5]:
            r.append(f"- `{v['valor'][:200]}` · {v['ocorrencias']} · {v['fontes'][0]['arquivo']}")
        r.append("")
    if nao_lidos:
        r += ["## Não lidos", ""] + [f"- {i['arquivo']}: {i.get('situacao')} ({i.get('metodo', '')})" for i in nao_lidos[:60]]
        if len(nao_lidos) > 60:
            r.append(f"- ... e mais {len(nao_lidos) - 60} (ver indice.csv)")
    if sigilosas:
        r += ["", "## Pastas sigilosas ignoradas", ""] + [f"- {s}" for s in sigilosas]
    r += ["", "Atenção: CPF, telefone e endereço de outras pessoas (cônjuge, filhos, parte contrária, testemunhas) "
          "também aparecem nos documentos. A qualificação da procuração ou da petição inicial costuma ser a melhor fonte."]
    (saida / "resumo.md").write_text("\n".join(r), encoding="utf-8")
    print(f"OK {cli.name}: {len(indice)} arquivos, {len(nao_lidos)} não lidos, {sum(len(v) for v in cand.values())} "
          f"valores candidatos. {saida / 'resumo.md'}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Extração de texto e dados cadastrais da pasta do cliente.")
    ap.add_argument("pasta", nargs="?", type=Path, help="pasta de um cliente")
    ap.add_argument("--lote", type=Path, help="pasta Clientes: processa todas as pastas Área/Cliente")
    ap.add_argument("--audio", action="store_true", help="transcrever áudios (lento)")
    ap.add_argument("--max-paginas", type=int, default=40, help="páginas lidas por PDF (padrão 40)")
    ap.add_argument("--max-mb", type=int, default=60, help="pula arquivos maiores (padrão 60 MB)")
    ap.add_argument("--refazer", action="store_true", help="ignora o que já foi extraído")
    args = ap.parse_args()
    if bool(args.pasta) == bool(args.lote):
        ap.error("informe a pasta de um cliente OU --lote <pasta Clientes>")
    alvos = list(pastas_cliente(args.lote)) if args.lote else [args.pasta]
    for cli in alvos:
        if not cli.is_dir():
            print(f"pasta não encontrada: {cli}", file=sys.stderr)
            continue
        processar_cliente(cli.resolve(), args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
