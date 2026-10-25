// Site dos Games Vira-Voto (Cloudflare Worker com arquivos estáticos em public/) + placar público.
// O placar conta acessos, curtidas, comentários (toques em Comentar no Instagram), reposts, compartilhamentos, partidas,
// pessoas atendidas e leituras da Cartilha, da Apostila e do Guia.
// Não guarda IP, nome nem cookie: só números. Fica num Durable Object com SQLite, que já vem no plano grátis
// e não precisa de nenhum banco para configurar no painel.
// © 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Código feito com auxílio de IA.
import { DurableObject } from 'cloudflare:workers';

const EVENTOS = new Set(['acessos', 'compartilhamentos', 'curtidas', 'comentarios', 'reposts', 'partidas', 'pessoas', 'cartilha', 'apostila', 'guia']);
const DIARIOS = new Set(['acessos', 'compartilhamentos', 'curtidas', 'comentarios', 'reposts', 'partidas', 'pessoas']);
// Números de antes do placar existir (ele começou em 21/10/2026). Só entram se vierem de uma fonte conferida
// (por exemplo, o painel da Cloudflare) e aparecem separados, em "base", com a nota dizendo de onde vieram.
// Painel da Cloudflare (Workers & Pages > jogaviravoto > Métricas, últimos 30 dias, enviado em 22/10/2026): cerca de 4 mil pedidos de
// arquivos de 15 a 20/10, dos quais uns 1,9 mil num só pico de 6 horas de respostas 3xx (robô ou recarga), que ficou de fora. Os ~2,1 mil
// restantes, divididos por 4 a 5 pedidos por visita (página, fontes, ícone, prévia do WhatsApp), dão 420 a 525 visitas: usamos 400.
// Números do painel da Cloudflare (Workers & Pages > jogaviravoto > Métricas), conferidos à mão e mostrados à parte no placar.
const PAINEL = {
  conferido: '23/10/2026, 11h30',
  desde: '15/10/2026',
  pedidos: 4950,
  servidores: ['Rio de Janeiro', 'São Paulo', 'Uberlândia', 'Curitiba', 'Caçador (SC)', 'Fortaleza'],
  exterior: ['Toronto', 'Dallas', 'Milão', 'Sydney', 'Newark', 'Atlanta'],
};
const BASE = { acessos: 400 };
const BASE_NOTA = 'Os acessos de 15 a 20/10/2026 (cerca de 400) são uma estimativa conservadora feita com o painel da Cloudflare, porque o placar só começou a contar em 21/10; curtidas, comentários, reposts e compartilhamentos desse período não foram registrados.';
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(dados, status = 200) {
  return new Response(JSON.stringify(dados), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...CORS },
  });
}

// dia no horário de Brasília (UTC-3)
function hoje() {
  return new Date(Date.now() - 3 * 3600e3).toISOString().slice(0, 10);
}

// só conta chamadas do próprio site, das cópias offline e de endereços com "viravoto" ou "brunochapadeiro"
function origemOk(req) {
  const o = req.headers.get('Origin');
  if (!o || o === 'null') return true;
  try {
    return /viravoto|brunochapadeiro/.test(new URL(o).hostname);
  } catch (e) {
    return false;
  }
}

export class Placar extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec('CREATE TABLE IF NOT EXISTS contador (chave TEXT PRIMARY KEY, valor INTEGER NOT NULL DEFAULT 0)');
  }

  soma(chaves) {
    for (const k of chaves) {
      this.sql.exec('INSERT INTO contador (chave, valor) VALUES (?, 1) ON CONFLICT(chave) DO UPDATE SET valor = valor + 1', k);
    }
    return true;
  }

  le(dia) {
    const saida = { atualizado: new Date().toISOString(), dia, totais: {}, hoje: {}, jogos: {} };
    const linhas = this.sql.exec("SELECT chave, valor FROM contador WHERE chave NOT LIKE 'dia:%' OR chave LIKE ?", 'dia:' + dia + ':%').toArray();
    for (const r of linhas) {
      if (r.chave.startsWith('jogo:')) saida.jogos[r.chave.slice(5)] = r.valor;
      else if (r.chave.startsWith('dia:')) saida.hoje[r.chave.split(':')[2]] = r.valor;
      else saida.totais[r.chave] = r.valor;
    }
    return saida;
  }
}

async function placar(req, env) {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
  const obj = env.PLACAR.get(env.PLACAR.idFromName('geral'));
  const url = new URL(req.url);
  const dia = hoje();
  if (req.method === 'POST') {
    if (!origemOk(req)) return json({ ok: false }, 403);
    const e = url.searchParams.get('e');
    if (!EVENTOS.has(e)) return json({ ok: false, erro: 'evento desconhecido' }, 400);
    const chaves = [e];
    if (DIARIOS.has(e)) chaves.push('dia:' + dia + ':' + e);
    const j = url.searchParams.get('j');
    if (e === 'partidas' && /^\d{1,2}$/.test(j || '') && +j >= 1 && +j <= 30) chaves.push('jogo:' + +j);
    await obj.soma(chaves);
    return json({ ok: true });
  }
  if (req.method === 'GET' || req.method === 'HEAD') {
    const saida = await obj.le(dia);
    if (Object.keys(BASE).length) { saida.base = BASE; saida.base_nota = BASE_NOTA; }
    saida.painel = PAINEL;
    return json(saida);
  }
  return json({ ok: false }, 405);
}

// ---------------- Apuração: lê os arquivos públicos de resultados do TSE (2º turno, Presidente) ----------------
// Fonte única: resultados.tse.jus.br (os mesmos arquivos do app oficial de Resultados). O Worker só junta Brasil, exterior e
// as 27 UFs num arquivo pequeno e guarda por 20 segundos, para não sobrecarregar o TSE. Nada é calculado além de somas e diferenças.
const TSE = 'https://resultados.tse.jus.br/oficial/ele2026';
const ELE2 = '6258';
const UFS = ['ac', 'al', 'am', 'ap', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mg', 'ms', 'mt', 'pa', 'pb', 'pe', 'pi', 'pr', 'rj', 'rn', 'ro', 'rr', 'rs', 'sc', 'se', 'sp', 'to'];
const num = (x) => { const n = Number(String(x ?? '').replace(/\./g, '').replace(',', '.')); return Number.isFinite(n) ? n : 0; };

function resumoTSE(d) {
  const cands = [];
  for (const cg of d.carg || []) for (const ag of cg.agr || []) for (const p of ag.par || []) for (const c of p.cand || []) {
    cands.push({ n: c.n, nm: c.nmu, v: num(c.vap), p: num(c.pvapn ?? c.pvap), e: c.e, st: c.st || '' });
  }
  const s = d.s || {}, e = d.e || {}, v = d.v || {};
  return {
    cd: d.cdabr, dg: d.dg, hg: d.hg, dt: d.dt, ht: d.ht, tf: d.tf,
    s: { ts: num(s.ts), st: num(s.st), pst: num(s.pstn ?? s.pst) },
    e: { te: num(e.te), c: num(e.c), pc: num(e.pcn ?? e.pc), a: num(e.a), pa: num(e.pan ?? e.pa) },
    v: { tv: num(v.tv), vv: num(v.vv), vb: num(v.vb), pvb: num(v.pvbn ?? v.pvb), vn: num(v.tvn), pvn: num(v.ptvnn ?? v.ptvn) },
    cand: cands,
  };
}

async function lerTSE(uf, ele) {
  const u = `${TSE}/${ele}/dados/${uf}/${uf}-c0001-e00${ele}-u.json`;
  try {
    const r = await fetch(u, { cf: { cacheTtl: 20, cacheEverything: true }, headers: {
      'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36',
      'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'pt-BR,pt;q=0.9',
      'Referer': 'https://resultados.tse.jus.br/oficial/app/index.html' } });
    if (!r.ok) return { cd: uf, erro: r.status };
    return resumoTSE(await r.json());
  } catch (err) {
    return { cd: uf, erro: String(err).slice(0, 80) };
  }
}

async function apuracao(req, ctx) {
  const ele = new URL(req.url).searchParams.get('e') === '6257' ? '6257' : ELE2;   // 6257 = 1º turno (só para conferir a página)
  const cache = caches.default;
  const chave = new Request(new URL(`/api/apuracao?v=1&e=${ele}`, req.url).toString());
  const guardado = await cache.match(chave);
  if (guardado) return guardado;
  const [br, zz, ...ufs] = await Promise.all([lerTSE('br', ele), lerTSE('zz', ele), ...UFS.map((u) => lerTSE(u, ele))]);
  const corpo = { fonte: 'TSE, resultados.tse.jus.br (arquivos oficiais de divulgação)', eleicao: ele, lido: new Date().toISOString(), br, zz, ufs };
  const resp = new Response(JSON.stringify(corpo), {
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=20', ...CORS },
  });
  ctx.waitUntil(cache.put(chave, resp.clone()));
  return resp;
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    if (url.pathname === '/api/placar' || url.pathname === '/api/placar/') return placar(req, env);
    if (url.pathname === '/api/apuracao' || url.pathname === '/api/apuracao/') return apuracao(req, ctx);
    // tudo o mais: os arquivos do site (páginas, PDFs, áudios, imagens)
    return env.ASSETS.fetch(req);
  },
};
