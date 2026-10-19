# Games Vira-Voto

Site: https://jogaviravoto.brunochapadeiro.workers.dev/

Jogos, Cartilha, Apostila, Guia da banquinha, kit de postagem e materiais para imprimir, com placar público
de acessos e compartilhamentos em `/api/placar`.

- `public/`: o site (páginas, PDFs, áudios, imagens). É gerado automaticamente; não edite à mão.
- `src/index.js`: o placar público (um Durable Object com SQLite, sem nenhum banco para configurar).
- `wrangler.jsonc`: a configuração do Worker `jogaviravoto` no Cloudflare.

Cada envio para a branch `main` publica o site sozinho, pelo Cloudflare Workers Builds.

© 2026 Prof. Bruno Chapadeiro · Licença Creative Commons CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br) · https://instagram.com/brunochapadeiro
Feito com auxílio de IA.
