// Vigie a Democracia, antigo Games Vira-Voto (Cloudflare Worker com arquivos estáticos em public/) + placar público.
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

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
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
