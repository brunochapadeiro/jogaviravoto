/* Vigie a Democracia: carimbo da ronda (só neste aparelho), app instalável e barra de navegação no celular.
   © 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Feito com auxílio de IA. */
(function () {
  var slug = location.pathname.replace(/^\/+|\/+$/g, '').replace(/\.html$/, '') || 'inicio';
  try { var v = JSON.parse(localStorage.getItem('vigie-visitas') || '{}'); if (!v[slug]) { v[slug] = new Date(Date.now() - 3 * 36e5).toISOString().slice(0, 10); localStorage.setItem('vigie-visitas', JSON.stringify(v)); } } catch (e) {}
  if ('serviceWorker' in navigator && location.protocol === 'https:') addEventListener('load', function () { navigator.serviceWorker.register('/sw.js').catch(function () {}); });
  if (document.querySelector('.vg-nav')) { var bd = function () { document.body.classList.add('vg-com-nav'); }; if (document.body) bd(); else addEventListener('DOMContentLoaded', bd); return; }
  var s = document.currentScript; if (!s || !s.hasAttribute('data-nav') || document.querySelector('nav.baixo')) return;
  var MAPA = {"vota-como-voce": "congresso", "parlamentares": "congresso", "semana": "congresso", "congresso": "congresso", "familia": "fatos", "boato": "fatos", "roleta": "fatos", "checagem": "fatos", "quemdisse": "fatos", "roleta-saude": "trabalho", "pode-ou-nao": "trabalho", "6x1": "trabalho", "ir": "trabalho", "programas": "trabalho", "denuncie": "denuncia", "assedio": "denuncia", "praca": "jogos", "jogos": "jogos", "quiz": "jogos", "show": "jogos", "baralho": "jogos"}, atual = MAPA[slug] || (slug === 'denuncie' ? 'denuncia' : '');
  var I = {"congresso": "<path d=\"M3 21h18M4 10h16M12 3 4 7h16zM6 10v8M10 10v8M14 10v8M18 10v8M4 18h16\"/>", "fatos": "<path d=\"M9 11.5 11.2 14 15.5 9\"/><circle cx=\"12\" cy=\"12\" r=\"9\"/>", "trabalho": "<rect x=\"3\" y=\"7\" width=\"18\" height=\"13\" rx=\"2\"/><path d=\"M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18\"/>", "denuncia": "<path d=\"M4 21V4M4 4h12l-2 4 2 4H4\"/>", "jogos": "<rect x=\"2.5\" y=\"7\" width=\"19\" height=\"11\" rx=\"5\"/><path d=\"M7 10.5v4M5 12.5h4M15.5 11.5h.01M18 13.5h.01\"/>", "inicio": "<path d=\"M3 11 12 4l9 7M5 10v10h14V10\"/>", "busca": "<circle cx=\"11\" cy=\"11\" r=\"7\"/><path d=\"m20 20-3.5-3.5\"/>", "pessoa": "<circle cx=\"12\" cy=\"8\" r=\"4\"/><path d=\"M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6\"/>"};
  var itens = [['inicio', 'Início', '/'], ['congresso', 'Congresso', '/#congresso'], ['fatos', 'Fatos', '/#fatos'], ['denuncia', 'Denunciar', '/denuncie'], ['jogos', 'Jogar', '/#jogos']];
  var css = '.vg-baixo{position:fixed;left:0;right:0;bottom:0;z-index:40;background:#17191E;border-top:1px solid #3A3D45;padding:6px 8px calc(6px + env(safe-area-inset-bottom,0px));display:none}'
    + '.vg-baixo ul{list-style:none;margin:0 auto;padding:0;max-width:40rem;display:grid;grid-template-columns:repeat(5,1fr);gap:2px}'
    + '.vg-baixo a{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-height:54px;color:#FBF8F1;text-decoration:none;font:700 .78rem/1.1 "Atkinson Hyperlegible",system-ui,sans-serif;border-radius:12px}'
    + '.vg-baixo a svg{width:24px;height:24px}.vg-baixo a[aria-current]{background:rgba(255,255,255,.14);color:#FFE58F}.vg-baixo a:focus-visible{outline:3px solid #FFE58F;outline-offset:-3px}'
    + '@media (max-width:62rem){.vg-baixo{display:block}body.vg-tem-baixo{padding-bottom:76px}}@media print{.vg-baixo{display:none!important}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  var nav = document.createElement('nav'); nav.className = 'vg-baixo'; nav.setAttribute('aria-label', 'Seções do site');
  var ul = document.createElement('ul');
  itens.forEach(function (x) { var li = document.createElement('li'), a = document.createElement('a'); a.href = x[2];
    a.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + I[x[0]] + '</svg>';
    a.appendChild(document.createTextNode(x[1])); if (x[0] === atual) a.setAttribute('aria-current', 'page'); li.appendChild(a); ul.appendChild(li); });
  nav.appendChild(ul);
  function poe() { document.body.appendChild(nav); document.body.classList.add('vg-tem-baixo'); }
  if (document.body) poe(); else addEventListener('DOMContentLoaded', poe);
})();
