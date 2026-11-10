/* Vigie a Democracia: Compare os estados. Cruza quaisquer dois dados dos 27 estados (urna, eleitos, votos das bancadas,
   presença, alinhamento e IBGE) e mostra o resultado de três jeitos: uma frase, um gráfico e uma tabela.
   Roda no aparelho de quem usa; nada é enviado. Não é ranking de parlamentares: os números são de estados e de bancadas.
   © 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Feito com auxílio de IA (Claude). */
(function () {
  'use strict';
  var $ = function (s) { return document.querySelector(s); };
  var NS = 'http://www.w3.org/2000/svg';
  var D = null, IND = {}, ORD = [], sortCol = 'x', sortDir = -1;
  var box = $('#ce'), fx = $('#ce-x'), fy = $('#ce-y'), out = $('#ce-res'), frase = $('#ce-frase');
  if (!box) return;

  function el(t, a) {
    var e = document.createElement(t), k;
    if (a) for (k in a) { var v = a[k]; if (v == null || v === false) continue;
      if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else e.setAttribute(k, v === true ? '' : v); }
    for (var i = 2; i < arguments.length; i++) add(e, arguments[i]);
    return e;
  }
  function add(e, c) { if (c == null || c === false) return; if (Array.isArray(c)) { c.forEach(function (x) { add(e, x); }); return; } e.append(c.nodeType ? c : document.createTextNode(String(c))); }
  function sv(t, a) { var e = document.createElementNS(NS, t); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function fmt(i, v) {
    if (v == null) return 'sem dado';
    if (i.unid === '%') return v.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%';
    if (i.unid === 'R$') return 'R$ ' + Math.round(v).toLocaleString('pt-BR');
    if (i.unid === 'índice') return v.toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
    if (v >= 1e6) return (v / 1e6).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' milhões';
    return Math.round(v).toLocaleString('pt-BR');
  }
  function curtoN(i, v) { // rótulo curto para o eixo
    if (i.unid === 'R$') return 'R$ ' + (v >= 1000 ? (v / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' mil' : Math.round(v));
    if (i.unid === 'pessoas' && v >= 1e6) return (v / 1e6).toLocaleString('pt-BR', { maximumFractionDigits: 0 }) + ' mi';
    return fmt(i, v);
  }

  fetch('/dados/estados.json').then(function (r) { return r.json(); }).then(function (d) { D = d; monta(); })
    .catch(function () { frase.textContent = 'Não foi possível carregar os dados dos estados. Confira a internet e recarregue a página.'; });

  function monta() {
    D.grupos.forEach(function (g) {
      var gx = el('optgroup', { label: g.nome }), gy = el('optgroup', { label: g.nome });
      g.itens.forEach(function (i) { i.grupo = g.nome; IND[i.id] = i; ORD.push(i.id);
        gx.append(el('option', { value: i.id }, i.curto)); gy.append(el('option', { value: i.id }, i.curto)); });
      fx.append(gx); fy.append(gy);
    });
    fy.prepend(el('option', { value: '' }, 'Nenhum: só ver o primeiro em ordem'));
    var q = new URLSearchParams(location.search);
    fx.value = IND[q.get('cx')] ? q.get('cx') : 'desocupacao';
    if (!IND[fx.value]) fx.value = ORD[0];
    fy.value = q.has('cy') ? (IND[q.get('cy')] ? q.get('cy') : '') : (IND['lula-t2'] ? 'lula-t2' : '');
    fx.addEventListener('change', function () { desenha(true); });
    fy.addEventListener('change', function () { desenha(true); });
    $('#ce-trocar').addEventListener('click', function () { if (!fy.value) return; var t = fx.value; fx.value = fy.value; fy.value = t; desenha(true); });
    box.querySelectorAll('[data-cx]').forEach(function (b) {
      if (!IND[b.dataset.cx] || (b.dataset.cy && !IND[b.dataset.cy])) { b.hidden = true; return; }
      b.addEventListener('click', function () { fx.value = b.dataset.cx; fy.value = b.dataset.cy || ''; desenha(true); $('#ce-t2').focus(); });
    });
    var uf = $('#cz-uf'); if (uf) uf.addEventListener('change', function () { desenha(false); });
    box.hidden = false;
    desenha(false);
  }

  function pontos(ix, iy) {
    return Object.keys(D.ufs).map(function (u) { return { u: u, n: D.ufs[u], x: ix.v[u], y: iy ? iy.v[u] : null }; })
      .filter(function (p) { return p.x != null && (!iy || p.y != null); });
  }
  function corr(ps) {
    var n = ps.length; if (n < 5) return null;
    var mx = 0, my = 0; ps.forEach(function (p) { mx += p.x; my += p.y; }); mx /= n; my /= n;
    var a = 0, b = 0, c = 0; ps.forEach(function (p) { a += (p.x - mx) * (p.y - my); b += (p.x - mx) * (p.x - mx); c += (p.y - my) * (p.y - my); });
    return b && c ? a / Math.sqrt(b * c) : null;
  }
  function forca(r) { var a = Math.abs(r); return a < 0.2 ? 'quase nenhuma' : a < 0.4 ? 'fraca' : a < 0.7 ? 'moderada' : 'forte'; }
  function destaque() { var s = $('#cz-uf'), v = s && s.value ? s.value : new URLSearchParams(location.search).get('uf'); return v && D.ufs[v] ? v : ''; }

  function desenha(muda) {
    var ix = IND[fx.value], iy = fy.value && fy.value !== fx.value ? IND[fy.value] : null;
    if (muda) { var q = new URLSearchParams(location.search); q.set('cx', ix.id); if (iy) q.set('cy', iy.id); else q.set('cy', ''); history.replaceState(null, '', '?' + q.toString() + '#ce'); }
    var ps = pontos(ix, iy), uf = destaque();
    out.textContent = '';
    var h = el('h3', { id: 'ce-t2', tabindex: '-1' }, iy ? ix.curto + ' × ' + iy.curto : ix.curto + ', estado por estado');
    var txt;
    if (iy) {
      var r = corr(ps);
      txt = r == null ? 'Há poucos estados com os dois dados para comparar.' :
        'Nos ' + ps.length + ' estados, ' + (Math.abs(r) < 0.2 ? 'os dois dados quase não andam juntos' :
          'onde “' + ix.curto + '” é maior, “' + iy.curto + '” tende a ser ' + (r > 0 ? 'maior' : 'menor')) +
        ' (relação ' + forca(r) + ', r = ' + r.toLocaleString('pt-BR', { maximumFractionDigits: 2 }) + '). Andar junto não quer dizer que um causa o outro.';
    } else {
      var o = ps.slice().sort(function (a, b) { return b.x - a.x; });
      txt = 'Maior valor: ' + o[0].n + ' (' + fmt(ix, o[0].x) + '). Menor: ' + o[o.length - 1].n + ' (' + fmt(ix, o[o.length - 1].x) + '). Brasil: ' + fmt(ix, ix.br) + '.';
    }
    if (uf) { var pu = ps.filter(function (p) { return p.u === uf; })[0];
      if (pu) txt += ' ' + D.ufs[uf] + ': ' + fmt(ix, pu.x) + (iy ? ' e ' + fmt(iy, pu.y) : '') + '.'; }
    frase.textContent = txt;
    var fr = el('p', { class: 'cz-frase' }, txt);
    var fig = iy ? dispersao(ix, iy, ps, uf) : barras(ix, ps, uf);
    var fontes = el('ul', { class: 'ce-fontes' }, [ix, iy].filter(Boolean).map(function (i) {
      return el('li', null, el('b', null, i.nome), ' — ', i.fonte, ' (', i.quando, ').', i.desc ? ' ' + i.desc : '', ' Brasil: ', fmt(i, i.br), '.'); }));
    out.append(el('div', { class: 'cz-card cz-largo ce-card' }, h, fr, fig, tabela(ix, iy, ps, uf), el('h4', null, 'De onde vêm estes números'), fontes,
      el('p', { class: 'cz-nota' }, 'Os números são de estados e de bancadas inteiras, não notas de pessoas. O site não faz ranking de parlamentares e não diz em quem votar.')));
  }

  function dispersao(ix, iy, ps, uf) {
    var W = Math.round(Math.max(300, Math.min(720, (out.clientWidth || 640) - 40))), H = Math.round(W < 520 ? W * 1.0 : W * 0.62), m = { l: 58, r: 14, t: 16, b: 52 };
    var xs = ps.map(function (p) { return p.x; }), ys = ps.map(function (p) { return p.y; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    var px = (x1 - x0) * 0.06 || 1, py = (y1 - y0) * 0.08 || 1; x0 -= px; x1 += px; y0 -= py; y1 += py;
    var X = function (v) { return m.l + (v - x0) / (x1 - x0) * (W - m.l - m.r); }, Y = function (v) { return H - m.b - (v - y0) / (y1 - y0) * (H - m.t - m.b); };
    var s = sv('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'ce-svg', role: 'img', 'aria-label': 'Gráfico de pontos: cada ponto é um estado. Eixo horizontal: ' + ix.curto + '. Eixo vertical: ' + iy.curto + '. A tabela logo abaixo traz os mesmos números.' });
    var nk = W < 520 ? 3 : 4;
    for (var k = 0; k <= nk; k++) {
      var vx = x0 + (x1 - x0) * k / nk, vy = y0 + (y1 - y0) * k / nk;
      s.append(sv('line', { x1: X(vx), x2: X(vx), y1: m.t, y2: H - m.b, class: 'ce-grade' }), sv('line', { x1: m.l, x2: W - m.r, y1: Y(vy), y2: Y(vy), class: 'ce-grade' }));
      var tx = sv('text', { x: X(vx), y: H - m.b + 18, 'text-anchor': 'middle', class: 'ce-eixo' }); tx.textContent = curtoN(ix, vx); s.append(tx);
      var ty = sv('text', { x: m.l - 6, y: Y(vy) + 4, 'text-anchor': 'end', class: 'ce-eixo' }); ty.textContent = curtoN(iy, vy); s.append(ty);
    }
    var lx = sv('text', { x: (m.l + W - m.r) / 2, y: H - 12, 'text-anchor': 'middle', class: 'ce-rot' }); lx.textContent = '→ ' + ix.curto; s.append(lx);
    var ly = sv('text', { x: 14, y: (m.t + H - m.b) / 2, 'text-anchor': 'middle', class: 'ce-rot', transform: 'rotate(-90 14 ' + (m.t + H - m.b) / 2 + ')' }); ly.textContent = '→ ' + iy.curto; s.append(ly);
    ps.slice().sort(function (a, b) { return (a.u === uf) - (b.u === uf); }).forEach(function (p) {
      var g = sv('g', { class: 'ce-pt' + (p.u === uf ? ' ce-sel' : '') });
      var t = sv('title', {}); t.textContent = p.n + ': ' + fmt(ix, p.x) + ' e ' + fmt(iy, p.y); g.append(t);
      g.append(sv('circle', { cx: X(p.x), cy: Y(p.y), r: p.u === uf ? 15 : 12 }));
      var l = sv('text', { x: X(p.x), y: Y(p.y) + 4, 'text-anchor': 'middle' }); l.textContent = p.u; g.append(l);
      s.append(g);
    });
    if (ix.br != null && iy.br != null && ix.br >= x0 && ix.br <= x1 && iy.br >= y0 && iy.br <= y1) {
      var b = sv('g', { class: 'ce-br' }); b.append(sv('rect', { x: X(ix.br) - 6, y: Y(iy.br) - 6, width: 12, height: 12, transform: 'rotate(45 ' + X(ix.br) + ' ' + Y(iy.br) + ')' }));
      var bt = sv('text', { x: X(ix.br) + 10, y: Y(iy.br) - 8 }); bt.textContent = 'Brasil'; b.append(bt); s.append(b);
    }
    return el('figure', { class: 'ce-fig' }, s, el('figcaption', null, 'Cada bolinha é um estado (sigla). O losango é o Brasil.' + (uf ? ' Em destaque: ' + D.ufs[uf] + '.' : ' Escolha um estado em “Onde?” para destacá-lo.')));
  }

  function barras(ix, ps, uf) {
    var o = ps.slice().sort(function (a, b) { return b.x - a.x; }), max = Math.max.apply(null, o.map(function (p) { return p.x; })) || 1;
    var ul = el('ol', { class: 'ce-barras', 'aria-label': ix.curto + ', do maior para o menor' });
    o.forEach(function (p) {
      ul.append(el('li', { class: p.u === uf ? 'ce-sel' : null }, el('span', { class: 'ce-uf' }, p.n),
        el('span', { class: 'ce-trilho', 'aria-hidden': 'true' }, el('span', { class: 'ce-barra', style: 'width:' + Math.max(2, 100 * p.x / max) + '%' })),
        el('b', null, fmt(ix, p.x))));
    });
    return ul;
  }

  function tabela(ix, iy, ps, uf) {
    var cols = [['n', 'Estado'], ['x', ix.curto]].concat(iy ? [['y', iy.curto]] : []);
    if (!cols.some(function (c) { return c[0] === sortCol; })) sortCol = 'x';
    var o = ps.slice().sort(function (a, b) { var A = a[sortCol], B = b[sortCol];
      return sortCol === 'n' ? sortDir * -A.localeCompare(B, 'pt') : sortDir * (A - B); });
    var tr = el('tr');
    cols.forEach(function (c) {
      var at = sortCol === c[0] ? (sortDir < 0 ? (c[0] === 'n' ? 'ascending' : 'descending') : (c[0] === 'n' ? 'descending' : 'ascending')) : null;
      var b = el('button', { type: 'button', class: 'ce-ord' }, c[1], el('span', { class: 'visually-hidden' }, ' (ordenar)'));
      b.addEventListener('click', function () { if (sortCol === c[0]) sortDir = -sortDir; else { sortCol = c[0]; sortDir = -1; } desenha(false);
        var nb = out.querySelectorAll('.ce-ord')[cols.indexOf(c)]; if (nb) nb.focus(); });
      tr.append(el('th', { scope: 'col', 'aria-sort': at }, b));
    });
    var tb = el('tbody');
    o.forEach(function (p) { tb.append(el('tr', { class: p.u === uf ? 'ce-sel' : null }, el('th', { scope: 'row' }, p.n),
      el('td', null, fmt(ix, p.x)), iy ? el('td', null, fmt(iy, p.y)) : null)); });
    tb.append(el('tr', { class: 'ce-tbr' }, el('th', { scope: 'row' }, 'Brasil'), el('td', null, fmt(ix, ix.br)), iy ? el('td', null, fmt(iy, iy.br)) : null));
    return el('details', { class: 'ce-tab', open: iy ? null : null }, el('summary', null, 'Ver a tabela com os ' + ps.length + ' estados'),
      el('div', { class: 'ce-rolar', tabindex: '0', role: 'region', 'aria-label': 'Tabela dos estados' }, el('table', null, el('thead', null, tr), tb)));
  }
})();
