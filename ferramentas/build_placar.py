"""Placar da semana (De olho no Congresso): página /semana e cards 4:5 e 9:16 a partir do placar.json do robô (ramo dados, semana/<data>).
Portátil: roda daqui (build) ou da pasta ferramentas/ do repositório, com marca.py, a11y.py, congresso_data.py, icons.json e base.css ao lado.
Uso: python3 build_placar.py --dados placar.json --site <pasta public do site> --saida <pasta> [--resumos resumos.json] [--cards]
resumos.json (opcional, escrito na revisão de segunda): {"manchete": "...", "destaques": ["sen:PEC-221-2019", ...],
  "resumos": {"sen:PEC-221-2019": "Fim da escala 6x1: ..."}}"""
import argparse, collections, html, json, shutil, sys, zipfile
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import marca as M
import a11y as A11
import congresso_data as C

E = html.escape
SITE = M.FLIPER
CURTO = SITE.replace("https://", "").rstrip("/")
SIM, NAO, OUTRO = "#2FA899", "#C47F18", "#5F6670"   # validados no fundo escuro (#15181D): CVD 14,4; visão normal 20,2
TX, TX2, TX3, SUP = "#F4F2EC", "#C9D1DB", "#9AA3AE", "#15181D"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
CASA = {"cam": "Câmara", "sen": "Senado"}
# Votos necessários para aprovar, por tipo (Câmara 513, Senado 81): PEC 3/5; PLP maioria absoluta; resto maioria simples dos presentes.
QUORUM = {("cam", "PEC"): 308, ("sen", "PEC"): 49, ("cam", "PLP"): 257, ("sen", "PLP"): 41}
PESO = {"PEC": 50, "PLP": 30, "MPV": 25, "PLV": 25, "PL": 20, "PDL": 15}


def br(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def dia(iso):
    a, m, d = iso[:10].split("-")
    return f"{int(d)}/{int(m)}"


def periodo_txt(ini, fim):
    a1, m1, d1 = map(int, ini.split("-")); a2, m2, d2 = map(int, fim.split("-"))
    if m1 == m2 and a1 == a2:
        return f"{d1} a {d2} de {MESES[m2 - 1]} de {a2}"
    return f"{d1} de {MESES[m1 - 1]} a {d2} de {MESES[m2 - 1]} de {a2}"


def classe_voto(casa, v):
    v = (v or "").strip()
    if v == "Sim": return "sim"
    if v in ("Não", "Nao"): return "nao"
    if v.lower().startswith("abst"): return "abst"
    if v.lower().startswith("obstru"): return "obst"
    return None  # Artigo 17 (presidente), ausências, licenças, presidente do Senado


def partido(p):
    p = (p or "").upper().replace("PC DO B", "PCDOB")
    return C.norm({"PCDOB": "PCdoB", "SOLIDARIEDADE": "SOLIDARIEDADE", "PODEMOS": "PODE", "UNIÃO BRASIL": "UNIÃO"}.get(p, p))


def le(dados):
    """Votações nominais das duas Casas num formato só."""
    vs = []
    for casa in ("camara", "senado"):
        cs = "cam" if casa == "camara" else "sen"
        for v in dados.get(casa, []):
            if not v.get("votos"): continue
            p = v.get("proposicao") or {}
            tipo, num, ano = p.get("tipo") or "?", p.get("numero") or "", p.get("ano") or ""
            cont = collections.Counter(); porp = collections.defaultdict(collections.Counter)
            for x in v["votos"]:
                k = classe_voto(cs, x[4])
                if not k: continue
                cont[k] += 1; porp[partido(x[2])][k] += 1
            aprovada = v.get("aprovada") if cs == "cam" else (v.get("resultado") == "A")
            vs.append(dict(casa=cs, id=str(v["id"]), data=v["data"], hora=v.get("hora", ""), descricao=v.get("descricao") or "",
                           chave=f"{cs}:{tipo}-{num}-{ano}", rotulo=f"{tipo} {num}/{ano}", tipo=tipo, ementa=p.get("ementa") or "",
                           aprovada=aprovada, cont=cont, porp=porp, url=v.get("url") or "", orient=v.get("orientacoes") or {}))
    return vs


def requerimento(v):
    d = v["descricao"].lower()
    return "requerimento" in d[:40] or "regime de tramitação" in d


def grupos(vs):
    g = collections.OrderedDict()
    for v in sorted(vs, key=lambda v: (v["data"], v["hora"])):
        g.setdefault(v["chave"], []).append(v)
    out = []
    for k, lst in g.items():
        merito = [v for v in lst if not requerimento(v)] or lst
        rep = merito[-1]
        s, n = rep["cont"]["sim"], rep["cont"]["nao"]
        disputa = 1 - abs(s - n) / max(1, s + n)
        out.append(dict(chave=k, rep=rep, todas=lst, n=len(lst), score=PESO.get(rep["tipo"], 5) + 20 * disputa - (40 if requerimento(rep) else 0)))
    return out


def resumo_auto(ementa, lim=170):
    e = " ".join(ementa.split())
    if len(e) <= lim: return e
    corte = e[:lim].rsplit(" ", 1)[0].rstrip(",;:")
    return corte + "…"


def nota_quorum(v):
    q = QUORUM.get((v["casa"], v["tipo"]))
    s, n = v["cont"]["sim"], v["cont"]["nao"]
    if q and not v["aprovada"] and s > n and s < q:
        return f"Teve maioria, mas {v['tipo']} precisa de {q} votos a favor."
    return ""


# ---------- gráficos ----------
def barras_partidos(v, rotulo, minimo, max_linhas=None, cls=""):
    """Uma barra por partido, comprimento = votos do partido; segmentos Sim, Não e outros (abstenção/obstrução).
    minimo: partidos com menos votos vão para "Outros"; max_linhas: só os maiores partidos (o resto em "Outros")."""
    grandes = sorted(v["porp"].items(), key=lambda x: -sum(x[1].values()))
    manter = [p for p, c in grandes if sum(c.values()) >= minimo]
    if max_linhas and len(manter) > max_linhas: manter = manter[:max_linhas - 1]
    pp = [(p, v["porp"][p]) for p in manter]
    resto = collections.Counter()
    nres = 0
    for p, c in v["porp"].items():
        if p not in manter: resto.update(c); nres += 1
    pp.sort(key=lambda x: (-(x[1]["sim"] / max(1, sum(x[1].values()))), -sum(x[1].values())))
    if nres: pp.append((f"Outros ({nres})", resto))
    mx = max(sum(c.values()) for _, c in pp)
    W, x0, x1, alt, gap = 1000, 220, 900, 34, 10
    H = len(pp) * (alt + gap) + 4
    desc = "; ".join(f"{(C.nome(p) if not p.startswith('Outros') else p)}: {c['sim']} sim, {c['nao']} não" + (f", {c['abst'] + c['obst']} outros" if c['abst'] + c['obst'] else "") for p, c in pp)
    out = []
    for i, (p, c) in enumerate(pp):
        y = i * (alt + gap) + 2
        nome = p if p.startswith("Outros") else C.nome(p)
        cor_dot = None if p.startswith("Outros") else C.COR.get(C.classe(p))
        if cor_dot and cor_dot != "none":
            out.append(f'<circle cx="{x0 - 12}" cy="{y + alt / 2}" r="7" fill="{cor_dot}"/>')
        out.append(f'<text x="{x0 - 26}" y="{y + alt / 2}" fill="{TX}" font-size="30" font-weight="700" text-anchor="end" dominant-baseline="middle">{E(nome)}</text>')
        x = x0
        tot = sum(c.values())
        larg = (x1 - x0) * tot / mx
        for k, cor in (("sim", SIM), ("nao", NAO), ("abst", OUTRO), ("obst", OUTRO)):
            if not c[k]: continue
            w = larg * c[k] / tot
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w - 2, 1):.1f}" height="{alt}" fill="{cor}"><title>{E(nome)}: {c[k]} {k}</title></rect>')
            if w > 44:
                out.append(f'<text x="{x + w / 2 - 1:.1f}" y="{y + alt / 2 + 1}" fill="#FFFFFF" font-size="24" font-weight="700" text-anchor="middle" dominant-baseline="middle">{c[k]}</text>')
            x += w
        if larg < 120:
            out.append(f'<text x="{x0 + larg + 10:.1f}" y="{y + alt / 2}" fill="{TX2}" font-size="24" dominant-baseline="middle">{c["sim"]}–{c["nao"]}</text>')
    return (f'<svg class="gr{(" " + cls) if cls else ""}" viewBox="0 0 {W} {H}" role="img" aria-label="{E(rotulo + ". " + desc)}" font-family="Atkinson Hyperlegible, sans-serif">'
            + "".join(out) + "</svg>")


def legenda_votos():
    return ('<p class="cd-leg"><span><i class="sw" style="background:' + SIM + '"></i>Sim</span><span><i class="sw" style="background:' + NAO
            + '"></i>Não</span><span><i class="sw" style="background:' + OUTRO + '"></i>Abstenção ou obstrução</span></p>')


def legenda_campos():
    it = [("pt", "PT"), ("esq", "Esquerda"), ("cen", "Centro"), ("dir", "Direita"), ("pl", "PL")]
    return '<p class="cd-leg cd-leg2">Bolinha: campo do partido no Raio-X · ' + "".join(f'<span><i class="sw" style="background:{C.COR[k]}"></i>{r}</span>' for k, r in it) + "</p>"


# ---------- cards ----------
def card(n, tot, corpo, fonte, rot, slug, cls=""):
    pe = (f'<div class="cd-pe"><span class="cd-fonte">{E(fonte)}</span><span class="cd-mk">{M.icon("ig")}{E(M.IG)}</span>'
          f'<span class="cd-cc">{CURTO}/{slug} · <span class="nw">CC BY-NC-SA 4.0</span></span></div>')
    return (f'<figure class="cd{(" " + cls) if cls else ""}" id="card-{n:02d}" role="group" aria-label="Card {n} de {tot}: {E(rot)}">'
            f'<div class="cd-in"><p class="cd-k">DE OLHO NO CONGRESSO · PLACAR DA SEMANA<span class="cd-n"> · {n}/{tot}</span></p>{corpo}</div>{pe}</figure>')


def bloco_destaque(gr, res, outros, pagina=False):
    v = gr["rep"]
    s, n, o = v["cont"]["sim"], v["cont"]["nao"], v["cont"]["abst"] + v["cont"]["obst"]
    resumo = res.get(gr["chave"]) or resumo_auto(v["ementa"])
    status = "Aprovada" if v["aprovada"] else "Rejeitada"
    turnos = " nos dois turnos" if gr["n"] == 2 and v["tipo"] == "PEC" and all(x["aprovada"] for x in gr["todas"]) else ""
    nq = nota_quorum(v)
    gov = v["orient"].get("Governo") or ""
    opo = v["orient"].get("Oposição") or ""
    ori = ""
    if gov or opo:
        ori = '<p class="cd-x2">Orientação' + (f' do governo: <b>{E(gov)}</b>' if gov else '') + (' · ' if gov and opo else '') + (f'da oposição: <b>{E(opo)}</b>' if opo else '') + "</p>"
    outra = ""
    for g2 in outros:
        if g2["chave"].split(":", 1)[1] == gr["chave"].split(":", 1)[1] and g2["chave"] != gr["chave"]:
            v2 = g2["rep"]
            outra = f'<p class="cd-x2">No {CASA[v2["casa"]]}: {"aprovada" if v2["aprovada"] else "rejeitada"} por {v2["cont"]["sim"]} a {v2["cont"]["nao"]} ({dia(v2["data"])}).</p>'
    minimo = 1 if pagina else (12 if v["casa"] == "cam" else 2)
    rot_g = f"Como votou cada partido: {v['rotulo']}, {CASA[v['casa']]}"
    if pagina:
        graf = barras_partidos(v, rot_g, minimo)
    else:
        graf = barras_partidos(v, rot_g, minimo, cls="so-story") + barras_partidos(v, rot_g, 1, max_linhas=8, cls="so-feed")
    corpo = (f'<p class="pl-tag">{E(v["rotulo"])} · {CASA[v["casa"]]} · {dia(v["data"])}</p>'
             f'<p class="cd-t3">{E(resumo)}</p>'
             f'<div class="pl-res"><span class="pl-st {"ok" if v["aprovada"] else "no"}">{status}{turnos}</span>'
             f'<span class="pl-n"><b style="color:{SIM}">{s}</b> sim</span><span class="pl-n"><b style="color:{NAO}">{n}</b> não</span>'
             + (f'<span class="pl-n"><b>{o}</b> outros</span>' if o else "") + "</div>"
             + (f'<p class="cd-x2 pl-q">{E(nq)}</p>' if nq else "")
             + graf + legenda_votos() + ori + outra
             + (f'<p class="cd-x2">O que foi votado: {E(resumo_auto(v["descricao"], 200))}</p>' if pagina else ""))
    return corpo


def governismo(vs):
    """Câmara: % dos votos sim/não de cada partido iguais à orientação do governo, só em votações divididas (≥ 10% contra o governo)."""
    divididas = []
    for v in vs:
        if v["casa"] != "cam": continue
        g = v["orient"].get("Governo")
        if g not in ("Sim", "Não"): continue
        lado = "sim" if g == "Sim" else "nao"
        contra = v["cont"]["nao" if lado == "sim" else "sim"]
        if contra / max(1, v["cont"]["sim"] + v["cont"]["nao"]) >= 0.10:
            divididas.append((v, lado))
    if len(divididas) < 3:
        return None, len(divididas)
    acc = collections.defaultdict(lambda: [0, 0])
    for v, lado in divididas:
        for p, c in v["porp"].items():
            acc[p][0] += c[lado]; acc[p][1] += c["sim"] + c["nao"]
    linhas = [(p, a / t) for p, (a, t) in acc.items() if t >= 5 * len(divididas) // 2]
    linhas.sort(key=lambda x: -x[1])
    return linhas, len(divididas)


def barras_gov(linhas, rotulo):
    W, x0, x1, alt, gap = 1000, 200, 900, 30, 10
    H = len(linhas) * (alt + gap) + 4
    out = [f'<line x1="{x0 + (x1 - x0) / 2}" y1="0" x2="{x0 + (x1 - x0) / 2}" y2="{H}" stroke="{TX3}" stroke-width="2" stroke-dasharray="6 6"/>']
    for i, (p, f) in enumerate(linhas):
        y = i * (alt + gap) + 2
        cor = C.COR.get(C.classe(p)); cor = TX3 if cor == "none" else cor
        out.append(f'<text x="{x0 - 14}" y="{y + alt / 2}" fill="{TX}" font-size="28" font-weight="700" text-anchor="end" dominant-baseline="middle">{E(C.nome(p))}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{(x1 - x0) * f:.1f}" height="{alt}" rx="4" fill="{cor}"><title>{E(C.nome(p))}: {br(100 * f)}%</title></rect>')
        out.append(f'<text x="{x0 + (x1 - x0) * f + 10:.1f}" y="{y + alt / 2}" fill="{TX}" font-size="26" font-weight="700" dominant-baseline="middle">{br(100 * f)}%</text>')
    desc = "; ".join(f"{C.nome(p)} {br(100 * f)}%" for p, f in linhas)
    return (f'<svg class="gr" viewBox="0 0 {W} {H}" role="img" aria-label="{E(rotulo + ". " + desc)}" font-family="Atkinson Hyperlegible, sans-serif">'
            + "".join(out) + "</svg>")


def montar(dados, res, slug):
    vs = le(dados)
    ini, fim = dados["periodo"]["inicio"], dados["periodo"]["fim"]
    per = periodo_txt(ini, fim)
    gs = grupos(vs)
    ncam = sum(1 for v in vs if v["casa"] == "cam"); nsen = sum(1 for v in vs if v["casa"] == "sen")
    pedidos = res.get("destaques")
    if pedidos:
        dest = [g for k in pedidos for g in gs if g["chave"] == k]
    else:
        dest = sorted([g for g in gs if not requerimento(g["rep"])], key=lambda g: -g["score"])[:3]
    resumos = res.get("resumos", {})
    gov, ndiv = governismo(vs)
    cards = []
    F_DADOS = "Fontes: Câmara dos Deputados e Senado Federal, dados abertos"
    if not vs:
        cards.append(("Semana sem votações nominais", f'<p class="cd-t2">Placar da semana</p><p class="cd-s">{E(per)}</p>'
                      '<p class="cd-x">Nenhuma votação nominal no plenário da Câmara nem do Senado. Votações simbólicas não registram o voto de cada parlamentar.</p>'
                      f'<p class="cd-s2">Acompanhe: {CURTO}/semana</p>', F_DADOS, "capa"))
    else:
        man = res.get("manchete")
        if not man and dest:
            g = dest[0]; v = g["rep"]
            man = f'{v["rotulo"]} ({CASA[v["casa"]]}): {"aprovada" if v["aprovada"] else "rejeitada"} por {v["cont"]["sim"]} a {v["cont"]["nao"]}.'
        cards.append(("Capa", f'<p class="cd-t2">Placar da semana</p><p class="cd-s">{E(per)}</p>'
                      f'<div class="cd-nums"><p><span>Câmara</span><b>{ncam}</b><span class="pl-u">votações nominais</span></p>'
                      f'<p><span>Senado</span><b>{nsen}</b><span class="pl-u">votações nominais</span></p></div>'
                      + (f'<p class="cd-x"><b>Destaque:</b> {E(man)}</p>' if man else "")
                      + '<p class="cd-s2 so-story">Como votou cada partido, nos cards a seguir →</p>', F_DADOS, "capa"))
        for g in dest:
            cards.append((g["rep"]["rotulo"], bloco_destaque(g, resumos, gs), F_DADOS + f'; {g["rep"]["rotulo"]}', "apertado"))
        if gov:
            cards.append(("Quem votou com o governo", f'<p class="cd-t3">Quem votou com o governo na Câmara</p>'
                          f'<p class="cd-x2">Nas {ndiv} votações divididas da semana: parte dos votos de cada partido igual à orientação do líder do governo</p>'
                          + barras_gov(gov, "Votos iguais à orientação do governo, por partido") + legenda_campos(), F_DADOS, "apertado"))
        resto = [g for g in gs if g not in dest]
        if resto:
            lis = "".join(f'<li><b>{E(g["rep"]["rotulo"])}</b> ({CASA[g["rep"]["casa"]]}, {dia(g["rep"]["data"])}): '
                          f'{"aprovada" if g["rep"]["aprovada"] else "rejeitada"}, {g["rep"]["cont"]["sim"]} a {g["rep"]["cont"]["nao"]}'
                          + (f' · {g["n"]} votações' if g["n"] > 1 else "") + "</li>" for g in resto[:7])
            mais = f'<p class="cd-x2">E mais {len(resto) - 7} no site.</p>' if len(resto) > 7 else ""
            cards.append(("As outras votações", f'<p class="cd-t3">As outras votações nominais</p><ul class="cd-lst">{lis}</ul>{mais}', F_DADOS, ""))
    cards.append(("Como ler", '<p class="cd-t3">Como ler o placar</p><ul class="cd-lst">'
                  "<li>Só entram votações nominais do plenário: nas simbólicas, ninguém registra o voto.</li>"
                  "<li>Orientação do governo: a do líder do governo na Câmara. O Senado não publica orientação nos dados abertos.</li>"
                  "<li>A bolinha ao lado do partido é o campo dele no Raio-X do Congresso (escala de 519 cientistas políticos).</li></ul>"
                  f'<p class="cd-s2">Todas as votações e os dados:<br><span class="url">{CURTO}/{slug}</span></p>'
                  '<p class="cd-x2">Salve e mande para quem precisa ver. Feito com auxílio de IA (Claude), com dados públicos.</p>', F_DADOS, "fim"))
    tot = len(cards)
    html_cards = [card(i + 1, tot, c, f, r, slug, k) for i, (r, c, f, k) in enumerate(cards)]
    return dict(vs=vs, gs=gs, dest=dest, gov=gov, ndiv=ndiv, per=per, ini=ini, fim=fim, ncam=ncam, nsen=nsen,
                cards=html_cards, rots=[r for r, _, _, _ in cards], resumos=resumos)


def legenda_post(D, res):
    lin = [f"PLACAR DA SEMANA ({dia(D['ini'])} a {dia(D['fim'])})", "",
           f"Câmara: {D['ncam']} votações nominais. Senado: {D['nsen']}." if D["vs"] else "Semana sem votações nominais no plenário.", ""]
    for g in D["dest"]:
        v = g["rep"]
        r = D["resumos"].get(g["chave"]) or resumo_auto(v["ementa"], 110)
        nq = nota_quorum(v)
        turnos = " nos dois turnos" if g["n"] == 2 and v["tipo"] == "PEC" and all(x["aprovada"] for x in g["todas"]) else ""
        lin.append(f"• {v['rotulo']} ({CASA[v['casa']]}): {r} {'Aprovada' if v['aprovada'] else 'Rejeitada'}{turnos}: {v['cont']['sim']} a {v['cont']['nao']}."
                   + (f" {nq}" if nq else ""))
    lin += ["", "Como votou cada partido: nos cards e no site (link na bio).",
            "Dados: Câmara dos Deputados e Senado Federal (dados abertos). Feito com auxílio de IA (Claude).",
            f"© 2026 {M.AUTOR} · {M.LIC}", "", "#DeOlhoNoCongresso #PlacarDaSemana #ViraVoto"]
    return "\n".join(lin)


CSS_PAG = """
main { display:flex; flex-direction:column; gap:18px; }
.nw { white-space:nowrap; }
.txt { width:100%; min-height:14em; font:inherit; font-size:.98rem; padding:10px 12px; border-radius:12px; border:2px solid var(--linha); background:var(--cartao); color:var(--tinta); }
.cd .gr { display:block; width:100%; height:auto; flex-shrink:0; }
.cd-in > * { flex-shrink:0; }
.so-feed { display:none !important; } html.feed .so-feed { display:block !important; } html.feed .gr.so-story { display:none !important; }
.cd-leg { display:flex; flex-wrap:wrap; gap:.6cqw 3cqw; font-size:3.2cqw; color:#C9D1DB; font-weight:700; }
.cd-leg span { display:inline-flex; align-items:center; gap:1.4cqw; } .cd-leg .sw { display:inline-block; width:3cqw; height:3cqw; border-radius:50%; }
.cd-leg2 { font-weight:400; font-size:2.9cqw; }
html.feed .cd-leg { font-size:2.8cqw; }
.pl-tag { align-self:flex-start; font-family:'Lexend', sans-serif; font-weight:700; font-size:3.6cqw; background:#FFE58F; color:#15181D; padding:1cqw 2.8cqw; border-radius:999px; }
html.feed .pl-tag { font-size:3.1cqw; }
.pl-res { display:flex; flex-wrap:wrap; align-items:baseline; gap:1cqw 4cqw; }
.pl-st { font-family:'Lexend', sans-serif; font-weight:800; font-size:5.2cqw; padding:.6cqw 2.6cqw; border-radius:2cqw; }
.pl-st.ok { background:rgba(47,168,153,.18); color:#7FE0D3; } .pl-st.no { background:rgba(196,127,24,.2); color:#F2C27A; }
.pl-n { font-size:4cqw; color:#C9D1DB; } .pl-n b { font-family:'Lexend', sans-serif; font-size:8cqw; margin-right:1cqw; }
html.feed .pl-st { font-size:4.4cqw; } html.feed .pl-n b { font-size:6.6cqw; } html.feed .pl-n { font-size:3.4cqw; }
.pl-q { color:#FFE58F !important; font-weight:700; }
.cd .url { font-size:3.6cqw; white-space:nowrap; font-weight:700; color:#FFE58F; }
.pl-u { font-size:3.2cqw; font-weight:400; color:#C9D1DB; }
.cd-lst { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:2cqw; }
.cd-lst li { border-left:1.2cqw solid rgba(255,229,143,.75); padding-left:2.6cqw; font-size:4cqw; line-height:1.3; color:#E6EAF0; }
html.feed .cd-lst { gap:1.3cqw; } html.feed .cd-lst li { font-size:3.5cqw; }
.cd.apertado .cd-t3 { font-size:5.6cqw; }
html.feed .cd.apertado .gr { width:86%; align-self:center; }
html.feed .cd.fim .cd-lst li { font-size:3.3cqw; } html.feed .cd.apertado .cd-in { gap:1.3cqw; } html.feed .cd.apertado .cd-t3 { font-size:4.6cqw; } html.feed .cd.apertado .cd-x2 { font-size:2.9cqw; }
.gr-pag { background:#15181D; border-radius:16px; padding:14px 14px 10px; color:#F4F2EC; }
.gr-pag .gr { display:block; width:100%; height:auto; }
.gr-pag .cd-leg { font-size:.9rem; gap:4px 14px; margin-top:8px; } .gr-pag .cd-leg .sw { width:12px; height:12px; }
.gr-pag .pl-tag { font-size:.85rem; padding:3px 10px; } .gr-pag .pl-st { font-size:1rem; padding:2px 8px; border-radius:8px; }
.gr-pag .pl-n { font-size:.95rem; } .gr-pag .pl-n b { font-size:1.6rem; } .gr-pag .cd-t3 { font-size:1.2rem; margin:8px 0; }
.gr-pag .cd-x2 { font-size:.92rem; color:#C9D1DB; margin-top:6px; } .gr-pag .pl-res { gap:4px 16px; margin-bottom:8px; }
.tb-wrap { overflow-x:auto; max-width:100%; border:2px solid var(--linha); border-radius:14px; background:var(--cartao); margin-top:10px; }
.tb { border-collapse:collapse; width:100%; font-size:.92rem; }
.tb caption { text-align:left; font-weight:700; padding:10px 12px 4px; }
.tb th, .tb td { padding:7px 9px; border-top:1px solid var(--linha); text-align:left; vertical-align:top; }
.tb thead th { font-size:.82rem; color:var(--suave); border-top:0; }
.tb .n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
.tb .contr { display:block; font-size:.82rem; color:var(--suave); font-weight:400; }
"""


def og_doc(tpl, slug, titulo, desc, img, alt):
    og = (f'<meta name="description" content="{E(desc)}">\n<meta property="og:type" content="website"><meta property="og:site_name" content="Games Vira-Voto">\n'
          f'<meta property="og:title" content="{E(titulo)}"><meta property="og:description" content="{E(desc)}">\n<meta property="og:url" content="{SITE}{slug}">\n'
          f'<meta property="og:image" content="{SITE}{img}"><meta property="og:image:type" content="image/png">\n'
          f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{E(alt)}">\n'
          '<meta property="og:locale" content="pt_BR"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="icone.svg" type="image/svg+xml">\n')
    head = '<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + og
    return head + tpl.replace('<div class="wrap">', '</head><body>\n<div class="wrap">', 1) + "\n</body></html>"


def pagina(D, slug, arquivo_semanas, legenda):
    base = (AQUI / "base.css").read_text(encoding="utf-8")
    css = (base.replace("__WML__", M.wm_tile_uri("rgba(20,24,30,.045)", 340)).replace("__WMD__", M.wm_tile_uri("rgba(242,240,234,.05)", 300))
           + A11.CSS + CSS_PAG)
    redes = f'<p class="redes"><a class="botao-ig" href="{M.IG_URL}" target="_blank" rel="noopener">{M.icon("ig")}Siga {E(M.IG)} no Instagram</a> {M.selo_html()}</p>'
    dest_html = "".join(f'<figure class="gr-pag" style="margin:12px 0 0">{bloco_destaque(g, D["resumos"], D["gs"], pagina=True)}'
                        f'<figcaption class="cd-x2"><a href="{E(g["rep"]["url"])}" target="_blank" rel="noopener" style="color:#FFE58F">Ficha da proposta</a></figcaption></figure>'
                        for g in D["dest"])
    gov_html = ""
    if D["gov"]:
        gov_html = (f'<section aria-labelledby="gv-t"><h2 id="gv-t">Quem votou com o governo na Câmara</h2>'
                    f'<p class="sub" style="font-size:1rem">Nas {D["ndiv"]} votações divididas da semana (pelo menos 10% contra a orientação do governo).</p>'
                    f'<figure class="gr-pag" style="margin:10px 0 0">{barras_gov(D["gov"], "Votos iguais à orientação do governo, por partido")}{legenda_campos()}</figure></section>')
    linhas = "".join(
        f'<tr><td>{dia(v["data"])}</td><td>{CASA[v["casa"]]}</td><td><a href="{E(v["url"])}" target="_blank" rel="noopener">{E(v["rotulo"])}</a>'
        f'<span class="contr">{E(resumo_auto(v["descricao"], 140))}</span></td><td>{"Aprovada" if v["aprovada"] else "Rejeitada"}</td>'
        f'<td class="n">{v["cont"]["sim"]}</td><td class="n">{v["cont"]["nao"]}</td><td class="n">{v["cont"]["abst"] + v["cont"]["obst"]}</td>'
        f'<td>{E(v["orient"].get("Governo") or "—")}</td></tr>' for v in sorted(D["vs"], key=lambda v: (v["data"], v["hora"])))
    tabela = ('<div class="tb-wrap" tabindex="0" role="region" aria-label="Tabela das votações nominais da semana"><table class="tb">'
              f'<caption>Votações nominais do plenário, {E(D["per"])}</caption><thead><tr><th scope="col">Dia</th><th scope="col">Casa</th><th scope="col">O que foi votado</th>'
              '<th scope="col">Resultado</th><th scope="col" class="n">Sim</th><th scope="col" class="n">Não</th><th scope="col" class="n">Outros</th><th scope="col">Governo orientou</th></tr></thead>'
              f'<tbody>{linhas}</tbody></table></div>') if D["vs"] else '<p>Nenhuma votação nominal no plenário nesta semana.</p>'
    arq = "".join(f'<li><a href="{E(s)}">{E(t)}</a></li>' for s, t in arquivo_semanas)
    corpo = f"""<div class="wrap">
  <a class="pular" href="#votacoes">Pular para as votações</a>
  <div class="topo"><a href="{SITE}">← Games Vira-Voto</a>{redes}</div>
  {A11.barra()}
  <p class="placa">DE OLHO NO CONGRESSO</p>
  <h1>Placar da <span>semana</span></h1>
  <p class="sub">{E(D["per"])}: o que a Câmara e o Senado votaram e como votou cada partido, com os dados abertos das duas Casas.</p>
  <main data-a11y-ler>
  <section aria-labelledby="dt-t"><h2 id="dt-t">Destaques</h2>{dest_html or '<p>Sem votações nominais nesta semana.</p>'}</section>
  {gov_html}
  <section class="caixa" aria-labelledby="vt-t" id="votacoes"><h2 id="vt-t">Todas as votações nominais</h2>{tabela}</section>
  <section class="caixa so-cards-alvo" aria-labelledby="cd-t"><h2 id="cd-t" class="cds-h">Cards para as redes</h2>
    <p class="sub cds-nota" style="font-size:.98rem;margin-top:4px">Prints desta página, sem foto nem imagem gerada.</p>
    <div class="baixar-cds"><a class="btn forte" href="arquivos/Placar_{D["fim"]}_carrossel.zip" download>Baixar carrossel</a>
      <a class="btn" href="arquivos/Placar_{D["fim"]}_stories.zip" download>Baixar cards para Stories</a></div>
    <div class="cds">{"".join(D["cards"])}</div></section>
  <section class="caixa" aria-labelledby="lg-t"><h2 id="lg-t">Legenda para o Instagram</h2>
    <textarea id="txt-lg" class="txt" readonly aria-label="Legenda">{E(legenda)}</textarea>
    <p class="acoes" style="margin-top:8px"><button type="button" class="btn forte" data-copia="txt-lg">Copiar a legenda</button></p></section>
  <section class="caixa" aria-labelledby="mt-t"><h2 id="mt-t">Como fizemos</h2><ul>
    <li>Votações nominais do plenário da Câmara e do Senado no período, pelos dados abertos de cada Casa. Votações simbólicas não registram o voto de cada parlamentar e ficam de fora.</li>
    <li>Partido: o do parlamentar no dia da votação, como registrado pela Casa. Abstenção e obstrução aparecem juntas como “outros”; ausências e o voto do presidente da sessão não entram.</li>
    <li>Orientação do governo: a do líder do governo na Câmara. O Senado não publica orientações nos dados abertos.</li>
    <li>Quem votou com o governo: só nas votações divididas, em que pelo menos 10% votaram contra a orientação do governo, e só quando há pelo menos três delas na semana.</li>
    <li>Bolinha do partido: campo ideológico no <a href="congresso">Raio-X do Congresso</a> (Bolognesi, Ribeiro e Codato, 2023).</li></ul></section>
  <section class="caixa" aria-labelledby="ft-t"><h2 id="ft-t">Fontes</h2><ul>
    <li><a href="https://dadosabertos.camara.leg.br" target="_blank" rel="noopener">Câmara dos Deputados, dados abertos (API v2)</a></li>
    <li><a href="https://legis.senado.leg.br/dadosabertos" target="_blank" rel="noopener">Senado Federal, dados abertos</a></li></ul></section>
  {('<section class="caixa" aria-labelledby="aq-t"><h2 id="aq-t">Semanas anteriores</h2><ul>' + arq + '</ul></section>') if arq else ''}
  </main>
  <footer>
    {A11.social(texto=f"Placar da semana no Congresso ({D['per']}): o que foi votado e como votou cada partido.", url=SITE + slug, conta_acesso=True)}
    {redes}
    <p>© 2026 {E(M.AUTOR)}. Licença Creative Commons {E(M.LIC)}. Feito com auxílio de IA (Claude), com dados públicos.</p>
    <p>Jogos, Cartilha e materiais: <a href="{SITE}">{CURTO}</a></p>
  </footer>
</div>
<script>(function(){{try{{var q=new URLSearchParams(location.search);if(q.get('formato')==='feed')document.documentElement.classList.add('feed');if(q.get('cards')==='1')document.documentElement.classList.add('so-cards');}}catch(x){{}}
document.querySelectorAll('[data-copia]').forEach(function(b){{var r=b.textContent;b.addEventListener('click',function(){{var t=document.getElementById(b.getAttribute('data-copia'));t.select();var ok=function(){{b.textContent='Copiado!';setTimeout(function(){{b.textContent=r;}},2000);}};
if(navigator.clipboard)navigator.clipboard.writeText(t.value).then(ok,function(){{document.execCommand('copy');ok();}});else{{document.execCommand('copy');ok();}}}});}});}})();</script>
{A11.script()}"""
    head = f"<title>Placar da semana</title>\n<style>{css}</style>\n"
    return og_doc(head + corpo, slug, f"Placar da semana: {D['per']}",
                  f"O que a Câmara e o Senado votaram de {D['per']} e como votou cada partido.", "og-congresso.png",
                  "Placar da semana: De olho no Congresso, de Prof. Bruno Chapadeiro")


def exporta(saida, site, slug, nrot, fim, legenda):
    from playwright.sync_api import sync_playwright
    import http.server, socketserver, threading, functools
    serv = saida / "_serv"; shutil.rmtree(serv, ignore_errors=True); serv.mkdir(parents=True)
    shutil.copytree(site / "fontes", serv / "fontes")
    shutil.copy(saida / f"{slug}.html", serv / f"{slug}.html")
    dst = saida / "cards"; shutil.rmtree(dst, ignore_errors=True); dst.mkdir()
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(serv))); porta = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    alts, avisos = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for formato, sufixo in (("story", ""), ("feed", "&formato=feed")):
            pg = b.new_page(viewport={"width": 400, "height": 900}, device_scale_factor=3)
            pg.route("**/api/placar**", lambda r: r.abort()); pg.route("https://vlibras.gov.br/**", lambda r: r.abort())
            pg.goto(f"http://127.0.0.1:{porta}/{slug}.html?cards=1{sufixo}"); pg.wait_for_timeout(800)
            pg.evaluate("document.fonts.ready")
            for i in range(nrot):
                el = pg.locator(f"#card-{i + 1:02d}")
                # ajuste automático: se o card transborda, o gráfico encolhe (até 45% da largura) e depois o texto
                pg.evaluate("""(sel) => { const c = document.querySelector(sel + ' .cd-in'); const g = [...c.querySelectorAll('.gr')].find(e => e.getBoundingClientRect().height > 0);
                  const sobra = () => c.scrollHeight - c.clientHeight; let w = g ? g.getBoundingClientRect().width / c.clientWidth * 100 : 0;
                  while (g && sobra() > 1 && w > 45) { w -= 3; g.style.width = w + '%'; g.style.alignSelf = 'center'; }
                  let f = 1; while (sobra() > 1 && f > 0.8) { f -= 0.04; c.style.fontSize = f + 'em'; c.querySelectorAll('.cd-t3,.cd-x,.cd-x2,.cd-lst li,.cd-leg').forEach(e => e.style.zoom = f); } }""", f"#card-{i + 1:02d}")
                f = dst / f"{formato}-{i + 1:02d}.png"; el.screenshot(path=str(f))
                aria = el.evaluate("e => [...e.querySelectorAll('svg[aria-label]')].map(s => 'Gráfico: ' + s.getAttribute('aria-label')).join('. ')")
                alts[f.name] = (aria + ". " if aria else "") + " ".join(el.inner_text().split())
                ov = pg.evaluate(f"(() => {{ const c = document.querySelector('#card-{i + 1:02d} .cd-in'); return c.scrollHeight - c.clientHeight; }})()")
                if ov > 1: avisos.append(f"transborda {formato} card {i + 1}: {ov}px")
            pg.close()
        b.close()
    srv.shutdown(); shutil.rmtree(serv, ignore_errors=True)
    (dst / "alt.json").write_text(json.dumps(alts, ensure_ascii=False, indent=1), encoding="utf-8")
    leia = (f"Placar da semana. Prints da página {SITE}{slug}\nDados: Câmara dos Deputados e Senado Federal (dados abertos).\n"
            f"© 2026 {M.AUTOR} · {M.LIC} · {M.IG}\n\nLEGENDA\n{legenda}\n\nTEXTO ALTERNATIVO (cole no campo de acessibilidade de cada imagem)\n")
    arq = saida / "arquivos"; arq.mkdir(exist_ok=True)
    for formato, nome in (("feed", f"Placar_{fim}_carrossel.zip"), ("story", f"Placar_{fim}_stories.zip")):
        with zipfile.ZipFile(arq / nome, "w", zipfile.ZIP_DEFLATED) as z:
            fs = sorted(dst.glob(f"{formato}-*.png"))
            for f in fs: z.write(f, f.name)
            z.writestr("LEIA-ME.txt", leia + "\n".join(f"{f.name}: {alts[f.name]}" for f in fs) + "\n")
    return avisos


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--dados", required=True); a.add_argument("--site", required=True); a.add_argument("--saida", required=True)
    a.add_argument("--resumos"); a.add_argument("--cards", action="store_true")
    o = a.parse_args()
    dados = json.loads(Path(o.dados).read_text(encoding="utf-8"))
    res = json.loads(Path(o.resumos).read_text(encoding="utf-8")) if o.resumos else {}
    site, saida = Path(o.site), Path(o.saida); saida.mkdir(parents=True, exist_ok=True)
    fim = dados["periodo"]["fim"]
    slug_sem = f"semana-{fim}"
    anteriores = sorted((p.stem for p in site.glob("semana-*.html") if p.stem != slug_sem), reverse=True)
    arquivo = [(s, "Semana até " + dia(s[7:]) + "/" + s[7:11]) for s in anteriores]
    D = montar(dados, res, "semana")
    leg = legenda_post(D, res)
    for slug in ("semana", slug_sem):
        (saida / f"{slug}.html").write_text(pagina(D, slug, arquivo, leg), encoding="utf-8")
    (saida / "legenda.txt").write_text(leg + "\n", encoding="utf-8")
    print(f"{D['per']}: câmara {D['ncam']}, senado {D['nsen']}, destaques {[g['chave'] for g in D['dest']]}, governismo {'sim' if D['gov'] else 'não'} ({D['ndiv']} divididas), {len(D['rots'])} cards")
    if o.cards:
        for av in exporta(saida, site, "semana", len(D["rots"]), fim, leg): print("AVISO", av)


if __name__ == "__main__":
    main()
