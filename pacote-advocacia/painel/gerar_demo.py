#!/usr/bin/env python3
"""Cria dados FICTÍCIOS para o painel em modo demonstração (python painel/servidor.py --demo).

Nomes, CPFs, processos e valores são inventados. Perfis de demonstração (PIN só para treino):
    Dra. Leulla (advogada) 111111 · Colaboradora 1 222222 · Colaboradora 2 333333
"""
import csv
import hashlib
import json
import secrets
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

DEMO = Path(sys.argv[1])
CLI = DEMO / "Clientes"
PACOTE = Path(__file__).resolve().parent.parent
hoje = date.today()

CLIENTES = [
    ("Previdenciário RGPS", "Joana Exemplo Ramos", "casada", "lavradora", "529.982.247-25", "0801234-56.2025.8.14.0061",
     "Aposentadoria por idade rural · Vara Única de Tucuruí · aguardando perícia", 3, 1),
    ("Previdenciário RPPS", "Benedito Exemplo Costa", "viúvo", "professor aposentado", "111.444.777-35", "",
     "Revisão de proventos (IPASET) · requerimento administrativo em análise", 1, 0),
    ("Previdenciário RPPS", "Raimunda Exemplo Lima", "solteira", "professora aposentada", "390.533.447-05", "",
     "Revisão de proventos (IPASET) · aguardando documentos", 0, 0),
    ("Família e Sucessões", "Carlos Exemplo Pereira", "divorciado", "comerciante", "", "0802345-67.2025.8.14.0061",
     "Revisão de alimentos · audiência de conciliação marcada", 4, 0),
    ("Consumidor", "Antônia Exemplo Souza", "casada", "do lar", "714.602.380-01", "0803456-78.2025.8.14.0061",
     "Empréstimo consignado não contratado · réplica", 2, 1),
    ("Direito Público", "José Exemplo Martins", "casado", "servidor municipal", "", "0804567-89.2025.8.14.0061",
     "Progressão funcional · sentença publicada", 5, 0),
    ("Ambiental", "Sítio Exemplo Ltda.", "", "", "", "",
     "Defesa em auto de infração ambiental · prazo de defesa", 6, 0),
]


def ficha(area, nome, ec, prof, cpf, cnj, caso, n_conf, n_dec):
    marca = lambda i: " [CONFIRMAR]" if i < n_conf else ""
    tel = "(94) 99123-4567 (fonte: conversa.eml) ou (94) 99876-5432 (fonte: procuracao.pdf) [DECIDIR]" if n_dec \
        else "(94) 99111-2233 (fonte: procuracao.pdf)"
    casos = f"- {cnj} · {caso} (fonte: inicial.docx)" if cnj else f"- consultivo · {caso}"
    return f"""# Ficha do cliente: {nome}

Área: {area}
Criada em: {hoje.isoformat()} · Origem: extração dos documentos da pasta (`_extracao/`)
Situação da ficha: {"em conferência" if n_conf or n_dec else "conferida"}

## Qualificação
- Nome completo: {nome} (fonte: procuracao.pdf, pág. 1){marca(0)}
- Nacionalidade: brasileira (fonte: procuracao.pdf, pág. 1)
- Estado civil: {ec or "[CONFIRMAR]"} (fonte: procuracao.pdf, pág. 1){marca(1)}
- Profissão: {prof or "[CONFIRMAR]"} (fonte: procuracao.pdf, pág. 1)
- Data de nascimento: 12/03/1965 (fonte: RG frente.jpg){marca(2)}
- Filiação: Maria Exemplo (fonte: procuracao.pdf, pág. 1)
- RG e órgão emissor: 1234567 SSP/PA (fonte: RG frente.jpg){marca(3)}
- CPF: {cpf + " (fonte: procuracao.pdf, pág. 1)" if cpf else "[CONFIRMAR]"}{marca(4)}
- NIS/PIS/NIT: [CONFIRMAR]
- Matrícula (servidor): {"12345-6 (fonte: contracheque.pdf)" if "RPPS" in area or "Público" in area else "não se aplica"}

## Contato
- Endereço: Rua Exemplo, nº 100, Bairro Centro (fonte: procuracao.pdf, pág. 1){marca(5)}
- CEP: 68455-000 (fonte: procuracao.pdf, pág. 1)
- Município/UF: Tucuruí/PA (fonte: procuracao.pdf, pág. 1)
- Telefone: {tel}
- E-mail: [CONFIRMAR]

## Casos
{casos}

## Benefícios e requerimentos (INSS ou regime próprio)
- {"NB 123.456.789-0 · aposentadoria por idade rural · indeferido (fonte: carta INSS.pdf)" if "RGPS" in area else "nenhum encontrado"}

## Documentos de praxe
- Procuração: sim (procuracao.pdf)
- Contrato de honorários: {"sim (contrato.pdf)" if n_conf % 2 == 0 else "não encontrado"}
- Declaração de hipossuficiência: não encontrado
- RG/CNH: sim (RG frente.jpg)
- CPF: sim (procuracao.pdf)
- Comprovante de residência: sim (conta de energia.pdf)

## Pendências
- Áudio de 12/05 não transcrito.

## Atendimentos
"""


for area, nome, ec, prof, cpf, cnj, caso, n_conf, n_dec in CLIENTES:
    p = CLI / area / nome
    (p / "00 Documentação do cliente").mkdir(parents=True, exist_ok=True)
    (p / "ficha-cliente.md").write_text(ficha(area, nome, ec, prof, cpf, cnj, caso, n_conf, n_dec), encoding="utf-8")
    for arq in ("procuracao.pdf", "RG frente.jpg", "conta de energia.pdf"):
        (p / "00 Documentação do cliente" / arq).write_bytes(b"documento ficticio de demonstracao")
    if cnj:
        caso_p = p / cnj / "02 Autos e peças recebidas"
        caso_p.mkdir(parents=True, exist_ok=True)
        (caso_p / "inicial.docx").write_bytes(b"documento ficticio")
# um cliente ainda sem ficha e um sigiloso (não aparece no painel)
(CLI / "Consumidor" / "Francisco Exemplo Alves").mkdir(parents=True, exist_ok=True)
sig = CLI / "Família e Sucessões" / "Cliente Sigiloso Exemplo"
sig.mkdir(parents=True, exist_ok=True)
(sig / "SIGILOSO.txt").write_text("segredo de justiça", encoding="utf-8")

PRAZOS = [
    (-1, "09:00", "Prazo", "Antônia Exemplo Souza", "0803456-78.2025.8.14.0061", "Réplica à contestação", "intimação de 10/11", ""),
    (1, "", "Exigência INSS", "Joana Exemplo Ramos", "INSS 1234567890", "Juntar CTPS e declaração do sindicato", "carta de exigência", ""),
    (2, "10:30", "Audiência", "Carlos Exemplo Pereira", "0802345-67.2025.8.14.0061", "Conciliação, CEJUSC Tucuruí", "despacho", ""),
    (4, "", "Prazo", "José Exemplo Martins", "0804567-89.2025.8.14.0061", "Recurso de apelação (15 dias úteis)", "sentença publicada", ""),
    (6, "", "Prazo", "Sítio Exemplo Ltda.", "AI 0000/2025", "Defesa administrativa ao órgão ambiental", "auto de infração", ""),
    (9, "14:00", "Perícia", "Joana Exemplo Ramos", "0801234-56.2025.8.14.0061", "Perícia médica no fórum", "intimação", "Dra. Leulla em " + hoje.isoformat()),
    (15, "", "Requerimento", "Raimunda Exemplo Lima", "IPASET", "Protocolar revisão de proventos", "planejamento", ""),
]
(CLI / "_painel").mkdir(parents=True, exist_ok=True)
with open(CLI / "_painel" / "prazos.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["data", "hora", "tipo", "cliente", "processo", "descricao", "fonte", "conferido"])
    for d, h, t, c, pr, desc, fo, conf in PRAZOS:
        w.writerow([(hoje + timedelta(days=d)).isoformat(), h, t, c, pr, desc, fo, conf])

inv = CLI / "_inventario"
inv.mkdir(exist_ok=True)
(inv / "andamento.md").write_text("# Andamento da importação\n\n- Demonstração: nenhum inventário real.\n", encoding="utf-8")

fin = DEMO / "Financeiro"
fin.mkdir(parents=True, exist_ok=True)
plan = fin / "Controle_Honorarios.xlsx"
py = sys.executable
for args in (["--cliente", "Joana Exemplo Ramos", "--area", "Previdenciário RGPS", "--tipo", "exito", "--percentual", "30"],
             ["--cliente", "Carlos Exemplo Pereira", "--area", "Família e Sucessões", "--tipo", "fixo", "--valor", "3000",
              "--parcelas", "3", "--primeiro-vencimento", hoje.replace(day=10).isoformat()],
             ["--cliente", "Antônia Exemplo Souza", "--area", "Consumidor", "--tipo", "misto", "--valor", "800",
              "--percentual", "20"]):
    subprocess.run([py, str(PACOTE / "scripts" / "lancar_honorario.py"), "--planilha", str(plan), *args],
                   check=False, capture_output=True)

usuarios = []
for nome, papel, pin, ini in (("Dra. Leulla", "advogada", "111111", "LM"), ("Colaboradora 1", "colaboradora", "222222", "C1"),
                              ("Colaboradora 2", "colaboradora", "333333", "C2")):
    sal = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(sal), 200_000).hex()
    usuarios.append({"id": secrets.token_hex(4), "nome": nome, "papel": papel, "iniciais": ini, "sal": sal, "hash": h})
(DEMO / "usuarios-demo.json").write_text(json.dumps(usuarios, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Demonstração criada em {DEMO}")
