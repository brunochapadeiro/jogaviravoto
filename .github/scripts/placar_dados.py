"""Placar da semana: baixa as votações nominais do plenário da Câmara e do Senado num período e grava um JSON compacto.
Só biblioteca padrão (roda no GitHub Actions). Fontes: dadosabertos.camara.leg.br (API v2) e legis.senado.leg.br/dadosabertos/votacao.
Uso: python3 placar_dados.py [--inicio AAAA-MM-DD] [--fim AAAA-MM-DD] --saida placar.json
Sem datas: os 7 dias que terminam ontem (horário de Brasília)."""
import argparse, datetime as dt, json, sys, time, urllib.request, urllib.error

UA = {"User-Agent": "Mozilla/5.0 (vigilia vira-voto; dados publicos)", "Accept": "application/json"}
CAM = "https://dadosabertos.camara.leg.br/api/v2"
SEN = "https://legis.senado.leg.br/dadosabertos"


def pega(url, tentativas=4):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if i == tentativas - 1:
                print("FALHOU", url, e, file=sys.stderr)
                return None
            time.sleep(2 * (i + 1))


def lista_camara(ini, fim):
    url = f"{CAM}/votacoes?dataInicio={ini}&dataFim={fim}&idOrgao=180&itens=200&ordem=ASC&ordenarPor=dataHoraRegistro"
    out = []
    while url:
        d = pega(url)
        if not d: break
        out += d.get("dados", [])
        url = next((l["href"] for l in d.get("links", []) if l.get("rel") == "next"), None)
    return out


def proposicao(det):
    for chave in ("proposicoesAfetadas", "objetosPossiveis"):
        for p in det.get(chave) or []:
            if p.get("siglaTipo") in ("PEC", "PLP", "PL", "MPV", "PDL", "PLV", "PRC", "PLN"):
                return dict(id=p.get("id"), tipo=p.get("siglaTipo"), numero=p.get("numero"), ano=p.get("ano"), ementa=p.get("ementa"))
    for chave in ("proposicoesAfetadas", "objetosPossiveis"):
        for p in det.get(chave) or []:
            return dict(id=p.get("id"), tipo=p.get("siglaTipo"), numero=p.get("numero"), ano=p.get("ano"), ementa=p.get("ementa"))
    return None


def camara(ini, fim):
    vs = []
    for v in lista_camara(ini, fim):
        vid = v["id"]
        votos = (pega(f"{CAM}/votacoes/{vid}/votos") or {}).get("dados") or []
        time.sleep(0.2)
        if not votos:
            continue  # votação simbólica: sem voto nominal
        det = (pega(f"{CAM}/votacoes/{vid}") or {}).get("dados") or {}
        ori = (pega(f"{CAM}/votacoes/{vid}/orientacoes") or {}).get("dados") or []
        time.sleep(0.2)
        vs.append(dict(
            id=vid, data=v.get("data"), hora=(v.get("dataHoraRegistro") or "")[11:16], descricao=v.get("descricao"),
            aprovada=str(v.get("aprovacao")) == "1", abertura=det.get("descUltimaAberturaVotacao"), proposicao=proposicao(det),
            orientacoes={o["siglaPartidoBloco"]: o.get("orientacaoVoto") or "" for o in ori},
            votos=[[x["deputado_"]["id"], x["deputado_"]["nome"], x["deputado_"]["siglaPartido"], x["deputado_"]["siglaUf"], x["tipoVoto"]] for x in votos],
            url=(f"https://www.camara.leg.br/propostas-legislativas/{proposicao(det)['id']}" if proposicao(det) else "https://www.camara.leg.br/busca-portal/proposicoes")))
    return vs


def senado(ini, fim):
    d = pega(f"{SEN}/votacao?dataInicio={ini}&dataFim={fim}") or []
    vs = []
    for v in d:
        if v.get("votacaoSecreta") == "S":
            votos = []
        else:
            votos = [[x.get("codigoParlamentar"), x.get("nomeParlamentar"), x.get("siglaPartidoParlamentar"), x.get("siglaUFParlamentar"), x.get("siglaVotoParlamentar")] for x in v.get("votos") or []]
        vs.append(dict(
            id=v.get("codigoSessaoVotacao"), data=v.get("dataSessao"), descricao=v.get("descricaoVotacao"), resultado=v.get("resultadoVotacao"),
            secreta=v.get("votacaoSecreta") == "S", proposicao=dict(tipo=v.get("sigla"), numero=v.get("numero"), ano=v.get("ano"), ementa=v.get("ementa"),
                                                                    identificacao=v.get("identificacao"), codigoMateria=v.get("codigoMateria")),
            totais=dict(sim=v.get("totalVotosSim"), nao=v.get("totalVotosNao"), abst=v.get("totalVotosAbstencao")), votos=votos,
            url=f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{v.get('codigoMateria')}"))
    return vs


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--inicio"); a.add_argument("--fim"); a.add_argument("--saida", required=True)
    o = a.parse_args()
    hoje = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).date()
    fim = o.fim or (hoje - dt.timedelta(days=1)).isoformat()
    ini = o.inicio or (dt.date.fromisoformat(fim) - dt.timedelta(days=6)).isoformat()
    cam, sen = camara(ini, fim), senado(ini, fim)
    res = dict(periodo=dict(inicio=ini, fim=fim), gerado=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               fontes=dict(camara="https://dadosabertos.camara.leg.br", senado="https://legis.senado.leg.br/dadosabertos"),
               camara=cam, senado=sen)
    with open(o.saida, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, separators=(",", ":"))
    print(f"periodo {ini} a {fim}: camara {len(cam)} votacoes nominais; senado {len(sen)} votacoes")


if __name__ == "__main__":
    main()
