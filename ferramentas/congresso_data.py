"""Dados do Raio-X do Congresso: eleitos (TSE) e classificação ideológica (Bolognesi, Ribeiro e Codato, 2023)."""
import csv, collections
from pathlib import Path

ARQ = Path(__file__).parent / "congresso" / "eleitos.csv"
# Bolognesi, B.; Ribeiro, E.; Codato, A. Uma nova classificação ideológica dos partidos políticos brasileiros. Dados, v. 66, n. 2, e20210164, 2023.
# DOI 10.1590/dados.2023.66.2.303. Survey com 519 cientistas políticos (ABCP), julho de 2018; escala 0 (esquerda) a 10 (direita).
ESTUDO = "Bolognesi, Ribeiro e Codato (2023), revista Dados"
ESTUDO_URL = "https://doi.org/10.1590/dados.2023.66.2.303"
NOTA = {"PSTU": 0.51, "PCO": 0.61, "PCB": 0.91, "PSOL": 1.28, "PCdoB": 1.92, "PT": 2.97, "PDT": 3.92, "PSB": 4.05, "REDE": 4.77,
        "CIDADANIA": 4.92, "PV": 5.29, "PTB": 6.10, "AVANTE": 6.32, "SOLIDARIEDADE": 6.50, "PMN": 6.88, "PMB": 6.90, "PHS": 6.96,
        "MDB": 7.01, "PSD": 7.09, "PSDB": 7.11, "PODE": 7.24, "PPL": 7.27, "PRTB": 7.45, "PROS": 7.47, "PRP": 7.59, "REPUBLICANOS": 7.78,
        "PL": 7.78, "PTC": 7.86, "DC": 8.11, "PSL": 8.11, "NOVO": 8.13, "PP": 8.20, "PSC": 8.33, "PATRIOTA": 8.55, "DEM": 8.57}
# Partidos que mudaram de nome ou se fundiram depois do survey (2018): a nota vem do(s) antecessor(es).
NOMES = {"PC do B": "PCdoB", "PCDOB": "PCdoB", "PPS": "CIDADANIA", "PRB": "REPUBLICANOS", "PR": "PL"}
NOTA["UNIÃO"] = round((NOTA["PSL"] + NOTA["DEM"]) / 2, 2)      # fusão PSL + DEM (2022)
NOTA["PRD"] = round((NOTA["PTB"] + NOTA["PATRIOTA"]) / 2, 2)   # fusão PTB + Patriota (2023)
HERANCA = [("União Brasil", "média de PSL e DEM, que se fundiram em 2022"), ("PRD", "média de PTB e Patriota, que se fundiram em 2023"),
           ("Republicanos", "nota do antigo PRB"), ("PL", "nota do antigo PR, anterior à filiação de Jair Bolsonaro, em 2021"),
           ("Cidadania", "nota do antigo PPS"), ("Missão", "partido criado depois da pesquisa: sem nota")]
SIGLA = {"PODE": "Podemos", "UNIÃO": "União", "REPUBLICANOS": "Republicanos", "SOLIDARIEDADE": "Solidariedade", "CIDADANIA": "Cidadania",
         "PATRIOTA": "Patriota", "AVANTE": "Avante", "NOVO": "Novo", "REDE": "Rede", "MISSÃO": "Missão"}

# Faixas do próprio estudo (média de 0 a 10)
FAIXAS = [(1.5, "Extrema-esquerda"), (3.0, "Esquerda"), (4.49, "Centro-esquerda"), (5.5, "Centro"), (7.0, "Centro-direita"), (8.5, "Direita"), (10, "Extrema-direita")]
CAMPOS3 = [("esq", "Esquerda e centro-esquerda", 4.49), ("cen", "Centro", 5.5), ("dir", "Centro-direita, direita e extrema-direita", 10)]


def norm(p):
    return NOMES.get(p, p)


def nome(p):
    p = norm(p)
    return SIGLA.get(p, p)


def nota(p):
    return NOTA.get(norm(p))


def faixa(n):
    if n is None: return "Sem classificação"
    return next(r for lim, r in FAIXAS if n <= lim)


def campo(n):
    if n is None: return "sem"
    return next(k for k, _, lim in CAMPOS3 if n <= lim)


def eleitos():
    # 2018 e 2022: cadastro de candidaturas do TSE; 2026: idem (situação final). Linhas com votos vêm do arquivo de resultado e duplicam o cadastro.
    return [x for x in csv.DictReader(open(ARQ, encoding="utf-8")) if not x["votos"]]


def bancadas(ano, cargo, rows=None):
    rows = rows if rows is not None else eleitos()
    c = collections.Counter(norm(x["partido"]) for x in rows if x["ano"] == ano and x["cargo"] == cargo)
    return c


def senado_2027(rows=None):
    """81 cadeiras a partir de 1º/2/2027: 27 eleitos em 2022 (mandato até 2031) + 54 eleitos em 2026. Partido pelo qual foram eleitos;
    o PSC foi incorporado ao Podemos em 2023."""
    c = bancadas("2022", "Senador", rows) + bancadas("2026", "Senador", rows)
    if "PSC" in c: c["PODE"] += c.pop("PSC")
    return c


def resumo(c):
    tot = sum(c.values())
    campos = collections.Counter(campo(nota(p)) for p in c.elements())
    media = sum(nota(p) * k for p, k in c.items() if nota(p) is not None) / sum(k for p, k in c.items() if nota(p) is not None)
    faixas = collections.Counter(faixa(nota(p)) for p in c.elements())
    return dict(total=tot, campos=dict(campos), media=round(media, 2), faixas=dict(faixas))


def perfil(ano, cargo, rows=None):
    rows = rows if rows is not None else eleitos()
    r = [x for x in rows if x["ano"] == ano and x["cargo"] == cargo]
    n = len(r)
    g = collections.Counter(x["genero"] for x in r)
    cr = collections.Counter(x["cor_raca"] for x in r)
    return dict(n=n, mulheres=g.get("FEMININO", 0), negros=cr.get("PRETA", 0) + cr.get("PARDA", 0), pretos=cr.get("PRETA", 0),
                pardos=cr.get("PARDA", 0), indigenas=cr.get("INDÍGENA", 0), brancos=cr.get("BRANCA", 0),
                ocup=collections.Counter(x["ocupacao"] for x in r))


if __name__ == "__main__":
    R = eleitos()
    for ano in ("2018", "2022", "2026"):
        c = bancadas(ano, "Deputado Federal", R); print("Câmara", ano, resumo(c))
    print("Senado 54 (2018)", resumo(bancadas("2018", "Senador", R)))
    print("Senado 54 (2026)", resumo(bancadas("2026", "Senador", R)))
    s = senado_2027(R); print("Senado 81 (2027)", resumo(s), s.most_common())
    for ano in ("2018", "2022", "2026"):
        p = perfil(ano, "Deputado Federal", R); print(ano, {k: v for k, v in p.items() if k != "ocup"}, p["ocup"].most_common(12))


# Para comparar bancadas entre eleições, partidos que se fundiram depois contam no sucessor de hoje.
SUCESSOR = {"PSL": "UNIÃO", "DEM": "UNIÃO", "PHS": "PODE", "PSC": "PODE", "PROS": "SOLIDARIEDADE", "PTB": "PRD", "PATRIOTA": "PRD",
            "PRP": "PRD", "PPL": "PCdoB", "PMN": "MOBILIZA", "PTC": "AGIR"}
CLASSES = [("pt", "PT", "#EC6155"), ("esq", "Outros de esquerda e centro-esquerda", "#A8453D"), ("cen", "Centro", "#8E949C"),
           ("sem", "Sem classificação", "none"), ("dir", "Outros de centro-direita a extrema-direita", "#3A639F"), ("pl", "PL", "#4D94F5")]
COR = {k: c for k, _, c in CLASSES}


def sucessor(p):
    p = norm(p)
    return SUCESSOR.get(p, p)


def classe(p):
    """Classe de cor de um partido (pela nota do partido na eleição): PT e PL destacados; o resto pelo campo."""
    p = norm(p)
    if p == "PT": return "pt"
    if p == "PL": return "pl"
    c = campo(nota(p))
    return {"esq": "esq", "cen": "cen", "dir": "dir", "sem": "sem"}[c]


def por_classe(c):
    k = collections.Counter()
    for p, n in c.items(): k[classe(p)] += n
    return k


def variacao(c_antes, c_depois):
    a, d = collections.Counter(), collections.Counter()
    for p, n in c_antes.items(): a[sucessor(p)] += n
    for p, n in c_depois.items(): d[sucessor(p)] += n
    return {p: d[p] - a[p] for p in set(a) | set(d)}, a, d
