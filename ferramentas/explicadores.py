"""Conteúdo das páginas explicativas (gerador: explicador.py). Situação em 23/11/2026.
Regras: fonte em tudo; número antes do adjetivo; fato separado de opinião (opinião sempre com quem diz); nada inventado."""

CSS_EXTRA = """<style>
.atual { margin:6px 0 0; }
.lado { display:grid; gap:12px; grid-template-columns:repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); margin-top:8px; }
.lado > div { border:2px solid var(--linha); border-radius:12px; padding:10px 14px; }
.lado h3 { margin:0 0 6px; font-size:1.05rem; }
.passos { margin:8px 0 0; padding-left:1.3em; display:flex; flex-direction:column; gap:6px; }
.cd-2c { display:grid; grid-template-columns:1fr 1fr; gap:2.4cqw; }
.cd-2c > div { background:rgba(255,255,255,.07); border-radius:3cqw; padding:2.6cqw 3cqw; }
.cd-2c b.h { display:block; font-family:'Lexend', sans-serif; font-size:4.2cqw; margin-bottom:1.2cqw; }
.cd-2c .a b.h { color:#7FE0D2; } .cd-2c .c b.h { color:#F0B05A; }
.cd-2c ul { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1.4cqw; font-size:3.5cqw; line-height:1.25; color:#E6EAF0; }
html.feed .cd-2c ul { font-size:3.05cqw; gap:1cqw; } html.feed .cd-2c b.h { font-size:3.7cqw; }
.cd-nums.dois p span { font-size:3.6cqw; font-weight:400; line-height:1.25; color:#DCE2E9; margin-top:1cqw; }
html.feed .cd-nums.dois p span { font-size:3.1cqw; }
.cd-nums.dois b { font-size:8.4cqw; white-space:nowrap; }
html.feed .cd-nums.dois b { font-size:8cqw; }
</style>"""

CAMARA_PL = "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=2562481"
FORUM = "https://revistaforum.com.br/politica/pl-das-big-techs/"
TVSIM = "https://tvsimbrasil.com.br/brasil/politica/noticia/2026/11/15/camara-vota-regulacao-big-techs-pressao-casa-branca"
DACRE = "https://diariodoacre.com.br/big-techs-veem-risco-de-interferencia-em-algoritmos-e-inseguranca-juridica-em-projeto-que-a-camara-pode-votar-na-terca/"
GAZBT = "https://www.gazetadopovo.com.br/republica/sem-consenso-votacao-do-pl-das-big-techs-e-adiada-na-camara"
DPBT = "https://www.diariodepernambuco.com.br/politica/2026/11/11729386-votacao-do-pl-das-big-techs-devera-ficar-para-a-proxima-semana-diz-hugo-motta.html"
L = lambda u, t: f'<a href="{u}" target="_blank" rel="noopener">{t}</a>'

BIG = dict(
    slug="big-techs", zip="Big_Techs", cor="#1F4E8C", kicker="PL DAS BIG TECHS", placa="CONGRESSO",
    titulo="PL das Big Techs: o que é e o que muda", curto="PL das Big Techs",
    desc="O PL 4.675/2025 dá ao Cade regras próprias para as maiores plataformas digitais. O que muda, quem defende, quem critica e quando vota. Com fontes.",
    soc="PL das Big Techs: o que é, o que muda e quem defende ou critica, com fontes.",
    og=("PL das Big Techs", "Congresso · explicado", "O que muda com o PL 4.675/2025", "Concorrência nas plataformas digitais: o que diz o texto, quem defende, quem critica e quando vota."),
    h1="PL das Big Techs <span>(PL 4.675/2025)</span>",
    sub="O projeto dá ao Cade, o órgão que defende a concorrência, regras próprias para as maiores plataformas digitais. O que muda, o que não muda, quem defende, quem critica e quando vota.",
    atual="Situação em 23/11/2026: a votação prevista para 17/11 foi adiada, sem consenso entre as bancadas. O presidente da Câmara, Hugo Motta (Republicanos-PB), disse que a nova data depende das conversas do relator com as bancadas. Ainda não há data.",
    data_txt="23/11/2026",
    atalhos=[("frase", "Em uma frase"), ("quem", "Quem entra"), ("muda", "O que muda"), ("conteudo", "É sobre conteúdo?"),
             ("debate", "Quem defende e quem critica"), ("fora", "Pressão de fora"), ("caminho", "Próximos passos")],
    secoes=[
        f"""  <section class="forma" id="frase" aria-labelledby="frase-t" style="--c:#1F4E8C;--ce:#A6C8FF"><h2 id="frase-t">Em uma frase</h2>
    <p class="def">O PL 4.675/2025 muda a lei de defesa da concorrência (Lei 12.529/2011) para que o <b>Cade</b> possa impor obrigações às maiores plataformas digitais <b>antes</b> que uma prática prejudique a concorrência, e não só depois.</p>
    <ul><li><b>Autor:</b> Poder Executivo, em 18/9/2025.</li><li><b>Relator na Câmara:</b> deputado Aliel Machado (PV-PR), que mudou o texto em julho de 2026.</li>
    <li><b>Apelido:</b> “PL das Big Techs”. Não confunda com o PL 2630/2020, o “PL das Fake News”, que trata de conteúdo nas redes.</li></ul>
    <p class="fte">Fontes: {L(CAMARA_PL, 'Câmara dos Deputados, ficha do PL 4.675/2025')}; {L(FORUM, 'Revista Fórum')}.</p></section>""",
        f"""  <section class="forma" id="quem" aria-labelledby="quem-t" style="--c:#2D6A2E;--ce:#93D896"><h2 id="quem-t">Quem entra na regra</h2>
    <ul class="nums"><li><b>R$ 50 bi</b><span class="t">de faturamento por ano no mundo</span><span class="f">referência do parecer do relator</span></li>
    <li><b>R$ 5 bi</b><span class="t">de faturamento por ano no Brasil</span><span class="f">referência do parecer do relator</span></li></ul>
    <p>Passar desses valores <b>não enquadra automaticamente</b>. O Cade decide, com decisão fundamentada, se a empresa é um “agente econômico de relevância sistêmica em mercados digitais”, olhando seis pontos:</p>
    <ul><li>mercado de vários lados (quem usa e quem anuncia ou vende)</li><li>efeito de rede (quanto mais gente usa, mais difícil sair)</li><li>empresa que atua em vários elos e monta um “ecossistema”</li>
    <li>dependência de terceiros (lojas, apps, criadores)</li><li>controle e cruzamento de dados</li><li>controle do acesso a esse ecossistema</li></ul>
    <p class="fte">Fontes: {L(FORUM, 'Revista Fórum')}; {L(DACRE, 'Diário do Acre')}.</p></section>""",
        f"""  <section class="forma" id="muda" aria-labelledby="muda-t" style="--c:#9A5F0C;--ce:#F0B05A"><h2 id="muda-t">O que muda</h2>
    <ul><li><b>Nova Superintendência de Mercados Digitais</b>, dentro do Cade, para acompanhar, pedir informações, investigar e cobrar as obrigações.</li>
    <li><b>Transparência:</b> divulgar termos de uso, critérios de ranqueamento e de busca, preços e taxas cobradas.</li>
    <li><b>Aviso antes:</b> avisar com antecedência quem usa a plataforma quando as regras mudarem.</li>
    <li><b>Sem favorecer o próprio produto</b> (o chamado autofavorecimento) contra o de outras empresas.</li>
    <li><b>Portabilidade e interoperabilidade:</b> levar seus dados para outro serviço e fazer serviços conversarem entre si.</li>
    <li><b>Consultas e audiências públicas</b> antes das decisões. Quem descumprir responde às sanções da lei da concorrência e a multas previstas no projeto.</li></ul>
    <p class="fte">Fontes: {L(FORUM, 'Revista Fórum')}; {L(DACRE, 'Diário do Acre')}.</p></section>""",
        f"""  <section class="forma" id="conteudo" aria-labelledby="conteudo-t" style="--c:#1F7F73;--ce:#5FD3C2"><h2 id="conteudo-t">É sobre conteúdo ou censura?</h2>
    <p class="def">O projeto muda a <b>lei da concorrência</b>. A ementa oficial fala em designar empresas, dar obrigações e criar a superintendência no Cade.</p>
    <div class="lado"><div><h3>O que dizem o relator e entidades da sociedade civil</h3><p>O texto trata de concorrência e não de conteúdo: não decide que post fica ou sai. (Aliel Machado; Data Privacy Brasil, Artigo 19 e Idec)</p></div>
    <div><h3>O que dizem as empresas</h3><p>Se o Cade puder mexer em ranqueamento, dados e termos de uso, isso pode mudar a forma como o conteúdo chega às pessoas e trazer insegurança jurídica. (Conselho Digital)</p></div></div>
    <p class="fte">Fontes: {L(CAMARA_PL, 'Câmara, ementa do PL 4.675/2025')}; {L(TVSIM, 'TV Sim (15/11/2026)')}; {L(DACRE, 'Diário do Acre')}.</p></section>""",
        f"""  <section class="forma" id="debate" aria-labelledby="debate-t" style="--c:#4B3F99;--ce:#B7B1F2"><h2 id="debate-t">Quem defende e quem critica</h2>
    <div class="lado"><div><h3>A favor</h3><ul><li>O governo federal, autor do projeto</li><li>22 economistas e professores, em carta de 13/11/2026 ao presidente da Câmara, Hugo Motta: dizem que o texto reduz a concentração de poder econômico e protege pequenos negócios</li><li>Entidades como Data Privacy Brasil, Artigo 19 e Idec</li></ul></div>
    <div><h3>Contra ou com ressalvas</h3><ul><li>Conselho Digital (reúne Amazon, Google, Meta, OpenAI, TikTok, Kwai e Hotmart): risco de interferência nos algoritmos e poder demais ao Cade sem prova de conduta errada; propõe reforçar o Cade com pessoal e orçamento</li><li>ALAI (associação latino-americana de internet): pede critérios mais claros para “relevância sistêmica”</li><li>Parte do centrão e da oposição na Câmara</li></ul></div></div>
    <p class="fte">Fontes: {L(TVSIM, 'TV Sim (15/11/2026)')}; {L(DACRE, 'Diário do Acre')}; {L(FORUM, 'Revista Fórum')}.</p></section>""",
        f"""  <section class="forma" id="fora" aria-labelledby="fora-t" style="--c:#B3261E;--ce:#FF8F84"><h2 id="fora-t">Pressão de fora</h2>
    <ul><li><b>Abril de 2026:</b> o projeto aparece no relatório anual de barreiras comerciais do USTR, o escritório de comércio do governo dos EUA.</li>
    <li><b>Julho de 2026:</b> 20 congressistas republicanos dos EUA pedem retaliação contra o Brasil por causa do projeto.</li>
    <li>Segundo a CNN Brasil, o tema entrou nas negociações do tarifaço entre Brasil e EUA.</li></ul>
    <p class="fte">Fonte: {L(TVSIM, 'TV Sim (15/11/2026), com informações da CNN Brasil')}.</p></section>""",
        f"""  <section class="forma" id="caminho" aria-labelledby="caminho-t" style="--c:#17191E;--ce:#F2F0EA"><h2 id="caminho-t">Onde está e próximos passos</h2>
    <ol class="passos"><li><b>18/3/2026:</b> a Câmara aprova a urgência, por 276 votos a 186. O projeto pode ir direto ao plenário.</li>
    <li><b>8/7/2026:</b> o relator apresenta o parecer no plenário.</li>
    <li><b>17/11/2026:</b> a votação no plenário da Câmara é adiada, sem consenso entre as bancadas. A nova data ainda não foi marcada.</li>
    <li><b>Depois:</b> vai ao Senado. Se o Senado mudar o texto, volta à Câmara. No fim, sanção ou veto do presidente.</li></ol>
    <p>Como votou cada deputado vai aparecer no <a href="/semana">Placar da semana</a>. Quer cobrar? Veja <a href="/quem-cobrar">de quem cobrar cada coisa</a> e <a href="/parlamentares">a ficha de cada parlamentar</a>.</p>
    <p class="fte">Fontes: {L(CAMARA_PL, 'Câmara, ficha do PL 4.675/2025')}; {L(TVSIM, 'TV Sim (15/11/2026)')}; {L(FORUM, 'Revista Fórum')}; adiamento: {L(GAZBT, 'Gazeta do Povo (17/11/2026)')} e {L(DPBT, 'Diario de Pernambuco (17/11/2026)')}.</p></section>""",
    ],
    fontes=[
        f"Tramitação e ementa: {L(CAMARA_PL, 'Câmara dos Deputados, ficha do PL 4.675/2025')} (consultada em 16/11/2026).",
        f"Adiamento de 17/11: {L(GAZBT, 'Gazeta do Povo, “Sem consenso, votação do PL das Big Techs é adiada na Câmara” (17/11/2026)')}; {L(DPBT, 'Diario de Pernambuco, “Votação do PL das big techs deverá ficar para a próxima semana, diz Hugo Motta” (17/11/2026)')}.",
        f"Conteúdo do parecer, critérios e obrigações: {L(FORUM, 'Revista Fórum, “Veja as propostas do PL das Big Techs”')}; {L(DACRE, 'Diário do Acre, “Big techs veem risco de interferência em algoritmos…”')}.",
        f"Urgência (276 a 186), carta dos economistas, pressão dos EUA, posições a favor e contra: {L(TVSIM, 'TV Sim, “Câmara vota regulação das big techs sob pressão da Casa Branca” (15/11/2026)')}.",
    ],
    cards=[
        dict(tipo="capa", rotulo="Capa: PL das Big Techs", alt="O que é o PL 4.675/2025, que espera votação na Câmara. A votação de 17/11 foi adiada.",
             fonte="Fontes em cada card: Câmara dos Deputados e imprensa",
             html='<p class="cd-t">PL das Big Techs</p><p class="cd-s">O que é o PL 4.675/2025, que espera votação na Câmara.</p><p class="cd-x">O que muda, quem entra, quem defende, quem critica e o que vem depois.</p><p class="cd-s2">Passe para o lado →</p>'),
        dict(rotulo="Em uma frase", alt="O projeto dá ao Cade poder de impor obrigações às maiores plataformas antes de um abuso, e não só depois.",
             fonte="Fonte: Câmara dos Deputados, PL 4.675/2025",
             html='<p class="ff-tag dado">EM UMA FRASE</p><p class="cd-t2">O Cade passa a poder criar regras para as maiores plataformas antes de um abuso, e não só depois.</p><p class="cd-x">Cade é o órgão federal que defende a concorrência. O projeto muda a lei da concorrência (Lei 12.529/2011).</p><p class="cd-x2">Autor: governo federal (set./2025). Relator: Aliel Machado (PV-PR).</p>'),
        dict(rotulo="Quem entra", alt="Referência de faturamento: R$ 50 bilhões no mundo ou R$ 5 bilhões no Brasil por ano; o Cade decide caso a caso.",
             fonte="Fontes: parecer do relator, via Revista Fórum e Diário do Acre",
             html='<p class="ff-tag dado">QUEM ENTRA</p><div class="cd-nums dois"><p><b>R$ 50 bi</b><span>por ano no mundo</span></p><p><b>R$ 5 bi</b><span>por ano no Brasil</span></p></div><p class="cd-t3">É a referência de faturamento. Não enquadra sozinha.</p><p class="cd-x">O Cade decide caso a caso, olhando efeito de rede, controle de dados e quanto outras empresas dependem da plataforma.</p>'),
        dict(rotulo="O que muda", alt="Superintendência de Mercados Digitais, transparência, aviso prévio, sem autofavorecimento, portabilidade.",
             fonte="Fontes: parecer do relator, via Revista Fórum e Diário do Acre",
             html='<p class="ff-tag ok">O QUE MUDA</p><ul class="cd-lst"><li>Nova <b>Superintendência de Mercados Digitais</b> no Cade</li><li>Mostrar <b>regras, ranqueamento, preços e taxas</b></li><li><b>Avisar antes</b> quando mudar as regras</li><li><b>Não favorecer</b> o próprio produto contra o dos outros</li><li>Levar seus <b>dados</b> para outro serviço</li></ul>'),
        dict(rotulo="É sobre conteúdo?", alt="O relator e entidades dizem que trata de concorrência; as empresas dizem que mexer no ranqueamento pode mudar como o conteúdo chega.",
             fonte="Fontes: Câmara (ementa); TV Sim, 15/11/2026; Diário do Acre",
             html='<p class="ff-tag alerta">É CENSURA?</p><p class="cd-t3">A lei que muda é a da concorrência. Não é o PL das Fake News (PL 2630).</p><p class="cd-x"><b>Relator, Idec, Artigo 19 e Data Privacy Brasil:</b> o texto trata de concorrência, não decide que post fica ou sai.</p><p class="cd-x"><b>Empresas (Conselho Digital):</b> mexer no ranqueamento pode mudar como o conteúdo chega a você.</p>'),
        dict(rotulo="Quem defende e quem critica", alt="A favor: governo, 22 economistas, Idec, Artigo 19, Data Privacy Brasil. Contra ou com ressalvas: Conselho Digital, ALAI, parte do centrão e da oposição.",
             fonte="Fontes: TV Sim, 15/11/2026; Diário do Acre",
             html='<p class="ff-tag dado">O DEBATE</p><div class="cd-2c"><div class="a"><b class="h">A favor</b><ul><li>Governo federal</li><li>22 economistas, em carta de 13/11</li><li>Idec, Artigo 19, Data Privacy Brasil</li></ul></div><div class="c"><b class="h">Contra ou com ressalvas</b><ul><li>Conselho Digital: Amazon, Google, Meta, OpenAI, TikTok, Kwai, Hotmart</li><li>ALAI</li><li>Parte do centrão e da oposição</li></ul></div></div><p class="cd-x2">A favor: menos concentração, mais chance para pequenos negócios. Contra: poder demais ao Cade e insegurança jurídica.</p>'),
        dict(rotulo="Pressão de fora", alt="Relatório do USTR em abril, pedido de retaliação de 20 republicanos em julho, e o tema no tarifaço.",
             fonte="Fonte: TV Sim, 15/11/2026, com informações da CNN Brasil",
             html='<p class="ff-tag alerta">PRESSÃO DE FORA</p><ul class="cd-lst anos"><li><b>Abril de 2026</b>O projeto entra no relatório de barreiras comerciais do governo dos EUA (USTR)</li><li><b>Julho de 2026</b>20 congressistas republicanos pedem retaliação contra o Brasil</li><li><b>Tarifaço</b>Segundo a CNN Brasil, o tema entrou na negociação entre os dois países</li></ul>'),
        dict(tipo="fim", rotulo="Próximos passos", alt="Urgência aprovada por 276 a 186 em 18/3; votação de 17/11 adiada, sem nova data; depois Senado e sanção.",
             fonte="Fontes: Câmara dos Deputados; TV Sim, 15/11/2026; Gazeta do Povo, 17/11/2026",
             html='<p class="cd-t2">E agora?</p><ul class="cd-lst anos"><li><b>18/3: urgência aprovada</b>276 votos a 186</li><li><b>17/11: votação adiada</b>sem consenso; nova data ainda não marcada</li><li><b>Depois: Senado</b>se mudar, volta à Câmara; no fim, sanção ou veto</li></ul><p class="cd-s2">O que muda, o debate e as fontes:<span class="ff-url" style="font-size:3.1cqw">vigieademocracia.brunochapadeiro.workers.dev/big-techs</span></p>'),
    ],
    whatsapp=("PL das Big Techs (PL 4.675/2025): a votação na Câmara, prevista para 17/11, foi adiada e ainda não tem nova data.\n\n"
              "O que é: o Cade, órgão que defende a concorrência, passa a poder impor obrigações às maiores plataformas digitais antes de um abuso, e não só depois. "
              "Entra quem fatura mais de R$ 50 bi no mundo ou R$ 5 bi no Brasil por ano, e o Cade decide caso a caso.\n\n"
              "O que muda, quem defende, quem critica e próximos passos, com fonte: https://vigieademocracia.brunochapadeiro.workers.dev/big-techs"),
    legenda=("PL DAS BIG TECHS: O QUE É E O QUE MUDA\n\n"
             "O PL 4.675/2025 espera votação na Câmara: a de 17/11 foi adiada, sem nova data. Em resumo:\n\n"
             "• O Cade, órgão que defende a concorrência, passa a poder impor obrigações às maiores plataformas digitais antes de um abuso, e não só depois.\n"
             "• Referência: faturamento de R$ 50 bi por ano no mundo ou R$ 5 bi no Brasil. Não enquadra sozinha: o Cade decide caso a caso.\n"
             "• Obrigações: mostrar regras, ranqueamento, preços e taxas; avisar antes de mudar as regras; não favorecer o próprio produto; portabilidade de dados.\n"
             "• A favor: governo, 22 economistas (carta de 13/11), Idec, Artigo 19, Data Privacy Brasil. Contra ou com ressalvas: Conselho Digital (Amazon, Google, Meta e outras), ALAI, parte do centrão e da oposição.\n"
             "• A urgência passou por 276 a 186 em março. Depois da Câmara, vai ao Senado.\n\n"
             "Tudo com fonte no site (link na bio): vigieademocracia.brunochapadeiro.workers.dev/big-techs\n"
             "Fontes: Câmara dos Deputados; Revista Fórum; TV Sim (15/11/2026); Diário do Acre. Feito com auxílio de IA (Claude).\n"
             "© 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0\n\n"
             "#DeOlhoNoCongresso #BigTechs #PL4675"),
)

# ------------------------------------------------------------------ ajuste fiscal
AGSEN = "https://www12.senado.leg.br/noticias/materias/2026/11/12/texto-principal-do-ajuste-fiscal-e-aprovado-pelo-senado"
PRES = "https://www12.senado.leg.br/institucional/presidencia/consultarnoticia?noticia_id=senado-aprova-texto-base-de-projeto-de-ajuste-fiscal-com-previsao-de-economia-de-ate-r-60-bilhoes"
VOT = "https://www25.senado.leg.br/web/atividade/materias/-/materia/176328/votacoes"
OPOVO = "https://www.opovo.com.br/noticias/economia/2026/11/12/por-40-a-38-senado-aprova-urgencia-para-plp-de-ajuste-fiscal.html"
ISTOE = "https://istoe.com.br/moretti-pacote-fiscal-salario-minimo-saude-2026-2"
FENACON = "https://fenacon.org.br/noticias/senado-completa-votacao-e-ajuste-fiscal-segue-para-a-camara/"
OPOVO18 = "https://www.opovo.com.br/noticias/economia/2026/11/18/senado-aprova-plp-de-ajuste-fiscal-texto-segue-para-camara.html"
CEF = "https://www.congressoemfoco.com.br/noticia/131713/motta-convoca-sessao-extra-para-discutir-ajuste-fiscal-na-segunda"
GAZ19 = "https://www.gazetadopovo.com.br/republica/motta-agenda-votacao-ajuste-fiscal-lula-camara-segunda-feira-23/"
GAZETA = "https://gazetadopovo.com.br/republica/ministro-de-lula-rebate-criticas-ao-ajuste-fiscal-e-dispara-contra-esquerda-sectaria"
OREIRO = "https://joseluisoreiro.substack.com/p/o-pacote-fiscal-do-senado-plp-2992026"
PODCAST = "https://open.spotify.com/episode/5zZxfXS2rLBSidVmClO1EZ"

AJUSTE = dict(
    slug="ajuste-fiscal", zip="Ajuste_fiscal", cor="#2D6A2E", kicker="AJUSTE FISCAL", placa="BOLSO",
    titulo="Ajuste fiscal: o que é e o que muda", curto="Ajuste fiscal",
    desc="O PLP 299/2026, aprovado no Senado (69 a 2 na versão final) e agora na Câmara: o que muda nos gastos e nos benefícios fiscais, o que fica protegido, o debate e os próximos passos. Com fontes.",
    soc="Ajuste fiscal (PLP 299/2026): o que muda, o que fica protegido e o debate, com fontes.",
    og=("Ajuste fiscal", "Bolso · explicado", "O que muda com o PLP 299/2026", "Gastos, benefícios fiscais, saúde, salário mínimo e o debate, com os números oficiais."),
    h1="Ajuste fiscal <span>(PLP 299/2026)</span>",
    sub="O projeto do governo para equilibrar as contas de 2027. O Senado concluiu a votação em 18/11 e o texto está na Câmara. O que muda, o que fica protegido, quem defende, quem critica e o que vem agora.",
    atual="Situação em 23/11/2026: o Senado concluiu a votação em 18/11 (69 a 2 na versão final). Na Câmara, o relator é Mauro Benevides Filho (União-CE); o presidente, Hugo Motta (Republicanos-PB), marcou sessão nesta segunda (23/11) para começar a discussão. A data da votação ainda não está confirmada.",
    data_txt="23/11/2026",
    atalhos=[("numeros", "Os números"), ("gasto", "Gastos"), ("impostos", "Benefícios fiscais"), ("protegido", "O que fica protegido"),
             ("duvidas", "Salário mínimo, saúde, Bolsa Família"), ("debate", "O debate"), ("caminho", "Próximos passos"), ("ouca", "Ouça")],
    secoes=[
        f"""  <section aria-labelledby="nm-t" id="numeros"><h2 id="nm-t">Os números</h2><ul class="nums">
    <li><b>R$ 50 a 60 bi</b><span class="t">de economia prevista em 2027</span><span class="d">o relatório técnico do Senado estima R$ 45,1 a 56,1 bi</span><span class="f">Fonte: Ministério do Planejamento, via Senado (12/11/2026)</span></li>
    <li><b>0,5% do PIB</b><span class="t">meta de superávit primário em 2027, cerca de R$ 73,2 bi</span><span class="d">aceita resultado entre 0,25% e 0,75%</span><span class="f">Fontes: Agência Senado; IstoÉ (16/11/2026)</span></li>
    <li><b>45 a 31</b><span class="t">votos no Senado para o texto principal, em 12/11</span><span class="d">a urgência passou antes por 40 a 38</span><span class="f">Fonte: Senado Federal, votações do PLP 299/2026</span></li></ul>
    <p class="fte" style="margin-top:8px">Superávit primário: quanto o governo arrecada a mais do que gasta, sem contar os juros da dívida. Valores de economia são estimativas, não resultado.</p></section>""",
        f"""  <section class="forma" id="gasto" aria-labelledby="gasto-t" style="--c:#2D6A2E;--ce:#93D896"><h2 id="gasto-t">O que muda nos gastos</h2>
    <ul><li><b>Limite menor em ano de aperto:</b> quando houver bloqueio extra de despesas, o gasto só pode crescer 2% acima da inflação, e não 2,5% como no arcabouço fiscal. Vale só para o ano em que for aplicado.</li>
    <li><b>Mais bloqueio:</b> o governo pode bloquear mais despesas para buscar o centro da meta, mesmo quando o resultado já estiver dentro da faixa aceita.</li>
    <li><b>Lei Kandir:</b> o texto de 12/11 baixava o repasse aos estados de R$ 4 bi para R$ 1 bi por ano e deixava o resto para 2031 a 2037. Pelo acordo de 18/11, o repasse fica em R$ 2 bi em 2027 e o que falta é pago de 2028 a 2030 (fontes: Agência Senado, via Fenacon; Gazeta do Povo, 19/11/2026).</li>
    <li><b>Emendas aprovadas no Senado:</b> restos a pagar de contratos e convênios plurianuais não podem ser bloqueados até o fim de 2027 (Randolfe Rodrigues); parte da economia pode virar investimento no ano seguinte, inclusive indicado por bancadas estaduais (Jader Barbalho); o Fundo Constitucional do DF fica fora da trava se houver déficit (Izalci Lucas).</li></ul>
    <p class="fte">Fontes: {L(AGSEN, 'Agência Senado (12/11/2026)')}; {L(PRES, 'Senado, Presidência (12/11/2026)')}.</p></section>""",
        f"""  <section class="forma" id="impostos" aria-labelledby="impostos-t" style="--c:#9A5F0C;--ce:#F0B05A"><h2 id="impostos-t">O que muda nos benefícios fiscais</h2>
    <ul><li><b>Corte de 10% nos benefícios fiscais</b> (isenções, créditos e regimes especiais que reduzem imposto de empresas e setores).</li>
    <li><b>Ficam de fora do corte:</b> a desoneração da folha de pagamento, a indústria de informática e semicondutores, e a compra de carro por pessoas com deficiência ou com autismo.</li>
    <li><b>Compensação de créditos:</b> o governo pode limitar, por um tempo, o uso de créditos tributários para abater imposto devido.</li>
    <li><b>Diesel:</b> até R$ 10,5 bi da subvenção ao diesel ficam fora da conta da meta de 2026. O governo cita o conflito no Oriente Médio. O dinheiro continua sendo gasto público.</li></ul>
    <p class="fte">Fontes: {L(PRES, 'Senado, Presidência (12/11/2026)')}; {L(AGSEN, 'Agência Senado (12/11/2026)')}.</p></section>""",
        f"""  <section class="forma" id="protegido" aria-labelledby="protegido-t" style="--c:#1F4E8C;--ce:#A6C8FF"><h2 id="protegido-t">O que fica protegido e o que não muda</h2>
    <ul><li><b>Não podem ser bloqueados:</b> os juros da dívida pública e os fundos de ciência, tecnologia e inovação.</li>
    <li><b>Pisos da saúde e da educação continuam.</b> Mas, até 2030, a receita extra do imposto de exportação de petróleo pode ficar fora do cálculo de algumas obrigações, entre elas o piso da saúde.</li>
    <li><b>Supersalários:</b> o Congresso tem 60 dias (prazo reduzido em 18/11) para analisar a regulamentação dos pagamentos acima do teto. O projeto não acaba com os “penduricalhos” sozinho.</li></ul>
    <p class="fte">Fonte: {L(PRES, 'Senado, Presidência (12/11/2026)')}.</p></section>""",
        f"""  <section class="forma" id="duvidas" aria-labelledby="duvidas-t" style="--c:#1F7F73;--ce:#5FD3C2"><h2 id="duvidas-t">Salário mínimo, saúde e Bolsa Família</h2>
    <p class="def">O que circula nas redes, o que dizem os resumos oficiais e o que diz o governo.</p>
    <ul><li><b>Salário mínimo:</b> os resumos do Senado sobre o texto aprovado não citam mudança na regra do salário mínimo. O ministro do Planejamento, Bruno Moretti, diz que a regra de valorização não muda e chama de “mentira” a ideia de que a trava de 2% reduz o aumento.</li>
    <li><b>Saúde e educação:</b> os pisos continuam valendo. A mudança no cálculo com a receita do petróleo (acima) pode limitar o crescimento do piso da saúde, mas não acaba com ele. Moretti diz que as duas áreas devem ter cerca de R$ 30 bi a mais em 2027.</li>
    <li><b>Bolsa Família:</b> os resumos do Senado não citam o programa. Moretti diz que ele não será reduzido.</li></ul>
    <p class="fte">Fontes: {L(PRES, 'Senado, Presidência')}; {L(AGSEN, 'Agência Senado')}; {L(ISTOE, 'IstoÉ (16/11/2026)')}; {L(GAZETA, 'Gazeta do Povo')}. O que é dito pelo ministro está marcado como fala dele.</p></section>""",
        f"""  <section class="forma" id="debate" aria-labelledby="debate-t" style="--c:#4B3F99;--ce:#B7B1F2"><h2 id="debate-t">O debate</h2>
    <div class="lado"><div><h3>O governo</h3><p>O pacote não tira direitos sociais, combate privilégios e, aprovado ainda em 2026, abre espaço para a queda dos juros (Selic). (Bruno Moretti, ministro do Planejamento)</p></div>
    <div><h3>Deputados de PT, PCdoB, PSOL e PV</h3><p>Apresentaram propostas para fazer o ajuste mais pela arrecadação, cobrando mais de quem ganha mais e cortando benefícios fiscais, e menos pelo corte de despesas. (Entre eles, Gleisi Hoffmann, Lindbergh Farias, Rui Falcão, Erika Hilton e Sâmia Bomfim)</p></div>
    <div><h3>Economista José Luis Oreiro</h3><p>O ajuste tira R$ 45 a 60 bi da economia em um ano, sobretudo do investimento público, e não mexe no custo da dívida ligado à Selic. Pode frear a atividade em 2027.</p></div>
    <div><h3>No voto do Senado</h3><p>PT, MDB e PSB votaram quase todos a favor; o PL votou 12 a 2 contra; PSD, PP e Republicanos se dividiram. Veja <a href="/semana">o placar por partido</a>.</p></div></div>
    <p class="fte">Fontes: {L(GAZETA, 'Gazeta do Povo')}; {L(ISTOE, 'IstoÉ (16/11/2026)')}; {L(OREIRO, 'José Luis Oreiro, Substack')}; {L(VOT, 'Senado Federal, votações')}.</p></section>""",
        f"""  <section class="forma" id="caminho" aria-labelledby="caminho-t" style="--c:#17191E;--ce:#F2F0EA"><h2 id="caminho-t">Onde está e próximos passos</h2>
    <ol class="passos"><li><b>11/11/2026:</b> o líder do governo, Jaques Wagner (PT-BA), apresenta o projeto a pedido do Executivo. Relator: Eduardo Braga (MDB-AM).</li>
    <li><b>12/11/2026:</b> o Senado aprova a urgência (40 a 38) e o texto principal (45 a 31).</li>
    <li><b>18/11/2026:</b> o Senado rejeita 3 destaques (47 a 30, 45 a 32 e 49 a 31), o da Lei Kandir é retirado após acordo, e a versão final é aprovada por 69 a 2.</li>
    <li><b>23/11/2026:</b> na Câmara, sessão para começar a discussão. Relator: Mauro Benevides Filho (União-CE). Data da votação ainda não confirmada.</li>
    <li><b>Depois:</b> vai à Câmara. Como é lei complementar, precisa de maioria absoluta: 257 deputados (no Senado, 41). Se a Câmara mudar, volta ao Senado. No fim, sanção ou veto.</li></ol>
    <p class="fte">Fontes: {L(AGSEN, 'Agência Senado')}; {L(VOT, 'Senado Federal, votações')}; {L(OPOVO, 'O Povo (12/11/2026)')}; {L(FENACON, 'Agência Senado, via Fenacon (19/11/2026)')}; {L(OPOVO18, 'O Povo (18/11/2026)')}; {L(CEF, 'Congresso em Foco (19/11/2026)')}; Constituição Federal, art. 69.</p></section>""",
        f"""  <section class="caixa" id="ouca" aria-labelledby="ouca-t"><h2 id="ouca-t">Ouça</h2>
    <p>{L(PODCAST, 'Calma Urgente, episódio “É Justo o Ajuste?” (16/11/2026)')}: Alessandra Orofino, Gregório Duvivier e Bruno Torturra entrevistam o ministro do Planejamento, Bruno Moretti, sobre o motivo do ajuste, o pacote, os juros e a subvenção ao diesel. 97 minutos, no Spotify.</p>
    <p class="fte">É uma entrevista com o ministro: as falas dele são a posição do governo.</p></section>""",
    ],
    fontes=[
        f"Conteúdo do texto aprovado: {L(AGSEN, 'Agência Senado, “Texto principal do ajuste fiscal é aprovado pelo Senado” (12/11/2026)')}; {L(PRES, 'Senado Federal, Presidência, “Senado aprova texto-base de projeto de ajuste fiscal com previsão de economia de até R$ 60 bilhões”')}.",
        f"Placares: {L(VOT, 'Senado Federal, votações do PLP 299/2026')} e dados abertos do Senado (placar da semana); urgência: {L(OPOVO, 'O Povo (12/11/2026)')}.",
        f"Governo e críticas: {L(ISTOE, 'IstoÉ, “Moretti defende pacote fiscal…” (16/11/2026)')}; {L(GAZETA, 'Gazeta do Povo, “Ministro de Lula rebate críticas ao ajuste fiscal…”')}; {L(OREIRO, 'José Luis Oreiro, “O Pacote Fiscal do Senado (PLP 299/2026)”')}.",
        f"Conclusão no Senado (18/11): {L(FENACON, 'Agência Senado, “Senado completa votação, e ajuste fiscal segue para a Câmara”, reproduzida pela Fenacon (19/11/2026)')}; {L(OPOVO18, 'O Povo (18/11/2026)')}; Lei Kandir: {L(GAZ19, 'Gazeta do Povo (19/11/2026)')}; Câmara: {L(CEF, 'Congresso em Foco (19/11/2026)')}.",
        f"Para ouvir: {L(PODCAST, 'Calma Urgente, “É Justo o Ajuste?”, Spotify (16/11/2026)')}.",
    ],
    cards=[
        dict(tipo="capa", rotulo="Capa: Ajuste fiscal", alt="O que é o PLP 299/2026, aprovado no Senado por 69 a 2 na versão final e que agora está na Câmara.",
             fonte="Fontes em cada card: Senado Federal e imprensa",
             html='<p class="cd-t">Ajuste fiscal</p><p class="cd-s">O que é o PLP 299/2026, aprovado no Senado (69 a 2 na versão final) e que agora está na Câmara.</p><p class="cd-x">O que muda, o que fica protegido, o debate e o que vem depois.</p><p class="cd-s2">Passe para o lado →</p>'),
        dict(rotulo="Os números", alt="Economia prevista de R$ 50 a 60 bilhões em 2027 e meta de superávit de 0,5% do PIB.",
             fonte="Fontes: Ministério do Planejamento, via Senado; Agência Senado (12/11/2026)",
             html='<p class="ff-tag dado">OS NÚMEROS</p><p class="cd-big">R$ 50 a 60 bi</p><p class="cd-t3">de economia prevista em 2027, segundo o governo.</p><p class="cd-x">Meta para 2027: superávit de 0,5% do PIB, cerca de R$ 73 bi, ou seja, arrecadar mais do que gastar, sem contar os juros.</p><p class="cd-x2">É estimativa. O relatório do Senado calcula R$ 45 a 56 bi.</p>'),
        dict(rotulo="Gastos", alt="Trava de 2% acima da inflação em ano de bloqueio, mais bloqueios e Lei Kandir menor.",
             fonte="Fontes: Agência Senado (12 e 18/11/2026); Gazeta do Povo (19/11/2026)",
             html='<p class="ff-tag dado">GASTOS</p><ul class="cd-lst"><li>Em ano de aperto, o gasto sobe no máximo <b>2% acima da inflação</b>, não 2,5%</li><li>O governo pode <b>bloquear mais</b> para chegar ao centro da meta</li><li>Lei Kandir: repasse aos estados cai de <b>R$ 4 bi para R$ 2 bi</b> em 2027; o que falta é pago de 2028 a 2030</li></ul>'),
        dict(rotulo="Benefícios fiscais", alt="Corte de 10% nos benefícios fiscais com exceções, limite à compensação de créditos e diesel fora da meta.",
             fonte="Fontes: Senado, Presidência; Agência Senado (12/11/2026)",
             html='<p class="ff-tag dado">BENEFÍCIOS FISCAIS</p><p class="cd-t3">Corte de 10% nas isenções e regimes especiais de impostos.</p><ul class="cd-lst"><li>Fora do corte: desoneração da folha, informática e semicondutores, carro para PcD e autistas</li><li>Limite ao uso de créditos tributários para abater imposto</li><li>Até R$ 10,5 bi do subsídio ao diesel fora da meta de 2026</li></ul>'),
        dict(rotulo="O que fica protegido", alt="Juros da dívida e fundos de ciência não podem ser bloqueados; pisos continuam, mas receita do petróleo sai do cálculo do piso da saúde até 2030.",
             fonte="Fonte: Senado, Presidência (12/11/2026)",
             html='<p class="ff-tag ok">O QUE FICA PROTEGIDO</p><ul class="cd-lst"><li><b>Não podem ser bloqueados:</b> juros da dívida e fundos de ciência e tecnologia</li><li><b>Pisos de saúde e educação continuam.</b> Mas, até 2030, a receita extra da exportação de petróleo pode sair do cálculo do piso da saúde</li><li><b>Supersalários:</b> 60 dias para o Congresso analisar a regra. Não acabam sozinhos</li></ul>'),
        dict(rotulo="Salário mínimo e Bolsa Família", alt="Os resumos do Senado não citam mudança; o ministro diz que não mudam.",
             fonte="Fontes: Senado (resumos do texto); IstoÉ e Gazeta do Povo, falas do ministro",
             html='<p class="ff-tag alerta">CIRCULA NAS REDES</p><p class="cd-t3">Mexe no salário mínimo ou no Bolsa Família?</p><p class="cd-x"><b>O texto:</b> os resumos oficiais do Senado não citam mudança em nenhum dos dois.</p><p class="cd-x"><b>O governo:</b> o ministro Bruno Moretti diz que a regra do mínimo não muda e que o Bolsa Família não será reduzido.</p><p class="cd-x2">Na dúvida, confira a fonte antes de compartilhar.</p>'),
        dict(rotulo="O debate", alt="Governo, deputados de esquerda e o economista José Luis Oreiro; no Senado, o PL votou 12 a 2 contra.",
             fonte="Fontes: IstoÉ; Gazeta do Povo; J. L. Oreiro; Senado Federal",
             html='<p class="ff-tag dado">O DEBATE</p><ul class="cd-lst"><li><b>Governo:</b> não tira direitos e abre espaço para os juros caírem</li><li><b>Deputados de PT, PCdoB, PSOL e PV:</b> ajuste deveria vir mais de imposto de quem ganha mais</li><li><b>Economista J. L. Oreiro:</b> corta investimento, não mexe nos juros e pode frear a economia em 2027</li><li><b>No voto:</b> PT, MDB e PSB a favor; PL 12 a 2 contra</li></ul>'),
        dict(tipo="fim", rotulo="Próximos passos", alt="Senado conclui em 18/11 por 69 a 2; agora a Câmara, que precisa de 257 votos; depois sanção ou veto.",
             fonte="Fontes: Agência Senado; Congresso em Foco; Constituição, art. 69",
             html='<p class="cd-t2">E agora?</p><ul class="cd-lst anos"><li><b>18/11: Senado conclui</b>versão final aprovada por 69 a 2</li><li><b>Agora: Câmara</b>precisa de 257 votos; relator Mauro Benevides Filho</li><li><b>No fim</b>sanção ou veto do presidente</li></ul><p class="cd-s2">Tudo com fonte, e onde ouvir o ministro:<span class="ff-url" style="font-size:3.0cqw">vigieademocracia.brunochapadeiro.workers.dev/ajuste-fiscal</span></p>'),
    ],
    whatsapp=("Ajuste fiscal (PLP 299/2026): o Senado concluiu a votação em 18/11 (69 a 2 na versão final). Agora está na Câmara.\n\n"
              "O que muda: em ano de aperto, o gasto só cresce 2% acima da inflação (e não 2,5%); corte de 10% nos benefícios fiscais de empresas e setores; economia prevista de R$ 50 a 60 bi em 2027.\n"
              "Os pisos de saúde e educação continuam, e os resumos do Senado não citam mudança no salário mínimo nem no Bolsa Família.\n\n"
              "O que muda, o que fica protegido e o debate, com fonte: https://vigieademocracia.brunochapadeiro.workers.dev/ajuste-fiscal"),
    legenda=("AJUSTE FISCAL: O QUE É E O QUE MUDA\n\n"
             "O Senado aprovou o PLP 299/2026: texto principal por 45 a 31 (12/11) e versão final por 69 a 2 (18/11). Agora está na Câmara. Em resumo:\n\n"
             "• Economia prevista de R$ 50 a 60 bi em 2027 (governo). Meta: superávit de 0,5% do PIB.\n"
             "• Em ano de aperto, o gasto sobe no máximo 2% acima da inflação, não 2,5%.\n"
             "• Corte de 10% nos benefícios fiscais, com exceções (folha, informática, carro para PcD e autistas).\n"
             "• Juros da dívida e fundos de ciência não podem ser bloqueados. Pisos de saúde e educação continuam, mas a receita extra do petróleo pode sair do cálculo do piso da saúde até 2030.\n"
             "• Os resumos do Senado não citam mudança no salário mínimo nem no Bolsa Família; o ministro Bruno Moretti diz que não mudam.\n"
             "• Próximos passos: a Câmara, que precisa de 257 votos; relator Mauro Benevides Filho (União-CE). Depois, sanção ou veto.\n\n"
             "O debate, as fontes e o podcast com o ministro no site (link na bio): vigieademocracia.brunochapadeiro.workers.dev/ajuste-fiscal\n"
             "Fontes: Agência Senado; Senado Federal; IstoÉ; Gazeta do Povo. Feito com auxílio de IA (Claude).\n"
             "© 2026 Prof. Bruno Chapadeiro · CC BY-NC-SA 4.0\n\n"
             "#DeOlhoNoCongresso #AjusteFiscal #PLP299"),
)

PAGINAS = [BIG, AJUSTE]
