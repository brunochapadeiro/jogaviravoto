"""Dados do cruzador (/cruzar): urna do TSE por UF (1º e 2º turno, Presidente) e eleitos de 2026 por UF e partido.
Lê o ramo "dados" (pastas presidente/ e eleitos/) e grava public/dados/cruzar.json. Confere os totais contra os arquivos oficiais.

Uso:
  git fetch origin dados && git archive origin/dados presidente eleitos | tar -x -C /tmp/dados
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
    t2 = saida["br"]["t2"]["cand"]
    print(f"ok: {caminho} ({os.path.getsize(caminho)} bytes); 2º turno Brasil {t2[0]['nome']} {t2[0]['pct']}% x {t2[1]['nome']} {t2[1]['pct']}%")


if __name__ == "__main__":
    main()
