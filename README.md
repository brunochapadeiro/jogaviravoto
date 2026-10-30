# Vigie a Democracia (antigo Games Vira-Voto)

Site: https://vigieademocracia.brunochapadeiro.workers.dev/

Fatos com fonte, os votos do Congresso (teste "Quem vota como você?" e a ficha de cada parlamentar), canais de denúncia de
assédio eleitoral, jogos e o arquivo das eleições de 2026, com placar público de acessos e compartilhamentos em `/api/placar`.
Funciona como aplicativo (PWA): `manifest.webmanifest`, `sw.js` e `vigia.js` em `public/`.

- `public/`: o site (páginas, PDFs, áudios, imagens). É gerado automaticamente; não edite à mão.
- `src/index.js`: o placar público (um Durable Object com SQLite, sem nenhum banco para configurar).
- `wrangler.jsonc`: o Worker `vigieademocracia` (o antigo `jogaviravoto`, renomeado): o site e o placar.
- `vigie/wrangler.jsonc`: cópia da configuração acima.
- `redirect/`: o Worker `jogaviravoto` (endereço antigo), que só redireciona para o endereço novo.

Cada envio para a branch `main` publica o site sozinho: pelo Cloudflare Workers Builds (repositório conectado no painel) ou, como plano B manual, pelo GitHub Actions (`.github/workflows/publicar.yml`).

© 2026 Prof. Bruno Chapadeiro · Licença Creative Commons CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br) · https://instagram.com/brunochapadeiro
Feito com auxílio de IA.
