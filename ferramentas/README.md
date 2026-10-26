# Ferramentas da vigília (De olho no Congresso)

Gerador do **Placar da semana**: página `/semana` (e `/semana-AAAA-MM-DD`) e cards 4:5 e 9:16 para o Instagram,
a partir do JSON que o robô `.github/workflows/semana.yml` grava toda segunda, às 6h de Brasília, no ramo `dados`
(pasta `semana/<data final>/placar.json`; a última semana está em `semana/ultima.txt`).

## Rodar

```bash
pip install qrcode playwright   # Playwright com Chromium (no ambiente da Claude já vem instalado)
git fetch origin dados && git show origin:dados:semana/ultima.txt   # ou: git archive origin/dados semana | tar -x -C /tmp
python3 ferramentas/build_placar.py --dados /tmp/semana/<data>/placar.json --site public --saida /tmp/placar \
        --resumos /tmp/resumos.json --cards
```

`resumos.json` (opcional, escrito na revisão de segunda):

```json
{"manchete": "frase da capa (opcional)",
 "destaques": ["sen:PEC-221-2019", "cam:PLP-281-2019"],
 "resumos": {"sen:PEC-221-2019": "Fim da escala 6x1: 40 horas por semana, duas folgas, sem corte de salário."}}
```

Chaves: `cam:` ou `sen:` + `TIPO-NÚMERO-ANO`. Resumos de até 90 caracteres, em linguagem simples, sem adjetivo.
Sem `destaques`, o gerador escolhe até 3 (PEC > PLP > MPV > PL, e as mais disputadas). Os avisos "transborda" indicam card que
não coube mesmo com o ajuste automático: encurte o resumo.

## Publicar (só depois da revisão humana)

Copiar `semana.html`, `semana-<data>.html` e `arquivos/Placar_<data>_*.zip` para `public/` (zips em `public/arquivos/`),
fazer commit no `main` e conferir o deploy do Cloudflare (Workers Builds).

## Regras

Fonte em tudo; número antes do adjetivo; nenhuma imagem gerada de pessoa real; aviso de IA; correção pública de erros.
Votações simbólicas não entram (não registram voto). A orientação do governo é a do líder do governo na Câmara.

© 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0
