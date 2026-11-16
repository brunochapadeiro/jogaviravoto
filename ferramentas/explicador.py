"""Páginas explicativas com cards para as redes (molde da página /assedio).

Uso: python3 ferramentas/explicador.py --site public [--so big-techs|ajuste-fiscal] [--sem-cards]
Gera public/<slug>.html, public/og-<slug>.png e public/arquivos/<Nome>_carrossel.zip e _stories.zip
(prints da própria página: ?cards=1 para Stories 9:16 e ?cards=1&formato=feed para o carrossel 4:5).
O conteúdo de cada página fica em ferramentas/explicadores.py. Depois, rode ferramentas/site/organiza.py --site public.
"""
import argparse, html, re, sys, zipfile, urllib.parse
from pathlib import Path

B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
import explicadores as X  # noqa: E402

SITE = "https://vigieademocracia.brunochapadeiro.workers.dev/"
E = lambda s: html.escape(s, quote=True)


def molde(pub):
    h = (pub / "assedio.html").read_text(encoding="utf-8")
    cab = h[:h.find("</head>")]
    corpo_ini = h[h.find("</head>"):h.find("<!--/vg-trilha-->") + len("<!--/vg-trilha-->")]
    pe = h[h.find("</main>"):]
    ig = re.search(r'<svg class="ic" viewBox="0 0 448 512" aria-hidden="true"><path fill="currentColor" d="M224\.1[^"]*"/></svg>', h).group(0)
    wa = re.search(r'<svg class="ic" viewBox="0 0 448 512" aria-hidden="true"><path fill="currentColor" d="M380\.9[^"]*"/></svg>', h).group(0)
    return cab, corpo_ini, pe, ig, wa


def troca_meta(cab, P):
    url = SITE + P["slug"]
    og = SITE + f"og-{P['slug']}.png"
    cab = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(P["desc"])}">', cab)
    cab = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(P["titulo"])}">', cab)
    cab = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(P["desc"])}">', cab)
    cab = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', cab)
    cab = cab.replace(SITE + "og-assedio.png", og)
    cab = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{E(P["titulo"])}, de Prof. Bruno Chapadeiro">', cab)
    cab = re.sub(r"<title>[^<]*</title>", f"<title>{E(P['titulo'])}</title>", cab)
    return cab + X.CSS_EXTRA


def card(P, i, n, c, ig):
    cls = "cd" + ({"capa": " capa", "fim": " fim"}.get(c.get("tipo"), ""))
    rot = f"Card {i} de {n}: {c['rotulo']}"
    return (f'<figure class="{cls}" id="card-{i:02d}" role="group" aria-label="{E(rot)}"><div class="cd-in">'
            f'<p class="cd-k">{E(P["kicker"])}<span class="cd-n"> · {i}/{n}</span></p>{c["html"]}</div>'
            f'<div class="cd-pe"><span class="cd-fonte">{E(c["fonte"])}</span><span class="cd-mk">{ig}@brunochapadeiro</span>'
            f'<span class="cd-cc">vigieademocracia.brunochapadeiro.workers.dev · <span class="nw">CC BY-NC-SA 4.0</span></span></div></figure>')


def pagina(pub, P):
    cab, ini, pe, ig, wa = molde(pub)
    cab = troca_meta(cab, P)
    ini = ini.replace('href="#formas"', 'href="#conteudo"')
    n = len(P["cards"])
    cards = "".join(card(P, i + 1, n, c, ig) for i, c in enumerate(P["cards"]))
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(P["whatsapp"])
    secoes = "\n".join(P["secoes"])
    fontes = "".join(f"<li>{f}</li>" for f in P["fontes"])
    main = f"""
  <p class="placa">{E(P['placa'])}</p>
  <h1>{P['h1']}</h1>
  <p class="sub">{P['sub']}</p>
  <p class="fte atual">{E(P['atual'])}</p>
  <main data-a11y-ler id="conteudo">
  <nav class="caixa" aria-labelledby="vd-t" id="formas"><h2 id="vd-t">Vá direto ao ponto</h2><ul class="chips">{''.join(f'<li><a href="#{a}">{E(t)}</a></li>' for a, t in P['atalhos'])}<li><a class="forte-c" href="#cards">Cards para postar</a></li></ul></nav>
{secoes}
  <section class="caixa so-cards-alvo" aria-labelledby="cd-t" id="cards"><h2 id="cd-t" class="cds-h">{E(P['curto'])} em {n} cards</h2>
    <p class="sub cds-nota" style="font-size:.98rem;margin-top:4px">Prints desta página, sem foto, voz ou imagem gerada, com a fonte em cada card.</p>
    <div class="baixar-cds"><a class="btn forte" href="arquivos/{P['zip']}_carrossel.zip" download>Baixar carrossel</a>
      <a class="btn" href="arquivos/{P['zip']}_stories.zip" download>Baixar cards para Stories</a></div>
    <details class="ver-d" id="ver-cds"><summary>Ver os {n} cards</summary><div class="cds">{cards}</div></details></section>
  <section class="caixa" aria-labelledby="wa-t" id="postar"><h2 id="wa-t">Para mandar e postar</h2>
    <details class="ver-d"><summary>Texto para o WhatsApp e legenda para o Instagram</summary>
    <h3 style="margin-top:6px">No WhatsApp</h3>
    <textarea id="txt-wa" class="txt" style="min-height:10em" readonly aria-label="Texto para o WhatsApp">{E(P['whatsapp'])}</textarea>
    <p class="acoes" style="margin-top:8px"><button type="button" class="btn forte" data-copia="txt-wa">Copiar o texto</button>
      <a class="btn" href="{E(wa_url)}" target="_blank" rel="noopener">{wa} Mandar no WhatsApp</a></p>
    <h3 style="margin-top:14px">Legenda para o Instagram</h3>
    <textarea id="txt-lg" class="txt" style="min-height:18em" readonly aria-label="Legenda para o Instagram">{E(P['legenda'])}</textarea>
    <p class="acoes" style="margin-top:8px"><button type="button" class="btn forte" data-copia="txt-lg">Copiar a legenda</button></p></details></section>
  <section class="caixa" aria-labelledby="ft-t" id="fontes"><h2 id="ft-t">Fontes</h2><ul>{fontes}</ul>
    <p class="fte">Situação em {E(P['data_txt'])}. Viu um erro? Avise no Instagram @brunochapadeiro: a correção sai em público, com data. Feito com auxílio de IA (Claude), com revisão do Prof. Bruno Chapadeiro.</p></section>
  """
    # rodapé: texto do compartilhar
    pe = re.sub(r'data-soc-texto="[^"]*"', f'data-soc-texto="{E(P["soc"])}"', pe)
    pe = pe.replace(SITE + "assedio", SITE + P["slug"])
    pe = re.sub(r'href="https://wa\.me/\?text=[^"]*" target="_blank" rel="noopener" class="soc-i"',
                f'href="https://wa.me/?text={urllib.parse.quote(P["soc"] + " " + SITE + P["slug"])}" target="_blank" rel="noopener" class="soc-i"', pe)
    (pub / f"{P['slug']}.html").write_text(cab + ini + main + pe, encoding="utf-8")


def og(pub, P, page):
    sys.path.insert(0, str(B))
    import marca as M
    fontes = (pub / "fontes").resolve().as_uri()
    cor = P["cor"]
    page.set_viewport_size({"width": 1200, "height": 630})
    page.set_content(f"""<html><head><style>
@font-face {{ font-family:'Lexend'; src:url('{fontes}/Lexend-var.woff2'); font-weight:100 900; }}
@font-face {{ font-family:'Atk'; src:url('{fontes}/AtkinsonHyperlegible-Regular.woff2'); font-weight:400; }}
@font-face {{ font-family:'Atk'; src:url('{fontes}/AtkinsonHyperlegible-Bold.woff2'); font-weight:700; }}
body {{ margin:0; width:1200px; height:630px; background:#FBF8F1 {M.wm_tile_uri('rgba(20,24,30,.05)', 300)}; font-family:'Atk'; color:#17191E; position:relative; overflow:hidden; }}
.placa {{ position:absolute; left:60px; top:80px; width:500px; height:380px; background:#FFE58F; border:4px solid #17191E; transform:rotate(-3deg); display:flex; align-items:center; justify-content:center; text-align:center;
  font-family:'Lexend'; font-weight:700; font-size:58px; line-height:1.08; padding:30px; box-sizing:border-box; border-top:22px solid {cor}; }}
.dir {{ position:absolute; left:640px; top:80px; width:500px; }}
.k {{ font-weight:700; color:#B3261E; letter-spacing:.06em; text-transform:uppercase; font-size:26px; margin:0 0 14px; }}
h1 {{ font-family:'Lexend'; font-weight:700; font-size:50px; line-height:1.05; margin:0 0 18px; }}
p.d {{ font-size:26px; line-height:1.4; color:#3A3D45; margin:0; }}
.pe {{ position:absolute; left:0; right:0; bottom:0; height:86px; background:#17191E; color:#FBF8F1; display:flex; align-items:center; justify-content:space-between; padding:0 64px; font-size:20px; }}
.pe b {{ font-size:30px; display:flex; align-items:center; gap:14px; }} .pe svg {{ width:34px; height:34px; }} .pe .r {{ text-align:right; line-height:1.4; }}
</style></head><body><div class="placa">{E(P['og'][0])}</div><div class="dir"><p class="k">{E(P['og'][1])}</p><h1>{E(P['og'][2])}</h1><p class="d">{E(P['og'][3])}</p></div>
<div class="pe"><b>{M.icon('ig')}@brunochapadeiro</b><div class="r">© Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0<br>vigieademocracia.brunochapadeiro.workers.dev</div></div></body></html>""")
    page.wait_for_timeout(300)
    page.screenshot(path=str(pub / f"og-{P['slug']}.png"))


def prints(pub, P, page, saida):
    """Cards: 1080 x 1920 (Stories) e 1080 x 1350 (carrossel). Devolve avisos de texto que transborda."""
    avisos = []
    url = (pub / f"{P['slug']}.html").resolve().as_uri()
    out = {}
    for fmt, q in (("story", "?cards=1"), ("feed", "?cards=1&formato=feed")):
        page.set_viewport_size({"width": 400, "height": 900})
        page.goto(url + q)
        page.wait_for_timeout(600)
        page.evaluate("document.fonts.ready")
        figs = page.query_selector_all("figure.cd")
        lst = []
        for i, f in enumerate(figs, 1):
            over = f.evaluate("e => { const i = e.querySelector('.cd-in'); return i.scrollHeight - i.clientHeight; }")
            if over > 2: avisos.append(f"AVISO: card {i} ({fmt}) transborda {over}px")
            p = saida / f"{P['slug']}-{fmt}-{i:02d}.png"
            f.screenshot(path=str(p))
            lst.append(p)
        out[fmt] = lst
    leia = P["legenda"] + "\n\n" + "\n".join(f"Card {i}: {c['rotulo']}. {c['alt']}" for i, c in enumerate(P["cards"], 1))
    for fmt, nome in (("feed", "carrossel"), ("story", "stories")):
        with zipfile.ZipFile(pub / "arquivos" / f"{P['zip']}_{nome}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for i, p in enumerate(out[fmt], 1):
                z.write(p, f"{fmt}-{i:02d}.png")
            z.writestr("LEIA-ME.txt", leia)
    return out, avisos


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--site", default="public"); a.add_argument("--so"); a.add_argument("--saida", default="/tmp/explicador")
    a.add_argument("--sem-cards", action="store_true")
    o = a.parse_args()
    pub = Path(o.site); saida = Path(o.saida); saida.mkdir(parents=True, exist_ok=True)
    pags = [P for P in X.PAGINAS if not o.so or P["slug"] == o.so]
    for P in pags:
        pagina(pub, P)
    if o.sem_cards: return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(device_scale_factor=3)
        for P in pags:
            _, av = prints(pub, P, pg, saida)
            for x in av: print(x)
            og(pub, P, b.new_page())
            print(f"ok: /{P['slug']} com {len(P['cards'])} cards")
        b.close()


if __name__ == "__main__":
    main()
