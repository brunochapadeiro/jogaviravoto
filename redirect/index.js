// Endereço antigo do Vigie a Democracia (Games Vira-Voto): manda tudo para o mesmo caminho no endereço novo.
// GET e HEAD: 301 (permanente). Outros métodos (o placar, por exemplo): 308, que mantém o método e o corpo.
// © 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Código feito com auxílio de IA.
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    const destino = (env.NOVO_ENDERECO || 'https://vigieademocracia.brunochapadeiro.workers.dev') + u.pathname + u.search;
    return Response.redirect(destino, req.method === 'GET' || req.method === 'HEAD' ? 301 : 308);
  },
};
