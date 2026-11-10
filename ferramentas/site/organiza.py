"""Organiza o Vigie a Democracia por temas, a partir de catalogo.py, ciencia.py e novidades.json.

Gera:  public/index.html (início), public/tema/<id>.html (um por tema), public/jogar.html, public/cruzar.html
Ajusta em todas as páginas: o menu (Início, Temas, Cruzar, Jogar, Denunciar), a trilha "Você está em" e o bloco "Continue no tema"
(entre marcadores <!--vg-trilha--> e <!--vg-mais-->, então pode rodar quantas vezes quiser), e também vigia.js, vigie.css, sw.js e o manifesto.

Uso:  python3 ferramentas/site/organiza.py --site public [--og]     (--og refaz as imagens de prévia das páginas novas)
Antes, para os dados do cruzador:  python3 ferramentas/site/cruzar_dados.py --dados <pasta do ramo dados> --site public
© 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Feito com auxílio de IA (Claude)."""
import argparse, hashlib, html, json, re, sys
from datetime import date
from pathlib import Path

B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
import catalogo as C
import ciencia as CI

E = html.escape
SITE = C.SITE
MOLDE = B / "molde"
BASE_CSS = (MOLDE / "base.css").read_text(encoding="utf-8")
HOME_CSS_ANTIGO = (MOLDE / "home_antigo.css").read_text(encoding="utf-8")
ACOES = (MOLDE / "acoes.html").read_text(encoding="utf-8")
OLHO = (MOLDE / "olho.svg").read_text(encoding="utf-8")
RODAPE = (MOLDE / "rodape.html").read_text(encoding="utf-8")
SCRIPTS = (MOLDE / "scripts.html").read_text(encoding="utf-8")
NOVIDADES = sorted(json.loads((B / "novidades.json").read_text(encoding="utf-8")), key=lambda n: n["data"], reverse=True)
MESES = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()

ICO = {  # traço simples, 24x24
    "inicio": '<path d="M3 11 12 4l9 7M5 10v10h14V10"/>',
    "temas": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>',
    "cruzar": '<circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/>',
    "jogos": '<rect x="2.5" y="7" width="19" height="11" rx="5"/><path d="M7 10.5v4M5 12.5h4M15.5 11.5h.01M18 13.5h.01"/>',
    "congresso": '<path d="M3 21h18M4 10h16M12 3 4 7h16zM6 10v8M10 10v8M14 10v8M18 10v8M4 18h16"/>',
    "fatos": '<path d="M9 11.5 11.2 14 15.5 9"/><circle cx="12" cy="12" r="9"/>',
    "mente": '<path d="M9 21v-3H7a2 2 0 0 1-2-2v-2.5L3 13l2-3.5A7 7 0 0 1 19 10c0 2.6-1.1 4.6-3 6.1V21"/><path d="M12 13.2c-1.6-1.1-3-2.1-2.7-3.4.3-1.1 1.9-1.3 2.7-.2.8-1.1 2.4-.9 2.7.2.3 1.3-1.1 2.3-2.7 3.4z"/>',
    "denuncia": '<path d="M4 21V4M4 4h12l-2 4 2 4H4"/>',
    "bolso": '<path d="M4 7.5h14.5A1.5 1.5 0 0 1 20 9v9.5a1.5 1.5 0 0 1-1.5 1.5H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M4 7.5 15 4v3.5M16 13.5h1.5"/>',
    "urna": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="m8.5 12.5 2.2 2.2 4.8-4.8M9 7h6"/>',
    "pessoa": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
    "busca": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "telao": '<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 16v4"/>',
    "imprimir": '<path d="M7 9V3h10v6M7 17H4.5A1.5 1.5 0 0 1 3 15.5v-5A1.5 1.5 0 0 1 4.5 9h15a1.5 1.5 0 0 1 1.5 1.5v5a1.5 1.5 0 0 1-1.5 1.5H17"/><rect x="7" y="14" width="10" height="7" rx="1"/>',
    "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "ciencia": '<path d="M9 3h6M10 3v6l-5.5 9.5A1.7 1.7 0 0 0 6 21h12a1.7 1.7 0 0 0 1.5-2.5L14 9V3"/><path d="M7.5 15h9"/>',
    "novo": '<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
}


def ico(k):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICO[k]}</svg>'


def data_br(d, longa=False):
    a, m, dd = d.split("-")
    return f"{int(dd)} de {MESES[int(m) - 1]} de {a}" if longa else f"{dd}/{m}/{a}"


# ------------------------------------------------------------------ peças comuns
NAV = [("inicio", "Início", "/"), ("temas", "Temas", "/#temas"), ("cruzar", "Cruzar", "/cruzar"), ("jogos", "Jogar", "/jogar"), ("denuncia", "Denunciar", "/denuncie")]


def nav(atual):
    lis = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if k == atual else ""}>{ico(k)}<span>{E(n)}</span></a></li>' for k, n, h in NAV)
    return f'<nav class="vg-nav" aria-label="Seções do site"><ul>{lis}</ul></nav>'


def cabecalho(atual, home=False):
    alvo = "#topo" if home else "/"
    return (f'<header class="vg-topo" id="topo"><a class="vg-marca" href="{alvo}" aria-label="Vigie a Democracia, página inicial">{OLHO}<span>Vigie a Democracia</span></a>'
            f'{nav(atual)}{ACOES}</header>')


def rodape(texto, url):
    from urllib.parse import quote
    r = RODAPE
    r = re.sub(r'data-soc-texto="[^"]*"', f'data-soc-texto="{E(texto)}"', r, count=1)
    r = re.sub(r'data-soc-url="[^"]*"', f'data-soc-url="{E(url)}"', r, count=1)
    r = re.sub(r'href="https://wa\.me/\?text=[^"]*"', f'href="https://wa.me/?text={quote(texto + " " + url, safe="")}"', r, count=1)
    return r


CAMINHOS = ("https://wa.me/5524988091268/?text=Ol%C3%A1%2C+tenho+um+problema+de+sa%C3%BAde+relacionado+ao+meu+trabalho+e+gostaria+de+apoio.")


def convite(tag="p"):
    abre = '<aside class="vg-convite" aria-label="Apoio e novidades"><p>' if tag == "aside" else '<p class="vg-convite">'
    fecha = '</p></aside>' if tag == "aside" else '</p>'
    return (f'{abre}Adoeceu por causa do trabalho? O projeto <a href="{CAMINHOS}" target="_blank" rel="noopener">Caminhos do Trabalho (UFF)'
            f'<span class="visually-hidden"> (abre o WhatsApp)</span></a> acolhe pelo WhatsApp (24) 98809-1268. E siga '
            f'<a href="https://instagram.com/brunochapadeiro" target="_blank" rel="noopener">@brunochapadeiro<span class="visually-hidden"> no Instagram (abre outro site)</span></a> para as novidades.{fecha}')


def trilha(passos):
    """passos: [(rótulo, href ou None)]; o último é a página atual."""
    lis = []
    for i, (rot, h) in enumerate(passos):
        if i == len(passos) - 1:
            lis.append(f'<li><span aria-current="page">{E(rot)}</span></li>')
        else:
            lis.append(f'<li><a href="{h}">{E(rot)}</a></li>')
    return f'<!--vg-trilha--><nav class="vg-trilha" aria-label="Você está em"><ol>{"".join(lis)}</ol></nav><!--/vg-trilha-->'


def cores_css():
    linhas = []
    for t in C.TEMAS:
        sel = f'[data-tema="{t["id"]}"]'
        linhas.append(f'{sel} {{ --c:{t["cor"]}; }}')
        linhas.append(f'@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {sel} {{ --c:{t["corEsc"]}; }} }}')
        linhas.append(f':root[data-theme="dark"] {sel} {{ --c:{t["corEsc"]}; }}')
    return "\n".join(linhas) + "\n"


def tema_de(item):
    return C.TEMA[item["tema"]]


def link_attrs(it):
    if it["externo"]:
        return f' href="{E(it["href"])}" target="_blank" rel="noopener"'
    return f' href="{E(it["href"])}"'


def selo_fmt(it):
    t = C.FORMATOS[it["fmt"]] + (" · PDF" if it["pdf"] else "")
    return f'<span class="fmt">{E(t)}</span>'


def cartao(it, com_tema=False, grande=False):
    tm = tema_de(it)
    como = " · ".join(C.COMO[c] for c in it["como"])
    ext = '<span class="visually-hidden"> (abre outro site)</span>' if it["externo"] else ""
    chip = f'<span class="chip-t">{ico(tm["ic"])}{E(tm["curto"])}</span>' if com_tema else ""
    quem = f'<small class="quem">{E(it["quem"])}</small>' if it["quem"] else ""
    return (f'<li class="cartao{" grande" if grande else ""}" data-tema="{tm["id"]}"><a{link_attrs(it)}>'
            f'<span class="topo-c">{selo_fmt(it)}{chip}</span><b>{E(it["nome"])}{ext}</b><span class="d">{E(it["desc"])}</span>'
            f'{f"<span class=como>{E(como)}</span>" if como else ""}{quem}</a></li>')


# ------------------------------------------------------------------ CSS das páginas novas
CSS = r"""
[hidden] { display:none !important; }
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
.wrap.larga { max-width:68rem; gap:0; padding-top:10px; padding-bottom:56px; }
.larga main { display:flex; flex-direction:column; gap:44px; padding-top:18px; }
.larga h2 { font-family:'Lexend', sans-serif; font-size:clamp(1.3rem, 3.4vw, 1.6rem); line-height:1.15; margin:0; letter-spacing:-.01em; }
.sec-cab { display:flex; flex-direction:column; gap:4px; margin-bottom:14px; } .sec-cab p { margin:0; color:var(--suave); }
.sec-cab .mais-l { font-weight:700; }
/* intenções */
.intencoes { list-style:none; margin:0; padding:0; display:grid; gap:12px; grid-template-columns:minmax(0, 1fr); }
@media (min-width: 36rem) { .intencoes { grid-template-columns:repeat(2, minmax(0, 1fr)); } }
@media (min-width: 60rem) { .intencoes { grid-template-columns:repeat(3, minmax(0, 1fr)); } }
.intencao { position:relative; background:var(--cartao); border:1px solid var(--linha); border-radius:20px; padding:16px; display:flex; gap:14px; align-items:center; }
.intencao:hover { border-color:var(--c); }
.intencao .ic-a { width:48px; height:48px; border-radius:15px; flex-shrink:0; display:flex; align-items:center; justify-content:center; background:var(--c); color:#fff; }
.intencao .ic-a svg { width:26px; height:26px; }
.intencao a { font-family:'Lexend', sans-serif; font-weight:700; font-size:1.05rem; line-height:1.2; color:var(--tinta); text-decoration:none; display:block; }
.intencao a::after { content:""; position:absolute; inset:0; border-radius:20px; }
.intencao a:focus-visible { outline:none; } .intencao:has(a:focus-visible) { outline:4px solid var(--azul); outline-offset:3px; }
.intencao p { margin:2px 0 0; font-size:.92rem; line-height:1.35; color:var(--suave); }
/* grade de temas */
.temas-g { list-style:none; margin:0; padding:0; display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(min(100%, 19.5rem), 1fr)); }
.tema-c { background:var(--cartao); border:1px solid var(--linha); border-top:6px solid var(--c); border-radius:20px; padding:18px; display:flex; flex-direction:column; gap:12px; }
.tema-c .tema-cab { display:flex; gap:12px; align-items:flex-start; }
.ic-a { width:44px; height:44px; border-radius:14px; flex-shrink:0; display:flex; align-items:center; justify-content:center; background:var(--c); color:#fff; }
.ic-a svg { width:24px; height:24px; }
.tema-c h3 { margin:0; font-family:'Lexend', sans-serif; font-size:1.25rem; line-height:1.15; }
.tema-c h3 a { color:var(--tinta); text-decoration:none; } .tema-c h3 a:hover { text-decoration:underline; }
.tema-c .tema-cab p { margin:4px 0 0; color:var(--suave); font-size:.94rem; line-height:1.4; }
.tema-c .visto { margin-left:auto; flex-shrink:0; font-size:.78rem; font-weight:700; color:var(--c); border:2px solid var(--c); border-radius:999px; padding:1px 8px; }
.tema-c ul { list-style:none; margin:0; padding:0; }
.tema-c li { border-top:1px solid var(--linha); }
.tema-c li a { display:flex; justify-content:space-between; gap:10px; align-items:center; padding:9px 2px; min-height:44px; font-weight:700; text-decoration:none; }
.tema-c li a .f { flex-shrink:0; font-size:.78rem; font-weight:700; color:var(--suave); }
.tema-c .ver { margin-top:auto; display:flex; align-items:center; justify-content:center; gap:8px; min-height:48px; border-radius:999px; background:var(--c); color:#fff; font-weight:700; text-decoration:none; }
.tema-c .ver svg { width:20px; height:20px; }
/* cruze (faixa) */
.faixa { background:#17191E; color:#FBF8F1; border-radius:22px; padding:22px clamp(16px, 4vw, 32px); display:grid; gap:16px; }
@media (min-width: 52rem) { .faixa { grid-template-columns:minmax(0, 1.2fr) minmax(0, 1fr); align-items:center; } }
.faixa h2 { color:#FBF8F1; } .faixa p { margin:0; color:#E6E3DA; } .faixa .kicker { color:#FFE58F; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.85rem; }
.faixa ul { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; }
.faixa li a { display:flex; align-items:center; gap:10px; min-height:52px; padding:8px 14px; border-radius:14px; background:rgba(251,248,241,.08); border:1px solid #3A3D45; color:#FBF8F1; text-decoration:none; font-weight:700; }
.faixa li a:hover { background:rgba(251,248,241,.16); } .faixa li a svg { width:22px; height:22px; flex-shrink:0; color:#FFE58F; }
.faixa :focus-visible { outline-color:#FFE58F; }
.faixa .btn { border-color:#FFE58F; background:#FFE58F; color:#17191E; justify-self:start; }
/* novidades */
.novas { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; }
.novas li { border-top:1px solid var(--linha); padding:12px 0; display:grid; gap:2px 14px; grid-template-columns:auto minmax(0, 1fr); }
.novas li:last-child { border-bottom:1px solid var(--linha); }
.novas time { grid-row:span 3; font-family:'Lexend', sans-serif; font-weight:700; font-size:.95rem; color:var(--suave); min-width:3.3em; padding-top:2px; }
.novas a { font-weight:700; font-size:1.05rem; } .novas p { margin:0; color:var(--suave); font-size:.95rem; }
.chip-t { display:inline-flex; align-items:center; gap:5px; font-size:.78rem; font-weight:700; color:var(--c); }
.chip-t svg { width:15px; height:15px; }
/* cartões de itens */
.cartoes { list-style:none; margin:0; padding:0; display:grid; gap:12px; grid-template-columns:repeat(auto-fill, minmax(min(100%, 19rem), 1fr)); }
.cartao a { height:100%; display:flex; flex-direction:column; gap:5px; padding:14px 16px; min-height:56px; background:var(--cartao); border:1px solid var(--linha); border-left:6px solid var(--c);
  border-radius:16px; text-decoration:none; color:var(--tinta); }
.cartao a:hover { border-color:var(--c); }
.cartao .topo-c { display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; }
.cartao .fmt { font-size:.74rem; font-weight:700; letter-spacing:.02em; padding:2px 8px; border-radius:6px; background:var(--tinta); color:var(--papel); }
.cartao b { color:var(--azul); font-size:1.06rem; line-height:1.25; }
.cartao .d { font-size:.93rem; color:var(--suave); line-height:1.4; }
.cartao .como { font-size:.84rem; font-weight:700; color:var(--c); }
.cartao .quem { font-size:.85rem; font-style:italic; color:var(--suave); }
.cartao.grande a { padding:18px; border-left-width:8px; } .cartao.grande b { font-family:'Lexend', sans-serif; font-size:1.2rem; color:var(--tinta); }
/* página de tema */
.tema-topo { display:flex; flex-direction:column; gap:12px; padding-top:6px; }
.tema-topo .linha { display:flex; gap:16px; align-items:center; }
.tema-topo .ic-a { width:64px; height:64px; border-radius:20px; } .tema-topo .ic-a svg { width:36px; height:36px; }
.tema-topo h1 { font-size:clamp(2rem, 6vw, 3.2rem); }
.tema-topo .sub { color:var(--suave); max-width:44rem; font-size:clamp(1.05rem, 2.4vw, 1.2rem); }
.tema-topo .meta { margin:0; font-size:.95rem; color:var(--suave); font-weight:700; }
.indice { list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:8px; }
.indice a { display:inline-flex; align-items:center; gap:6px; min-height:44px; padding:6px 14px; border-radius:999px; border:2px solid var(--linha); background:var(--cartao); font-weight:700; text-decoration:none; color:var(--tinta); }
.indice a:hover { border-color:var(--c, var(--tinta)); } .indice svg { width:18px; height:18px; color:var(--c, var(--suave)); }
.ciencia-l { list-style:none; margin:0; padding:0; display:grid; gap:12px; grid-template-columns:repeat(auto-fill, minmax(min(100%, 20rem), 1fr)); }
.ciencia-l li { background:var(--cartao); border:1px solid var(--linha); border-radius:16px; padding:14px 16px; display:flex; flex-direction:column; gap:6px; }
.ciencia-l .tipo-e { margin:0; font-size:.8rem; font-weight:700; letter-spacing:.03em; text-transform:uppercase; color:var(--suave); }
.ciencia-l p { margin:0; } .ciencia-l .ref { font-size:.88rem; color:var(--suave); overflow-wrap:anywhere; }
.nota { margin:10px 0 0; font-size:.92rem; color:var(--suave); }
/* ronda com seis postos */
.carimbos.seis { grid-template-columns:repeat(3, minmax(0, 1fr)); row-gap:14px; }
@media (min-width: 40rem) { .carimbos.seis { grid-template-columns:repeat(6, minmax(0, 1fr)); } }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) :is(.ic-a, .tema-c .ver, .carimbos li.feito .selo-r) { color:#17191E; } }
:root[data-theme="dark"] :is(.ic-a, .tema-c .ver, .carimbos li.feito .selo-r) { color:#17191E; }
html.a11y-contraste .faixa, html.a11y-contraste .faixa * { background-color:#000 !important; }
@media print { .faixa, .busca, .app, .ronda, .indice { display:none !important; } .cartao a { border:1px solid #999; } }
"""

CSS_CRUZAR = r"""

.ce { display:flex; flex-direction:column; gap:12px; scroll-margin-top:12px; }
.ce-ex-t { margin:0; font-weight:700; }
.ce-ex { list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:8px; }
.ce-ex .btn { min-height:48px; }
.ce-form { grid-template-columns:repeat(auto-fill, minmax(min(100%, 16rem), 1fr)); }
.ce-form .btn { grid-column:auto; }
.ce-card h3 { font-size:clamp(1.15rem, 3vw, 1.35rem); } .ce-card h4 { margin:8px 0 0; font-family:'Lexend', sans-serif; font-size:1rem; }
.ce-fig { margin:0; } .ce-fig figcaption { font-size:.9rem; color:var(--suave); margin-top:4px; }
.ce-svg { width:100%; height:auto; display:block; background:var(--papel); border:1px solid var(--linha); border-radius:14px; }
.ce-grade { stroke:var(--linha); stroke-width:1; }
.ce-eixo { fill:var(--suave); font-size:12px; font-family:'Atkinson Hyperlegible', sans-serif; }
.ce-rot { fill:var(--tinta); font-size:13px; font-weight:700; font-family:'Atkinson Hyperlegible', sans-serif; }
.ce-pt circle { fill:var(--azul); stroke:var(--papel); stroke-width:1.5; }
.ce-pt text { fill:var(--papel); font-size:9.5px; font-weight:700; font-family:'Atkinson Hyperlegible', sans-serif; pointer-events:none; }
.ce-pt.ce-sel circle { fill:var(--verm); stroke:var(--tinta); stroke-width:3; } .ce-pt.ce-sel text { font-size:11px; }
.ce-br rect { fill:var(--tinta); stroke:var(--papel); stroke-width:2; } .ce-br text { paint-order:stroke; stroke:var(--papel); stroke-width:4px; stroke-linejoin:round; fill:var(--tinta); font-size:12px; font-weight:700; font-family:'Atkinson Hyperlegible', sans-serif; }
.ce-barras { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:4px; }
.ce-barras li { display:grid; grid-template-columns:minmax(6.5rem, 9.5rem) minmax(0, 1fr) auto; gap:8px; align-items:center; padding:2px 6px; border-radius:8px; }
.ce-barras li.ce-sel { background:var(--papel); outline:2px solid var(--verm); }
.ce-uf { font-size:.92rem; overflow-wrap:anywhere; } .ce-barras b { font-size:.92rem; white-space:nowrap; }
.ce-trilho { height:14px; border-radius:7px; background:var(--linha); overflow:hidden; } .ce-barra { display:block; height:100%; background:var(--azul); border-radius:7px; }
.ce-sel .ce-barra { background:var(--verm); }
.ce-tab summary { cursor:pointer; font-weight:700; min-height:44px; display:flex; align-items:center; }
.ce-rolar { overflow-x:auto; max-width:100%; }
.ce-tab table { border-collapse:collapse; width:100%; font-size:.95rem; }
.ce-tab th, .ce-tab td { padding:6px 8px; border-bottom:1px solid var(--linha); text-align:left; }
.ce-tab td { text-align:right; white-space:nowrap; } .ce-tab thead th:not(:first-child) { text-align:right; }
.ce-tab tr.ce-sel { background:var(--papel); outline:2px solid var(--verm); } .ce-tbr th, .ce-tbr td { font-weight:700; }
.ce-ord { font:inherit; font-weight:700; background:none; border:0; color:var(--azul); cursor:pointer; min-height:44px; padding:0; text-align:inherit; text-decoration:underline; }
th[aria-sort="ascending"] .ce-ord::after { content:" ▲"; } th[aria-sort="descending"] .ce-ord::after { content:" ▼"; }
.ce-fontes { margin:0; padding-left:1.1em; font-size:.92rem; overflow-wrap:anywhere; } .ce-fontes li + li { margin-top:4px; }
.cz-form { background:var(--cartao); border:2px solid var(--linha); border-radius:20px; padding:16px clamp(14px, 3vw, 22px); display:grid; gap:14px;
  grid-template-columns:repeat(auto-fill, minmax(min(100%, 14rem), 1fr)); align-items:end; }
.cz-form label, .cz-form legend { font-weight:700; display:block; margin-bottom:4px; }
.cz-form select { font:inherit; width:100%; min-height:52px; padding:6px 12px; border-radius:14px; border:2px solid var(--linha); background:var(--papel); color:var(--tinta); }
.cz-form select:focus { border-color:var(--tinta); }
.cz-form fieldset { border:0; margin:0; padding:0; min-width:0; }
.cz-seg { display:flex; gap:4px; flex-wrap:wrap; }
.cz-seg label { margin:0; display:inline-flex; align-items:center; gap:6px; min-height:48px; padding:4px 14px; border-radius:999px; border:2px solid var(--linha); background:var(--papel); font-weight:700; cursor:pointer; }
.cz-seg input { width:20px; height:20px; accent-color:var(--azul); }
.cz-seg label:has(input:checked) { border-color:var(--tinta); background:var(--tinta); color:var(--papel); }
.cz-seg label:has(input:focus-visible) { outline:4px solid var(--azul); outline-offset:2px; }
.cz-eu { grid-column:1 / -1; display:flex; gap:10px; align-items:flex-start; }
.cz-eu input { width:24px; height:24px; margin-top:2px; accent-color:var(--azul); flex-shrink:0; }
.cz-eu label { margin:0; } .cz-eu small { display:block; font-weight:400; color:var(--suave); }
.cz-form .btn, .cz-form fieldset { grid-column:1 / -1; justify-self:start; }
#cz-res { display:grid; gap:16px; grid-template-columns:minmax(0, 1fr); }
@media (min-width: 60rem) { #cz-res { grid-template-columns:repeat(2, minmax(0, 1fr)); } #cz-res > .cz-novo, #cz-res > .cz-largo { grid-column:1 / -1; }
  .cz-votos { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); column-gap:28px; } }
.cz-card { background:var(--cartao); border:1px solid var(--linha); border-radius:20px; padding:18px clamp(14px, 3vw, 22px); display:flex; flex-direction:column; gap:10px; min-width:0; }
.cz-card h2 { font-size:clamp(1.2rem, 3vw, 1.4rem); } .cz-card h3 { margin:6px 0 0; font-size:1.02rem; font-family:'Lexend', sans-serif; }
.cz-card p { margin:0; }
.cz-novo { border:2px solid var(--tinta); }
.cz-kicker { font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.82rem; color:var(--verm); }
.cz-num { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 10px; }
.cz-num b { font-family:'Lexend', sans-serif; font-weight:800; font-size:clamp(3rem, 12vw, 5.2rem); line-height:1; letter-spacing:-.03em; }
.cz-num span { font-family:'Lexend', sans-serif; font-weight:700; font-size:clamp(1.05rem, 3vw, 1.35rem); }
.cz-frase { font-size:1.08rem; }
.cz-nota, .cz-fonte { font-size:.9rem; color:var(--suave); overflow-wrap:anywhere; }
.cz-af { font-style:italic; color:var(--suave); font-size:.95rem; }
.cz-votos { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; }
.cz-votos > li { border-top:1px solid var(--linha); padding:12px 0; display:flex; flex-direction:column; gap:6px; }
.cz-barra { display:flex; height:22px; border-radius:6px; overflow:hidden; background:var(--linha); }
.cz-barra span { display:block; height:100%; }
.cz-S { background:#1F6F3A; } .cz-N { background:#B3261E; } .cz-O { background:#B07A12; } .cz-F { background:repeating-linear-gradient(45deg, #8A8D96 0 4px, #B9BCC3 4px 8px); }
.cz-uL { background:#C9281D; } .cz-uF { background:#1F4E8C; }
.cz-urna { height:30px; }
.cz-leg { display:flex; flex-wrap:wrap; gap:4px 14px; font-size:.9rem; }
.cz-l::before { content:""; display:inline-block; width:.8em; height:.8em; border-radius:3px; margin-right:5px; vertical-align:-.05em; }
.cz-lS::before { background:#1F6F3A; } .cz-lN::before { background:#B3261E; } .cz-lO::before { background:#B07A12; } .cz-lF::before { background:#8A8D96; }
.cz-luL::before { background:#C9281D; } .cz-luF::before { background:#1F4E8C; }
.cz-cruza { border-top:2px dashed var(--linha); padding-top:10px; }
.cz-cruza ul { margin:6px 0; padding-left:1.2em; }
details.cz-o-que summary, details.cz-part summary { cursor:pointer; font-weight:700; color:var(--azul); min-height:44px; display:flex; align-items:center; }
.cz-tab-w { overflow-x:auto; } .cz-tab { border-collapse:collapse; font-size:.95rem; min-width:16rem; }
.cz-tab th, .cz-tab td { text-align:left; padding:6px 12px 6px 0; border-bottom:1px solid var(--linha); } .cz-tab td { font-variant-numeric:tabular-nums; }
.cz-dl { margin:0; display:grid; gap:10px; grid-template-columns:repeat(auto-fill, minmax(min(100%, 10rem), 1fr)); }
.cz-dl div { background:var(--papel); border-radius:14px; padding:10px 12px; }
.cz-dl dt { font-size:.88rem; color:var(--suave); font-weight:700; } .cz-dl dd { margin:2px 0 0; font-family:'Lexend', sans-serif; font-weight:800; font-size:1.6rem; }
.cz-dl small { display:block; font-family:'Atkinson Hyperlegible', sans-serif; font-weight:400; font-size:.85rem; color:var(--suave); }
.cz-chips { list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:6px; }
.cz-chips li { padding:3px 10px; border-radius:999px; border:1px solid var(--linha); background:var(--papel); font-size:.92rem; }
.cz-chips li.on { border:2px solid var(--tinta); background:#FFE58F; color:#17191E; }
.cz-sci { list-style:none; margin:0; padding:0; display:grid; gap:14px 22px; grid-template-columns:repeat(auto-fill, minmax(min(100%, 22rem), 1fr)); }
.cz-sci li { border-left:4px solid var(--azul); padding-left:12px; display:flex; flex-direction:column; gap:4px; }
.cz-tipo { font-size:.8rem; font-weight:700; letter-spacing:.03em; text-transform:uppercase; color:var(--suave); }
.cz-links { list-style:none; margin:0; padding:0; }
.cz-links li { border-top:1px solid var(--linha); } .cz-links a { display:flex; gap:10px; align-items:center; min-height:48px; padding:6px 0; text-decoration:none; }
.cz-links .fmt { flex-shrink:0; font-size:.72rem; font-weight:700; padding:2px 7px; border-radius:6px; background:var(--tinta); color:var(--papel); }
.cz-comp .acoes { margin:0; } .cz-st { font-weight:700; } .cz-st:empty { display:none; }
.cz-aviso { font-weight:700; } .cz-aviso:empty { display:none; }
.cz-como { margin:0; padding-left:1.2em; display:flex; flex-direction:column; gap:4px; }
html.a11y-contraste .cz-barra span { border-right:2px solid #000; }
@media print { .cz-form, .cz-comp { display:none !important; } }
"""


def doc(slug, titulo, desc, og, corpo, css="", js="", atual="temas", home=False, cab_extra="", wrap="larga", texto_soc=None):
    url = SITE + (slug if slug != "index" else "")
    og_url = SITE + og
    head_js = ("<script>/* endereços antigos dos Games Vira-Voto (/#j5, /#materiais, /#placar) agora ficam em /jogos */\n"
               "(function () { var h = location.hash; if (/^#(j\\d{1,2}|materiais|conversar|placar|inicio)$/.test(h)) location.replace('jogos' + h); })();</script>\n") if home else ""
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(titulo)}</title>
{head_js}<meta name="description" content="{E(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Vigie a Democracia">
<meta property="og:title" content="{E(titulo)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og_url}"><meta property="og:image:secure_url" content="{og_url}">
<meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{E(titulo)}, de Prof. Bruno Chapadeiro">
<meta property="og:locale" content="pt_BR"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/icone.svg" type="image/svg+xml">
<style>
{BASE_CSS}
{HOME_CSS_ANTIGO if home else ""}
{CSS}
{css}
{cores_css()}</style>
<link rel="stylesheet" href="/vigie.css"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#17191E"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta name="apple-mobile-web-app-title" content="Vigie">
</head><body class="vg-com-nav">
<div class="wrap {wrap}{' home' if home else ''}">
  <a class="pular" href="#conteudo">Pular para o conteúdo</a>
  {cabecalho(atual, home)}
  {cab_extra}
  <main id="conteudo" data-a11y-ler>
{corpo}
  </main>
  {convite("aside")}
  {rodape(texto_soc or (titulo + ": de graça, com fonte, no Vigie a Democracia."), url)}
</div>
{SCRIPTS}
{js}
<script src="/vigia.js" defer></script>
</body></html>
"""


# ------------------------------------------------------------------ busca e ronda
def mapa_ronda():
    m = {}
    for slug, iid in C.PAGINA_ITEM.items():
        m[slug] = C.ITENS[iid]["tema"]
    for slug, iid in C.ATALHOS.items():
        m.setdefault(slug, C.ITENS[iid]["tema"])
    for t in C.TEMAS:
        m["tema/" + t["id"]] = t["id"]
    return m


def indice_busca():
    idx = [dict(n=t["nome"], d=t["frase"], t="tema " + t["curto"], h="/tema/" + t["id"], p="Tema") for t in C.TEMAS]
    idx.append(dict(n="Jogar", d="Todos os jogos, por jeito de jogar: telão, grupo, celular e papel.", t="jogos telão grupo papel imprimir", h="/jogar", p="Jogar"))
    idx.append(dict(n="Acessibilidade", d="Letra maior, contraste, espaçamento, leitura em voz alta e Libras.", t="acessibilidade libras contraste leitor de tela", h="/acessibilidade", p="Ajuda"))
    for it in C.I:
        idx.append(dict(n=it["nome"], d=it["desc"], t=it["tags"] + " " + C.FORMATOS[it["fmt"]], h=it["href"], p=tema_de(it)["nome"]))
    vistos, saida = set(), []
    for x in idx:
        if x["h"] not in vistos:
            vistos.add(x["h"]); saida.append(x)
    return saida


# ------------------------------------------------------------------ página inicial
HOME_JS = r"""<script>
(function () {
  var $ = function (s) { return document.querySelector(s); }, $$ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };
  var POSTOS = __POSTOS__, MAPA = __MAPA__, NIVEIS = [[0, 'Primeiro olhar'], [3, 'Olho aberto'], [6, 'Sentinela'], [10, 'Fiscal da democracia']], IDX = __IDX__;
  function le(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function dataBR(d) { return d ? d.slice(8, 10) + '/' + d.slice(5, 7) : ''; }
  function ronda() {
    var vis = le('vigie-visitas') || {}, paginas = Object.keys(vis).filter(function (s) { return s !== 'inicio'; }), feitos = {};
    paginas.forEach(function (s) { var p = MAPA[s]; if (p && (!feitos[p] || vis[s] < feitos[p])) feitos[p] = vis[s]; });
    var n = Object.keys(feitos).length, nivel = NIVEIS[0][1];
    NIVEIS.forEach(function (x) { if (paginas.length >= x[0]) nivel = x[1]; });
    if (n === POSTOS.length && paginas.length >= 10) nivel = 'Guardiã e guardião da democracia';
    $('#r-nivel').textContent = nivel;
    POSTOS.forEach(function (p) {
      var ok = !!feitos[p.id], li = $('#r-' + p.id), card = $('.tema-c[data-tema="' + p.id + '"] .visto');
      li.classList.toggle('feito', ok); li.querySelector('.st').textContent = ok ? ', carimbado em ' + dataBR(feitos[p.id]) : ', falta visitar';
      if (card) card.hidden = !ok;
    });
    var falta = POSTOS.filter(function (p) { return !feitos[p.id]; })[0], t = $('#r-txt');
    t.replaceChildren(document.createTextNode(n + (n === 1 ? ' tema carimbado' : ' temas carimbados') + ' de ' + POSTOS.length + ', ' + paginas.length + (paginas.length === 1 ? ' página aberta. ' : ' páginas abertas. ')));
    if (falta) { var a = document.createElement('a'); a.href = '/tema/' + falta.id; a.textContent = 'Próximo tema: ' + falta.nome; t.append(a); }
    else t.append('Ronda completa. Volte sempre: o site muda toda semana.');
    $('#r-zera').hidden = !paginas.length;
  }
  $('#r-zera').addEventListener('click', function () { try { localStorage.removeItem('vigie-visitas'); } catch (e) {} ronda(); $('#r-nivel').focus(); });
  ronda(); addEventListener('pageshow', ronda);
  var sem = function (s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); };
  var T = IDX.map(function (x) { return sem([x.n, x.d, x.t, x.p].join(' ')); });
  var q = $('#q'), out = $('#achados'), cont = $('#achados-n');
  function busca() {
    var v = sem(q.value.trim()); out.replaceChildren(); cont.textContent = '';
    if (v.length < 2) return;
    var ps = v.split(/\s+/), L = IDX.filter(function (x, k) { return ps.every(function (p) { return T[k].indexOf(p) >= 0; }); }).slice(0, 8);
    cont.textContent = L.length ? (L.length === 1 ? '1 resultado' : L.length + ' resultados') : 'Nada encontrado. Tente outra palavra, como deputado, boato, assédio, NR-1 ou 6x1.';
    L.forEach(function (x) { var li = document.createElement('li'), a = document.createElement('a'), b = document.createElement('b'), sm = document.createElement('small');
      a.href = x.h; b.textContent = x.n; sm.textContent = x.p + '. ' + x.d; a.append(b, sm); li.append(a); out.append(li); });
  }
  q.addEventListener('input', busca);
  q.addEventListener('keydown', function (e) { if (e.key === 'Escape') { q.value = ''; busca(); } });
  $('#f-busca').addEventListener('submit', function (e) { e.preventDefault(); var a = out.querySelector('a'); if (a) a.focus(); });
  if ('IntersectionObserver' in window) {
    var alvo = { topo: '/', temas: '/#temas' };
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (!e.isIntersecting) return; var a = $('.vg-nav a[href="' + alvo[e.target.id] + '"]'); if (!a) return;
      $$('.vg-nav a').forEach(function (x) { x.removeAttribute('aria-current'); }); a.setAttribute('aria-current', 'page'); }); }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(alvo).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }
  var pedido = null, bt = $('#instalar'), ios = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  var instalado = matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  if (instalado) $('#app').hidden = true; else if (ios) $('#app-ios').hidden = false; else $('#app-outro').hidden = false;
  addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); pedido = e; bt.hidden = false; $('#app-outro').hidden = true; });
  bt.addEventListener('click', function () { if (!pedido) return; pedido.prompt(); pedido.userChoice.catch(function () { return null; }).then(function (r) { pedido = null; bt.hidden = true;
    $('#app-txt').textContent = r && r.outcome === 'accepted' ? 'Pronto: o Vigie está na sua tela inicial.' : 'Tudo bem. Se mudar de ideia, use o menu do navegador e escolha Instalar app.'; }); });
  addEventListener('appinstalled', function () { bt.hidden = true; $('#app-txt').textContent = 'Pronto: o Vigie está na sua tela inicial.'; });
})();
</script>"""


def bloco_novidades(lista, titulo_id="nv-t", titulo="Novidades", sub=None, limite=6):
    if not lista:
        return ""
    lis = []
    for n in lista[:limite]:
        tm = C.TEMA[n["tema"]]
        lis.append(f'<li data-tema="{tm["id"]}"><time datetime="{n["data"]}">{n["data"][8:10]}/{n["data"][5:7]}</time>'
                   f'<span class="chip-t">{ico(tm["ic"])}{E(tm["nome"])}</span><a href="{E(n["href"])}">{E(n["titulo"])}</a><p>{E(n["desc"])}</p></li>')
    sub = sub or "O que entrou ou mudou no site, com a data. O Placar da semana sai às segundas, depois de conferido."
    return (f'<section id="novidades" aria-labelledby="{titulo_id}"><div class="sec-cab"><h2 id="{titulo_id}">{E(titulo)}</h2><p>{E(sub)}</p></div>'
            f'<ul class="novas">{"".join(lis)}</ul></section>')


def home():
    intenc = "".join(
        f'<li class="intencao" data-tema="{x["tema"]}"><span class="ic-a">{ico(x["ic"])}</span><div><a href="{x["href"]}">{E(x["t"])}</a><p>{E(x["d"])}</p></div></li>'
        for x in C.INTENCOES)
    temas = []
    for t in C.TEMAS:
        its = C.itens_do_tema(t["id"])
        top = [x for x in its if x["dest"] and x["tema"] == t["id"]][:3]
        lis = "".join(f'<li><a{link_attrs(x)}><span>{E(x["nome"])}</span><span class="f">{E(C.FORMATOS[x["fmt"]])}</span></a></li>' for x in top)
        temas.append(f'<li class="tema-c" data-tema="{t["id"]}"><div class="tema-cab"><span class="ic-a">{ico(t["ic"])}</span><div><h3><a href="/tema/{t["id"]}">{E(t["nome"])}</a></h3>'
                     f'<p>{E(t["frase"])}</p></div><span class="visto" hidden>Carimbado</span></div><ul>{lis}</ul>'
                     f'<a class="ver" href="/tema/{t["id"]}">Ver os {len(its)} itens<span class="visually-hidden"> de {E(t["nome"])}</span>{ico("seta")}</a></li>')
    carimbos = "".join(f'<li id="r-{t["id"]}" data-tema="{t["id"]}"><a href="/tema/{t["id"]}"><span class="selo-r">{ico(t["ic"])}</span><span>{E(t["curto"])}</span>'
                       f'<span class="st visually-hidden"></span></a></li>' for t in C.TEMAS)
    participe = "".join(cartao(x, com_tema=True) for x in C.I if x["fmt"] in ("campanha", "canal"))
    exemplos = [("/cruzar?uf=RJ&assunto=Trabalho", "Rio de Janeiro × fim da escala 6x1"), ("/cruzar?uf=BR&assunto=Terra%20e%20ambiente&partido=PL", "PL × terra e meio ambiente"),
                ("/cruzar?uf=BA&assunto=Democracia&eu=1", "Seu teste × a bancada da Bahia")]
    corpo = f"""  <section class="hero" aria-labelledby="h-wm">
    <h1 class="wm" id="h-wm">{OLHO}Vigie a Democracia</h1>
    <p class="sub">Fatos com fonte, os votos do Congresso, canais de denúncia e jogos para acompanhar a política o ano inteiro, organizados em seis temas. De graça e sem cadastro.</p>
    <form class="busca" id="f-busca" role="search"><label for="q">Buscar no site</label>{ico("busca")}
      <input id="q" type="search" autocomplete="off" placeholder="Ex.: deputado, NR-1, boato, 6x1" aria-describedby="achados-n"></form>
    <p class="achados-n" id="achados-n" aria-live="polite"></p>
    <ul class="achados" id="achados"></ul>
  </section>
  <section aria-labelledby="in-t"><div class="sec-cab"><h2 id="in-t">O que você quer fazer?</h2></div><ul class="intencoes">{intenc}</ul></section>
  <section id="temas" aria-labelledby="tm-t"><div class="sec-cab"><h2 id="tm-t">Temas</h2><p>Cada tema reúne páginas, jogos, dados, materiais para imprimir e o que diz a ciência, com a fonte de cada informação.</p></div>
    <ul class="temas-g">{"".join(temas)}</ul></section>
  <section class="faixa" aria-labelledby="cz-h"><div><p class="kicker">Novo</p><h2 id="cz-h">Cruze os dados</h2>
    <p>Escolha o estado, o assunto e o partido. O site junta os votos da Câmara e do Senado, a urna do TSE, os eleitos de 2026, as suas respostas do teste e estudos científicos, e mostra um dado novo, com a fonte, pronto para postar.</p>
    <p><a class="btn" href="/cruzar">Cruzar agora</a></p></div>
    <ul aria-label="Exemplos de cruzamento">{"".join(f'<li><a href="{E(h)}">{ico("cruzar")}{E(t)}</a></li>' for h, t in exemplos)}</ul></section>
  {bloco_novidades(NOVIDADES)}
  <section class="ronda" aria-labelledby="r-t">
    <h2 id="r-t">Sua ronda</h2>
    <p>Quem vigia passa por todos os temas. Cada tema ganha um carimbo quando você abre uma página dele. Fica guardado só neste aparelho.</p>
    <p class="nivel" id="r-nivel" tabindex="-1">Primeiro olhar</p>
    <ol class="carimbos seis" aria-label="Temas da ronda">{carimbos}</ol>
    <div class="rodape-r"><p id="r-txt" aria-live="polite"></p><button type="button" class="zera" id="r-zera" hidden>Zerar a ronda</button></div>
  </section>
  <section id="participe" aria-labelledby="pt-t"><div class="sec-cab"><h2 id="pt-t">Participe</h2><p>Campanhas e canais de mobilização de fora do site. Não são órgãos públicos: dizemos quem organiza.</p></div>
    <ul class="cartoes">{participe}</ul></section>
  <section class="app" id="app" aria-labelledby="app-t">
    <div class="app-cab">{OLHO}<h2 id="app-t">Tenha o Vigie no celular</h2></div>
    <p id="app-txt">Instale como aplicativo: abre direto da tela inicial, sem loja e sem cadastro, e as páginas que você já viu funcionam até sem internet.</p>
    <button type="button" class="btn forte" id="instalar" hidden>Instalar o app</button>
    <p id="app-ios" hidden>No iPhone ou iPad, abra no Safari, toque em Compartilhar (o quadrado com a seta para cima) e depois em Adicionar à Tela de Início.</p>
    <p id="app-outro" hidden>No Android, abra no Chrome, toque no menu de três pontos e escolha Instalar app. No computador, use o ícone de instalar na barra de endereço.</p>
  </section>"""
    js = (HOME_JS.replace("__POSTOS__", json.dumps([dict(id=t["id"], nome=t["nome"]) for t in C.TEMAS], ensure_ascii=False))
          .replace("__MAPA__", json.dumps(mapa_ronda(), ensure_ascii=False))
          .replace("__IDX__", json.dumps(indice_busca(), ensure_ascii=False).replace("</", "<\\/")))
    return doc("index", "Vigie a Democracia",
               "Fatos com fonte, os votos do Congresso, canais de denúncia, jogos e o cruzador de dados, em seis temas. De graça e sem cadastro.",
               "og-vigie.png", corpo, js=js, atual="inicio", home=True, texto_soc="Vigie a Democracia: fatos com fonte, os votos do Congresso, canais de denúncia e jogos. De graça:")


# ------------------------------------------------------------------ páginas de tema
GRUPOS = [("comecar", "Comece por aqui", None), ("jogos", "Jogos, testes e calculadoras", ("jogo", "teste", "calc")),
          ("dados", "Dados e ferramentas", ("dados", "ferramenta")), ("ler", "Para ler, com fonte", ("leitura",)),
          ("imprimir", "Para imprimir", ("imprimir",)), ("participe", "Participe", ("campanha", "canal"))]
ASSUNTO_DO_TEMA = {"congresso": "Democracia", "fatos": "Redes", "trabalho": "Trabalho", "direitos": "Direitos", "bolso": "Impostos", "eleicoes": None}


def estudos_do_tema(t):
    vistos, L = set(), []
    for a in t["assuntos"]:
        for e in CI.do_assunto(a):
            if e["id"] not in vistos:
                vistos.add(e["id"]); L.append(e)
    return L


def outros_cz(asu):
    L = [x for x in CI.ASSUNTOS if x != asu][:3]
    return "".join(f'<li><a href="/cruzar?assunto={E(x)}">{ico("cruzar")}{E(x)}</a></li>' for x in L)


def pagina_tema(t):
    its = C.itens_do_tema(t["id"])
    dest = [x for x in its if x["dest"] and x["tema"] == t["id"]]
    secoes, indice = [], []
    for gid, gnome, fmts in GRUPOS:
        L = dest if gid == "comecar" else [x for x in its if x["fmt"] in fmts and x not in dest]
        if not L:
            continue
        indice.append(f'<li><a href="#{gid}">{E(gnome)} <span class="visually-hidden">({len(L)})</span></a></li>')
        secoes.append(f'<section id="{gid}" aria-labelledby="{gid}-t"><div class="sec-cab"><h2 id="{gid}-t">{E(gnome)}</h2></div>'
                      f'<ul class="cartoes">{"".join(cartao(x, com_tema=x["tema"] != t["id"], grande=gid == "comecar") for x in L)}</ul></section>')
    asu = ASSUNTO_DO_TEMA[t["id"]]
    cz = (f'<section class="faixa" aria-labelledby="cz-h"><div><p class="kicker">Cruze os dados</p><h2 id="cz-h">{E(t["pergunta"])}</h2>'
          f'<p>Veja como votou a bancada do seu estado sobre {E(asu.lower() if asu else "o tema")}, o que deu a urna e o que dizem os estudos, num card pronto para postar.</p>'
          f'<p><a class="btn" href="/cruzar?assunto={E(asu)}">Cruzar {E(asu.lower())} com o seu estado</a></p></div>'
          f'<ul aria-label="Outros cruzamentos">{outros_cz(asu)}</ul></section>') if asu else \
         (f'<section class="faixa" aria-labelledby="cz-h"><div><p class="kicker">Cruze os dados</p><h2 id="cz-h">Como votou o seu estado?</h2>'
          f'<p>O cruzador junta a urna do TSE de cada estado, os eleitos de 2026 e os votos da bancada no Congresso.</p><p><a class="btn" href="/cruzar">Abrir o cruzador</a></p></div>'
          f'<ul aria-label="Exemplos"><li><a href="/cruzar?uf=SP&assunto=Trabalho">{ico("cruzar")}São Paulo</a></li><li><a href="/cruzar?uf=MG&assunto=Trabalho">{ico("cruzar")}Minas Gerais</a></li><li><a href="/cruzar?uf=PE&assunto=Trabalho">{ico("cruzar")}Pernambuco</a></li></ul></section>')
    est = estudos_do_tema(t)
    ciencia = ""
    if est:
        lis = "".join(f'<li><p class="tipo-e">{E(e["tipo"])}</p><p>{E(e["achado"])}</p><p class="ref">{E(e["ref"])}. <a href="https://doi.org/{E(e["doi"])}" target="_blank" rel="noopener">'
                      f'<span lang="en">{E(e["titulo"])}</span><span class="visually-hidden"> (abre outro site)</span></a></p></li>' for e in est)
        extra = (" Nos temas de saúde do trabalhador, a base do site é também a dos documentos oficiais e da Saúde do Trabalhador: as Diretrizes da Fundacentro para a NR-1, "
                 "a Política Nacional de Saúde do Trabalhador e da Trabalhadora (PNSTT) e a Lista de Doenças Relacionadas ao Trabalho (LDRT), que estão em cada jogo.") if t["id"] == "trabalho" else ""
        ciencia = (f'<section id="ciencia" aria-labelledby="ci-t"><div class="sec-cab"><h2 id="ci-t">O que diz a ciência</h2>'
                   f'<p>Estudos revisados por pares, conferidos no PubMed ou na página da revista. Estudo observacional mostra associação, não prova sozinho a causa.{E(extra)}</p></div>'
                   f'<ul class="ciencia-l">{lis}</ul></section>')
        indice.append('<li><a href="#ciencia">O que diz a ciência</a></li>')
    novs = [n for n in NOVIDADES if n["tema"] == t["id"]]
    atual = novs[0]["data"] if novs else NOVIDADES[-1]["data"]
    nov = bloco_novidades(novs, "nv-t", "Novidades do tema", "O que entrou ou mudou neste tema, com a data.", limite=5)
    outros = "".join(f'<li data-tema="{o["id"]}"><a href="/tema/{o["id"]}">{ico(o["ic"])}{E(o["nome"])}</a></li>' for o in C.TEMAS if o["id"] != t["id"])
    corpo = f"""  <section class="tema-topo" data-tema="{t["id"]}" aria-labelledby="h1">
    <div class="linha"><span class="ic-a">{ico(t["ic"])}</span><h1 id="h1">{E(t["nome"])}</h1></div>
    <p class="sub">{E(t["frase"])}</p>
    <p class="meta">{len(its)} itens · atualizado em {data_br(atual)}</p>
    <nav aria-label="Nesta página"><ul class="indice">{"".join(indice)}</ul></nav>
  </section>
  {"".join(secoes)}
  {cz}
  {ciencia}
  {nov}
  <section aria-labelledby="ot-t"><div class="sec-cab"><h2 id="ot-t">Outros temas</h2></div><ul class="indice">{outros}</ul></section>"""
    cab = trilha([("Início", "/"), ("Temas", "/#temas"), (t["nome"], None)])
    return doc(f"tema/{t['id']}", f"{t['nome']} · Vigie a Democracia", t["frase"], f"og-tema-{t['id']}.png", corpo, cab_extra=cab,
               texto_soc=f"{t['nome']}: jogos, dados e fontes no Vigie a Democracia.")


# ------------------------------------------------------------------ jogar
def pagina_jogar():
    secs, ind = [], []
    for gid, gnome, gdesc, ids in C.JOGAR:
        ind.append(f'<li><a href="#{gid}">{ico({"telao": "telao", "grupo": "pessoa", "celular": "jogos", "papel": "imprimir"}[gid])}{E(gnome)}</a></li>')
        secs.append(f'<section id="{gid}" aria-labelledby="{gid}-t"><div class="sec-cab"><h2 id="{gid}-t">{E(gnome)}</h2><p>{E(gdesc)}</p></div>'
                    f'<ul class="cartoes">{"".join(cartao(C.ITENS[i], com_tema=True) for i in ids)}</ul></section>')
    corpo = f"""  <section class="tema-topo" aria-labelledby="h1">
    <div class="linha"><span class="ic-a" style="--c:#17191E">{ico("jogos")}</span><h1 id="h1">Jogar e aprender</h1></div>
    <p class="sub">Todos os jogos do site, pelo jeito de jogar. Cada resposta traz a fonte. De graça, sem cadastro e sem coletar dados de quem joga.</p>
    <nav aria-label="Jeitos de jogar"><ul class="indice">{"".join(ind)}</ul></nav>
  </section>
  {"".join(secs)}
  <section class="caixa" aria-labelledby="cd-t"><h2 id="cd-t">Vai conduzir com um grupo?</h2>
    <ul><li>No telão: abra o jogo no computador ligado ao projetor e mostre o QR code; a plateia entra pelo celular, sem cadastro.</li>
    <li>Sem internet: imprima o kit em A4 colorido. Placas de A a F servem para a plateia responder levantando a mão.</li>
    <li>Combine antes que ninguém precisa se identificar, e que a resposta certa vem sempre com a fonte para a conversa continuar.</li></ul></section>"""
    cab = trilha([("Início", "/"), ("Jogar", None)])
    return doc("jogar", "Jogar e aprender · Vigie a Democracia", "Todos os jogos do Vigie a Democracia, pelo jeito de jogar: no telão, em grupo, no celular ou no papel.",
               "og-jogar.png", corpo, atual="jogos", cab_extra=cab, texto_soc="Jogos com fonte para o telão, a roda, o celular e o papel, no Vigie a Democracia:")


# ------------------------------------------------------------------ cruzar
def pagina_cruzar():
    sci = {a: [dict(tipo=e["tipo"], achado=e["achado"], ref=e["ref"], doi=e["doi"], titulo=e["titulo"]) for e in CI.do_assunto(a)] for a in CI.ASSUNTOS}
    sem = {a: t for a, t in CI.SEM_ESTUDO.items() if t}
    ASSUNTO_TEMA = {"Trabalho": "trabalho", "Impostos": "bolso", "Contas públicas": "bolso", "Direitos": "direitos", "Terra e ambiente": "fatos",
                    "Democracia": "congresso", "Redes": "fatos", "Segurança": "congresso"}
    LINKS = {"Trabalho": ["j4", "saude-mental", "roleta-saude", "assedio", "denuncie"], "Impostos": ["j14", "j3", "familia", "j17"],
             "Contas públicas": ["j3", "familia", "quem-cobrar"], "Direitos": ["denuncie", "assedio", "pode-ou-nao"],
             "Terra e ambiente": ["j13", "indigenas", "quem-cobrar"], "Democracia": ["vota-como-voce", "parlamentares", "semana", "raiox"],
             "Redes": ["j2", "familia", "checagem", "j6"], "Segurança": ["quem-cobrar", "vota-como-voce", "parlamentares"]}
    links = {a: [dict(n=C.ITENS[i]["nome"], h=C.ITENS[i]["href"], f=C.FORMATOS[C.ITENS[i]["fmt"]]) for i in ids] for a, ids in LINKS.items()}
    tema = {a: dict(id=t, nome=C.TEMA[t]["nome"]) for a, t in ASSUNTO_TEMA.items()}
    cz = dict(ordem=CI.ASSUNTOS, sci=sci, sem=sem, links=links, tema=tema)
    corpo = f"""  <section class="tema-topo" data-tema="congresso" aria-labelledby="h1">
    <div class="linha"><span class="ic-a">{ico("cruzar")}</span><h1 id="h1">Cruze os dados</h1></div>
    <p class="sub">Escolha o lugar, o assunto e o partido. O site junta os votos da Câmara e do Senado, a urna do TSE, os eleitos de 2026, os dados do IBGE e estudos científicos e mostra um dado novo, sempre com a fonte. Mais abaixo, <a href="#ce">compare os estados</a> cruzando quaisquer dois dados.</p>
  </section>
  <p class="cz-aviso" id="cz-aviso" role="status">Carregando os dados…</p>
  <form class="cz-form" id="cz-form" hidden aria-describedby="cz-ajuda">
    <div><label for="cz-uf">Onde?</label><select id="cz-uf" name="uf"></select></div>
    <div><label for="cz-as">Qual assunto?</label><select id="cz-as" name="assunto"></select></div>
    <div><label for="cz-pt">Qual partido? <small>(partido atual)</small></label><select id="cz-pt" name="partido"></select></div>
    <fieldset><legend>Qual Casa?</legend><div class="cz-seg">
      <label><input type="radio" name="casa" value="CS" checked> As duas</label><label><input type="radio" name="casa" value="C"> Câmara</label><label><input type="radio" name="casa" value="S"> Senado</label></div></fieldset>
    <div class="cz-eu"><input type="checkbox" id="cz-eu" name="eu" disabled><label for="cz-eu">Comparar com as minhas respostas do teste
      <small id="cz-eu-txt">Responda a pelo menos 3 afirmações no <a href="/vota-como-voce">Quem vota como você?</a> para liberar.</small></label></div>
    <button type="submit" class="btn forte">Ver o resultado</button>
  </form>
  <p id="cz-ajuda" class="nota">Os resultados mudam na hora, a cada escolha. O endereço da página guarda o cruzamento: copie e mande para alguém.</p>
  <p class="visually-hidden" id="cz-resumo" aria-live="polite"></p>
  <div id="cz-res"></div>
  <section class="ce" id="ce" aria-labelledby="ce-t" hidden>
    <div class="sec-cab"><h2 id="ce-t">Compare os estados</h2>
    <p>Escolha <b>dois dados quaisquer</b> e veja os 27 estados lado a lado: urna, eleitos, votos das bancadas, presença, trabalho e renda. São 49 dados, que se cruzam de todas as formas. O resultado vem em frase, em gráfico e em tabela.</p></div>
    <p class="ce-ex-t" id="ce-ex-t">Comece por um exemplo:</p>
    <ul class="ce-ex" aria-labelledby="ce-ex-t">
      <li><button type="button" class="btn" data-cx="desocupacao" data-cy="lula-t2">Desemprego × voto em Lula</button></li>
      <li><button type="button" class="btn" data-cx="rendimento" data-cy="comparec-t2">Renda × comparecimento</button></li>
      <li><button type="button" class="btn" data-cx="informalidade" data-cy="voto-6x1-C">Informalidade × fim da 6x1</button></li>
      <li><button type="button" class="btn" data-cx="gini" data-cy="eleitos-pl">Desigualdade × eleitos do PL</button></li>
      <li><button type="button" class="btn" data-cx="gov-C" data-cy="lula-t2">Bancada com o governo × voto em Lula</button></li>
      <li><button type="button" class="btn" data-cx="rendimento" data-cy="">Renda, estado por estado</button></li>
    </ul>
    <div class="cz-form ce-form">
      <div><label for="ce-x">Primeiro dado</label><select id="ce-x"></select></div>
      <div><label for="ce-y">Segundo dado</label><select id="ce-y"></select></div>
      <button type="button" class="btn" id="ce-trocar">Trocar os dois de lugar</button>
    </div>
    <p class="nota">Para destacar um estado, escolha-o em “Onde?”, lá em cima. O endereço da página guarda a comparação.</p>
    <p class="visually-hidden" id="ce-frase" aria-live="polite"></p>
    <div id="ce-res"></div>
  </section>
  <section class="caixa" aria-labelledby="cm-t"><h2 id="cm-t">De onde vêm os dados</h2>
    <ul class="cz-como">
      <li>Votos, presença, alinhamento com o governo e cota: dados abertos da Câmara dos Deputados e do Senado Federal, de 2023 a 2026, com o placar de cada votação conferido contra o oficial.</li>
      <li>Urna: arquivos oficiais de divulgação do TSE, com 100% das seções apuradas, do 1º e do 2º turno para Presidente.</li>
      <li>Trabalho, renda e população: IBGE, Sidra (PNAD Contínua e Estimativas de População), com a tabela e o período de cada número.</li>
      <li>Quer ir além? Veja o <a href="/bases">guia das bases de dados</a>: Base dos Dados, gráficos do Nexo, HubPolítico e as fontes oficiais.</li>
      <li>Eleitos de 2026: Portal de Dados Abertos do TSE.</li>
      <li>Ciência: estudos revisados por pares, com DOI, conferidos no PubMed ou na página da revista. Quando não há estudo que meça o efeito de uma votação, dizemos isso.</li>
      <li>Nada do que você escolhe sai do seu aparelho. O site não tem ranking de parlamentares e não diz em quem votar.</li></ul></section>"""
    js = '<script src="/qr.js"></script>\n<script>window.CZ = ' + json.dumps(cz, ensure_ascii=False).replace("</", "<\\/") + ";</script>\n<script>" + (B / "cruzar.js").read_text(encoding="utf-8") + "</script>\n<script>" + (B / "comparar.js").read_text(encoding="utf-8") + "</script>"
    cab = trilha([("Início", "/"), ("Cruze os dados", None)])
    return doc("cruzar", "Cruze os dados · Vigie a Democracia",
               "Estado, assunto e partido: veja como votou a bancada, o que deu a urna, quem foi eleito em 2026 e o que dizem os estudos científicos, com a fonte e um card pronto para postar.",
               "og-cruzar.png", corpo, css=CSS_CRUZAR, js=js, atual="cruzar", cab_extra=cab, texto_soc="Cruze os dados do seu estado: votos, urna, eleitos e ciência, com fonte:")


# ------------------------------------------------------------------ bases de dados (guia)
BASES = [
    dict(id="basedosdados", nome="Base dos Dados", url="https://basedosdados.org/", quem="Organiza: Base dos Dados, organização sem fins lucrativos.",
         oque="Centenas de conjuntos de dados públicos já limpos e organizados: IBGE, TSE, Receita Federal, CGU, INEP e outros, com séries históricas por município.",
         para=["estudar", "pesquisar"], passos=["Procure um assunto na busca do site (por exemplo, “eleições” ou “escolas”).",
         "Abra o conjunto e leia o guia de uso: ele diz de onde vem cada dado e o que dá para cruzar.",
         "Baixe a tabela ou consulte com SQL (BigQuery), Python ou R."], acesso="Para baixar tabelas grandes ou usar o BigQuery, é preciso criar uma conta.",
         vigie="No Vigie, o Compare os estados usa dados das mesmas fontes oficiais (TSE e IBGE)."),
    dict(id="nexo", nome="Nexo Jornal: gráficos", url="https://www.nexojornal.com.br/grafico/", quem="Organiza: Nexo Jornal, jornal digital.",
         oque="Gráficos que explicam, com números, temas do noticiário: economia, política, sociedade, meio ambiente.",
         para=["comecar", "estudar"], passos=["Abra a seção de gráficos e escolha um tema.", "Leia o título e a frase de baixo: eles dizem o que o gráfico mostra.",
         "Confira a fonte no rodapé de cada gráfico antes de compartilhar."], acesso="Parte do conteúdo exige assinatura depois de algumas leituras.",
         vigie="No Vigie, cada gráfico do Compare os estados vem com uma frase e uma tabela, para quem não enxerga o gráfico."),
    dict(id="hubpolitico", nome="HubPolítico", url="https://hubpolitico.com.br/", quem="Organiza: HubPolítico Inteligência e Dados Ltda., empresa privada.",
         oque="Resultados das eleições de 2026 por estado, cidade e bairro, arquivo das eleições de 1998 a 2024 e perfis de políticos com votações, proposições, patrimônio declarado e gastos de campanha, a partir de dados do TSE, da Câmara e do Senado.",
         para=["estudar", "pesquisar"], passos=["Busque sua cidade para ver o mapa da votação por bairro.", "Abra o perfil de um político para ver votos e gastos de campanha.",
         "Volte à fonte oficial (TSE, Câmara ou Senado) quando for usar um número em público."], acesso="Algumas funções pedem cadastro.",
         vigie="O HubPolítico tem um índice próprio de posição política; o critério é dele. O Vigie não faz ranking de parlamentares e não diz em quem votar."),
]
OFICIAIS = [
    ("IBGE: Sidra", "https://sidra.ibge.gov.br/", "Tabelas de população, trabalho, renda e preços, por estado e município. É de onde vêm os dados de trabalho e renda do Compare os estados."),
    ("TSE: Portal de Dados Abertos", "https://dadosabertos.tse.jus.br/", "Candidatos, eleitos, votação por seção, prestação de contas de campanha."),
    ("Câmara dos Deputados: Dados Abertos", "https://dadosabertos.camara.leg.br/", "Votações nominais, presença, proposições e cota parlamentar."),
    ("Senado Federal: Dados Abertos", "https://www12.senado.leg.br/dados-abertos", "Votações, matérias e gastos dos senadores."),
    ("Portal da Transparência", "https://portaldatransparencia.gov.br/", "Gastos do governo federal, programas sociais e servidores (CGU)."),
]
PUBLICO = [("todos", "Todos"), ("comecar", "Para começar (qualquer idade)"), ("estudar", "Para estudar (escola e faculdade)"), ("pesquisar", "Para pesquisar (tabelas e programação)")]
CSS_BASES = r"""
.bd-filtro { display:flex; flex-wrap:wrap; gap:8px; margin:0; padding:0; list-style:none; }
.bd-filtro button { font:inherit; font-weight:700; min-height:48px; padding:6px 16px; border-radius:999px; border:2px solid var(--linha); background:var(--cartao); color:var(--tinta); cursor:pointer; }
.bd-filtro button[aria-pressed="true"] { background:var(--tinta); color:var(--papel); border-color:var(--tinta); }
.bd-lista { list-style:none; margin:0; padding:0; display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(min(100%, 20rem), 1fr)); }
.bd-c { background:var(--cartao); border:2px solid var(--linha); border-radius:20px; padding:18px clamp(14px, 3vw, 22px); display:flex; flex-direction:column; gap:10px; height:100%; box-sizing:border-box; }
.bd-c h2 { margin:0; font-size:clamp(1.25rem, 3.5vw, 1.5rem); }
.bd-c p { margin:0; } .bd-quem { color:var(--suave); font-weight:700; font-size:.95rem; }
.bd-para { display:flex; flex-wrap:wrap; gap:6px; margin:0; padding:0; list-style:none; }
.bd-para li { font-size:.85rem; font-weight:700; padding:2px 10px; border-radius:999px; border:1px solid var(--linha); background:var(--papel); }
.bd-c ol { margin:0; padding-left:1.3em; } .bd-c ol li + li { margin-top:4px; }
.bd-c h3 { margin:4px 0 0; font-size:1rem; font-family:'Lexend', sans-serif; }
.bd-acesso, .bd-vigie { font-size:.95rem; } .bd-vigie { border-left:4px solid var(--azul); padding-left:10px; }
.bd-c .btn { align-self:flex-start; margin-top:auto; }
.bd-of { margin:0; padding-left:1.1em; } .bd-of li + li { margin-top:8px; }
"""
JS_BASES = r"""<script>(function () {
  var bs = document.querySelectorAll('.bd-filtro button'), cs = document.querySelectorAll('.bd-c'), st = document.getElementById('bd-st');
  bs.forEach(function (b) { b.addEventListener('click', function () {
    bs.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    var f = b.dataset.f, n = 0;
    cs.forEach(function (c) { var ok = f === 'todos' || c.dataset.para.split(' ').indexOf(f) >= 0; c.parentNode.hidden = !ok; if (ok) n++; });
    st.textContent = n + (n === 1 ? ' base' : ' bases') + ' para “' + b.textContent + '”.';
  }); });
})();</script>"""


def pagina_bases():
    nomes = dict(PUBLICO)
    cards = []
    for b in BASES:
        para = "".join(f"<li>{E(nomes[p].split(' (')[0])}</li>" for p in b["para"])
        passos = "".join(f"<li>{E(x)}</li>" for x in b["passos"])
        cards.append(
            f'<li><article class="bd-c" data-para="{" ".join(b["para"])}" aria-labelledby="bd-{b["id"]}">'
            f'<h2 id="bd-{b["id"]}">{E(b["nome"])}</h2><p class="bd-quem">{E(b["quem"])}</p>'
            f'<ul class="bd-para" aria-label="Para quem">{para}</ul><p>{E(b["oque"])}</p>'
            f'<h3>Como usar, em 3 passos</h3><ol>{passos}</ol>'
            f'<p class="bd-acesso"><b>Acesso:</b> {E(b["acesso"])}</p><p class="bd-vigie">{E(b["vigie"])}</p>'
            f'<a class="btn forte" href="{E(b["url"])}" target="_blank" rel="noopener">Abrir {E(b["nome"])}<span class="visually-hidden"> (abre outro site)</span></a>'
            f'</article></li>')
    of = "".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(n)}<span class="visually-hidden"> (abre outro site)</span></a>: {E(d)}</li>' for n, u, d in OFICIAIS)
    filtro = "".join(f'<li><button type="button" data-f="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{E(v)}</button></li>' for k, v in PUBLICO)
    corpo = f"""  <section class="tema-topo" data-tema="fatos" aria-labelledby="h1">
    <div class="linha"><span class="ic-a">{ico("cruzar")}</span><h1 id="h1">Bases de dados para <span>todo mundo</span></h1></div>
    <p class="sub">Onde achar números confiáveis sobre o Brasil, para quem está começando e para quem pesquisa. Dizemos quem organiza cada base, o que ela tem e como usar em 3 passos.</p>
    <p><a class="btn forte" href="/cruzar#ce">Cruzar os dados dos estados aqui mesmo</a></p>
  </section>
  <section aria-labelledby="bd-f-t"><h2 id="bd-f-t">Para quem?</h2>
    <ul class="bd-filtro" aria-labelledby="bd-f-t">{filtro}</ul>
    <p class="visually-hidden" id="bd-st" role="status" aria-live="polite"></p></section>
  <ul class="bd-lista" aria-label="Bases de dados">{"".join(cards)}</ul>
  <section class="caixa" aria-labelledby="bd-of-t"><h2 id="bd-of-t">As fontes oficiais, direto na origem</h2>
    <p>Todo número das bases acima nasce em um órgão público. Quando for usar um dado em público, confira na origem.</p>
    <ul class="bd-of">{of}</ul></section>
  <section class="caixa" aria-labelledby="bd-dc-t"><h2 id="bd-dc-t">Antes de compartilhar um número</h2>
    <ul><li>Veja de onde ele vem e de quando é.</li><li>Dois dados que andam juntos não provam que um causa o outro.</li>
    <li>Desconfie de gráfico sem fonte, sem data ou com o eixo cortado.</li></ul></section>"""
    cab = trilha([("Início", "/"), ("Fatos e boatos", "/tema/fatos"), ("Bases de dados", None)])
    return doc("bases", "Bases de dados para todo mundo · Vigie a Democracia",
               "Base dos Dados, gráficos do Nexo, HubPolítico e as fontes oficiais (IBGE, TSE, Câmara, Senado): quem organiza, o que têm e como usar em 3 passos.",
               "og-cruzar.png", corpo, css=CSS_BASES, js=JS_BASES, atual="cruzar", cab_extra=cab, texto_soc="Bases de dados confiáveis, com quem organiza e como usar:")

# ------------------------------------------------------------------ ajustes nas páginas que já existem
CSS_COMUM = r"""/*vg-temas*/
.vg-trilha { margin:2px 0 -4px; } body > .vg-trilha { max-width:46rem; margin:4px auto 0; padding:0 max(16px, env(safe-area-inset-left, 0px)); box-sizing:border-box; }
.vg-trilha ol { list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; align-items:center; font-size:.92rem; }
.vg-trilha li { display:inline-flex; align-items:center; }
.vg-trilha li + li::before { content:"›"; margin:0 8px; color:var(--suave); }
.vg-trilha a { display:inline-flex; align-items:center; min-height:44px; font-weight:700; }
.vg-trilha [aria-current] { color:var(--suave); }
.vg-mais { border-top:3px solid var(--c, var(--tinta)); padding-top:16px; margin-top:12px; display:flex; flex-direction:column; gap:12px; }
.vg-mais h2 { margin:0; font-family:'Lexend', sans-serif; font-size:1.3rem; line-height:1.2; }
.vg-mais ul { list-style:none; margin:0; padding:0; display:grid; gap:8px; grid-template-columns:repeat(auto-fill, minmax(min(100%, 15rem), 1fr)); }
.vg-mais li a { display:flex; flex-direction:column; gap:2px; height:100%; padding:10px 14px; min-height:52px; border-radius:14px; border:1px solid var(--linha); border-left:5px solid var(--c, var(--tinta));
  background:var(--cartao); text-decoration:none; color:var(--tinta); }
.vg-mais li a b { color:var(--azul); } .vg-mais li a small { color:var(--suave); font-size:.85rem; font-weight:700; }
.vg-mais .vg-btns { display:flex; flex-wrap:wrap; gap:8px; margin:0; }
.vg-mais .vg-btns a { display:inline-flex; align-items:center; min-height:48px; padding:6px 18px; border-radius:999px; border:2px solid var(--tinta); color:var(--tinta); font-weight:700; text-decoration:none; }
.vg-mais .vg-btns a.forte { background:var(--tinta); color:var(--papel); }
.vg-convite { margin:16px 0 0; padding:12px 16px; border-radius:14px; background:var(--cartao); border:1px dashed var(--linha); font-size:.95rem; }
.vg-mais .vg-convite { margin:0; } aside.vg-convite p { margin:0; }
@media print { .vg-trilha, .vg-mais { display:none !important; } }
/*/vg-temas*/"""


def bloco_mais(tid, atual_href):
    t = C.TEMA[tid]
    its = [x for x in C.itens_do_tema(tid) if x["href"] != atual_href and x["fmt"] not in ("campanha", "canal")]
    its = sorted(its, key=lambda x: (not x["dest"], C.I.index(x)))[:4]
    lis = "".join(f'<li><a{link_attrs(x)}><b>{E(x["nome"])}</b><small>{E(C.FORMATOS[x["fmt"]])}{" · PDF" if x["pdf"] else ""}</small></a></li>' for x in its)
    asu = ASSUNTO_DO_TEMA[tid]
    cz = f'/cruzar?assunto={asu}' if asu else '/cruzar'
    return (f'<!--vg-mais--><section class="vg-mais" data-tema="{tid}" aria-labelledby="vg-mais-t"><h2 id="vg-mais-t">Continue em {E(t["nome"])}</h2><ul>{lis}</ul>'
            f'<p class="vg-btns"><a class="forte" href="/tema/{tid}">Tudo sobre {E(t["nome"])}</a><a href="{E(cz)}">Cruze os dados</a><a href="/#temas">Todos os temas</a></p>{convite()}</section><!--/vg-mais-->')


def ajusta_paginas(pub):
    novas = {"index.html", "jogar.html", "cruzar.html", "bases.html"}
    n = 0
    for f in sorted(pub.glob("*.html")):
        if f.name in novas:
            continue
        s = f.read_text(encoding="utf-8")
        if 'class="vg-nav"' not in s:
            continue
        slug = f.stem
        iid = C.PAGINA_ITEM.get(slug) or (C.PAGINA_ITEM.get("semana") if slug.startswith("semana-") else None)
        it = C.ITENS.get(iid) if iid else None
        atual = "denuncia" if slug == "denuncie" else ("inicio" if not it else "temas")
        s = re.sub(r'<nav class="vg-nav" aria-label="Seções do site"><ul>.*?</ul></nav>', lambda m: nav(atual), s, count=1, flags=re.S)
        s = re.sub(r"<!--vg-trilha-->.*?<!--/vg-trilha-->", "", s, flags=re.S)
        s = re.sub(r"<!--vg-mais-->.*?<!--/vg-mais-->\s*", "", s, flags=re.S)
        s = re.sub(r"\n(?:[ \t]*\n)+([ \t]*<footer>)", r"\n\1", s, count=1)
        if it:
            t = tema_de(it)
            nome = it["nome"] if not slug.startswith("semana-") else "Placar de " + data_br(slug[7:])
            passos = [("Início", "/"), (t["nome"], "/tema/" + t["id"]), (nome, None)]
        else:
            passos = [("Início", "/"), (C.SOLTAS.get(slug) or slug.capitalize(), None)]
        s = s.replace("</header>", "</header>" + trilha(passos), 1)
        if it:
            s = s.replace("<footer>", bloco_mais(it["tema"], it["href"]) + "\n  <footer>", 1)
        f.write_text(s, encoding="utf-8")
        n += 1
    return n


def ajusta_vigia(pub):
    p = pub / "vigia.js"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"var MAPA = \{.*?\}, atual", lambda m: "var MAPA = " + json.dumps(mapa_ronda(), ensure_ascii=False) + ", atual", s, count=1, flags=re.S)
    s = re.sub(r"var I = \{.*?\};\n", lambda m: "var I = " + json.dumps({k: ICO[k] for k in ("inicio", "temas", "cruzar", "jogos", "denuncia")}, ensure_ascii=False) + ";\n", s, count=1, flags=re.S)
    s = re.sub(r"var itens = \[.*?\];", lambda m: "var itens = " + json.dumps([[k, n, h] for k, n, h in NAV], ensure_ascii=False) + ";", s, count=1, flags=re.S)
    s = s.replace("atual = MAPA[slug] || (slug === 'denuncie' ? 'denuncia' : '')", "atual = slug === 'denuncie' ? 'denuncia' : (slug === 'cruzar' ? 'cruzar' : (slug === 'jogar' || slug === 'jogos' ? 'jogos' : (MAPA[slug] ? 'temas' : '')))")
    p.write_text(s, encoding="utf-8")


def ajusta_css(pub):
    p = pub / "vigie.css"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"\n?/\*vg-temas\*/.*?/\*/vg-temas\*/", "", s, flags=re.S).rstrip() + "\n" + CSS_COMUM.replace("/*/vg-temas*/", cores_css() + "/*/vg-temas*/") + "\n"
    p.write_text(s, encoding="utf-8")


def ajusta_manifesto(pub):
    p = pub / "manifest.webmanifest"
    m = json.loads(p.read_text(encoding="utf-8"))
    m["description"] = "Fatos com fonte, os votos do Congresso, canais de denúncia, jogos e o cruzador de dados, em seis temas. De graça e sem cadastro."
    ic = [dict(src="/icone-192.png", sizes="192x192")]
    m["shortcuts"] = [dict(name="Cruze os dados", short_name="Cruzar", url="/cruzar", icons=ic),
                      dict(name="Quem vota como você?", short_name="Teste", url="/vota-como-voce", icons=ic),
                      dict(name="Jogar e aprender", short_name="Jogar", url="/jogar", icons=ic),
                      dict(name="Onde denunciar e buscar apoio", short_name="Denunciar", url="/denuncie", icons=ic)]
    p.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")


def ajusta_sw(pub):
    p = pub / "sw.js"
    s = p.read_text(encoding="utf-8")
    h = hashlib.sha1()
    for f in sorted(pub.glob("*.html")) + sorted((pub / "tema").glob("*.html")) + sorted((pub / "dados").glob("*.json")) + [pub / "vigia.js", pub / "vigie.css"]:
        h.update(f.read_bytes())
    s = re.sub(r"const V = 'vigie-[^']*';", f"const V = 'vigie-{h.hexdigest()[:10]}';", s, count=1)
    pre = ["/", "/offline", "/cruzar", "/jogar", "/denuncie", "/vota-como-voce", "/parlamentares", "/dados/vota-como-voce.json", "/dados/parlamentares.json", "/dados/cruzar.json", "/dados/estados.json", "/bases",
           "/vigia.js", "/vigie.css", "/icone.svg", "/icone-192.png", "/fontes/AtkinsonHyperlegible-Regular.woff2", "/fontes/AtkinsonHyperlegible-Bold.woff2", "/fontes/Lexend-var.woff2"]
    s = re.sub(r"const PRE = \[.*?\];", "const PRE = " + json.dumps(pre) + ";", s, count=1, flags=re.S)
    p.write_text(s, encoding="utf-8")


# ------------------------------------------------------------------ imagens de prévia (1200x630)
def og_imagens(pub):
    from playwright.sync_api import sync_playwright
    sys.path.insert(0, str(B.parent))
    import marca as M
    fontes = (pub / "fontes").resolve().as_uri()
    alvos = [("og-cruzar.png", "Cruze os dados", "Novo no Vigie", "Seu estado, o assunto e o partido", "Votos da bancada, urna do TSE, eleitos de 2026 e o que diz a ciência, num card pronto para postar.", "#1F4E8C"),
             ("og-jogar.png", "Jogar e aprender", "Telão, roda, celular e papel", "Jogos com fonte para qualquer grupo", "Palestra, aula, praça ou sindicato: cada resposta traz a fonte. De graça.", "#17191E")]
    for t in C.TEMAS:
        alvos.append((f"og-tema-{t['id']}.png", t["nome"], "Vigie a Democracia · tema", t["nome"], t["frase"], t["cor"]))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        for nome, placa, kicker, titulo, desc, cor in alvos:
            pg.set_content(f"""<html><head><style>
@font-face {{ font-family:'Lexend'; src:url('{fontes}/Lexend-var.woff2'); font-weight:100 900; }}
@font-face {{ font-family:'Atk'; src:url('{fontes}/AtkinsonHyperlegible-Regular.woff2'); font-weight:400; }}
@font-face {{ font-family:'Atk'; src:url('{fontes}/AtkinsonHyperlegible-Bold.woff2'); font-weight:700; }}
body {{ margin:0; width:1200px; height:630px; background:#FBF8F1 {M.wm_tile_uri('rgba(20,24,30,.05)', 300).replace('url(', 'url(', 1)}; font-family:'Atk'; color:#17191E; position:relative; overflow:hidden; }}
.placa {{ position:absolute; left:60px; top:80px; width:500px; height:380px; background:#FFE58F; border:4px solid #17191E; transform:rotate(-3deg); display:flex; align-items:center; justify-content:center; text-align:center;
  font-family:'Lexend'; font-weight:700; font-size:{58 if len(placa) < 20 else 46}px; line-height:1.08; padding:30px; box-sizing:border-box; border-top:22px solid {cor}; }}
.dir {{ position:absolute; left:640px; top:80px; width:500px; }}
.k {{ font-family:'Atk'; font-weight:700; color:#B3261E; letter-spacing:.06em; text-transform:uppercase; font-size:26px; margin:0 0 14px; }}
h1 {{ font-family:'Lexend'; font-weight:700; font-size:{54 if len(titulo) < 34 else 44}px; line-height:1.05; margin:0 0 18px; }}
p.d {{ font-size:26px; line-height:1.4; color:#3A3D45; margin:0; }}
.pe {{ position:absolute; left:0; right:0; bottom:0; height:86px; background:#17191E; color:#FBF8F1; display:flex; align-items:center; justify-content:space-between; padding:0 64px; font-size:20px; }}
.pe b {{ font-size:30px; display:flex; align-items:center; gap:14px; }} .pe svg {{ width:34px; height:34px; }} .pe .r {{ text-align:right; line-height:1.4; }}
</style></head><body><div class="placa">{E(placa)}</div><div class="dir"><p class="k">{E(kicker)}</p><h1>{E(titulo)}</h1><p class="d">{E(desc)}</p></div>
<div class="pe"><b>{M.icon('ig')}@brunochapadeiro</b><div class="r">© Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0<br>vigieademocracia.brunochapadeiro.workers.dev</div></div></body></html>""")
            pg.wait_for_timeout(250)
            pg.screenshot(path=str(pub / nome))
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="public")
    ap.add_argument("--og", action="store_true")
    a = ap.parse_args()
    pub = Path(a.site)
    (pub / "tema").mkdir(exist_ok=True)
    (pub / "index.html").write_text(home(), encoding="utf-8")
    for t in C.TEMAS:
        (pub / "tema" / f"{t['id']}.html").write_text(pagina_tema(t), encoding="utf-8")
    (pub / "jogar.html").write_text(pagina_jogar(), encoding="utf-8")
    (pub / "cruzar.html").write_text(pagina_cruzar(), encoding="utf-8")
    (pub / "bases.html").write_text(pagina_bases(), encoding="utf-8")
    n = ajusta_paginas(pub)
    ajusta_vigia(pub); ajusta_css(pub); ajusta_manifesto(pub)
    if a.og or not (pub / "og-cruzar.png").exists():
        og_imagens(pub)
    ajusta_sw(pub)
    print(f"ok: início, {len(C.TEMAS)} temas, jogar, cruzar, bases; {n} páginas com menu, trilha e 'continue no tema'")


if __name__ == "__main__":
    main()
