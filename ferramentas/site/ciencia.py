"""O que diz a ciência: estudos revisados por pares, conferidos um a um (título, revista, ano e DOI) no PubMed ou na página do periódico.
Cada estudo serve a um ou mais assuntos (as chaves de ASSUNTOS, que batem com o "tema" das votações em parlamentares.json, e os temas do site).
Regra: o achado é o que o próprio estudo diz, sem exagero; quando o estudo é observacional, a frase diz "associado a", não "causa".
Conferido em 9/11/2026."""

ESTUDOS = [
    # ---------------------------------------------------------------- jornada e saúde
    dict(id="pega2021", assuntos=["Trabalho", "trabalho"], tipo="Estimativa OMS/OIT, 194 países",
         ref="Pega F, et al. Environment International, 2021", doi="10.1016/j.envint.2021.106595",
         titulo="Global, regional, and national burdens of ischemic heart disease and stroke attributable to exposure to long working hours for 194 countries, 2000–2016",
         achado="Trabalhar 55 horas ou mais por semana foi ligado a cerca de 745 mil mortes por infarto e AVC no mundo em 2016, segundo a OMS e a OIT. Eram 488 milhões de pessoas nessa jornada."),
    dict(id="kivimaki2015", assuntos=["Trabalho", "trabalho"], tipo="Meta-análise, 603.838 pessoas",
         ref="Kivimäki M, et al. The Lancet, 2015", doi="10.1016/S0140-6736(15)60295-1",
         titulo="Long working hours and risk of coronary heart disease and stroke: a systematic review and meta-analysis",
         achado="Quem trabalha 55 horas ou mais por semana teve risco 33% maior de AVC do que quem trabalha de 35 a 40 horas. Quanto mais horas, maior o risco."),
    dict(id="virtanen2018", assuntos=["trabalho"], tipo="Meta-análise, 189.729 pessoas de 35 países",
         ref="Virtanen M, et al. Scandinavian Journal of Work, Environment & Health, 2018", doi="10.5271/sjweh.3712",
         titulo="Long working hours and depressive symptoms: systematic review and meta-analysis",
         achado="Jornadas longas foram associadas a 14% mais casos novos de sintomas depressivos; a associação foi maior na Ásia, menor na Europa e nula na América do Norte e na Austrália."),
    dict(id="fan2025", assuntos=["Trabalho", "trabalho"], tipo="Estudo de intervenção, 2.896 trabalhadores em 141 empresas",
         ref="Fan W, et al. Nature Human Behaviour, 2025", doi="10.1038/s41562-025-02259-6",
         titulo="Work time reduction via a 4-day workweek finds improvements in workers' well-being",
         achado="Com quatro dias de trabalho e o mesmo salário, por seis meses, melhoraram o burnout, a satisfação com o trabalho e a saúde mental e física. Nas 12 empresas de comparação, não."),
    # ---------------------------------------------------------------- riscos psicossociais e assédio
    dict(id="niedhammer2021", assuntos=["trabalho", "direitos"], tipo="Revisão de 72 meta-análises",
         ref="Niedhammer I, Bertrais S, Witt K. Scandinavian Journal of Work, Environment & Health, 2021", doi="10.5271/sjweh.3968",
         titulo="Psychosocial work exposures and health outcomes: a meta-review of 72 literature reviews with meta-analysis",
         achado="As revisões de melhor qualidade ligam alta exigência com pouco controle sobre o trabalho, e as jornadas longas, a doença coronariana, AVC e depressão. As associações são mais fortes para os transtornos mentais."),
    dict(id="rugulies2017", assuntos=["trabalho"], tipo="Meta-análise de 8 coortes, 84.963 trabalhadores",
         ref="Rugulies R, Aust B, Madsen IEH. Scandinavian Journal of Work, Environment & Health, 2017", doi="10.5271/sjweh.3632",
         titulo="Effort–reward imbalance at work and risk of depressive disorders",
         achado="Quem vive desequilíbrio entre o esforço que dá e o que recebe (salário, respeito, segurança) teve risco 49% maior de desenvolver depressão."),
    dict(id="theorell2015", assuntos=["trabalho", "direitos"], tipo="Revisão sistemática com meta-análise, 59 estudos",
         ref="Theorell T, et al. BMC Public Health, 2015", doi="10.1186/s12889-015-1954-4",
         titulo="A systematic review including meta-analysis of work environment and depressive symptoms",
         achado="Pouca autonomia, alta pressão com pouco controle e o assédio no trabalho aumentam os sintomas depressivos com o tempo, em homens e mulheres. São condições que a organização do trabalho pode mudar."),
    dict(id="nielsen2014", assuntos=["direitos", "trabalho"], tipo="Meta-análise de estudos longitudinais",
         ref="Nielsen MB, Magerøy N, Gjerstad J, Einarsen S. Tidsskrift for Den norske legeforening, 2014", doi="10.4045/tidsskr.13.0880",
         titulo="Workplace bullying and subsequent health problems",
         achado="Quem sofreu assédio no trabalho teve 68% mais chance de problemas de saúde mental depois, e 77% mais de sintomas físicos. Adoecer também aumentou a chance de ser assediado: um ciclo."),
    # ---------------------------------------------------------------- igualdade e cotas
    dict(id="bennedsen2022", assuntos=["Trabalho", "direitos"], tipo="Estudo quase-experimental, dados de empresas da Dinamarca",
         ref="Bennedsen M, et al. The Journal of Finance, 2022", doi="10.1111/jofi.13136",
         titulo="Do Firms Respond to Gender Pay Gap Transparency?",
         achado="Quando a lei obrigou as empresas a divulgar salários por sexo, a diferença entre homens e mulheres caiu cerca de 2 pontos percentuais (13%), sem afetar o lucro das empresas."),
    dict(id="vieira2019", assuntos=["Direitos"], tipo="Estudo com dados de universidades brasileiras",
         ref="Vieira RS, Arends-Kuenning M. Economics of Education Review, 2019", doi="10.1016/j.econedurev.2019.101931",
         titulo="Affirmative action in Brazilian universities: Effects on the enrollment of targeted groups",
         achado="As cotas aumentaram a matrícula de estudantes de escola pública e de pessoas negras, inclusive nos cursos mais disputados. Só as cotas com critério racial mudaram o perfil racial dos alunos."),
    # ---------------------------------------------------------------- impostos
    dict(id="medeiros2015", assuntos=["Impostos", "bolso"], tipo="Estudo com dados do Imposto de Renda",
         ref="Medeiros M, Souza PHGF, Castro FA. Dados – Revista de Ciências Sociais, 2015", doi="10.1590/00115258201537",
         titulo="O topo da distribuição de renda no Brasil: primeiras estimativas com dados tributários e comparação com pesquisas domiciliares (2006-2012)",
         achado="Pelos dados do Imposto de Renda, o 1% mais rico ficou com quase 25% da renda do país entre 2006 e 2012, e o 0,1% mais rico, sozinho, com 11%. As pesquisas domiciliares subestimavam o topo."),
    dict(id="alstadsaeter2019", assuntos=["Impostos"], tipo="Estudo com vazamentos de dados e registros fiscais",
         ref="Alstadsæter A, Johannesen N, Zucman G. American Economic Review, 2019", doi="10.1257/aer.20172043",
         titulo="Tax Evasion and Inequality",
         achado="Com dados de vazamentos de contas no exterior, os 0,01% mais ricos sonegavam cerca de 25% dos impostos que deviam, enquanto as auditorias comuns achavam menos de 5% de sonegação em todas as faixas. A sonegação cresce com a riqueza."),
    # ---------------------------------------------------------------- programas sociais
    dict(id="rasella2013", assuntos=["bolso"], tipo="Estudo com 2.853 municípios",
         ref="Rasella D, et al. The Lancet, 2013", doi="10.1016/S0140-6736(13)60715-1",
         titulo="Effect of a conditional cash transfer programme on childhood mortality: a nationwide analysis of Brazilian municipalities",
         achado="Onde o Bolsa Família chegava a mais famílias, morriam menos crianças de até 5 anos: 17% menos no geral, 65% menos por desnutrição e 53% menos por diarreia."),
    dict(id="ramos2021", assuntos=["bolso"], tipo="Estudo com 6,3 milhões de crianças (Coorte de 100 Milhões)",
         ref="Ramos D, et al. PLOS Medicine, 2021", doi="10.1371/journal.pmed.1003509",
         titulo="Conditional cash transfer program and child mortality: A cross-sectional analysis nested within the 100 Million Brazilian Cohort",
         achado="Crianças de 1 a 4 anos de famílias do Bolsa Família tiveram 17% menos chance de morrer. O efeito foi maior entre filhos de mães negras, prematuros e nos municípios mais pobres."),
    dict(id="bonfim2024", assuntos=["bolso", "trabalho"], tipo="Coorte de 69.901 pessoas",
         ref="Bonfim C, et al. PLOS Medicine, 2024", doi="10.1371/journal.pmed.1004486",
         titulo="Conditional cash transfers and mortality in people hospitalised with psychiatric disorders",
         achado="Pessoas que já tinham sido internadas por transtorno mental e passaram a receber o Bolsa Família tiveram 7% menos risco de morrer."),
    dict(id="wardle2024", assuntos=["bolso"], tipo="Comissão de especialistas da The Lancet Public Health",
         ref="Wardle H, et al. The Lancet Public Health, 2024", doi="10.1016/S2468-2667(24)00167-1",
         titulo="The Lancet Public Health Commission on gambling",
         achado="Cerca de 80 milhões de adultos no mundo têm jogo problemático. Entre quem aposta em esportes, até 8,9% dos adultos e 16,3% dos adolescentes podem ter transtorno do jogo; nos cassinos online, 15,8% e 26,4%."),
    # ---------------------------------------------------------------- terra e ambiente
    dict(id="baragwanath2020", assuntos=["Terra e ambiente"], tipo="Estudo com imagens de satélite, 1982–2016",
         ref="Baragwanath K, Bayi E. PNAS, 2020", doi="10.1073/pnas.1917874117",
         titulo="Collective property rights reduce deforestation in the Brazilian Amazon",
         achado="Terras indígenas com a demarcação concluída (homologadas) têm significativamente menos desmatamento; nas que não têm o direito pleno, o efeito não aparece."),
    dict(id="nepstad2006", assuntos=["Terra e ambiente"], tipo="Estudo com imagens de satélite da Amazônia",
         ref="Nepstad D, et al. Conservation Biology, 2006", doi="10.1111/j.1523-1739.2006.00351.x",
         titulo="Inhibition of Amazon deforestation and fire by parks and indigenous lands",
         achado="Terras indígenas e unidades de conservação freiam o desmatamento e o fogo; muitas terras indígenas impediram o desmatamento mesmo cercadas por ele. São a principal barreira ao desmatamento na Amazônia."),
    dict(id="assuncao2015", assuntos=["Terra e ambiente"], tipo="Estudo com dados de municípios da Amazônia",
         ref="Assunção J, Gandour C, Rocha R. Environment and Development Economics, 2015", doi="10.1017/S1355770X15000078",
         titulo="Deforestation slowdown in the Brazilian Amazon: prices or policies?",
         achado="As políticas de fiscalização e controle de 2004 e 2008 evitaram cerca de 73 mil km² de desmatamento de 2005 a 2009, mais da metade do que seria derrubado sem elas."),
    # ---------------------------------------------------------------- democracia
    dict(id="luhrmann2019", assuntos=["Democracia"], tipo="Estudo com dados do V-Dem desde 1900",
         ref="Lührmann A, Lindberg SI. Democratization, 2019", doi="10.1080/13510347.2019.1582029",
         titulo="A third wave of autocratization is here: what is new about it?",
         achado="Hoje as democracias costumam recuar aos poucos e por dentro: em 33 de 47 casos desde 1994, quem enfraqueceu a democracia foram governantes eleitos, usando leis e processos de fachada."),
    # ---------------------------------------------------------------- redes e desinformação
    dict(id="vosoughi2018", assuntos=["Redes", "fatos"], tipo="Estudo com 126 mil boatos no Twitter, 2006–2017",
         ref="Vosoughi S, Roy D, Aral S. Science, 2018", doi="10.1126/science.aap9559",
         titulo="The spread of true and false news online",
         achado="A mentira se espalhou mais longe, mais rápido e para mais gente do que a verdade, sobretudo na política. Quem espalha são pessoas, não robôs: a novidade e a surpresa atraem o compartilhamento."),
    dict(id="walter2020", assuntos=["Redes", "fatos"], tipo="Meta-análise de 30 estudos, 20.963 pessoas",
         ref="Walter N, et al. Political Communication, 2020", doi="10.1080/10584609.2019.1668894",
         titulo="Fact-Checking: A Meta-Analysis of What Works and for Whom",
         achado="A checagem de fatos corrige crenças falsas, mas o efeito cai quando a checagem desmente só parte da frase, usa escalas de verdade ou mexe com as convicções políticas de quem lê."),
    dict(id="pennycook2019", assuntos=["Redes", "fatos"], tipo="Dois estudos, 3.446 pessoas",
         ref="Pennycook G, Rand DG. Cognition, 2019", doi="10.1016/j.cognition.2018.06.011",
         titulo="Lazy, not biased: Susceptibility to partisan fake news is better explained by lack of reasoning than by motivated reasoning",
         achado="Quem para para pensar acredita menos em notícia falsa, mesmo quando ela agrada ao seu lado político. O problema maior é a pressa, mais do que o partidarismo."),
    # ---------------------------------------------------------------- segurança e drogas
    dict(id="hughes2010", assuntos=["Segurança"], tipo="Estudo de caso de Portugal",
         ref="Hughes CE, Stevens A. British Journal of Criminology, 2010", doi="10.1093/bjc/azq038",
         titulo="What can we learn from the Portuguese decriminalization of illicit drugs?",
         achado="Depois que Portugal deixou de tratar o porte para uso como crime, em 2001, o uso de drogas não explodiu, caíram o uso problemático e os danos ligados às drogas, e o sistema penal ficou menos sobrecarregado."),
]

# assuntos das votações (parlamentares.json) e temas do site sem estudo direto: dizemos isso com franqueza
SEM_ESTUDO = {
    "Contas públicas": "Não há estudo científico que meça o efeito do arcabouço fiscal de 2023 sobre a vida das pessoas; as fontes aqui são a lei e os relatórios oficiais.",
    "Democracia": None, "Segurança": None,
}

ASSUNTOS = ["Trabalho", "Impostos", "Contas públicas", "Direitos", "Terra e ambiente", "Democracia", "Redes", "Segurança"]


def do_assunto(chave):
    return [e for e in ESTUDOS if chave in e["assuntos"]]
