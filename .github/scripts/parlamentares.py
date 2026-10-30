"""Ficha de cada parlamentar (Câmara e Senado, legislatura 2023–2027) a partir dos dados abertos oficiais.
Só biblioteca padrão (roda no GitHub Actions). Gera, na pasta de saída:
  parlamentares.json  uma linha por parlamentar que exerceu mandato desde 1/2/2023: participação nas votações nominais,
                      alinhamento com o governo, gastos da cota parlamentar por ano e por tipo
  votacoes.json       todas as votações nominais do plenário (resumo), para escolher as votações-chave
  votos.json          o voto de cada parlamentar em cada votação nominal (compacto), para o teste "Quem vota como você?"
Fontes: dadosabertos.camara.leg.br (arquivos anuais e API v2), camara.leg.br/cotas, legis.senado.leg.br/dadosabertos,
senado.leg.br/transparencia (CEAPS).
Uso: python3 parlamentares.py --saida <pasta> [--anos 2023,2024,2025,2026]"""
import argparse, csv, datetime as dt, http.client, io, json, re, sys, time, unicodedata, urllib.request, urllib.error, zipfile
from collections import defaultdict, Counter
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (vigilia vira-voto; dados publicos)", "Accept": "application/json"}
CAM = "https://dadosabertos.camara.leg.br"
SEN = "https://legis.senado.leg.br/dadosabertos"
INI_LEG, FIM_LEG = "2023-02-01", "2027-01-31"
csv.field_size_limit(10**8)


def baixa(url, tentativas=4, timeout=300):
    hdr = dict(UA) if "/dadosabertos" in url else {"User-Agent": UA["User-Agent"], "Accept": "*/*"}
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.IncompleteRead, http.client.HTTPException) as e:
            if i == tentativas - 1:
                print("FALHOU", url, e, file=sys.stderr)
                return None
            time.sleep(3 * (i + 1))


def js(url):
    b = baixa(url, timeout=90)
    try:
        return json.loads(b.decode("utf-8")) if b else None
    except json.JSONDecodeError:
        return None


def linhas_csv(b, enc="utf-8-sig", pular=0):
    t = b.decode(enc, "replace")
    if pular:
        t = t.split("\n", pular)[-1]
    return csv.DictReader(io.StringIO(t), delimiter=";")


def num(x):
    x = (x or "").strip()
    if not x:
        return 0.0
    if "," in x:
        x = x.replace(".", "").replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return 0.0


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z ]", " ", s).split()


def intervalos_dentro(ivs):
    out = []
    for a, b in ivs:
        a, b = max(a, INI_LEG), min(b or FIM_LEG, FIM_LEG)
        if a <= b:
            out.append((a, b))
    return sorted(out)


def em(d, ivs):
    return any(a <= d <= b for a, b in ivs)


# ------------------------------------------------------------------ Câmara
def camara(anos):
    vot, votos, ori = {}, defaultdict(dict), defaultdict(dict)
    props = defaultdict(list)
    for ano in anos:
        b = baixa(f"{CAM}/arquivos/votacoes/csv/votacoes-{ano}.csv")
        for r in linhas_csv(b):
            if r["siglaOrgao"] == "PLEN" and r["data"] >= INI_LEG:
                vot[r["id"]] = dict(id=r["id"], data=r["data"], hora=(r["dataHoraRegistro"] or "")[11:16], desc=r["descricao"],
                                    aprov=r["aprovacao"], sim=int(r["votosSim"] or 0), nao=int(r["votosNao"] or 0), out=int(r["votosOutros"] or 0),
                                    abertura=r.get("ultimaAberturaVotacao_descricao") or "")
        b = baixa(f"{CAM}/arquivos/votacoesVotos/csv/votacoesVotos-{ano}.csv")
        for r in linhas_csv(b):
            if r["idVotacao"] in vot and r["deputado_idLegislatura"] == "57":
                votos[r["idVotacao"]][r["deputado_id"]] = (r["voto"], r["deputado_siglaPartido"], r["deputado_siglaUf"], r["deputado_nome"])
        b = baixa(f"{CAM}/arquivos/votacoesOrientacoes/csv/votacoesOrientacoes-{ano}.csv")
        for r in linhas_csv(b):
            if r["idVotacao"] in vot:
                ori[r["idVotacao"]][r["siglaBancada"]] = r["orientacao"]
        b = baixa(f"{CAM}/arquivos/votacoesProposicoes/csv/votacoesProposicoes-{ano}.csv")
        for r in linhas_csv(b):
            if r["idVotacao"] in vot:
                props[r["idVotacao"]].append(dict(id=r["proposicao_id"], titulo=r["proposicao_titulo"], ementa=(r["proposicao_ementa"] or "")[:400]))
        print("câmara", ano, "votações do plenário:", sum(1 for v in vot.values() if v["data"][:4] == str(ano)), file=sys.stderr)
    nominais = {k: v for k, v in vot.items() if votos.get(k)}
    for k, v in nominais.items():
        v["props"] = props.get(k, [])[:3]
        v["gov"] = ori[k].get("Governo") or ori[k].get("GOV.") or ""
        v["ori"] = {s: o for s, o in ori[k].items() if o}
        c = Counter(x[0] for x in votos[k].values())
        v["cont"] = dict(c)

    # deputados que exerceram mandato na legislatura 57
    deps, pag = {}, 1
    while True:
        d = js(f"{CAM}/api/v2/deputados?idLegislatura=57&itens=100&pagina={pag}&ordem=ASC&ordenarPor=nome")
        if not d or not d.get("dados"):
            break
        for x in d["dados"]:
            deps[str(x["id"])] = dict(id=str(x["id"]), casa="C", nome=x["nome"].strip(), partido=x["siglaPartido"], uf=x["siglaUf"], foto=x["urlFoto"])
        if not any(l.get("rel") == "next" for l in d.get("links", [])):
            break
        pag += 1
    # também quem votou e não veio na lista
    for k in nominais:
        for did, (_, p, u, n) in votos[k].items():
            deps.setdefault(did, dict(id=did, casa="C", nome=n.strip(), partido=p, uf=u, foto=f"https://www.camara.leg.br/internet/deputado/bandep/{did}.jpg"))
    print("deputados:", len(deps), file=sys.stderr)

    for i, (did, dep) in enumerate(deps.items()):
        h = js(f"{CAM}/api/v2/deputados/{did}/historico") or {}
        evs = sorted(((x.get("dataHora") or "")[:10], x.get("situacao") or "", x.get("idLegislatura")) for x in h.get("dados", []))
        ivs, ini = [], None
        for data, sit, leg in evs:
            if sit == "Exercício" and ini is None:
                ini = data
            elif sit != "Exercício" and ini is not None:
                ivs.append((ini, data)); ini = None
        if ini is not None:
            ivs.append((ini, None))
        dep["ivs"] = intervalos_dentro(ivs)
        det = (js(f"{CAM}/api/v2/deputados/{did}") or {}).get("dados") or {}
        us = det.get("ultimoStatus") or {}
        if us:
            dep.update(nome=(us.get("nome") or dep["nome"]).strip(), partido=us.get("siglaPartido") or dep["partido"], uf=us.get("siglaUf") or dep["uf"],
                       situacao=us.get("situacao") or "", nomeEleitoral=(us.get("nomeEleitoral") or "").strip(), foto=us.get("urlFoto") or dep["foto"])
        dep["nomeCivil"] = (det.get("nomeCivil") or "").strip()
        time.sleep(0.12)
        if i % 100 == 0:
            print("histórico", i, file=sys.stderr)

    # participação e alinhamento
    for did, dep in deps.items():
        n = votou = gn = gi = 0
        for k, v in nominais.items():
            meu = votos[k].get(did)
            if not em(v["data"], dep["ivs"]) and not meu:
                continue
            n += 1
            if meu and meu[0] != "Artigo 17":
                votou += 1
            g = v["gov"]
            if g in ("Sim", "Não") and meu and meu[0] in ("Sim", "Não"):
                gn += 1; gi += meu[0] == g
        dep["part"] = dict(n=n, votou=votou)
        dep["gov"] = dict(n=gn, igual=gi)
        dep["exercicio"] = [list(x) for x in dep.pop("ivs")]

    # cota parlamentar (CEAP)
    for ano in anos:
        b = baixa(f"https://www.camara.leg.br/cotas/Ano-{ano}.csv.zip", timeout=600)
        if not b:
            continue
        z = zipfile.ZipFile(io.BytesIO(b))
        with z.open(z.namelist()[0]) as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"), delimiter=";"):
                did = (r.get("ideCadastro") or "").strip()
                if did in deps:
                    dep = deps[did]
                    v = num(r.get("vlrLiquido"))
                    dep.setdefault("ceap", {}).setdefault(str(ano), 0.0)
                    dep["ceap"][str(ano)] += v
                    cat = (r.get("txtDescricao") or "").strip().capitalize()
                    dep.setdefault("ceapCat", Counter())[cat] += v
        print("ceap câmara", ano, file=sys.stderr)
    return deps, nominais, votos


# ------------------------------------------------------------------ Senado
CODS_PRESENTE = {"Sim", "Não", "Abstenção", "P-NRV", "Presidente", "Obstrução", "Votou"}


def senado(anos):
    lst = js(f"{SEN}/senador/lista/legislatura/57.json") or {}
    pars = (((lst.get("ListaParlamentarLegislatura") or {}).get("Parlamentares") or {}).get("Parlamentar")) or []
    sens = {}
    for p in pars:
        idp = p.get("IdentificacaoParlamentar") or {}
        cod = str(idp.get("CodigoParlamentar"))
        mand = (p.get("Mandatos") or {}).get("Mandato") or []
        mand = mand if isinstance(mand, list) else [mand]
        ivs = []
        for m in mand:
            for chave in ("Exercicios",):
                ex = ((m.get(chave) or {}).get("Exercicio")) or []
                ex = ex if isinstance(ex, list) else [ex]
                for e in ex:
                    ivs.append(((e.get("DataInicio") or "")[:10], (e.get("DataFim") or "")[:10] or None))
        sens[cod] = dict(id=cod, casa="S", nome=(idp.get("NomeParlamentar") or "").strip(), nomeCivil=(idp.get("NomeCompletoParlamentar") or "").strip(),
                         partido=idp.get("SiglaPartidoParlamentar") or "", uf=idp.get("UfParlamentar") or "",
                         foto=idp.get("UrlFotoParlamentar") or "", ivs=intervalos_dentro(ivs))
    sens = {k: v for k, v in sens.items() if v["ivs"]}
    print("senadores com exercício na legislatura:", len(sens), file=sys.stderr)

    vots, votos = {}, defaultdict(dict)
    for ano in anos:
        for mes in range(1, 13):
            fim_mes = (dt.date(ano + (mes == 12), mes % 12 + 1, 1) - dt.timedelta(days=1)).isoformat()
            a, b = f"{ano}-{mes:02d}-01", fim_mes
            a = max(a, INI_LEG)
            if a > b:
                continue
            d = js(f"{SEN}/votacao?dataInicio={a}&dataFim={b}") or []
            for v in d:
                k = str(v.get("codigoSessaoVotacao"))
                vots[k] = dict(id=k, data=(v.get("dataSessao") or "")[:10], desc=v.get("descricaoVotacao") or "", resultado=v.get("resultadoVotacao") or "",
                               secreta=v.get("votacaoSecreta") == "S", ident=v.get("identificacao") or "", ementa=(v.get("ementa") or "")[:400],
                               materia=v.get("codigoMateria"), sim=v.get("totalVotosSim"), nao=v.get("totalVotosNao"), abst=v.get("totalVotosAbstencao"))
                for x in v.get("votos") or []:
                    c = str(x.get("codigoParlamentar"))
                    votos[k][c] = (x.get("siglaVotoParlamentar") or "", x.get("siglaPartidoParlamentar") or "", x.get("siglaUFParlamentar") or "", x.get("nomeParlamentar") or "")
                    if c not in sens:
                        sens[c] = dict(id=c, casa="S", nome=(x.get("nomeParlamentar") or "").strip(), nomeCivil="", partido=x.get("siglaPartidoParlamentar") or "",
                                       uf=x.get("siglaUFParlamentar") or "", foto="", ivs=[])
            time.sleep(0.5)
        print("senado", ano, len(vots), file=sys.stderr)
    nominais = {k: v for k, v in vots.items() if votos.get(k) and not v["secreta"]}

    # líder do governo no Senado (Jaques Wagner) como referência de orientação: o Senado não publica orientações nos dados abertos
    lider = next((c for c, s in sens.items() if "JAQUES WAGNER" in " ".join(norm(s["nome"]))), None)
    for c, s in sens.items():
        n = pres = just = gn = gi = 0
        for k, v in nominais.items():
            meu = votos[k].get(c)
            if not meu:
                continue
            n += 1
            if meu[0] in CODS_PRESENTE:
                pres += 1
            elif meu[0] != "NCom":
                just += 1
            g = votos[k].get(lider, ("",))[0] if lider else ""
            if c != lider and g in ("Sim", "Não") and meu[0] in ("Sim", "Não"):
                gn += 1; gi += meu[0] == g
        s["part"] = dict(n=n, votou=pres, justificada=just)
        s["gov"] = dict(n=gn, igual=gi, ref="líder do governo")
        s["exercicio"] = [list(x) for x in s.pop("ivs")]

    # CEAPS (por nome do senador)
    por_nome = {" ".join(norm(s["nome"])): c for c, s in sens.items()}
    sem = Counter()
    for ano in anos:
        b = baixa(f"https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_{ano}.csv", timeout=300)
        if not b:
            continue
        for r in linhas_csv(b, enc="latin-1", pular=1):
            nome = " ".join(norm(r.get("SENADOR")))
            c = por_nome.get(nome)
            if not c:
                sem[nome] += 1
                continue
            v = num(r.get("VALOR_REEMBOLSADO"))
            s = sens[c]
            s.setdefault("ceap", {}).setdefault(str(ano), 0.0)
            s["ceap"][str(ano)] += v
            s.setdefault("ceapCat", Counter())[(r.get("TIPO_DESPESA") or "").strip()] += v
        print("ceaps", ano, file=sys.stderr)
    if sem:
        print("CEAPS sem correspondência:", sem.most_common(15), file=sys.stderr)
    return sens, nominais, votos, lider


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--saida", required=True); a.add_argument("--anos", default="2023,2024,2025,2026"); a.add_argument("--casas", default="C,S")
    o = a.parse_args()
    anos = [int(x) for x in o.anos.split(",")]
    sai = Path(o.saida); sai.mkdir(parents=True, exist_ok=True)
    import traceback
    casas = o.casas.split(",")
    try:
        if "C" not in casas:
            raise RuntimeError("Câmara pulada (--casas)")
        deps, cv, cvotos = camara(anos)
    except Exception:
        traceback.print_exc(); deps, cv, cvotos = {}, {}, {}
        (sai / "_erro_camara.txt").write_text(traceback.format_exc(), encoding="utf-8")
    try:
        if "S" not in casas:
            raise RuntimeError("Senado pulado (--casas)")
        sens, sv, svotos, lider = senado(anos)
    except Exception:
        traceback.print_exc(); sens, sv, svotos, lider = {}, {}, {}, None
        (sai / "_erro_senado.txt").write_text(traceback.format_exc(), encoding="utf-8")

    pars = []
    for p in list(deps.values()) + list(sens.values()):
        cat = p.pop("ceapCat", Counter())
        p["ceap"] = {k: round(v, 2) for k, v in (p.get("ceap") or {}).items()}
        p["ceapCat"] = [[k, round(v, 2)] for k, v in cat.most_common(6)]
        pars.append(p)
    (sai / "parlamentares.json").write_text(json.dumps(pars, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    resumo = [dict(casa="C", **{k: v[k] for k in ("id", "data", "hora", "desc", "aprov", "sim", "nao", "out", "abertura", "props", "gov", "cont")}) for v in cv.values()]
    resumo += [dict(casa="S", **v) for v in sv.values()]
    (sai / "votacoes.json").write_text(json.dumps(resumo, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    cod = {"Sim": "S", "Não": "N", "Abstenção": "A", "Obstrução": "O", "Artigo 17": "P", "Presidente": "P", "P-NRV": "R", "NCom": "F"}
    vv = {}
    for casa, votos in (("C", cvotos), ("S", svotos)):
        for k, d in votos.items():
            if (casa == "C" and k in cv) or (casa == "S" and k in sv):
                vv[f"{casa}:{k}"] = {pid: [cod.get(x[0], "J"), x[1]] for pid, x in d.items()}
    (sai / "votos.json").write_text(json.dumps(vv, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    meta = dict(gerado=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), anos=anos, deputados=len(deps), senadores=len(sens),
                votacoes_camara=len(cv), votacoes_senado=len(sv), lider_governo_senado=lider,
                fontes=["https://dadosabertos.camara.leg.br", "https://www.camara.leg.br/cotas", "https://legis.senado.leg.br/dadosabertos",
                        "https://www.senado.leg.br/transparencia/LAI/verba"])
    (sai / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
