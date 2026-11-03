// Teste da sala ao vivo do Vigie a Democracia: cria uma sala, conecta o telão e 5 celulares por WebSocket e 2 por consulta,
// vota e confere os resultados. Uso: node ferramentas/teste_sala.mjs https://vigieademocracia.brunochapadeiro.workers.dev
// No GitHub Actions (.github/workflows/sala.yml), o resultado sai nas anotações da execução. A sala de teste se apaga em 6 horas.
// © 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Feito com auxílio de IA.
const B = process.argv[2] || 'http://127.0.0.1:8787';
const W = B.replace(/^http/, 'ws');
const espera = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (...a) => console.log(...a);
let falhas = 0, oks = 0; const GH = !!process.env.GITHUB_ACTIONS;
const ok = (c, m) => { if (!c) { falhas++; log((GH && falhas <= 9 ? '::error title=Sala ao vivo::' : 'FALHA ') + m); } else { oks++; log('ok', m); } };
const r = await fetch(B + '/api/sala/nova', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jogo: 'cenas' }) });
const s = await r.json(); ok(s.ok && /^[A-HJ-NP-Z2-9]{4}$/.test(s.codigo), 'cria sala ' + s.codigo);
function conecta(papel, pid) {
  return new Promise((res, rej) => {
    const q = papel === 'telao' ? `papel=telao&chave=${s.chave}` : `pid=${pid}`;
    const ws = new WebSocket(`${W}/api/sala/${s.codigo}/ws?${q}`);
    ws.ultimo = null; ws.msgs = [];
    ws.onmessage = (e) => { const d = JSON.parse(e.data); ws.msgs.push(d); if (d.tipo === 'estado') ws.ultimo = d; };
    ws.onopen = () => res(ws); ws.onerror = (e) => rej(new Error('ws erro ' + papel));
  });
}
const tel = await conecta('telao');
const cels = [];
for (let k = 0; k < 5; k++) cels.push(await conecta('plateia', 'pessoa' + k + 'abcdef'));
await espera(600);
ok(tel.ultimo && tel.ultimo.pessoas === 5, 'telão vê 5 pessoas: ' + (tel.ultimo && tel.ultimo.pessoas));
// chave errada não controla
const errada = await fetch(`${B}/api/sala/${s.codigo}/estado?papel=telao&chave=x`); ok(errada.status === 403, 'chave errada barrada');
// tela 0: escolha com 4 opções
tel.send(JSON.stringify({ c: 'tela', i: 0, tipo: 'escolha', n: 4 }));
await espera(400);
ok(cels[0].ultimo.tela.i === 0 && cels[0].ultimo.tela.fase === 'aberta', 'celular recebe tela 0 aberta');
[1, 1, 2, 1, 3].forEach((v, k) => cels[k].send(JSON.stringify({ c: 'voto', i: 0, v })));
cels[0].send(JSON.stringify({ c: 'voto', i: 0, v: 0 }));   // troca o voto
cels[1].send(JSON.stringify({ c: 'voto', i: 0, v: 9 }));   // inválido
// 2 pessoas pela consulta (sem WebSocket)
for (const pid of ['consulta1aaaaaa', 'consulta2bbbbbb']) {
  await fetch(`${B}/api/sala/${s.codigo}/estado?pid=${pid}`);
  const v = await (await fetch(`${B}/api/sala/${s.codigo}/msg?pid=${pid}`, { method: 'POST', body: JSON.stringify({ c: 'voto', i: 0, v: 1 }) })).json();
  ok(v.ok && v.meu === '1', 'voto por consulta ' + pid);
}
await espera(800);
const c = tel.ultimo.res && tel.ultimo.res.contagem;
ok(JSON.stringify(c) === JSON.stringify([1, 4, 1, 1]), 'contagem [1,4,1,1]: ' + JSON.stringify(c));
ok(tel.ultimo.respostas === 7 && tel.ultimo.pessoas === 7, `7 respostas e 7 pessoas: ${tel.ultimo.respostas} / ${tel.ultimo.pessoas}`);
ok(!cels[2].ultimo.res, 'plateia não vê resultado antes de revelar');
tel.send(JSON.stringify({ c: 'fase', fase: 'revelada' }));
await espera(400);
ok(cels[2].ultimo.tela.fase === 'revelada' && cels[2].ultimo.res && cels[2].ultimo.res.contagem[1] === 4, 'plateia vê resultado revelado');
cels[3].send(JSON.stringify({ c: 'voto', i: 0, v: 0 })); await espera(300);
ok(tel.ultimo.res.contagem[0] === 1, 'voto depois de revelar não conta');
// tela 1: nuvem
tel.send(JSON.stringify({ c: 'tela', i: 1, tipo: 'nuvem', n: 0 })); await espera(300);
const pal = [['Metas', 'pressão'], ['metas!', 'cuidado'], ['METAS', 'merda'], ['chefe idiota'], ['pressão', 'https://x.com', '12345', 'a', 'b', 'c']];
pal.forEach((ps, k) => ps.forEach((p) => cels[k].send(JSON.stringify({ c: 'voto', i: 1, v: p }))));
await espera(800);
const nv = Object.fromEntries(tel.ultimo.res.palavras);
ok(nv.metas === 3 && nv['pressão'] === 2 && nv.cuidado === 1 && !nv.merda && !nv['chefe idiota'], 'nuvem: ' + JSON.stringify(tel.ultimo.res.palavras));
ok(!('https://x.com' in nv) && !('12345' in nv) && !('c' in nv), 'nuvem: links, números e a 4ª palavra fora');
tel.send(JSON.stringify({ c: 'oculta', p: 'cuidado' })); await espera(300);
ok(!tel.ultimo.res.palavras.some((x) => x[0] === 'cuidado'), 'quem apresenta esconde palavra');
// tela 2: ordenar 3 itens
tel.send(JSON.stringify({ c: 'tela', i: 2, tipo: 'ordenar', n: 3 })); await espera(300);
cels[0].send(JSON.stringify({ c: 'voto', i: 2, v: [0, 1, 2] }));
cels[1].send(JSON.stringify({ c: 'voto', i: 2, v: [1, 0, 2] }));
cels[2].send(JSON.stringify({ c: 'voto', i: 2, v: [0, 0, 2] }));   // inválido
await espera(700);
ok(JSON.stringify(tel.ultimo.res.media) === JSON.stringify([1.5, 1.5, 3]) && tel.ultimo.res.total === 2, 'ordenar média ' + JSON.stringify(tel.ultimo.res.media));
// escala
tel.send(JSON.stringify({ c: 'tela', i: 3, tipo: 'escala', n: 4 })); await espera(300);
cels.forEach((w, k) => w.send(JSON.stringify({ c: 'voto', i: 3, v: k % 4 }))); await espera(600);
ok(JSON.stringify(tel.ultimo.res.contagem) === JSON.stringify([2, 1, 1, 1]), 'escala ' + JSON.stringify(tel.ultimo.res.contagem));
// fim com histórico
tel.send(JSON.stringify({ c: 'tela', i: 'fim', tipo: 'fim', n: 0 })); await espera(400);
ok(cels[4].ultimo.tela.tipo === 'fim', 'plateia recebe o fim');
ok(Array.isArray(tel.ultimo.historico) && tel.ultimo.historico.length === 4, 'histórico com 4 telas');
// celular não controla
cels[0].send(JSON.stringify({ c: 'tela', i: 0, tipo: 'escolha', n: 4 })); await espera(300);
ok(tel.ultimo.tela.tipo === 'fim', 'celular não troca a tela');
// sala inexistente e código inválido
ok((await fetch(`${B}/api/sala/ZZZZ/estado`)).status === 404, 'sala inexistente 404');
ok((await fetch(`${B}/api/sala/ab1/estado`)).status === 400, 'código inválido 400');
// reconexão do celular mantém o voto
cels[1].close(); await espera(300);
const volta = await conecta('plateia', 'pessoa1abcdef'); await espera(300);
ok(volta.ultimo && volta.ultimo.tela.tipo === 'fim', 'reconecta');
for (const w of [tel, volta, ...cels]) try { w.close(); } catch (e) {}
log((GH ? (falhas ? '::error title=Sala ao vivo::' : '::notice title=Sala ao vivo::') : '') + (falhas ? `${falhas} falha(s), ${oks} ok` : `TUDO OK: ${oks} conferências, sala ${s.codigo}`));
process.exit(falhas ? 1 : 0);
