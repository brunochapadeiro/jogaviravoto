"""Barra de acessibilidade comum às páginas do site (Games, Roleta, Roteiros, Acessibilidade, Kit) e barra social
(acessos, curtir, comentar, repostar e compartilhar, com os números do placar público, como no Instagram).
Letra maior ou menor, alto contraste, espaçamento para dislexia, sem movimento, ouvir (voz do próprio aparelho),
Libras (VLibras, do governo federal) e link de ajuda. As escolhas ficam guardadas só neste aparelho."""
import marca as M

SITE = M.FLIPER

CSS_BARRA = """
html.a11y-zoom body { zoom: var(--a11y-zoom); }
footer p, footer a, .regras h2, .regras li { overflow-wrap: anywhere; }
html.a11y-zoom .top { flex-wrap: wrap; row-gap: 6px; } html.a11y-zoom .xp { white-space: normal; }
html.a11y-zoom .botao-ig, html.a11y-zoom .btn, html.a11y-zoom .redes a { max-width: 100%; white-space: normal; }
details.a11y { margin: 0; font-size: 15px; }
details.a11y > summary { list-style: none; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 4px 14px;
  border-radius: 999px; border: 2px solid currentColor; font-weight: 700; }
details.a11y > summary::-webkit-details-marker { display: none; }
details.a11y > summary svg { width: 1.3em; height: 1.3em; }
.a11y-bar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 10px; }
.a11y-bar button, .a11y-bar a { font: inherit; font-weight: 700; min-height: 44px; min-width: 44px; padding: 4px 12px; border-radius: 10px;
  border: 2px solid currentColor; background: transparent; color: inherit; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; }
.a11y-bar button[aria-pressed="true"] { background: #1F4E8C; border-color: #1F4E8C; color: #fff; }
.a11y-zl { font-variant-numeric: tabular-nums; min-width: 3.2em; text-align: center; }
.a11y-aviso { flex-basis: 100%; margin: 0; font-size: 14px; }
.a11y-aviso:empty { display: none; }
html.a11y-contraste body, html.a11y-contraste body *:not(svg):not(svg *):not(i) { background-color: #000 !important; background-image: none !important;
  color: #fff !important; border-color: #fff !important; text-shadow: none !important; box-shadow: none !important; }
html.a11y-contraste a, html.a11y-contraste a * { color: #FFE600 !important; }
html.a11y-contraste button, html.a11y-contraste .btn { border: 2px solid #fff !important; }
html.a11y-contraste .a11y-bar button[aria-pressed="true"] { background: #FFE600 !important; color: #000 !important; }
html.a11y-contraste :focus-visible { outline: 4px solid #FFE600 !important; outline-offset: 3px; }
html.a11y-espaco body * { letter-spacing: .05em !important; word-spacing: .16em !important; line-height: 1.75 !important; }
html.a11y-parado *, html.a11y-parado *::before, html.a11y-parado *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
"""

ICONE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<circle cx="12" cy="4.5" r="2"/><path d="M4 8.5l8 1.5 8-1.5M12 10v5M12 15l-3.5 6M12 15l3.5 6"/></svg>')


def barra(abrir=False):
    return (f'<details class="a11y"{" open" if abrir else ""}><summary>{ICONE}Acessibilidade</summary>'
            '<div class="a11y-bar" role="group" aria-label="Opções de acessibilidade">'
            '<button type="button" data-a11y="menos" aria-label="Diminuir a letra">A−</button>'
            '<span class="a11y-zl" id="a11y-zl" aria-live="polite">100%</span>'
            '<button type="button" data-a11y="mais" aria-label="Aumentar a letra">A+</button>'
            '<button type="button" data-a11y="c" aria-pressed="false">Contraste</button>'
            '<button type="button" data-a11y="e" aria-pressed="false">Espaçamento</button>'
            '<button type="button" data-a11y="m" aria-pressed="false">Sem movimento</button>'
            '<button type="button" data-a11y="ouvir" aria-pressed="false">Ouvir</button>'
            '<button type="button" data-a11y="libras">Libras</button>'
            f'<a href="{SITE}acessibilidade">Ajuda</a>'
            '<p class="a11y-aviso" id="a11y-aviso" aria-live="polite"></p></div></details>')


ICO = {
    "ver": '<path d="M1.6 12S5.4 4.8 12 4.8 22.4 12 22.4 12 18.6 19.2 12 19.2 1.6 12 1.6 12z"/><circle cx="12" cy="12" r="3.3"/>',
    "curtir": '<path d="M12 20.6s-7.7-4.7-9.7-9.4C.8 7.7 3 4 6.8 4c2.2 0 3.8 1.2 5.2 3 1.4-1.8 3-3 5.2-3 3.8 0 6 3.7 4.5 7.2-2 4.7-9.7 9.4-9.7 9.4z"/>',
    "comentar": '<path d="M20.6 16.9A9.2 9.2 0 1 0 17 20.4l4.6 1.2z"/>',
    "repostar": '<path d="M17 2.5l3.5 3.5-3.5 3.5"/><path d="M3.5 11.5V9.6A3.6 3.6 0 0 1 7.1 6h13.4"/><path d="M7 21.5L3.5 18 7 14.5"/><path d="M20.5 12.5v1.9a3.6 3.6 0 0 1-3.6 3.6H3.5"/>',
    "compartilhar": '<path d="M21.8 2.6L10.3 13.4"/><path d="M21.8 2.6l-6.9 18.8-4.6-8L2.2 9.2z"/>',
}


def _svg(k):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{ICO[k]}</svg>')


def social(texto="Games Vira-Voto: jogos rápidos, Cartilha e plano para votar no domingo, 25/10. De graça e com fonte:",
           url=None, grande=False, titulo=None, placar=None, conta_acesso=False):
    """Barra igual à do Instagram, com o número absoluto ao lado de cada ícone (placar público do site).
    acessos (abre o placar) · curtir (1 vez por aparelho) · comentar (no Instagram, onde cada pessoa assina e há moderação)
    · repostar (story, status ou feed, pelo menu do celular, ou copia o link) · compartilhar (WhatsApp)."""
    import urllib.parse as U
    url = url or SITE
    placar = placar or (SITE + "#placar")
    wa = "https://wa.me/?text=" + U.quote(f"{texto} {url}", safe="")
    item = lambda tag, k, n, lbl, extra="": (
        f'<li><{tag} class="soc-i" data-soc="{k}"{extra}><span class="soc-v">{_svg(k)}<b data-soc-n="{n}"></b></span>'
        f'<span class="soc-l">{lbl}</span></{tag.split()[0]}></li>')
    tit = f'<p class="soc-k">{titulo}</p>' if titulo else ""
    import html as _h
    return (f'<div class="soc{" grande" if grande else ""}"{" data-conta-acesso" if conta_acesso else ""} data-soc-texto="{_h.escape(texto)}" data-soc-url="{_h.escape(url)}">{tit}'
            f'<p class="soc-ac"><a class="soc-a" data-soc="ver" href="{placar}">{_svg("ver")}<b data-soc-n="acessos"></b><span class="soc-al"></span>'
            '<span class="soc-vp">Ver o placar</span></a></p>'
            '<ul class="soc-row" role="list">'
            + item('button type="button"', "curtir", "curtidas", "curtir", ' aria-pressed="false"')
            + item('button type="button"', "comentar", "comentarios", "comentar", ' aria-expanded="false"')
            + item('button type="button"', "repostar", "reposts", "repostar")
            + item(f'a href="{_h.escape(wa)}" target="_blank" rel="noopener"', "compartilhar", "compartilhamentos", "compartilhar")
            + '</ul>'
            '<div class="soc-p" hidden><p>Os comentários ficam no Instagram do Prof. Bruno Chapadeiro: lá cada pessoa assina o que escreve, '
            'e tem moderação.</p><p class="soc-bs">'
            f'<a class="soc-b" data-soc-com href="{M.IG_URL}" target="_blank" rel="noopener">Comentar no Instagram</a>'
            f'<a class="soc-b" data-soc-com href="https://ig.me/m/{M.IG.lstrip("@")}" target="_blank" rel="noopener">Mandar mensagem direta</a></p></div>'
            '<p class="soc-st" aria-live="polite"></p></div>')


def curtir():
    """Mantido por compatibilidade: agora é a barra completa (acessos, curtir, comentar, repostar, compartilhar)."""
    return social()


SOC_CSS = """
.soc { margin: 0; }
.soc-k { margin: 0 0 4px; font-size: 13px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.soc-ac { margin: 0 0 2px; }
.soc-a { display: inline-flex; align-items: center; flex-wrap: wrap; gap: 4px 8px; min-height: 44px; padding: 2px 8px 2px 4px; border-radius: 12px; color: inherit; text-decoration: none; font-size: 16px; }
.soc-a svg { width: 26px; height: 26px; flex: none; }
.soc-a b { font-size: 19px; font-weight: 700; font-variant-numeric: tabular-nums; } .soc-a b:empty { display: none; }
.soc-vp { text-decoration: underline; text-underline-offset: 3px; font-weight: 700; }
.soc-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(76px, 1fr)); gap: 4px; margin: 0; padding: 0; list-style: none; }
.soc-row > li { display: flex; min-width: 0; }
.soc-i { flex: 1; min-width: 0; min-height: 58px; padding: 6px 2px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
  font: inherit; color: inherit; background: transparent; border: 0; border-radius: 12px; cursor: pointer; text-decoration: none; }
.soc-i:hover, .soc-a:hover { background: rgba(128,128,128,.14); }
.soc-i:focus-visible, .soc-a:focus-visible, .soc-b:focus-visible { outline: 3px solid #1F4E8C; outline-offset: 2px; }
.soc-v { display: inline-flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 2px 4px; }
.soc-i svg { width: 24px; height: 24px; flex: none; }
.soc-i b { font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1.1; }
.soc-i b:empty { display: none; }
.soc-l { font-size: 12.5px; line-height: 1.15; }
.soc.grande .soc-a b { font-size: 24px; } .soc.grande .soc-a svg { width: 30px; height: 30px; }
.soc-i[data-soc="curtir"][aria-pressed="true"] svg { fill: #E8173A; stroke: #E8173A; animation: soc-pop .35s ease-out; }
@keyframes soc-pop { 0% { transform: scale(1); } 45% { transform: scale(1.3); } 100% { transform: scale(1); } }
@media (prefers-reduced-motion: reduce) { .soc-i svg { animation: none !important; } }
.soc-p { margin: 8px 0 0; padding: 10px 12px; border: 2px solid currentColor; border-radius: 12px; font-size: 15px; }
.soc-p p { margin: 0; } .soc-bs { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px !important; }
.soc-b { display: inline-flex; align-items: center; min-height: 44px; padding: 4px 14px; border-radius: 999px; border: 2px solid currentColor; color: inherit; font-weight: 700; text-decoration: none; }
.soc-st { margin: 6px 0 0; font-size: 14px; overflow-wrap: anywhere; } .soc-st:empty { display: none; }
@media print { .soc { display: none !important; } }
"""

JS = """
(function () {
  var H = document.documentElement, K = 'vv-a11y', st = { z: 1, c: 0, e: 0, m: 0 }, Z = [0.9, 1, 1.15, 1.3, 1.5], CONT = '__CONT__';
  try { var g = JSON.parse(localStorage.getItem(K) || '{}'); for (var k in g) st[k] = g[k]; } catch (x) {}
  function aviso(t) { var a = document.getElementById('a11y-aviso'); if (a) a.textContent = t; }
  function aplica() {
    H.style.setProperty('--a11y-zoom', st.z); H.classList.toggle('a11y-zoom', st.z !== 1); H.classList.toggle('a11y-contraste', !!st.c); H.classList.toggle('a11y-espaco', !!st.e); H.classList.toggle('a11y-parado', !!st.m);
    document.querySelectorAll('[data-a11y="c"],[data-a11y="e"],[data-a11y="m"]').forEach(function (b) { b.setAttribute('aria-pressed', String(!!st[b.getAttribute('data-a11y')])); });
    var zl = document.getElementById('a11y-zl'); if (zl) zl.textContent = Math.round(st.z * 100) + '%';
    try { localStorage.setItem(K, JSON.stringify(st)); } catch (x) {}
  }
  function zoom(d) { var i = Z.indexOf(st.z); if (i < 0) i = 1; st.z = Z[Math.max(0, Math.min(Z.length - 1, i + d))]; aplica(); }
  var falando = false;
  function ouvir(b) {
    var s = window.speechSynthesis;
    if (!s || !window.SpeechSynthesisUtterance) { aviso('Este navegador não lê em voz alta. Use o leitor de tela do celular (TalkBack ou VoiceOver).'); return; }
    if (falando) { s.cancel(); falando = false; b.setAttribute('aria-pressed', 'false'); return; }
    var alvo = document.querySelector('[data-a11y-ler]') || document.querySelector('main') || document.body;
    var t = (alvo.innerText || '').replace(/\\s+/g, ' ').trim(); if (!t) return;
    var partes = t.match(/[^.!?:]+[.!?:]*/g) || [t], vz = s.getVoices();
    var v = vz.filter(function (x) { return /pt[-_]BR/i.test(x.lang); })[0] || vz.filter(function (x) { return /^pt/i.test(x.lang); })[0];
    s.cancel(); falando = true; b.setAttribute('aria-pressed', 'true'); aviso('Lendo em voz alta. Toque em Ouvir de novo para parar.');
    partes.forEach(function (p, i) {
      var u = new SpeechSynthesisUtterance(p.trim()); u.lang = 'pt-BR'; if (v) u.voice = v;
      if (i === partes.length - 1) u.onend = function () { falando = false; b.setAttribute('aria-pressed', 'false'); aviso(''); };
      s.speak(u);
    });
  }
  function libras() {
    var ab = document.querySelector('[vw-access-button]');
    if (window.VLibras && ab) { ab.click(); return; }
    aviso('Abrindo o VLibras…');
    var d = document.createElement('div'); d.setAttribute('vw', ''); d.className = 'enabled';
    d.innerHTML = '<div vw-access-button class="active"></div><div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div>';
    document.body.appendChild(d);
    var sc = document.createElement('script'); sc.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
    sc.onload = function () { try { new window.VLibras.Widget('https://vlibras.gov.br/app');
      setTimeout(function () { var b = document.querySelector('[vw-access-button]'); if (b) b.click(); aviso('Libras: o intérprete virtual aparece no canto da tela. Toque num texto para ele traduzir.'); }, 1500);
    } catch (x) { aviso('Não foi possível abrir o VLibras aqui.'); } };
    sc.onerror = function () { aviso('Não foi possível abrir o VLibras aqui. No site Vigie a Democracia ele funciona.'); };
    document.head.appendChild(sc);
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-a11y]'); if (!b) return; var k = b.getAttribute('data-a11y');
    if (k === 'mais') zoom(1); else if (k === 'menos') zoom(-1); else if (k === 'ouvir') ouvir(b); else if (k === 'libras') libras(); else { st[k] = st[k] ? 0 : 1; aplica(); }
  });
  aplica();
})();
""".replace("__CONT__", M.CONTADOR)


SOC_JS = r"""
(function () {
  var CONT = '__CONT__', D = null, base = {}, nota = '', seq = 0, ult = {};
  var PUB = (function () { try { return location.protocol === 'file:' || (/^https?:$/.test(location.protocol) && !/claude|anthropic/.test(location.hostname)); } catch (x) { return false; } })();
  var CK = 'vv-curtiu', ja = false; try { ja = localStorage.getItem(CK) === '1'; } catch (x) {}
  function fmt(n) { return (n || 0).toLocaleString('pt-BR'); }
  function tot(k) { return D ? ((D.totais && D.totais[k]) || 0) + (base[k] || 0) : null; }
  var NOME = { ver: function (n) { return n + ' acessos' + (base.acessos ? ' desde 15/10, com estimativa de 15 a 20/10' : '') + '. Ver o placar'; }, curtir: function (n) { return 'Curtir. ' + n + ' curtidas'; },
    comentar: function (n) { return 'Comentar no Instagram. ' + n + ' vezes'; }, repostar: function (n) { return 'Repostar. ' + n + ' reposts'; },
    compartilhar: function (n) { return 'Compartilhar no WhatsApp. ' + n + ' compartilhamentos'; } };
  var CH = { ver: 'acessos', curtir: 'curtidas', comentar: 'comentarios', repostar: 'reposts', compartilhar: 'compartilhamentos' };
  function prepara(el) {
    if (!el.getAttribute('data-soc-id')) { seq += 1; var id = 'soc-p-' + seq + '-' + Math.random().toString(36).slice(2, 6); el.setAttribute('data-soc-id', id);
      var p = el.querySelector('.soc-p'), b = el.querySelector('[data-soc="comentar"]'); if (p && b) { p.id = id; b.setAttribute('aria-controls', id); } }
    el.querySelectorAll('[data-soc]').forEach(function (b) {
      var k = b.getAttribute('data-soc'), n = tot(CH[k]), nb = b.querySelector('[data-soc-n]');
      if (nb) nb.textContent = n === null ? '' : fmt(n);
      var al = b.querySelector('.soc-al'); if (al) al.textContent = n === null ? '' : (n === 1 ? 'acesso' : 'acessos');
      var nome = n === null ? { ver: 'Ver o placar de acessos', curtir: 'Curtir', comentar: 'Comentar no Instagram', repostar: 'Repostar', compartilhar: 'Compartilhar no WhatsApp' }[k] : NOME[k](fmt(n));
      b.setAttribute('aria-label', nome);
      if (k === 'curtir') b.setAttribute('aria-pressed', String(ja));
    });
  }
  function pintaTudo() { document.querySelectorAll('.soc').forEach(prepara); }
  function dados(d) { if (!d || !d.totais) return; D = d; base = d.base || {}; nota = d.base_nota || ''; pintaTudo(); }
  function soma(k) { if (!D) return; D.totais = D.totais || {}; D.totais[k] = (D.totais[k] || 0) + 1; pintaTudo(); }
  function envia(e) {
    if (!PUB) return; var u = CONT + '?e=' + e;
    try { if (navigator.sendBeacon && navigator.sendBeacon(u)) return; } catch (x) {}
    try { fetch(u, { method: 'POST', mode: 'cors', keepalive: true }).catch(function () {}); } catch (x) {}
  }
  function conta(e) { var t = Date.now(); if (ult[e] && t - ult[e] < 15000) return; ult[e] = t; envia(e); soma(e); }
  function st(el, t) { var s = el.querySelector('.soc-st'); if (s) s.textContent = t; }
  window.vvSocial = { prepara: prepara, dados: dados, pinta: pintaTudo, nota: function () { return nota; } };
  pintaTudo();
  if (document.querySelector('.soc[data-conta-acesso]') && PUB) {
    var a = false; try { a = sessionStorage.getItem('vv-acesso') === '1'; sessionStorage.setItem('vv-acesso', '1'); } catch (x) {}
    if (!a) envia('acessos');
  }
  if (PUB && document.querySelector('.soc')) setTimeout(function () {
    if (D) return;
    try { fetch(CONT, { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) { if (d && !D) dados(d); }).catch(function () {}); } catch (x) {}
  }, 700);
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-soc],[data-soc-com]'); if (!t) return;
    var bar = t.closest('.soc'); if (!bar) return;
    if (t.hasAttribute('data-soc-com')) { conta('comentarios'); return; }
    var k = t.getAttribute('data-soc');
    if (k === 'curtir') {
      if (ja) { st(bar, 'Você já curtiu daqui. Obrigado!'); return; }
      ja = true; try { localStorage.setItem(CK, '1'); } catch (x) {}
      envia('curtidas'); soma('curtidas'); if (!D) pintaTudo(); st(bar, 'Curtido. Obrigado!');
    } else if (k === 'comentar') {
      var p = bar.querySelector('.soc-p'), ab = p.hidden; p.hidden = !ab; t.setAttribute('aria-expanded', String(ab));
      if (ab) { var l = p.querySelector('a'); if (l) l.focus(); }
    } else if (k === 'repostar') {
      var tx = bar.getAttribute('data-soc-texto') || document.title, u = bar.getAttribute('data-soc-url') || location.href;
      var copia = function () {
        var ok = function () { conta('reposts'); st(bar, 'Link copiado. Cole no seu story, status ou post.'); };
        try { navigator.clipboard.writeText(tx + ' ' + u).then(ok, function () { st(bar, 'Copie este link e cole no seu story, status ou post: ' + u); }); }
        catch (x) { st(bar, 'Copie este link e cole no seu story, status ou post: ' + u); }
      };
      if (navigator.share) navigator.share({ title: document.title, text: tx, url: u }).then(function () { conta('reposts'); st(bar, 'Obrigado por repostar!'); },
        function (er) { if (!(er && er.name === 'AbortError')) copia(); });
      else copia();
    } else if (k === 'compartilhar') { conta('compartilhamentos'); }
  });
})();
"""


CSS = CSS_BARRA + SOC_CSS


def script():
    return f"<script>{JS}</script><script>{SOC_JS.replace('__CONT__', M.CONTADOR)}</script>"


def script_social():
    """Só a barra social (para as páginas da Cartilha, da Apostila e do Guia, que têm a própria barra de acessibilidade)."""
    return f"<script>{SOC_JS.replace('__CONT__', M.CONTADOR)}</script>"
