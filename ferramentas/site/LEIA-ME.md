# Organização por temas e cruzador de dados

Gerador da página inicial, das páginas de tema (`/tema/<id>`), da página `/jogar` e do cruzador (`/cruzar`),
e dos ajustes comuns em todas as páginas: menu (Início, Temas, Cruzar, Jogar, Denunciar), trilha "Você está em"
e o bloco "Continue no tema" (entre os marcadores `<!--vg-trilha-->` e `<!--vg-mais-->`).

## Arquivos

- `catalogo.py`: os 6 temas e todos os itens do site (página, jogo, PDF, campanha), com tema, formato e jeito de jogar.
  Para pôr algo novo no site, acrescente um item aqui.
- `ciencia.py`: estudos revisados por pares (DOI conferido no PubMed ou na revista) por assunto. A frase diz só o que o estudo diz.
- `novidades.json`: o que entrou ou mudou, com data e tema. Aparece no início e em cada tema.
- `cruzar.js`: o cruzador, que roda no aparelho de quem usa (nada é enviado).
- `comparar.js`: Compare os estados (em `/cruzar#ce`): cruza quaisquer dois dos indicadores de `public/dados/estados.json` (frase, gráfico e tabela).
- `cruzar_dados.py`: monta `public/dados/cruzar.json` (urna do TSE por UF e eleitos de 2026), `public/dados/estados.json` (todos os indicadores por UF, com o IBGE) e confere os placares.
- A página `/bases` (guia das bases de dados) sai de `BASES` e `OFICIAIS` em `organiza.py`.
- `organiza.py`: gera tudo. `molde/` guarda o cabeçalho, o rodapé, os scripts e o CSS base da página inicial antiga.

## Rodar

```bash
git fetch origin dados && mkdir -p /tmp/dados && git archive origin/dados presidente eleitos ibge | tar -x -C /tmp/dados
python3 ferramentas/site/cruzar_dados.py --dados /tmp/dados --site public
python3 ferramentas/site/organiza.py --site public          # --og refaz as imagens de prévia
npx wrangler dev --config vigie/wrangler.jsonc --port 8787   # conferir antes de publicar
```

O `organiza.py` pode rodar quantas vezes for preciso: ele troca o que está entre os marcadores e refaz as páginas novas.

## Dados do IBGE (pasta `ibge` do ramo dados)

O servidor do IBGE só responde pelo `apisidra` (o `servicodados` não responde ao GitHub). Para atualizar, despache `baixar.yml` com `nome=ibge` e estes endereços (n1 = Brasil, n3 = UFs):

```
https://apisidra.ibge.gov.br/values/t/4099/n1/all/n3/all/v/4099/p/last%201     desemprego
https://apisidra.ibge.gov.br/values/t/5436/n1/all/n3/all/v/5933/p/last%201     rendimento
https://apisidra.ibge.gov.br/values/t/8529/n1/all/n3/all/v/12466/p/last%201    informalidade
https://apisidra.ibge.gov.br/values/t/7435/n1/all/n3/all/v/10681/p/last%201    Gini
https://apisidra.ibge.gov.br/values/t/6579/n1/all/n3/all/v/9324/p/last%201     população
```

## Regras

Fonte em tudo; nada publicado sem o OK do Prof. Bruno; sem ranking de parlamentares; estudo observacional diz "associado a";
quando não há estudo, o site diz isso. Selo CC BY-NC-SA 4.0, marca d'água "Prof. Bruno Chapadeiro" e @brunochapadeiro em todo material.

© 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0 · Feito com auxílio de IA (Claude)
