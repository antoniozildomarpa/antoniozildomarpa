"""Calcula os retroativos da gratificação omitida nos proventos e grava o resultado no caso.json.

Uso: python calc_retroativos.py caminho/caso.json [--data-calculo AAAA-MM-DD] [--sem-selic]

Regras (as mesmas do caso-modelo validado em 2026):
- diferença mensal = percentual x vencimento base vigente na competência (paridade: use "reajustes");
- com "sobre_horas_normais", a base é vencimento base + horas normais (Lei 11.920/2023, art. 20, § 2º);
- termo inicial = mês da DIB (proporcional aos dias se a DIB não for dia 1º);
  termo final = mês da data do cálculo (inclusive);
- 13º em dezembro: no ano da DIB proporcional aos meses (mês com >= 15 dias conta), depois integral;
- correção e juros: SELIC (EC 113/2021, art. 3º), soma das taxas mensais (BCB SGS 4390) do mês
  seguinte ao vencimento até o mês anterior ao do cálculo, mais 1% no mês do cálculo; competência
  do próprio mês do cálculo não tem correção.
"""
import json, sys, datetime as dt, urllib.request, calendar


def br(v):
    return f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def ym(s):
    a, m = s[:7].split('-')
    return int(a), int(m)


def add(a, m, n):
    t = a * 12 + (m - 1) + n
    return t // 12, t % 12 + 1


def selic_mensal(ini, fim):
    url = ('https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json'
           f'&dataInicial=01/{ini[1]:02d}/{ini[0]}&dataFinal=28/{fim[1]:02d}/{fim[0]}')
    with urllib.request.urlopen(url, timeout=30) as r:
        dados = json.load(r)
    return {(int(d['data'][6:]), int(d['data'][3:5])): float(d['valor']) for d in dados}


def main():
    args = sys.argv[1:]
    caminho = args[0]
    caso = json.load(open(caminho, encoding='utf-8'))
    hoje = dt.date.today().isoformat()
    if '--data-calculo' in args:
        hoje = args[args.index('--data-calculo') + 1]
    usar_selic = '--sem-selic' not in args

    g = caso['gratificacao']
    pct = g['percentual']
    dib = dt.date.fromisoformat(caso['beneficio']['dib'])
    calc = ym(hoje)
    venc_ini = caso['planilha']['vencimento_base']
    reajustes = sorted(caso.get('reajustes', []), key=lambda x: x['a_partir'])

    # base da gratificação: vencimento base, mais as horas normais (Lei 11.920/2023) quando pedido
    fator_hn = 1.0
    if g.get('sobre_horas_normais'):
        fator_hn += caso['planilha']['horas_normais'] / venc_ini

    def venc(a, m):
        v = venc_ini
        for rj in reajustes:
            if ym(rj['a_partir']) <= (a, m):
                v = rj['vencimento_base']
        return v * fator_hn

    comp = []  # (ano, mes, parcela, nominal)
    a, m = dib.year, dib.month
    while (a, m) <= calc:
        nominal = round(pct * venc(a, m), 2)
        if (a, m) == (dib.year, dib.month) and dib.day > 1:  # primeiro mês proporcional
            dm = calendar.monthrange(a, m)[1]
            dias = dm - dib.day + 1
            comp.append((a, m, f'Proventos ({dias}/{dm} dias)', round(nominal * dias / dm, 2)))
        else:
            comp.append((a, m, 'Proventos', nominal))
        if m == 12:
            if a == dib.year:
                dias_mes = calendar.monthrange(a, dib.month)[1]
                meses = 12 - dib.month + (1 if dias_mes - dib.day + 1 >= 15 else 0)
                comp.append((a, m, f'13º salário ({meses}/12)', round(nominal * meses / 12, 2)))
            else:
                comp.append((a, m, '13º salário', nominal))
        a, m = add(a, m, 1)

    taxas = selic_mensal(add(*comp[0][:2], 1), add(*calc, -1)) if usar_selic else {}
    linhas, tn, tc = [], 0.0, 0.0
    for a, m, parcela, nominal in comp:
        if (a, m) == calc or not usar_selic:
            s = 0.0
        else:
            s, x = 0.0, add(a, m, 1)
            while x < calc:
                if x not in taxas:
                    sys.exit(f'ERRO: SELIC de {x[1]:02d}/{x[0]} não disponível no BCB')
                s += taxas[x]
                x = add(*x, 1)
            s += 1.0
        cor = round(nominal * s / 100, 2)
        tn += nominal; tc += cor
        linhas.append({'competencia': f'{m:02d}/{a}', 'parcela': parcela, 'nominal': nominal,
                       'selic_pct': round(s, 2), 'correcao': cor, 'total': round(nominal + cor, 2)})

    caso['calculo'] = {
        'data_calculo': hoje,
        'mes_final': f'{calc[1]:02d}/{calc[0]}',
        'diferenca_mensal': round(pct * venc(*calc), 2),
        'proventos_revistos': round(caso['planilha']['total'] + round(pct * venc(*calc), 2), 2),
        'linhas': linhas,
        'total_nominal': round(tn, 2), 'total_correcao': round(tc, 2), 'total_geral': round(tn + tc, 2),
        'selic': usar_selic,
    }
    json.dump(caso, open(caminho, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    for l in linhas:
        print(f"{l['competencia']}  {l['parcela']:<20} {br(l['nominal']):>10} {br(l['selic_pct']):>6}% "
              f"{br(l['correcao']):>9} {br(l['total']):>10}")
    print(f"TOTAL nominal {br(tn)} | correção {br(tc)} | geral {br(tn + tc)} | "
          f"proventos revistos {br(caso['calculo']['proventos_revistos'])}")


if __name__ == '__main__':
    main()
