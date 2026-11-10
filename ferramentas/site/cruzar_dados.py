"""Dados do cruzador (/cruzar): urna do TSE por UF (1º e 2º turno, Presidente) e eleitos de 2026 por UF e partido.
Lê o ramo "dados" (pastas presidente/ e eleitos/) e grava public/dados/cruzar.json. Confere os totais contra os arquivos oficiais.

Também grava public/dados/estados.json: todos os indicadores por UF (urna, eleitos, votos da bancada, presença,
alinhamento e IBGE), para cruzar quaisquer dois deles em "Compare os estados".

Uso:
  git fetch origin dados && git archive origin/dados presidente eleitos ibge | tar -x -C /tmp/dados
  python3 ferramentas/site/cruzar_dados.py --dados /tmp/dados --site public
"""
import argparse, csv, glob, json, os, sys
from collections import Counter, defaultdict

UFS = "ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to".split()
NOMES = {"AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
         "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso",
         "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco", "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
         "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul", "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins"}
EM = {"AC": "no Acre", "AL": "em Alagoas", "AM": "no Amazonas", "AP": "no Amapá", "BA": "na Bahia", "CE": "no Ceará", "DF": "no Distrito Federal",
      "ES": "no Espírito Santo", "GO": "em Goiás", "MA": "no Maranhão", "MG": "em Minas Gerais", "MS": "em Mato Grosso do Sul", "MT": "em Mato Grosso",
      "PA": "no Pará", "PB": "na Paraíba", "PE": "em Pernambuco", "PI": "no Piauí", "PR": "no Paraná", "RJ": "no Rio de Janeiro", "RN": "no Rio Grande do Norte",
      "RO": "em Rondônia", "RR": "em Roraima", "RS": "no Rio Grande do Sul", "SC": "em Santa Catarina", "SE": "em Sergipe", "SP": "em São Paulo", "TO": "no Tocantins"}


def num(x):
    try:
        return float(str(x if x is not None else "").replace(".", "").replace(",", "."))
    except ValueError:
        return 0.0


def urna(pasta, ele, uf):
    f = glob.glob(os.path.join(pasta, "presidente", f"*_{uf}-c0001-e00{ele}-u.json"))
    if not f:
        sys.exit(f"falta o arquivo do TSE: {uf} {ele}")
    d = json.load(open(f[0], encoding="utf-8"))
    cands = []
    for cg in d.get("carg", []):
        for ag in cg.get("agr", []):
            for p in ag.get("par", []):
                for c in p.get("cand", []):
                    cands.append({"nome": c.get("nmu"), "votos": int(num(c.get("vap"))), "pct": num(c.get("pvap"))})
    cands.sort(key=lambda c: -c["votos"])
    e, v, s = d.get("e", {}), d.get("v", {}), d.get("s", {})
    assert d.get("tf") == "s" and num(s.get("pst")) == 100, f"{uf} {ele}: totalização não terminou"
    return {"cand": cands[:2] if ele == "6258" else cands[:3], "eleitores": int(num(e.get("te"))), "comparec": num(e.get("pc")),
            "abst": num(e.get("pa")), "brancos": num(v.get("pvb")), "nulos": num(v.get("ptvn")), "atualizado": f'{d.get("dg")} {d.get("hg")}'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", required=True)
    ap.add_argument("--site", required=True)
    a = ap.parse_args()

    # eleitos de 2026 (o arquivo repete algumas linhas com a situação em maiúsculas: fica uma por UF, cargo e número)
    vistos, eleitos = set(), []
    for x in csv.DictReader(open(os.path.join(a.dados, "eleitos", "eleitos.csv"), encoding="utf-8")):
        k = (x["uf"], x["cargo"], x["numero"])
        if x["ano"] != "2026" or k in vistos:
            continue
        vistos.add(k)
        eleitos.append(x)
    n = Counter(x["cargo"] for x in eleitos)
    assert n["Deputado Federal"] == 513 and n["Senador"] == 54, n

    def por_partido(lista):
        c = Counter(x["partido"].upper().replace("PCDOB", "PCdoB") for x in lista)
        return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))

    saida = {"fontes": {
        "urna": "TSE, resultados.tse.jus.br (arquivos oficiais de divulgação, Presidente, 1º turno 4/10/2026 e 2º turno 25/10/2026)",
        "eleitos": "TSE, Portal de Dados Abertos (candidatos eleitos em 2026 para a Câmara e o Senado)",
        "votos": "Câmara dos Deputados e Senado Federal, dados abertos (votações nominais e cota parlamentar, 2023 a 2026)"},
        "br": {}, "ufs": {}}
    saida["br"] = {"nome": "Brasil", "em": "no Brasil", "t1": urna(a.dados, "6257", "br"), "t2": urna(a.dados, "6258", "br"),
                   "eleitos": {"C": por_partido([x for x in eleitos if x["cargo"] == "Deputado Federal"]),
                               "S": por_partido([x for x in eleitos if x["cargo"] == "Senador"])}}
    soma2 = 0
    for uf in UFS:
        U = uf.upper()
        lst = [x for x in eleitos if x["uf"] == U]
        saida["ufs"][U] = {"nome": NOMES[U], "em": EM[U], "t1": urna(a.dados, "6257", uf), "t2": urna(a.dados, "6258", uf),
                           "eleitos": {"C": por_partido([x for x in lst if x["cargo"] == "Deputado Federal"]),
                                       "S": por_partido([x for x in lst if x["cargo"] == "Senador"])}}
        soma2 += saida["ufs"][U]["t2"]["cand"][0]["votos"] + saida["ufs"][U]["t2"]["cand"][1]["votos"]
    zz = urna(a.dados, "6258", "zz")
    soma2 += zz["cand"][0]["votos"] + zz["cand"][1]["votos"]
    br2 = sum(c["votos"] for c in saida["br"]["t2"]["cand"])
    assert soma2 == br2, f"2º turno: soma das UFs + exterior ({soma2}) diferente do Brasil ({br2})"
    saida["exterior"] = {"t2": zz}

    # confere: votos de cada parlamentar (chave) somam o placar oficial de cada votação
    P = json.load(open(os.path.join(a.site, "dados", "parlamentares.json"), encoding="utf-8"))
    for k, q in enumerate(P["perguntas"]):
        for casa, v in q["casas"].items():
            s = sum(1 for f in P["fichas"] if f["casa"] == casa and f["chave"][k] == "S")
            nn = sum(1 for f in P["fichas"] if f["casa"] == casa and f["chave"][k] == "N")
            if (s, nn) != (v["sim"], v["nao"]):
                print(f"AVISO {q['id']} {casa}: fichas {s} sim / {nn} não; oficial {v['sim']} / {v['nao']}")

    caminho = os.path.join(a.site, "dados", "cruzar.json")
    json.dump(saida, open(caminho, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    estados(a, saida, P)
    t2 = saida["br"]["t2"]["cand"]
    print(f"ok: {caminho} ({os.path.getsize(caminho)} bytes); 2º turno Brasil {t2[0]['nome']} {t2[0]['pct']}% x {t2[1]['nome']} {t2[1]['pct']}%")


# ------------------------------------------------------------------ todos os indicadores por UF (Compare os estados)
IBGE = [  # (tabela, variável, id, nome, curto, unidade, fonte)
    ("6579", "9324", "populacao", "População estimada", "População", "pessoas", "IBGE, Estimativas de População (tabela 6579)"),
    ("4099", "4099", "desocupacao", "Desemprego (taxa de desocupação)", "Desemprego", "%", "IBGE, PNAD Contínua trimestral (tabela 4099)"),
    ("8529", "12466", "informalidade", "Trabalho informal (taxa de informalidade)", "Informalidade", "%", "IBGE, PNAD Contínua trimestral (tabela 8529)"),
    ("5436", "5933", "rendimento", "Rendimento médio do trabalho, por mês", "Rendimento", "R$", "IBGE, PNAD Contínua trimestral (tabela 5436, todos os trabalhos, habitual)"),
    ("7435", "10681", "gini", "Desigualdade de renda (índice de Gini, de 0 a 1)", "Desigualdade (Gini)", "índice", "IBGE, PNAD Contínua anual (tabela 7435)"),
]


def le_sidra(pasta, tab, var):
    f = [x for x in glob.glob(os.path.join(pasta, "ibge", "*")) if f"_t_{tab}_" in x and f"_v_{var}_" in x]
    if not f:
        return None
    d = json.load(open(f[0], encoding="utf-8"))
    cab, linhas = d[0], d[1:]
    per = next((k for k in ("D3N",) if k in cab), None)
    v, br, quando = {}, None, None
    sigla = {n: k for k, n in NOMES.items()}
    for r in linhas:
        if r.get("D4N") not in (None, "Total"):
            continue
        try:
            x = float(r["V"])
        except ValueError:
            continue
        quando = r.get(per)
        if r["D1N"] == "Brasil":
            br = x
        elif r["D1N"] in sigla:
            v[sigla[r["D1N"]]] = x
    assert len(v) == 27, f"IBGE {tab}/{var}: {len(v)} UFs"
    return v, br, quando


def estados(a, saida, P):
    G = []
    def ind(id, nome, curto, unid, fonte, quando, desc, v, br=None, menor=False):
        return dict(id=id, nome=nome, curto=curto, unid=unid, fonte=fonte, quando=quando, desc=desc, br=br, v=v)
    ufs = saida["ufs"]; B = saida["br"]
    def cand(t, nomecand):
        return next((c["pct"] for c in t["cand"] if c["nome"] == nomecand), 0.0)
    urna = []
    for t, quando in (("t1", "1º turno, 4/10/2026"), ("t2", "2º turno, 25/10/2026")):
        tn = "1º" if t == "t1" else "2º"
        for nomecand, curto in (("LULA", "Lula"), ("FLAVIO BOLSONARO", "Flávio Bolsonaro")):
            urna.append(ind(f"{'lula' if nomecand == 'LULA' else 'flavio'}-{t}", f"Votos em {curto} no {tn} turno (% dos votos válidos)", f"{curto} {tn} turno", "%",
                            "TSE, resultados oficiais", quando, "", {u: cand(x[t], nomecand) for u, x in ufs.items()}, cand(B[t], nomecand)))
        urna.append(ind(f"comparec-{t}", f"Comparecimento no {tn} turno (% do eleitorado)", f"Comparecimento {tn} turno", "%", "TSE, resultados oficiais", quando, "",
                        {u: x[t]["comparec"] for u, x in ufs.items()}, B[t]["comparec"]))
        urna.append(ind(f"bn-{t}", f"Brancos e nulos no {tn} turno (% dos votos)", f"Brancos e nulos {tn} turno", "%", "TSE, resultados oficiais", quando, "",
                        {u: round(x[t]["brancos"] + x[t]["nulos"], 2) for u, x in ufs.items()}, round(B[t]["brancos"] + B[t]["nulos"], 2)))
    urna.append(ind("eleitores", "Eleitores aptos", "Eleitores", "pessoas", "TSE, resultados oficiais", "2026", "", {u: x["t2"]["eleitores"] for u, x in ufs.items()}, B["t2"]["eleitores"]))
    G.append(dict(id="urna", nome="Urna (TSE)", itens=urna))

    elei = [ind("dep-eleitos", "Deputados federais eleitos em 2026", "Deputados eleitos", "deputados", "TSE, dados abertos", "2026",
                "Número de vagas do estado na Câmara.", {u: sum(x["eleitos"]["C"].values()) for u, x in ufs.items()}, 513)]
    for pt in ("PL", "PT", "PSD", "UNIÃO", "PP", "REPUBLICANOS", "MDB", "PSOL"):
        elei.append(ind(f"eleitos-{pt.lower().replace('ã', 'a')}", f"Bancada eleita do {pt} em 2026 (% das vagas do estado na Câmara)", f"Eleitos do {pt}", "%", "TSE, dados abertos", "2026", "",
                        {u: round(100 * x["eleitos"]["C"].get(pt, 0) / max(1, sum(x["eleitos"]["C"].values())), 1) for u, x in ufs.items()},
                        round(100 * B["eleitos"]["C"].get(pt, 0) / 513, 1)))
    G.append(dict(id="eleitos", nome="Eleitos em 2026 (TSE)", itens=elei))

    cong = []
    for casa, ncasa in (("C", "deputados"), ("S", "senadores")):
        fs = [f for f in P["fichas"] if f["casa"] == casa]
        def media(ch, uf=None):
            xs = [f for f in fs if (uf is None or f["uf"] == uf) and f[ch]["n"]]
            num = sum(f[ch]["votou" if ch == "part" else "igual"] for f in xs); den = sum(f[ch]["n"] for f in xs)
            return round(100 * num / den, 1) if den else None
        cong.append(ind(f"presenca-{casa}", f"Presença dos {ncasa} do estado nas votações (% das votações em que votaram)", f"Presença ({ncasa})", "%",
                        "Câmara e Senado, dados abertos", "2023 a 2026", "Soma de todos os mandatos do estado no período, não é nota de ninguém.",
                        {u: media("part", u) for u in ufs}, media("part")))
        cong.append(ind(f"gov-{casa}", f"Votos dos {ncasa} do estado iguais à orientação do governo (%)", f"Com o governo ({ncasa})", "%",
                        "Câmara e Senado, dados abertos", "2023 a 2026", "Quanto a bancada votou igual ao líder do governo; não é nota de ninguém.",
                        {u: media("gov", u) for u in ufs}, media("gov")))
    for k, q in enumerate(P["perguntas"]):
        for casa, v in q["casas"].items():
            fs = [f for f in P["fichas"] if f["casa"] == casa]
            def sim(uf=None):
                cs = [f["chave"][k] for f in fs if uf is None or f["uf"] == uf]
                s_, n_ = cs.count("S"), cs.count("N")
                return round(100 * s_ / (s_ + n_), 1) if s_ + n_ else None
            nc = "Câmara" if casa == "C" else "Senado"
            cong.append(ind(f"voto-{q['id']}-{casa}", f"{q['curto']}: votos Sim da bancada do estado no {nc} (% de quem votou Sim ou Não)", f"Sim: {q['curto']} ({nc})", "%",
                            f"{nc}, votação nominal de {v.get('data', '')[8:10]}/{v.get('data', '')[5:7]}/{v.get('data', '')[:4]}", v.get("data", ""),
                            q["afirmacao"], {u: sim(u) for u in ufs}, sim()))
    G.append(dict(id="congresso", nome="Congresso (votos e presença das bancadas)", itens=cong))

    soc = []
    for tab, var, id_, nome, curto, unid, fonte in IBGE:
        r = le_sidra(a.dados, tab, var)
        if r:
            v, br, quando = r
            soc.append(ind(id_, nome, curto, unid, fonte, quando, "", v, br))
    if soc:
        G.append(dict(id="ibge", nome="Trabalho, renda e população (IBGE)", itens=soc))
    else:
        print("AVISO: sem a pasta ibge no ramo dados; Compare os estados fica sem os dados do IBGE")
    sai = dict(ufs={u: x["nome"] for u, x in ufs.items()}, grupos=G)
    caminho = os.path.join(a.site, "dados", "estados.json")
    json.dump(sai, open(caminho, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"ok: {caminho} ({os.path.getsize(caminho)} bytes); {sum(len(g['itens']) for g in G)} indicadores por UF")


if __name__ == "__main__":
    main()
