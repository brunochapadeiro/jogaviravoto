# Rotina semanal de atualização (toda segunda à tarde)

Feita por uma tarefa agendada do Claude, depois dos robôs de dados da manhã (Placar da semana às 9h UTC e Parlamentares às 9h30 UTC).
**Nada vai ao ar sem o OK do Prof. Bruno, item por item.** A rotina prepara tudo num ramo `atualizacao-AAAA-MM-DD`,
abre um pull request com a lista de mudanças (cada uma com a fonte) e avisa o Bruno. Ele responde OK ou não para cada item.

## 1. Dados oficiais (ramo `dados`)

- Placar da semana: se `semana/ultima.txt` tem uma semana nova com votações, gerar a página com `ferramentas/build_placar.py`
  (veja `ferramentas/README.md`), com resumos de até 90 caracteres, sem adjetivo, a partir das ementas oficiais.
- Parlamentares: se `parlamentares/meta.json` mudou, avisar o Bruno (o gerador da ficha pública ficou de fora do repositório).
- Rodar `cruzar_dados.py` e `organiza.py`. Os placares do cruzador são conferidos contra o oficial; aviso = parar e relatar.

## 2. Andamento dos temas (pesquisa na web, com fonte primária)

| Tema | O que acompanhar |
| --- | --- |
| Congresso e votos | pauta e votações nominais da semana; projetos dos 15 votos do teste (ex.: blindagem, dosimetria) |
| Fatos e boatos | checagens novas de Lupa, Aos Fatos, Estadão Verifica e g1 sobre temas do site |
| Saúde mental e trabalho | NR-1 (riscos psicossociais) e NR-17 no MTE, Fundacentro, Observatório Nacional de Saúde Mental e Trabalho, consultas públicas (AGU), LDRT, PNSTT |
| Assédio e denúncia | canais (MPT, MTE, Disque 100) mudaram? números novos de denúncias |
| Bolso e direitos sociais | IR (isenção até R$ 5 mil), Bolsa Família, Pé-de-Meia, fim da escala 6x1 (Emenda 141), bets (MP 1.394/2026, ADI 8027 no STF) |
| Eleições 2026 | nada novo a acompanhar; só correções |

Cada novidade vira uma linha em `ferramentas/site/novidades.json` (data, tema, título, descrição, link) e, se for o caso,
a correção do texto do item em `catalogo.py`. Datas que já passaram (audiência marcada, prazo de consulta) são revistas.

## 3. Ciência (uma vez por mês, na primeira segunda)

Procurar revisões sistemáticas e meta-análises novas sobre os assuntos de `ciencia.py` (PubMed e periódicos). Só entra
estudo revisado por pares, com DOI conferido; a frase resume o que o próprio estudo diz.

## 4. Conferir e entregar

- `wrangler dev`, axe (WCAG 2.2 AA) nas páginas mudadas, celular de 390 px sem rolagem lateral, tema escuro.
- Pull request com: o que mudou, a fonte de cada item, prints e a pergunta "Posso publicar? Responda OK ou não para cada item".
- Aviso ao Bruno com o link do pull request. Semana sem novidade: aviso curto dizendo isso.
