"""Extrai os eleitos (deputado federal e senador) dos arquivos baixados:
- arquivos de resultado do TSE (JSON "-u", ciclo 2026) e
- zips de candidaturas do Portal de Dados Abertos do TSE (consulta_cand_AAAA.zip, ciclos anteriores).
Saída: eleitos.csv (sem CPF, e-mail ou título) e partidos.csv (votos nominais e de legenda por partido, só JSON).
Uso: python3 eleitos.py <pasta_entrada> <pasta_saida>"""
import csv, io, json, sys, zipfile
from pathlib import Path

ENT, SAI = Path(sys.argv[1]), Path(sys.argv[2]); SAI.mkdir(parents=True, exist_ok=True)
ELEITO = ("ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "ELEITO POR MEDIA")
CARGOS = {"5": "Senador", "6": "Deputado Federal"}
CAMPOS = ["ano", "uf", "cargo", "numero", "nome_urna", "partido", "federacao", "situacao", "votos", "genero", "cor_raca", "ocupacao", "idade_posse", "instrucao", "reeleicao"]
linhas, partidos = [], []

for f in sorted(ENT.glob("*.json")):
    try: d = json.loads(f.read_text(encoding="utf-8"))
    except Exception: continue
    ano = "20" + d.get("dg", "//26")[-2:] if d.get("dg") else ""
    uf = d.get("cdabr", "").upper()
    feds = {}
    for c in d.get("carg", []):
        cargo = CARGOS.get(str(c.get("cd")))
        if not cargo: continue
        for fe in c.get("fed", []): feds[fe["n"]] = fe.get("sg", "")
        for a in c.get("agr", []):
            for p in a.get("par", []):
                partidos.append(dict(ano=ano, uf=uf, cargo=cargo, partido=p.get("sg"), numero=p.get("n"), federacao=feds.get(p.get("nfed"), ""),
                                     votos_nominais=p.get("tvtn", ""), votos_legenda=p.get("tvtl", ""), votos_validos=p.get("tvan", "")))
                for k in p.get("cand", []):
                    st = (k.get("st") or "").upper()
                    if st.startswith("ELEITO"):
                        linhas.append(dict(ano=ano, uf=uf, cargo=cargo, numero=k.get("n"), nome_urna=k.get("nmu"), partido=p.get("sg"),
                                           federacao=feds.get(p.get("nfed"), ""), situacao=k.get("st"), votos=k.get("vap", "")))

for z in sorted(ENT.glob("*.zip")):
    with zipfile.ZipFile(z) as zz:
        nomes = [n for n in zz.namelist() if n.lower().endswith(".csv")]
        br = [n for n in nomes if n.upper().endswith("_BRASIL.CSV")]
        for n in (br or nomes):
            with zz.open(n) as fh:
                r = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";")
                for x in r:
                    if x.get("CD_CARGO") not in CARGOS or x.get("DS_SIT_TOT_TURNO", "").upper() not in ELEITO: continue
                    linhas.append(dict(ano=x.get("ANO_ELEICAO"), uf=x.get("SG_UF"), cargo=CARGOS[x["CD_CARGO"]], numero=x.get("NR_CANDIDATO"),
                                       nome_urna=x.get("NM_URNA_CANDIDATO"), partido=x.get("SG_PARTIDO"), federacao=x.get("SG_FEDERACAO", ""),
                                       situacao=x.get("DS_SIT_TOT_TURNO"), genero=x.get("DS_GENERO"), cor_raca=x.get("DS_COR_RACA"),
                                       ocupacao=x.get("DS_OCUPACAO"), idade_posse=x.get("NR_IDADE_DATA_POSSE"), instrucao=x.get("DS_GRAU_INSTRUCAO"),
                                       reeleicao=x.get("ST_REELEICAO")))

with open(SAI / "eleitos.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=CAMPOS); w.writeheader(); [w.writerow({k: v for k, v in l.items() if k in CAMPOS}) for l in linhas]
if partidos:
    with open(SAI / "partidos.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(partidos[0])); w.writeheader(); w.writerows(partidos)
from collections import Counter
print("eleitos:", dict(Counter((l["ano"], l["cargo"]) for l in linhas)))
