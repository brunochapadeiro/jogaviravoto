/* Vigie a Democracia: Cruze os dados. Junta, no aparelho de quem usa, os votos da Câmara e do Senado (dados abertos),
   a urna do TSE, os eleitos de 2026 e estudos científicos. Nada sai do aparelho: as respostas do teste ficam só nele.
   © 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Feito com auxílio de IA (Claude). */
(function () {
  'use strict';
  var CZ = window.CZ;
  var $ = function (s) { return document.querySelector(s); };
  function el(t, a) {
    var e = document.createElement(t), k;
    if (a) for (k in a) { var v = a[k]; if (v == null || v === false) continue;
      if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else e.setAttribute(k, v === true ? '' : v); }
    for (var i = 2; i < arguments.length; i++) add(e, arguments[i]);
    return e;
  }
  function add(e, c) { if (c == null || c === false) return; if (Array.isArray(c)) { c.forEach(function (x) { add(e, x); }); return; } e.append(c.nodeType ? c : document.createTextNode(String(c))); }
  function pct(a, b) { return b ? Math.round(1000 * a / b) / 10 : 0; }
  function fP(n) { return n.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%'; }
  function fN(n) { return n.toLocaleString('pt-BR'); }
  function dBR(d) { return d.slice(8, 10) + '/' + d.slice(5, 7) + '/' + d.slice(0, 4); }
  var CASA = { C: 'Câmara', S: 'Senado' }, NA = { C: 'na Câmara', S: 'no Senado' }, TODA = { C: 'Toda a Câmara', S: 'Todo o Senado' },
      INTEIRA = { C: 'Na Câmara inteira', S: 'No Senado inteiro' }, DA = { C: 'da Câmara', S: 'do Senado' }, QUEM = { C: ['deputado', 'deputados', 'deputada ou deputado'], S: ['senador', 'senadores', 'senadora ou senador'] };
  var NOME = { 'LULA': 'Lula', 'FLAVIO BOLSONARO': 'Flávio Bolsonaro', 'RONALDO CAIADO': 'Ronaldo Caiado', 'ESCRITOR AUGUSTO CURY': 'Augusto Cury' };
  function nome(n) { return NOME[n] || n.toLowerCase().replace(/(^|\s)\S/g, function (m) { return m.toUpperCase(); }); }
  var NO_CONGRESSO = { 'Deputado Federal': 1, 'Senador': 1, 'mandato-2031': 1 };
  var P = null, U = null, R = {}, ultimo = null;
  try { R = JSON.parse(localStorage.getItem('vv-respostas') || '{}') || {}; } catch (e) { R = {}; }
  var form = $('#cz-form'), out = $('#cz-res'), aviso = $('#cz-aviso'), resumo = $('#cz-resumo');

  Promise.all([fetch('/dados/parlamentares.json').then(function (r) { return r.json(); }), fetch('/dados/cruzar.json').then(function (r) { return r.json(); })])
    .then(function (x) { P = x[0]; U = x[1]; monta(); })
    .catch(function () { aviso.textContent = 'Não foi possível carregar os dados. Confira a internet e recarregue a página.'; });

  function opcao(sel, v, t) { sel.append(el('option', { value: v }, t)); }

  function monta() {
    var q = new URLSearchParams(location.search);
    var uf = $('#cz-uf'), as = $('#cz-as'), pt = $('#cz-pt');
    opcao(uf, 'BR', 'Brasil (todos os estados)');
    Object.keys(U.ufs).sort(function (a, b) { return U.ufs[a].nome.localeCompare(U.ufs[b].nome, 'pt'); })
      .forEach(function (k) { opcao(uf, k, U.ufs[k].nome); });
    CZ.ordem.forEach(function (a) {
      var n = P.perguntas.filter(function (p) { return p.tema === a; }).length;
      if (n) opcao(as, a, a + ' (' + n + (n === 1 ? ' votação)' : ' votações)'));
    });
    var conta = {};
    P.fichas.forEach(function (f) { if (f.partido) conta[f.partido] = (conta[f.partido] || 0) + 1; });
    opcao(pt, '', 'Todos os partidos');
    Object.keys(conta).sort(function (a, b) { return conta[b] - conta[a] || a.localeCompare(b); }).forEach(function (k) { opcao(pt, k, k); });
    if (q.get('uf') && (U.ufs[q.get('uf')] || q.get('uf') === 'BR')) uf.value = q.get('uf');
    if (q.get('assunto') && CZ.ordem.indexOf(q.get('assunto')) >= 0) as.value = q.get('assunto');
    if (q.get('partido') && conta[q.get('partido')]) pt.value = q.get('partido');
    var casa = q.get('casa'); if (casa === 'C' || casa === 'S') form.querySelector('input[name="casa"][value="' + casa + '"]').checked = true;
    var nr = Object.keys(R).length, eu = $('#cz-eu');
    if (nr >= 3) { eu.disabled = false; $('#cz-eu-txt').textContent = 'Você respondeu ' + nr + ' afirmações do teste neste aparelho.'; if (q.get('eu') === '1') eu.checked = true; }
    form.addEventListener('change', calcula);
    form.addEventListener('submit', function (e) { e.preventDefault(); calcula(); var h = out.querySelector('h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus(); } });
    aviso.textContent = '';
    form.hidden = false;
    calcula();
  }

  function estado() {
    return { uf: $('#cz-uf').value, as: $('#cz-as').value, pt: $('#cz-pt').value,
             casa: (form.querySelector('input[name="casa"]:checked') || {}).value || 'CS', eu: $('#cz-eu').checked };
  }

  function escolhe(f, s) { return (s.uf === 'BR' || f.uf === s.uf) && (!s.pt || f.partido === s.pt) && (s.casa === 'CS' || f.casa === s.casa); }

  function conta(fichas, k) {
    var c = { S: 0, N: 0, O: 0, F: 0 };
    fichas.forEach(function (f) { var v = f.chave[k];
      if (v === 'S' || v === 'N') c[v]++; else if (v === 'A' || v === 'O' || v === 'P' || v === 'R') c.O++; else if (v === 'F' || v === 'J' || v === '.') c.F++; });
    c.votou = c.S + c.N + c.O; c.tot = c.votou + c.F;
    return c;
  }

  function lugar(s) { return s.uf === 'BR' ? (s.pt ? 'no Brasil' : '') : U.ufs[s.uf].em; }
  function deUF(s) { return s.uf === 'BR' ? '' : U.ufs[s.uf].em.replace(/^no /, 'do ').replace(/^na /, 'da ').replace(/^em /, 'de '); }
  function doPartido(s) { return s.pt ? 'do ' + s.pt : ''; }
  function junta() { return Array.prototype.filter.call(arguments, Boolean).join(' '); }

  function barra(c, rot) {
    var t = c.tot || 1, partes = [['S', 'Sim', c.S], ['N', 'Não', c.N], ['O', 'Abstenção ou obstrução', c.O], ['F', 'Ausente ou não votou', c.F]];
    var desc = rot + ': ' + partes.filter(function (p) { return p[2]; }).map(function (p) { return p[1] + ' ' + fN(p[2]); }).join(', ') + '.';
    var b = el('div', { class: 'cz-barra', role: 'img', 'aria-label': desc });
    partes.forEach(function (p) { if (p[2]) b.append(el('span', { class: 'cz-' + p[0], style: 'width:' + (100 * p[2] / t) + '%' })); });
    var leg = el('p', { class: 'cz-leg', 'aria-hidden': 'true' }, el('b', null, rot), ' ',
      partes.filter(function (p) { return p[2]; }).map(function (p) { return el('span', { class: 'cz-l cz-l' + p[0] }, p[1] + ' ' + fN(p[2])); }));
    return [b, leg];
  }

  function calcula() {
    if (!P) return;
    var s = estado(); ultimo = null;
    var qs = new URLSearchParams(); qs.set('uf', s.uf); qs.set('assunto', s.as); if (s.pt) qs.set('partido', s.pt); if (s.casa !== 'CS') qs.set('casa', s.casa); if (s.eu) qs.set('eu', '1');
    try { history.replaceState(null, '', '?' + qs.toString()); } catch (e) {}
    var sel = P.fichas.filter(function (f) { return escolhe(f, s); });
    var votos = [];
    P.perguntas.forEach(function (q, k) {
      if (q.tema !== s.as) return;
      Object.keys(q.casas).forEach(function (h) {
        if (s.casa !== 'CS' && s.casa !== h) return;
        var fs = sel.filter(function (f) { return f.casa === h; });
        votos.push({ q: q, k: k, h: h, c: conta(fs, k), br: conta(P.fichas.filter(function (f) { return f.casa === h; }), k), fs: fs });
      });
    });
    votos.sort(function (a, b) { return b.q.casas[b.h].data.localeCompare(a.q.casas[a.h].data); });
    out.replaceChildren();
    var com = votos.filter(function (v) { return v.c.votou > 0; });
    if (!com.length) {
      out.append(el('section', { class: 'cz-card' }, el('h2', null, 'Nenhum voto nesta combinação'),
        el('p', null, 'Não há ' + (s.pt ? 'parlamentares do ' + s.pt + ' ' : 'parlamentares ') + (s.uf === 'BR' ? '' : U.ufs[s.uf].em + ' ') +
          'que tenham votado ' + (s.casa === 'CS' ? '' : NA[s.casa] + ' ') + 'sobre ' + s.as + '. Troque o partido, a Casa ou o assunto.')));
      resumo.textContent = 'Nenhum voto nesta combinação.';
      urna(s); novo(s, null); ciencia(s); aprofunde(s);
      return;
    }
    var recente = function (q) { return Object.keys(q.casas).map(function (h) { return q.casas[h].data; }).sort().pop(); };
    var v0 = com.slice().sort(function (a, b) { return recente(b.q).localeCompare(recente(a.q)) || b.c.votou - a.c.votou; })[0];
    var q0 = v0.q, h0 = v0.h, c0 = v0.c, quem = QUEM[h0][1];
    var p0 = pct(c0.S, c0.votou), pb = pct(v0.br.S, v0.br.votou);
    var grupo = junta(quem, doPartido(s), deUF(s));
    var frase = 'Dos ' + fN(c0.votou) + ' ' + grupo + ' que votaram, ' + fN(c0.S) + ' disseram Sim e ' + fN(c0.N) + ' disseram Não' +
      (c0.O ? ' (' + fN(c0.O) + (c0.O === 1 ? ' se absteve ou obstruiu)' : ' se abstiveram ou obstruíram)') : '') + '.';
    var comp = (s.uf === 'BR' && !s.pt) ? '' : INTEIRA[h0] + ', ' + fP(pb) + ' votaram Sim.';
    ultimo = { s: s, q: q0, h: h0, p: p0, pb: pb, frase: frase, comp: comp, rot: 'dos ' + grupo + ' que votaram disseram Sim', c: c0, br: v0.br };
    // 1. o novo dado
    var cab = el('section', { class: 'cz-card cz-novo', 'aria-labelledby': 'cz-t1' },
      el('p', { class: 'cz-kicker' }, 'O dado que você cruzou'),
      el('h2', { id: 'cz-t1' }, q0.curto + ' · ' + CASA[h0] + ', ' + dBR(q0.casas[h0].data)),
      el('p', { class: 'cz-num' }, el('b', null, fP(p0)), el('span', null, ' ' + ultimo.rot)),
      el('p', { class: 'cz-frase' }, frase, ' ', comp),
      el('details', { class: 'cz-o-que' }, el('summary', null, 'O que foi votado'), el('p', null, q0.explica),
        el('p', null, el('a', { href: q0.casas[h0].url, target: '_blank', rel: 'noopener' }, 'Ver a votação no site ' + DA[h0], el('span', { class: 'visually-hidden' }, ' (abre outro site)')))),
      reeleitos(v0, s));
    out.append(cab);
    resumo.textContent = q0.curto + ': ' + fP(p0) + ' ' + ultimo.rot + '.';
    compartilha();
    // 2. todas as votações do assunto
    var lista = el('section', { class: 'cz-card cz-largo', 'aria-labelledby': 'cz-t2' }, el('h2', { id: 'cz-t2' }, 'Todas as votações sobre ' + s.as),
      el('p', { class: 'cz-nota' }, 'Cada barra é um voto do plenário. Partido atual de cada parlamentar; alguns mudaram de partido desde a votação.'));
    var ul = el('ul', { class: 'cz-votos' });
    votos.forEach(function (v) {
      var li = el('li', null, el('h3', null, v.q.curto + ' · ' + CASA[v.h] + ', ' + dBR(v.q.casas[v.h].data)), el('p', { class: 'cz-af' }, '“' + v.q.afirmacao + '”'));
      if (v.c.tot) add(li, barra(v.c, s.uf === 'BR' && !s.pt ? TODA[v.h] : junta('Seleção:', doPartido(s), lugar(s))));
      else li.append(el('p', { class: 'cz-nota' }, 'Ninguém desta seleção estava no mandato nesta votação.'));
      if (s.uf !== 'BR' || s.pt) add(li, barra(v.br, TODA[v.h]));
      if (s.uf !== 'BR' && !s.pt && v.c.votou) li.append(partidos(v));
      li.append(el('p', { class: 'cz-fonte' }, el('a', { href: v.q.casas[v.h].url, target: '_blank', rel: 'noopener' }, 'Fonte: ' + CASA[v.h] + ', votação de ' + dBR(v.q.casas[v.h].data), el('span', { class: 'visually-hidden' }, ' (abre outro site)'))));
      ul.append(li);
    });
    lista.append(ul); out.append(lista);
    // 3. você x bancada
    if (s.eu) out.append(voce(s, sel));
    bancada(s, sel); urna(s); novo(s, sel); aprofunde(s); ciencia(s);
  }

  function partidos(v) {
    var m = {};
    v.fs.forEach(function (f) { var x = f.chave[v.k]; if (x !== 'S' && x !== 'N') return; m[f.partido] = m[f.partido] || { S: 0, N: 0 }; m[f.partido][x]++; });
    var ks = Object.keys(m).sort(function (a, b) { return (m[b].S + m[b].N) - (m[a].S + m[a].N) || a.localeCompare(b); });
    var t = el('table', { class: 'cz-tab' }, el('caption', { class: 'visually-hidden' }, 'Votos por partido atual'),
      el('thead', null, el('tr', null, el('th', { scope: 'col' }, 'Partido atual'), el('th', { scope: 'col' }, 'Sim'), el('th', { scope: 'col' }, 'Não'))));
    var tb = el('tbody'); ks.forEach(function (k) { tb.append(el('tr', null, el('th', { scope: 'row' }, k), el('td', null, fN(m[k].S)), el('td', null, fN(m[k].N)))); });
    t.append(tb);
    return el('details', { class: 'cz-part' }, el('summary', null, 'Por partido'), el('div', { class: 'cz-tab-w' }, t));
  }

  function reeleitos(v, s) {
    function grupo(letra) {
      var fs = v.fs.filter(function (f) { return f.chave[v.k] === letra; });
      var n = fs.filter(function (f) { return NO_CONGRESSO[f.e26]; }).length;
      return [fs.length, n];
    }
    var a = grupo('S'), b = grupo('N');
    if (!a[0] && !b[0]) return null;
    function linha(rot, g) { return g[0] ? el('li', null, el('b', null, rot + ': '), fN(g[1]) + ' de ' + fN(g[0]) + ' (' + fP(pct(g[1], g[0])) + ') estarão no Congresso em 2027') : null; }
    return el('div', { class: 'cz-cruza' }, el('h3', null, 'Cruzamento: quem votou assim volta em 2027?'),
      el('ul', null, linha('Votaram Sim', a), linha('Votaram Não', b)),
      el('p', { class: 'cz-nota' }, 'Conta quem foi eleito em 2026 e os senadores com mandato até 2031. Quem não volta pode não ter se candidatado. Fontes: Câmara, Senado e TSE.'));
  }

  function voce(s, sel) {
    var qsA = P.perguntas.map(function (q, k) { return [q, k]; }).filter(function (x) { return R[x[0].id] && x[0].tema === s.as; });
    var todo = !qsA.length;
    if (todo) qsA = P.perguntas.map(function (q, k) { return [q, k]; }).filter(function (x) { return R[x[0].id]; });
    var maioria = 0, metade = 0, minoria = 0;
    sel.forEach(function (f) { var n = 0, ig = 0;
      qsA.forEach(function (x) { var v = f.chave[x[1]]; if (!x[0].casas[f.casa] || (v !== 'S' && v !== 'N')) return; n++; if (v === R[x[0].id]) ig++; });
      if (!n) return; if (ig * 2 > n) maioria++; else if (ig * 2 === n) metade++; else minoria++; });
    var t = maioria + metade + minoria;
    var sec = el('section', { class: 'cz-card cz-voce', 'aria-labelledby': 'cz-t3' }, el('h2', { id: 'cz-t3' }, 'Você e esta bancada'));
    if (!t) { sec.append(el('p', null, 'Ninguém desta seleção votou nas afirmações que você respondeu. Troque o assunto ou responda mais no teste.')); return sec; }
    sec.append(el('p', { class: 'cz-num' }, el('b', null, fN(maioria)), el('span', null, ' de ' + fN(t) + ' votaram como você na maioria das vezes')),
      el('p', null, (todo ? 'Você não respondeu às afirmações sobre ' + s.as + '; a conta usa todas as ' + qsA.length + ' que você respondeu. ' : 'Nas ' + qsA.length + ' afirmações sobre ' + s.as + ' que você respondeu. ') +
        fN(metade) + ' concordaram com você em metade dos votos e ' + fN(minoria) + ' em menos da metade. Suas respostas ficam só neste aparelho.'),
      el('p', null, el('a', { href: '/vota-como-voce' }, 'Ver nome a nome no teste Quem vota como você?')));
    return sec;
  }

  function bancada(s, sel) {
    function soma(fs) { var a = 0, b = 0, c = 0, d = 0; fs.forEach(function (f) { a += f.part.votou; b += f.part.n; c += f.gov.igual; d += f.gov.n; }); return { pres: pct(a, b), gov: pct(c, d), n: fs.length }; }
    var casaF = function (f) { return s.casa === 'CS' || f.casa === s.casa; };
    var x = soma(sel.filter(function (f) { return f.part.n; })), br = soma(P.fichas.filter(function (f) { return casaF(f) && f.part.n; }));
    var sec = el('section', { class: 'cz-card', 'aria-labelledby': 'cz-t4' }, el('h2', { id: 'cz-t4' }, 'A bancada nos 4 anos (2023 a 2026)'),
      el('dl', { class: 'cz-dl' },
        el('div', null, el('dt', null, 'Parlamentares na seleção'), el('dd', null, fN(x.n))),
        el('div', null, el('dt', null, 'Presença nas votações'), el('dd', null, fP(x.pres), el('small', null, 'Congresso: ' + fP(br.pres)))),
        el('div', null, el('dt', null, 'Votou como o governo orientou'), el('dd', null, fP(x.gov), el('small', null, 'Congresso: ' + fP(br.gov))))),
      el('p', { class: 'cz-nota' }, 'Inclui suplentes que exerceram o mandato. Presença: votações nominais em que a pessoa votou, entre as que ocorreram no seu mandato. Dados abertos da Câmara e do Senado até ' + dBR(P.atualizado) + '. Sem ranking: ',
        el('a', { href: '/parlamentares' }, 'veja a ficha de cada um'), '.'));
    out.append(sec);
  }

  function urna(s) {
    var d = s.uf === 'BR' ? U.br : U.ufs[s.uf], br = U.br;
    var sec = el('section', { class: 'cz-card', 'aria-labelledby': 'cz-t5' }, el('h2', { id: 'cz-t5' }, 'A urna ' + d.em + ' (Presidente, 2026)'));
    var c = d.t2.cand;
    var b = el('div', { class: 'cz-barra cz-urna', role: 'img', 'aria-label': '2º turno ' + d.em + ': ' + c.map(function (x) { return nome(x.nome) + ' ' + fP(x.pct); }).join(', ') });
    c.forEach(function (x, i) { b.append(el('span', { class: 'cz-u' + (x.nome === 'LULA' ? 'L' : 'F'), style: 'width:' + x.pct + '%' })); });
    sec.append(el('h3', null, '2º turno, 25/10'), b,
      el('p', { class: 'cz-leg', 'aria-hidden': 'true' }, c.map(function (x) { return el('span', { class: 'cz-l cz-lu' + (x.nome === 'LULA' ? 'L' : 'F') }, nome(x.nome) + ' ' + fP(x.pct)); })),
      el('p', null, 'Abstenção: ' + fP(d.t2.abst) + ' dos ' + fN(d.t2.eleitores) + ' eleitores.' + (s.uf === 'BR' ? '' : ' No Brasil: ' + nome(br.t2.cand[0].nome) + ' ' + fP(br.t2.cand[0].pct) + ', ' + nome(br.t2.cand[1].nome) + ' ' + fP(br.t2.cand[1].pct) + '.')),
      el('h3', null, '1º turno, 4/10'),
      el('p', null, d.t1.cand.map(function (x) { return nome(x.nome) + ' ' + fP(x.pct); }).join(' · ') + '. Abstenção: ' + fP(d.t1.abst) + '.'),
      el('p', { class: 'cz-fonte' }, 'Fonte: TSE, arquivos oficiais de divulgação (totalização de 100% das seções). ', el('a', { href: '/apuracao' }, 'Veja a apuração completa')));
    out.append(sec);
  }

  function novo(s, sel) {
    var d = s.uf === 'BR' ? U.br : U.ufs[s.uf];
    var sec = el('section', { class: 'cz-card', 'aria-labelledby': 'cz-t6' }, el('h2', { id: 'cz-t6' }, 'O Congresso que começa em 2027 ' + d.em));
    function chips(obj, rot) {
      var ks = Object.keys(obj); if (!ks.length) return null;
      var tot = ks.reduce(function (a, k) { return a + obj[k]; }, 0);
      return [el('h3', null, rot + ' eleitos em 2026: ' + fN(tot)), el('ul', { class: 'cz-chips' }, ks.map(function (k) {
        return el('li', { class: k === s.pt ? 'on' : null }, el('b', null, k), ' ' + fN(obj[k])); }))];
    }
    add(sec, chips(d.eleitos.C, 'Deputados federais'));
    add(sec, chips(d.eleitos.S, 'Senadores'));
    if (s.pt) {
      var hoje = P.fichas.filter(function (f) { return f.casa === 'C' && f.situacao === 'Exercício' && f.partido === s.pt && (s.uf === 'BR' || f.uf === s.uf); }).length;
      var depois = d.eleitos.C[s.pt] || 0;
      sec.append(el('p', { class: 'cz-frase' }, 'O ' + s.pt + ' tem hoje ' + fN(hoje) + (hoje === 1 ? ' deputado em exercício ' : ' deputados em exercício ') + d.em + ' e elegeu ' + fN(depois) + ' para a próxima legislatura.'));
    }
    sec.append(el('p', { class: 'cz-fonte' }, 'Fonte: TSE, candidatos eleitos em 2026. ', el('a', { href: '/congresso' }, 'Veja o Raio-X do novo Congresso')));
    out.append(sec);
  }

  function ciencia(s) {
    var L = CZ.sci[s.as] || [];
    var sec = el('section', { class: 'cz-card cz-ciencia cz-largo', 'aria-labelledby': 'cz-t7' }, el('h2', { id: 'cz-t7' }, 'O que diz a ciência sobre ' + s.as));
    if (!L.length) { sec.append(el('p', null, CZ.sem[s.as] || 'Não encontramos estudo científico que meça diretamente o efeito destas votações. As fontes aqui são os registros oficiais.')); out.append(sec); return; }
    var ul = el('ul', { class: 'cz-sci' });
    L.forEach(function (e) {
      ul.append(el('li', null, el('p', { class: 'cz-tipo' }, e.tipo), el('p', null, e.achado),
        el('p', { class: 'cz-fonte' }, e.ref + '. ', el('a', { href: 'https://doi.org/' + e.doi, target: '_blank', rel: 'noopener', lang: 'en' }, e.titulo, el('span', { class: 'visually-hidden', lang: 'pt-BR' }, ' (abre outro site)')))));
    });
    sec.append(ul, el('p', { class: 'cz-nota' }, 'Estudos revisados por pares, conferidos no PubMed ou na página da revista. Estudo observacional mostra associação, não prova sozinho a causa.'));
    out.append(sec);
  }

  function aprofunde(s) {
    var L = CZ.links[s.as] || [], t = CZ.tema[s.as];
    var sec = el('section', { class: 'cz-card', 'aria-labelledby': 'cz-t8' }, el('h2', { id: 'cz-t8' }, 'Jogue e aprofunde'));
    var ul = el('ul', { class: 'cz-links' });
    L.forEach(function (x) { ul.append(el('li', null, el('a', { href: x.h }, el('span', { class: 'fmt' }, x.f), el('b', null, x.n)))); });
    sec.append(ul);
    if (t) sec.append(el('p', null, el('a', { class: 'btn', href: '/tema/' + t.id }, 'Tudo sobre ' + t.nome)));
    out.append(sec);
  }

  function publico() { var u = new URL(location.href); u.searchParams.delete('eu'); return u.toString(); }
  function texto() {
    var u = ultimo; if (!u) return '';
    return u.q.curto + ' (' + CASA[u.h] + '): ' + u.frase + (u.comp ? ' ' + u.comp : '') + '\nFontes: dados abertos da Câmara e do Senado e TSE.\nCruze você também: ' + publico();
  }

  function compartilha() {
    if (!ultimo) return;
    var sec = el('section', { class: 'cz-card cz-comp cz-largo', 'aria-labelledby': 'cz-t9' }, el('h2', { id: 'cz-t9' }, 'Leve este cruzamento'),
      el('p', null, 'O card sai com a fonte, a licença e o endereço do site, pronto para o Instagram e o WhatsApp.'));
    var st = el('p', { class: 'cz-st', 'aria-live': 'polite' });
    var b1 = el('button', { type: 'button', class: 'btn forte' }, 'Baixar o card (imagem)');
    var b2 = el('button', { type: 'button', class: 'btn' }, 'Copiar o texto');
    var b3 = el('a', { class: 'btn', href: 'https://wa.me/?text=' + encodeURIComponent(texto()), target: '_blank', rel: 'noopener' }, 'Mandar no WhatsApp');
    var b4 = el('button', { type: 'button', class: 'btn' }, 'Copiar o link');
    b1.addEventListener('click', function () { card().then(function () { st.textContent = 'Card baixado.'; }, function () { st.textContent = 'Não foi possível gerar a imagem neste navegador.'; }); });
    b2.addEventListener('click', function () { copia(texto(), st, 'Texto copiado.'); });
    b4.addEventListener('click', function () { copia(publico(), st, 'Link copiado.'); });
    sec.append(el('p', { class: 'acoes' }, b1, b2, b3, b4), st);
    out.append(sec);
  }

  function copia(t, st, ok) {
    function velho() { var a = el('textarea'); a.value = t; document.body.append(a); a.select(); try { document.execCommand('copy'); st.textContent = ok; } catch (e) { st.textContent = 'Copie manualmente: ' + t; } a.remove(); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { st.textContent = ok; }, velho); else velho();
  }

  // card 1080x1350 para as redes, com a marca d'água, a licença e o endereço
  function card() {
    var u = ultimo, W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    var g = cv.getContext('2d');
    var fontes = document.fonts ? Promise.all(['800 120px Lexend', '700 40px Lexend', '400 34px "Atkinson Hyperlegible"', '700 34px "Atkinson Hyperlegible"'].map(function (f) { return document.fonts.load(f); })) : Promise.resolve();
    return fontes.then(function () {
      g.fillStyle = '#FBF8F1'; g.fillRect(0, 0, W, H);
      g.save(); g.fillStyle = 'rgba(20,24,30,.05)'; g.font = '700 26px "Atkinson Hyperlegible", sans-serif'; g.rotate(-Math.PI / 6);
      for (var y = -200; y < 2200; y += 190) for (var x = -900; x < 1500; x += 430) g.fillText('Prof. Bruno Chapadeiro', x, y);
      g.restore();
      g.fillStyle = '#FFE58F'; g.strokeStyle = '#17191E'; g.lineWidth = 4;
      g.fillRect(70, 70, 470, 70); g.strokeRect(70, 70, 470, 70);
      g.fillStyle = '#17191E'; g.font = '700 34px Lexend, sans-serif'; g.fillText('CRUZE OS DADOS', 96, 118);
      g.fillStyle = '#B3261E'; g.font = '700 34px "Atkinson Hyperlegible", sans-serif';
      var y0 = quebra(g, (u.q.curto + ' · ' + CASA[u.h]).toUpperCase(), 70, 220, 940, 44);
      g.fillStyle = '#17191E'; g.font = '800 200px Lexend, sans-serif'; g.fillText(fP(u.p), 62, y0 + 200);
      g.font = '700 44px Lexend, sans-serif';
      var y1 = quebra(g, u.rot + (u.s.uf === 'BR' && !u.s.pt ? ' ' + NA[u.h] : ''), 70, y0 + 280, 940, 56);
      g.fillStyle = '#2A2D35'; g.font = '400 36px "Atkinson Hyperlegible", sans-serif';
      var y2 = quebra(g, u.frase + (u.comp ? ' ' + u.comp : ''), 70, y1 + 34, 940, 48);
      g.fillStyle = '#4A4D57'; g.font = '400 28px "Atkinson Hyperlegible", sans-serif';
      var y3 = quebra(g, 'Fontes: dados abertos da Câmara e do Senado (votação de ' + dBR(u.q.casas[u.h].data) + ') e TSE.', 70, Math.min(y2 + 16, 960), 940, 36);
      // barras: a seleção e a Casa inteira
      var yb = Math.min(Math.max(y3, 900), 960), wb = 640;
      function barras(c, rot, y) {
        var t = c.tot || 1, x = 70, cores = [['S', '#1F6F3A'], ['N', '#B3261E'], ['O', '#B07A12'], ['F', '#9A9DA5']];
        g.fillStyle = '#17191E'; g.font = '700 24px "Atkinson Hyperlegible", sans-serif'; g.fillText(rot + ': Sim ' + fN(c.S) + ' (verde) · Não ' + fN(c.N) + ' (vermelho)', 70, y);
        cores.forEach(function (k) { var w = wb * c[k[0]] / t; if (w > 0) { g.fillStyle = k[1]; g.fillRect(x, y + 12, w, 30); x += w; } });
        return y + 80;
      }
      var yy = barras(u.c, 'Seleção', yb + 24);
      if (u.s.uf !== 'BR' || u.s.pt) yy = barras(u.br, u.h === 'C' ? 'Câmara inteira' : 'Senado inteiro', yy);
      g.fillStyle = '#4A4D57'; g.font = '400 20px "Atkinson Hyperlegible", sans-serif'; g.fillText('Cinza: ausente ou não votou.', 70, Math.min(yy - 10, 1160));
      // QR code do cruzamento
      if (window.qrcode) {
        var qr = window.qrcode(0, 'M'); qr.addData(publico()); qr.make();
        var n = qr.getModuleCount(), lado = 190, m = lado / (n + 8), qx = W - 70 - lado, qy = Math.min(Math.max(y3, 900), 950);
        g.fillStyle = '#FFFFFF'; g.fillRect(qx, qy, lado, lado); g.fillStyle = '#17191E';
        for (var r = 0; r < n; r++) for (var cc = 0; cc < n; cc++) if (qr.isDark(r, cc)) g.fillRect(qx + (cc + 4) * m, qy + (r + 4) * m, Math.ceil(m), Math.ceil(m));
        g.font = '700 20px "Atkinson Hyperlegible", sans-serif'; g.textAlign = 'center'; g.fillText('Cruze você também', qx + lado / 2, qy + lado + 26); g.textAlign = 'left';
      }
      g.fillStyle = '#17191E'; g.fillRect(0, H - 170, W, 170);
      g.fillStyle = '#FFE58F'; g.font = '700 22px "Atkinson Hyperlegible", sans-serif'; g.fillText('Adoeceu pelo trabalho? Caminhos do Trabalho UFF acolhe: WhatsApp (24) 98809-1268', 70, H - 126);
      g.fillStyle = '#FBF8F1'; g.font = '700 40px "Atkinson Hyperlegible", sans-serif'; g.fillText('@brunochapadeiro', 70, H - 74);
      g.font = '400 26px "Atkinson Hyperlegible", sans-serif'; g.fillText('vigieademocracia.brunochapadeiro.workers.dev/cruzar', 70, H - 32);
      g.textAlign = 'right'; g.fillText('© Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0', W - 70, H - 74);
      g.textAlign = 'left';
      return new Promise(function (ok, erro) {
        cv.toBlob(function (b) { if (!b) return erro(); var a = document.createElement('a'); a.href = URL.createObjectURL(b);
          a.download = 'Cruze_os_dados_' + (u.s.uf) + '_' + u.q.id + '.png'; document.body.append(a); a.click(); a.remove();
          setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000); ok(); }, 'image/png');
      });
    });
  }

  function quebra(g, t, x, y, w, lh) {
    var ps = t.split(' '), l = '';
    for (var i = 0; i < ps.length; i++) { var tst = l ? l + ' ' + ps[i] : ps[i]; if (g.measureText(tst).width > w && l) { g.fillText(l, x, y); y += lh; l = ps[i]; } else l = tst; }
    if (l) { g.fillText(l, x, y); y += lh; }
    return y;
  }
})();
