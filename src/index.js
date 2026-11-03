// Vigie a Democracia, antigo Games Vira-Voto (Cloudflare Worker com arquivos estáticos em public/) + placar público
// + salas ao vivo dos jogos no telão (a plateia responde pelo celular; veja "Sala ao vivo" mais abaixo).
// O mesmo código roda em dois Workers: jogaviravoto (endereço antigo, guarda o placar) e vigieademocracia (endereço novo).
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
    return /viravoto|vigie|brunochapadeiro/.test(new URL(o).hostname);
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

  async guardaApuracao(ele, texto) {
    await this.ctx.storage.put('apuracao:' + ele, texto);
    return true;
  }

  async leApuracao(ele) {
    return (await this.ctx.storage.get('apuracao:' + ele)) || null;
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

// ---------------- Apuração: resultados oficiais do TSE (2º turno, Presidente) ----------------
// O TSE bloqueia leitura direta a partir da Cloudflare e de outros sites. Por isso, um robô do GitHub Actions do próprio
// repositório (.github/workflows/apuracao.yml) lê os arquivos públicos de resultados.tse.jus.br a cada minuto e entrega aqui.
// Sem senha guardada: cada entrega vem assinada pelo GitHub (token OIDC) e só é aceita se for deste repositório, da branch main.
const ISS = 'https://token.actions.githubusercontent.com';
const AUD = 'jogaviravoto-apuracao';
const REPO = 'brunochapadeiro/jogaviravoto';
const b64u = (s) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), (c) => c.charCodeAt(0));

async function tokenGitHubOk(auth) {
  try {
    const t = (auth || '').replace(/^Bearer\s+/i, '');
    const [h, p, sig] = t.split('.');
    const cab = JSON.parse(new TextDecoder().decode(b64u(h)));
    const dados = JSON.parse(new TextDecoder().decode(b64u(p)));
    if (cab.alg !== 'RS256') return false;
    const jwks = await (await fetch(ISS + '/.well-known/jwks', { cf: { cacheTtl: 3600, cacheEverything: true } })).json();
    const jwk = (jwks.keys || []).find((k) => k.kid === cab.kid);
    if (!jwk) return false;
    const chave = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
    const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', chave, b64u(sig), new TextEncoder().encode(h + '.' + p));
    const agora = Date.now() / 1000;
    return ok && dados.iss === ISS && dados.aud === AUD && dados.repository === REPO && dados.ref === 'refs/heads/main' && dados.exp > agora;
  } catch (e) {
    return false;
  }
}

async function apuracao(req, env) {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
  const ele = new URL(req.url).searchParams.get('e') === '6257' ? '6257' : '6258';   // 6257 = 1º turno (só para conferir a página)
  const obj = env.PLACAR.get(env.PLACAR.idFromName('geral'));
  if (req.method === 'POST') {
    if (!(await tokenGitHubOk(req.headers.get('Authorization')))) return json({ ok: false, erro: 'não autorizado' }, 401);
    const texto = await req.text();
    if (texto.length > 300000) return json({ ok: false, erro: 'grande demais' }, 413);
    let d;
    try { d = JSON.parse(texto); } catch (e) { return json({ ok: false, erro: 'json' }, 400); }
    if (!d || !d.br || !Array.isArray(d.ufs)) return json({ ok: false, erro: 'formato' }, 400);
    d.recebido = new Date().toISOString();
    await obj.guardaApuracao(ele, JSON.stringify(d));
    return json({ ok: true });
  }
  const t = await obj.leApuracao(ele);
  return new Response(t || JSON.stringify({ vazio: true, eleicao: ele }), {
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=15', ...CORS },
  });
}

// ---------------- Sala ao vivo: o telão mostra a pergunta e um QR code, a plateia responde pelo celular ----------------
// Cada sala é um Durable Object (com SQLite, do plano grátis) com um código de 4 letras. Guarda só as respostas, sem nome,
// IP ou cookie: cada celular manda um número aleatório que ele mesmo sorteou, para não contar o mesmo voto duas vezes.
// A sala se apaga sozinha 6 horas depois do último comando de quem apresenta.
// Quem apresenta recebe uma chave secreta ao criar a sala; só com ela dá para trocar a tela.
// As perguntas ficam na própria página; a sala só sabe o número da tela, o tipo de resposta e quantas opções há.
const ALFA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';   // sem I, O, 0 e 1, que se confundem
const COD_RE = /^[A-HJ-NP-Z2-9]{4}$/;
const VALIDADE = 6 * 3600e3;
const MAX_PLATEIA = 1500;
const TIPOS = new Set(['escolha', 'escala', 'nuvem', 'ordenar', 'info', 'espera', 'fim']);
// palavrões e ofensas não aparecem na nuvem do telão (a pessoa vê a própria resposta como enviada, mas ela não é exibida);
// quem apresenta também pode esconder qualquer palavra com um toque
const VETO_INICIO = ['caralh', 'porra', 'merda', 'bosta', 'buceta', 'piroca', 'viado', 'arromb', 'estupr', 'vagabund', 'xoxot', 'boquet', 'foder', 'fodid',
  'cacete', 'filhadaput', 'filhodaput', 'desgracad', 'retardad', 'travec', 'crioul', 'hitler', 'nazis'];
const VETO_IGUAL = new Set(['cu', 'cuzao', 'puta', 'puto', 'putas', 'putos', 'fdp', 'vsf', 'pqp', 'tnc', 'pinto', 'rola', 'macaco', 'macaca', 'bicha', 'sapatao',
  'nazi', 'idiota', 'imbecil', 'otario', 'otaria', 'babaca', 'corno', 'corna', 'vadia', 'piranha', 'mongol', 'safado', 'safada', 'escroto', 'escrota', 'lixo humano']);
function vetada(s) {
  const t = semAcento(s);
  if (VETO_IGUAL.has(t)) return true;
  return t.split(/[^a-z]+/).some((w) => w && (VETO_IGUAL.has(w) || VETO_INICIO.some((v) => w.startsWith(v))));
}

function sorteia(n) { return [...crypto.getRandomValues(new Uint8Array(n))]; }
function codigoNovo() { return sorteia(4).map((x) => ALFA[x & 31]).join(''); }
function chaveNova() { return sorteia(16).map((x) => x.toString(16).padStart(2, '0')).join(''); }
function limpaPid(p) { return /^[a-z0-9]{8,32}$/.test(p || '') ? p : ''; }
function semAcento(s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, ''); }
function palavra(s) {
  let t = String(s || '').replace(/[\u0000-\u001f\u007f<>"`{}\[\]\\|^~*#@$%&=+_/]/g, ' ').replace(/\s+/g, ' ').trim().toLocaleLowerCase('pt-BR');
  t = t.replace(/^[.,;:!?'-]+|[.,;:!?'-]+$/g, '').slice(0, 28).trim();
  if (t.length < 2 || /^[\d\s.,-]+$/.test(t) || /https?:|www\.|\.com/.test(t)) return '';
  return t;
}

export class Sala extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec('CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT NOT NULL)');
    this.sql.exec('CREATE TABLE IF NOT EXISTS voto (tela INTEGER NOT NULL, pid TEXT NOT NULL, k INTEGER NOT NULL DEFAULT 0, val TEXT NOT NULL, PRIMARY KEY (tela, pid, k))');
    this.sql.exec('CREATE TABLE IF NOT EXISTS gente (pid TEXT PRIMARY KEY, t INTEGER NOT NULL)');
    this.m = null;
    this.timer = null;
    this.vistos = new Map();     // quem acompanha sem WebSocket (pela consulta a cada 3 s): pid -> hora
    this.ritmo = new WeakMap();  // limite de mensagens por conexão
    // o celular manda "ping" a cada 25 s; a resposta sai sem acordar a sala
    ctx.setWebSocketAutoResponse(new WebSocketRequestResponsePair('{"c":"ping"}', '{"tipo":"pong"}'));
  }

  meta() {
    if (!this.m) {
      const o = {};
      for (const r of this.sql.exec('SELECT k, v FROM meta')) o[r.k] = JSON.parse(r.v);
      this.m = o;
    }
    return this.m;
  }

  poe(k, v) {
    this.sql.exec('INSERT INTO meta (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v = excluded.v', k, JSON.stringify(v));
    this.meta()[k] = v;
  }

  ativa() { const m = this.meta(); return !!(m.codigo && m.ate > Date.now()); }

  async criar(cod, jogo) {
    if (this.ativa()) return { ok: false };
    this.sql.exec('DELETE FROM voto'); this.sql.exec('DELETE FROM gente'); this.sql.exec('DELETE FROM meta'); this.m = null;
    const chave = chaveNova();
    this.poe('codigo', cod); this.poe('jogo', jogo); this.poe('chave', chave); this.poe('ate', Date.now() + VALIDADE);
    this.poe('tela', { i: -1, tipo: 'espera', n: 0, fase: 'espera' });
    this.poe('ocultas', {});
    await this.ctx.storage.setAlarm(Date.now() + VALIDADE);
    return { ok: true, chave };
  }

  async alarm() {
    const m = this.meta();
    if (m.ate && m.ate > Date.now() + 1000) { await this.ctx.storage.setAlarm(m.ate); return; }
    for (const ws of this.ctx.getWebSockets()) { try { ws.close(4000, 'sala encerrada'); } catch (e) {} }
    this.sql.exec('DELETE FROM voto'); this.sql.exec('DELETE FROM gente'); this.sql.exec('DELETE FROM meta'); this.m = null;
  }

  pessoas() {
    const agora = Date.now(), ids = new Set();
    for (const ws of this.ctx.getWebSockets('plateia')) { const a = ws.deserializeAttachment(); if (a && a.pid) ids.add(a.pid); }
    for (const [pid, t] of this.vistos) { if (agora - t < 12000) ids.add(pid); else this.vistos.delete(pid); }
    return ids.size;
  }

  resultado(i) {
    const m = this.meta(), tl = m.tela || {};
    if (i == null) i = tl.i;
    const tipo = i === tl.i ? tl.tipo : (m.tipos || {})[i];
    const n = i === tl.i ? tl.n : ((m.ns || {})[i] || 0);
    const total = this.sql.exec('SELECT COUNT(DISTINCT pid) AS c FROM voto WHERE tela = ?', i).one().c;
    const r = { i, tipo, total };
    if (tipo === 'escolha' || tipo === 'escala') {
      const c = new Array(n).fill(0);
      for (const x of this.sql.exec('SELECT val, COUNT(*) AS c FROM voto WHERE tela = ? GROUP BY val', i)) { const k = +x.val; if (k >= 0 && k < n) c[k] = x.c; }
      r.contagem = c;
    } else if (tipo === 'ordenar') {
      const soma = new Array(n).fill(0); let k = 0;
      for (const x of this.sql.exec('SELECT val FROM voto WHERE tela = ?', i)) {
        const p = x.val.split(',').map(Number); if (p.length !== n) continue;
        p.forEach((item, pos) => { soma[item] += pos + 1; }); k++;
      }
      r.media = soma.map((s) => (k ? Math.round((s / k) * 100) / 100 : null)); r.total = k;
    } else if (tipo === 'nuvem') {
      const fora = new Set(((m.ocultas || {})[i]) || []);
      r.palavras = [];
      for (const x of this.sql.exec('SELECT val, COUNT(*) AS c FROM voto WHERE tela = ? GROUP BY val ORDER BY c DESC, val LIMIT 80', i)) {
        if (!fora.has(x.val) && !vetada(x.val)) r.palavras.push([x.val, x.c]);
      }
    }
    return r;
  }

  estado(papel, pid) {
    const m = this.meta(), tl = m.tela || {};
    const e = { tipo: 'estado', codigo: m.codigo, jogo: m.jogo, tela: tl, pessoas: this.pessoas(),
      entraram: this.sql.exec('SELECT COUNT(*) AS c FROM gente').one().c };
    if (tl.i >= 0) e.respostas = this.sql.exec('SELECT COUNT(DISTINCT pid) AS c FROM voto WHERE tela = ?', tl.i).one().c;
    if (papel === 'telao' || tl.fase === 'revelada') { if (tl.i >= 0 && tl.tipo !== 'info') e.res = this.resultado(tl.i); }
    if (papel === 'telao') e.historico = m.fim ? this.historico() : undefined;
    if (pid && tl.i >= 0) {
      const meus = this.sql.exec('SELECT val FROM voto WHERE tela = ? AND pid = ? ORDER BY k', tl.i, pid).toArray().map((x) => x.val);
      if (meus.length) e.meu = tl.tipo === 'nuvem' ? meus : meus[0];
    }
    return e;
  }

  historico() {
    const m = this.meta(), out = [];
    for (const i of Object.keys(m.tipos || {}).map(Number).sort((a, b) => a - b)) out.push(this.resultado(i));
    return out;
  }

  conhece(pid) {
    if (pid) this.sql.exec('INSERT INTO gente (pid, t) VALUES (?, ?) ON CONFLICT(pid) DO NOTHING', pid, Date.now());
  }

  manda(papel, dados) {
    const txt = JSON.stringify(dados);
    for (const ws of this.ctx.getWebSockets(papel)) { try { ws.send(txt); } catch (e) {} }
  }

  avisaTelao(ja) {
    if (ja) { if (this.timer) { clearTimeout(this.timer); this.timer = null; } this.manda('telao', this.estado('telao')); return; }
    if (this.timer) return;
    this.timer = setTimeout(() => { this.timer = null; this.manda('telao', this.estado('telao')); }, 350);
  }

  avisaTodos() {
    this.avisaTelao(true);
    this.manda('plateia', this.estado('plateia'));
  }

  // um comando de quem apresenta ou uma resposta da plateia
  trata(d, papel, pid) {
    if (!d || typeof d !== 'object') return false;
    const m = this.meta(), tl = m.tela || {};
    if (papel === 'telao') {
      if (d.c === 'tela') {
        const i = d.i === 'fim' ? -2 : Number(d.i);
        const tipo = TIPOS.has(d.tipo) ? d.tipo : 'info';
        const n = Math.max(0, Math.min(12, Number(d.n) || 0));
        if (!Number.isInteger(i) || i < -2 || i > 200) return false;
        const fase = tipo === 'info' || tipo === 'espera' || tipo === 'fim' ? 'info' : (d.fase === 'revelada' ? 'revelada' : 'aberta');
        this.poe('tela', { i, tipo, n, fase, t: Date.now() });
        if (i >= 0 && tipo !== 'info') { const ts = m.tipos || {}, ns = m.ns || {}; ts[i] = tipo; ns[i] = n; this.poe('tipos', ts); this.poe('ns', ns); }
        if (tipo === 'fim') this.poe('fim', true);
      } else if (d.c === 'fase') {
        if (!['aberta', 'fechada', 'revelada'].includes(d.fase) || tl.i < 0) return false;
        this.poe('tela', { ...tl, fase: d.fase });
      } else if (d.c === 'oculta') {
        const p = palavra(d.p); if (!p || tl.i < 0) return false;
        const oc = m.ocultas || {}; oc[tl.i] = [...new Set([...(oc[tl.i] || []), p])].slice(0, 200); this.poe('ocultas', oc);
        this.avisaTelao(true); return true;
      } else if (d.c === 'zera') {   // nova rodada com o mesmo QR code: apaga as respostas
        this.sql.exec('DELETE FROM voto'); this.poe('tipos', {}); this.poe('ns', {}); this.poe('ocultas', {}); this.poe('fim', false);
        this.poe('tela', { i: -1, tipo: 'espera', n: 0, fase: 'espera' });
      } else if (d.c === 'oi') {
        this.avisaTelao(true); return true;
      } else return false;
      if ((m.ate || 0) - Date.now() < VALIDADE - 600e3) { this.poe('ate', Date.now() + VALIDADE); this.ctx.storage.setAlarm(Date.now() + VALIDADE); }
      this.avisaTodos();
      return true;
    }
    // plateia
    if (d.c !== 'voto' || !pid || tl.fase !== 'aberta' || Number(d.i) !== tl.i) return false;
    let val = null;
    if (tl.tipo === 'escolha' || tl.tipo === 'escala') {
      const v = Number(d.v); if (!Number.isInteger(v) || v < 0 || v >= tl.n) return false; val = String(v);
    } else if (tl.tipo === 'ordenar') {
      const v = Array.isArray(d.v) ? d.v.map(Number) : [];
      if (v.length !== tl.n || new Set(v).size !== tl.n || v.some((x) => !Number.isInteger(x) || x < 0 || x >= tl.n)) return false;
      val = v.join(',');
    } else if (tl.tipo === 'nuvem') {
      const p = palavra(d.v); if (!p) return false;
      const ja = this.sql.exec('SELECT k, val FROM voto WHERE tela = ? AND pid = ?', tl.i, pid).toArray();
      if (ja.some((x) => x.val === p)) return true;
      if (ja.length >= 3) return false;
      this.sql.exec('INSERT INTO voto (tela, pid, k, val) VALUES (?, ?, ?, ?)', tl.i, pid, ja.length + 1, p);
      this.conhece(pid); this.avisaTelao(false); return true;
    } else return false;
    this.sql.exec('INSERT INTO voto (tela, pid, k, val) VALUES (?, ?, 0, ?) ON CONFLICT(tela, pid, k) DO UPDATE SET val = excluded.val', tl.i, pid, val);
    this.conhece(pid);
    this.avisaTelao(false);
    return true;
  }

  async fetch(req) {
    const url = new URL(req.url);
    const acao = url.pathname.split('/').filter(Boolean)[3] || '';
    if (!this.ativa()) return json({ ok: false, erro: 'Sala não encontrada. Confira o código ou peça um novo a quem apresenta.' }, 404);
    const m = this.meta();
    const chave = url.searchParams.get('chave') || '';
    const papel = chave && chave === m.chave ? 'telao' : 'plateia';
    const pid = limpaPid(url.searchParams.get('pid'));
    if (url.searchParams.get('papel') === 'telao' && papel !== 'telao') return json({ ok: false, erro: 'chave' }, 403);
    if (acao === 'ws') {
      if (req.headers.get('Upgrade') !== 'websocket') return json({ ok: false, erro: 'websocket' }, 426);
      if (papel === 'plateia' && (!pid || this.ctx.getWebSockets('plateia').length >= MAX_PLATEIA)) return json({ ok: false, erro: 'cheia' }, 429);
      const par = new WebSocketPair();
      this.ctx.acceptWebSocket(par[1], [papel]);
      par[1].serializeAttachment({ papel, pid });
      if (papel === 'plateia') { this.conhece(pid); this.vistos.delete(pid); }
      par[1].send(JSON.stringify(this.estado(papel, pid)));
      if (papel === 'plateia') this.avisaTelao(false);
      return new Response(null, { status: 101, webSocket: par[0] });
    }
    if (acao === 'estado' && req.method === 'GET') {
      if (papel === 'plateia' && pid) { if (!this.vistos.has(pid)) { this.conhece(pid); this.vistos.set(pid, Date.now()); this.avisaTelao(false); } else this.vistos.set(pid, Date.now()); }
      return json(this.estado(papel, pid));
    }
    if (acao === 'msg' && req.method === 'POST') {
      const txt = await req.text();
      if (txt.length > 600) return json({ ok: false }, 413);
      let d; try { d = JSON.parse(txt); } catch (e) { return json({ ok: false }, 400); }
      if (papel === 'plateia' && pid) this.vistos.set(pid, Date.now());
      const ok = this.trata(d, papel, pid);
      return json({ ok, ...this.estado(papel, pid) });
    }
    return json({ ok: false }, 404);
  }

  async webSocketMessage(ws, msg) {
    if (typeof msg !== 'string' || msg.length > 600) return;
    const a = ws.deserializeAttachment() || {};
    const agora = Date.now(), r = this.ritmo.get(ws) || { t: agora, n: 0 };
    if (agora - r.t > 10000) { r.t = agora; r.n = 0; }
    if (++r.n > 40) return;
    this.ritmo.set(ws, r);
    let d; try { d = JSON.parse(msg); } catch (e) { return; }
    if (!this.ativa()) { try { ws.close(4000, 'sala encerrada'); } catch (e) {} return; }
    const ok = this.trata(d, a.papel, a.pid);
    if (a.papel === 'plateia' && d.c === 'voto') { try { ws.send(JSON.stringify({ tipo: 'recebido', ok, i: d.i, ...(ok ? {} : this.estado('plateia', a.pid)) })); } catch (e) {} }
  }

  async webSocketClose(ws, code) {
    try { ws.close(1000, 'tchau'); } catch (e) {}
    if ((ws.deserializeAttachment() || {}).papel === 'plateia') this.avisaTelao(false);
  }

  async webSocketError(ws) {
    try { ws.close(1011, 'erro'); } catch (e) {}
  }
}

// a sala aceita chamadas do próprio endereço (inclusive no teste local) e dos endereços do site
function origemSala(req, url) {
  const o = req.headers.get('Origin');
  try { if (o && new URL(o).host === url.host) return true; } catch (e) {}
  return origemOk(req);
}

async function sala(req, env, url) {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
  if (!origemSala(req, url)) return json({ ok: false }, 403);
  const partes = url.pathname.split('/').filter(Boolean);   // api, sala, (nova | CÓDIGO), ação
  if (partes[2] === 'nova') {
    if (req.method !== 'POST') return json({ ok: false }, 405);
    let corpo = {}; try { corpo = await req.json(); } catch (e) {}
    const jogo = String(corpo.jogo || '');
    if (!/^[a-z0-9-]{2,24}$/.test(jogo)) return json({ ok: false, erro: 'jogo' }, 400);
    for (let t = 0; t < 8; t++) {
      const cod = codigoNovo();
      const r = await env.SALA.get(env.SALA.idFromName(cod)).criar(cod, jogo);
      if (r.ok) return json({ ok: true, codigo: cod, chave: r.chave, validade: VALIDADE });
    }
    return json({ ok: false, erro: 'Tente de novo em instantes.' }, 503);
  }
  const cod = (partes[2] || '').toUpperCase();
  if (!COD_RE.test(cod)) return json({ ok: false, erro: 'Código inválido: são 4 letras ou números.' }, 400);
  return env.SALA.get(env.SALA.idFromName(cod)).fetch(req);
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    if (url.pathname.startsWith('/api/sala/')) return sala(req, env, url);
    if (url.pathname === '/api/placar' || url.pathname === '/api/placar/') return placar(req, env);
    if (url.pathname === '/api/apuracao' || url.pathname === '/api/apuracao/') return apuracao(req, env);
    // Mudança de endereço: com NOVO_ENDERECO definido (e "run_worker_first" ligado) no Worker antigo, as páginas do endereço antigo
    // levam ao mesmo caminho no novo. Assim os QR codes já impressos continuam funcionando. O placar (/api) responde nos dois.
    if (env.NOVO_ENDERECO && (req.method === 'GET' || req.method === 'HEAD')) {
      const novo = new URL(env.NOVO_ENDERECO);
      if (url.hostname !== novo.hostname) return Response.redirect(novo.origin + url.pathname + url.search + url.hash, 301);
    }
    // tudo o mais: os arquivos do site (páginas, PDFs, áudios, imagens)
    return env.ASSETS.fetch(req);
  },
};
