/* Vigie a Democracia: guarda as páginas já abertas para funcionar sem internet. Não guarda nada pessoal.
   © 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Feito com auxílio de IA. */
const V = 'vigie-4bda42bcdc';
const PRE = ["/", "/offline", "/denuncie", "/vota-como-voce", "/parlamentares", "/dados/vota-como-voce.json", "/dados/parlamentares.json", "/vigia.js", "/icone.svg", "/icone-192.png", "/fontes/AtkinsonHyperlegible-Regular.woff2", "/fontes/AtkinsonHyperlegible-Bold.woff2", "/fontes/Lexend-var.woff2"];
const GRANDE = /\.(pdf|mp4|mp3|zip)$/i;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => Promise.all(PRE.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => null)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('vigie-') && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin || u.pathname.startsWith('/api/') || GRANDE.test(u.pathname)) return;
  if (r.mode === 'navigate') {  // páginas: primeiro a rede (sempre o mais novo), sem internet a cópia guardada
    e.respondWith(fetch(r).then(res => { if (res.ok) { const c = res.clone(); caches.open(V).then(x => x.put(r, c)); } return res; })
      .catch(() => caches.match(r, { ignoreSearch: true }).then(m => m || caches.match('/offline'))));
    return;
  }
  // fontes, imagens, dados: a cópia guardada na hora e a nova por trás
  e.respondWith(caches.open(V).then(c => c.match(r).then(m => {
    const rede = fetch(r).then(res => { if (res.ok) c.put(r, res.clone()); return res; }).catch(() => m);
    return m || rede;
  })));
});
