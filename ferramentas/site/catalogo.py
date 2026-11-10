"""Catálogo do Vigie a Democracia: um lugar só para os temas, as páginas, os jogos e os materiais.
Daqui saem a página inicial, as páginas de tema (/tema/<id>), a página Jogar, a busca, o menu, a trilha "Você está em"
e o bloco "Continue no tema" de cada página. Para pôr algo novo no site, acrescente um item aqui e rode organiza.py."""

SITE = "https://vigieademocracia.brunochapadeiro.workers.dev/"

# ------------------------------------------------------------------ temas (a ordem é a do site)
TEMAS = [
    dict(id="congresso", nome="Congresso e votos", curto="Congresso", ic="congresso", cor="#1F4E8C", corEsc="#A6C8FF",
         frase="Como votou quem foi eleito, de quem cobrar cada coisa e o que o Congresso decidiu na semana. Dados oficiais da Câmara e do Senado.",
         pergunta="Quer saber como vota quem representa você?", assuntos=["Democracia", "Contas públicas"]),
    dict(id="fatos", nome="Fatos e boatos", curto="Fatos", ic="fatos", cor="#1F7F73", corEsc="#5FD3C2",
         frase="Frases que circulam no zap, checadas com fonte, e jogos para treinar o olho antes de compartilhar.",
         pergunta="Recebeu uma mensagem e ficou na dúvida?", assuntos=["Redes", "fatos"]),
    dict(id="trabalho", nome="Saúde do Trabalhador e da Trabalhadora", curto="Saúde no trabalho", ic="mente", cor="#9A5F0C", corEsc="#F0B05A",
         frase="O trabalho como determinante da saúde. Dentro dele, a Saúde Mental Relacionada ao Trabalho: riscos psicossociais, NR-1, jornada e adoecimento, com jogos para o celular, o telão e o papel e a fonte de cada resposta.",
         pergunta="Vai falar de saúde do trabalhador ou de saúde mental no trabalho com um grupo?", assuntos=["Trabalho", "trabalho"]),
    dict(id="direitos", nome="Assédio e denúncia", curto="Denúncia", ic="denuncia", cor="#B3261E", corEsc="#FF8F84",
         frase="Assédio, discriminação, direito desrespeitado ou pressão pelo voto: como reconhecer, guardar provas e onde denunciar, até sem se identificar.",
         pergunta="Está passando por uma situação no trabalho?", assuntos=["Direitos", "direitos"]),
    dict(id="bolso", nome="Bolso e direitos sociais", curto="Bolso", ic="bolso", cor="#2D6A2E", corEsc="#93D896",
         frase="Imposto de renda, programas sociais, jornada e apostas: o que a política muda no seu mês, com os números oficiais.",
         pergunta="Quer ver o que muda no seu bolso?", assuntos=["Impostos", "bolso"]),
    dict(id="eleicoes", nome="Eleições 2026", curto="Eleições", ic="urna", cor="#4B3F99", corEsc="#B7B1F2",
         frase="O resultado oficial, as pesquisas e tudo o que usamos na campanha para conversar e virar voto, com as fontes.",
         pergunta="Quer rever a eleição ou usar os materiais da campanha?", assuntos=[]),
]

# formatos (o selo de cada item) e jeitos de jogar
FORMATOS = {
    "jogo": "Jogo", "teste": "Teste", "dados": "Dados e busca", "calc": "Calculadora", "leitura": "Leitura com fonte",
    "imprimir": "Para imprimir", "ferramenta": "Ferramenta", "campanha": "Campanha externa", "canal": "Canal externo",
}
COMO = {"celular": "No celular", "grupo": "Em grupo ou na roda", "telao": "No telão, com a plateia", "papel": "No papel"}

# ------------------------------------------------------------------ itens
# tema = tema principal (o carimbo da ronda e a trilha); mais = outros temas onde o item também aparece
I = []


def item(id, href, nome, desc, tema, fmt, como=(), mais=(), dest=False, tags="", pdf=False, externo=False, quem=""):
    I.append(dict(id=id, href=href, nome=nome, desc=desc, tema=tema, fmt=fmt, como=list(como), mais=list(mais), dest=dest,
                  tags=tags, pdf=pdf, externo=externo, quem=quem))


# Congresso e votos
item("vota-como-voce", "/vota-como-voce", "Quem vota como você?", "Responda a 15 afirmações sobre projetos que o Congresso votou de verdade e veja que partidos e parlamentares votaram como você.",
     "congresso", "teste", ["celular"], dest=True, tags="teste quiz votação deputado senador partido arcabouço reforma tributária 6x1 marco temporal dosimetria blindagem")
item("parlamentares", "/parlamentares", "A ficha de cada parlamentar", "Votos, presença, alinhamento com o governo e cota parlamentar de 752 deputados e senadores, de 2023 a 2026. Sem ranking.",
     "congresso", "dados", dest=True, tags="deputado deputada senador senadora ficha cota gastos presença faltas governo")
item("cruzar", "/cruzar", "Cruze os dados", "Escolha o estado, o assunto e o partido: veja como votou a bancada, o que deu a urna, quem foi eleito em 2026 e o que dizem os estudos científicos.",
     "congresso", "ferramenta", ["celular"], mais=["trabalho", "direitos", "bolso", "eleicoes", "fatos"], dest=True,
     tags="cruzar cruzamento dados estado uf bancada partido urna tse eleitos ciência estudos comparar")
item("comparar", "/cruzar#ce", "Compare os estados", "Escolha dois dados quaisquer (urna, eleitos, votos das bancadas, presença, desemprego, renda, desigualdade) e veja os 27 estados lado a lado, em frase, gráfico e tabela.",
     "congresso", "ferramenta", ["celular", "telao"], mais=["bolso", "trabalho", "eleicoes"], dest=True,
     tags="comparar estados cruzar ibge desemprego renda informalidade gini população urna eleitos bancada gráfico tabela")
item("bases", "/bases", "Bases de dados para todo mundo", "Base dos Dados, gráficos do Nexo, HubPolítico e as fontes oficiais: quem organiza, o que têm e como usar em 3 passos.",
     "fatos", "leitura", ["celular"], mais=["congresso"], tags="base dos dados nexo gráficos hubpolítico hub político dados abertos ibge tse câmara senado transparência pesquisa")
item("semana", "/semana", "Placar da semana", "O que a Câmara e o Senado votaram e como votou cada partido. Sai às segundas, depois de conferido.",
     "congresso", "dados", tags="semana votação plenário partido placar")
item("raiox", "/congresso", "Raio-X do novo Congresso", "Quem foi eleito em 2026 para a Câmara e o Senado, partido por partido, com os dados do TSE.",
     "congresso", "dados", mais=["eleicoes"], tags="eleitos 2026 bancada pl pt centrão novo congresso")
item("quem-cobrar", "/quem-cobrar", "De quem cobrar no Brasil?", "Buraco na rua, polícia, juros, INSS, enchente: prefeitura, estado, governo federal, Legislativo, Banco Central ou Justiça? 97 situações, com a lei de cada resposta.",
     "congresso", "jogo", ["celular", "grupo"], mais=["bolso"], tags="quem cobrar prefeito governador presidente vereador banco central juros competência jogo")
item("mapa-cobrar", "/arquivos/Mapa_De_quem_cobrar.pdf", "Mapa: de quem cobrar no Brasil?", "Prefeito, governador, presidente e Legislativo numa folha A4, com QR code para o jogo.",
     "congresso", "imprimir", ["papel"], pdf=True, tags="mapa imprimir pdf")

# Fatos e boatos
item("familia", "/familia", "Fato ou boato: o bolso e a família", "O que se diz de Lula e do PT sobre economia e valores cristãos, e o que mostram os números oficiais e as leis.",
     "fatos", "leitura", mais=["bolso"], dest=True, tags="boato fake news lula pt igreja cristão família economia inflação salário")
item("checagem", "/checagem", "Checagem do debate", "86 checagens de Lupa, Estadão Verifica, Aos Fatos e g1: o que era verdadeiro, impreciso ou falso no debate, e os temas com fonte.",
     "fatos", "leitura", mais=["eleicoes"], dest=True, tags="debate checagem lupa aos fatos estadão g1 debate na mão temas truques")
item("roleta", "/roleta", "Roleta dos fatos", "Um caso por vez: registro público, checagem, investigação ou arquivado, com a versão de cada lado e o link.",
     "fatos", "jogo", ["celular", "grupo"], tags="roleta fatos investigação checagem")
item("j2", "/jogos#j2", "Fato ou Boato?", "Doze frases que circulam no zap. Você decide: fato ou boato?", "fatos", "jogo", ["celular"], tags="boato fake news jogo zap whatsapp")
item("j16", "/jogos#j16", "Quem disse?", "Oito frases de Lula e de Flávio, com data e fonte. Adivinhe quem falou cada uma.", "fatos", "jogo", ["celular"], mais=["eleicoes"], tags="frase print jogo lula flávio")
item("j6", "/jogos#j6", "Pega o truque", "Alguém usa um truque para encerrar a conversa. Você reconhece e responde sem esquentar?", "fatos", "jogo", ["celular"], tags="truque falácia conversa discussão schopenhauer")
item("j3", "/jogos#j3", "Antes × Agora", "Oito números do governo anterior e de hoje. Subiu ou desceu?", "fatos", "jogo", ["celular"], mais=["bolso"], tags="números governo inflação desemprego")
item("j13", "/jogos#j13", "Desenhe a linha", "Desenhe como você acha que o desmatamento da Amazônia mudou. Depois, veja a linha real.", "fatos", "jogo", ["celular"], tags="desmatamento amazônia gráfico meio ambiente")

# Saúde do Trabalhador e da Trabalhadora (STT), com a Saúde Mental Relacionada ao Trabalho (SMRT) dentro dela
item("saude-mental", "/saude-mental", "Saúde Mental Relacionada ao Trabalho (SMRT) e riscos psicossociais",
     "12 jogos para todos que lidam com o tema: ergonomia, SST, psicologia, saúde, RH, CIPAs, sindicatos e ensino. No celular, no telão ou impressos, com a fonte de cada resposta.",
     "trabalho", "jogo", ["celular", "telao", "papel"], dest=True,
     tags="saúde mental riscos psicossociais nr-1 nr-17 aep aet iso 45003 fundacentro observatório saúde do trabalhador ergonomia sst burnout assédio telão qr code plateia palestra sipat cipa sindicato")
item("roleta-saude", "/roleta-saude", "Roleta da saúde no trabalho", "Mito ou verdade? Burnout, assédio moral, pausas, NR-1 e onde buscar ajuda, com a lei e a pesquisa de cada resposta.",
     "trabalho", "jogo", ["celular", "grupo", "telao"], dest=True, tags="saúde mental burnout assédio moral nr-1 trabalho jogo roleta")
item("j4", "/jogos#j4", "Seu tempo vale: o fim da escala 6x1", "A sua semana em horas: trabalho, condução, sono e o que sobra. E com duas folgas?", "trabalho", "calc", ["celular"], mais=["bolso"],
     tags="6x1 jornada folga escala 40 horas tempo")
item("praca", "/praca", "Jogos da praça", "Pode ou não pode? e a Roleta da saúde para jogar em roda, com kit para imprimir e placar de equipes.",
     "trabalho", "jogo", ["grupo", "telao", "papel"], mais=["direitos"], tags="praça grupo roda telão evento kit imprimir equipe")
item("sala", "/sala", "Entrar numa sala ao vivo", "Está numa palestra? Digite o código que aparece no telão e responda pelo celular. Anônimo, sem cadastro.",
     "trabalho", "ferramenta", ["celular", "telao"], tags="sala código telão plateia ao vivo responder")
item("kits-sm", "/saude-mental#imprimir", "Kits de saúde mental para imprimir", "Roteiro, folha da plateia, gabarito e placas de resposta de A a F para os 12 jogos, em A4 colorido.",
     "trabalho", "imprimir", ["papel"], tags="kit imprimir pdf placas saúde mental")
item("kit-roleta", "/arquivos/Kit_roleta_saude.pdf", "Kit Roleta da saúde", "Roleta de papel, cartas e placar para jogar sem internet.", "trabalho", "imprimir", ["papel"], pdf=True, tags="kit imprimir pdf roleta")

# Assédio e denúncia
item("denuncie", "/denuncie", "Onde denunciar e buscar apoio", "Salário, FGTS, assédio, discriminação, acidente, trabalho escravo ou infantil, pressão pelo voto: o canal certo para cada caso, com link e QR code.",
     "direitos", "dados", dest=True, tags="denúncia denunciar mpt ministério do trabalho anônimo qr code sindicato disque 100 ligue 180 cat cerest fgts salário trabalho escravo infantil apoio acolhimento")
item("assedio", "/assedio", "Assédio, discriminação e violência no trabalho", "Assédio moral, sexual e eleitoral, discriminação e outras violências: como reconhecer, o que diz a lei e o que fazer. Com 10 cards.",
     "direitos", "leitura", mais=["trabalho"], dest=True, tags="assédio moral sexual eleitoral discriminação racismo lgbtfobia violência lei provas nr-1 importunação")
item("pode-ou-nao", "/pode-ou-nao", "Pode ou não pode?", "Situações reais de assédio eleitoral no trabalho. A resposta vem com o que diz a lei e o que fazer.",
     "direitos", "jogo", ["celular", "grupo", "telao"], mais=["eleicoes"], tags="assédio eleitoral patrão chefe empresa voto jogo")
item("cartaz-den", "/arquivos/Cartaz_Onde_denunciar_no_trabalho.pdf", "Cartaz: onde denunciar no trabalho", "Uma folha A4 com os QR codes dos canais principais, para o mural da empresa, do sindicato, da escola ou da UBS.",
     "direitos", "imprimir", ["papel"], pdf=True, tags="cartaz imprimir qr code")
item("panfleto-den", "/arquivos/Panfleto_Onde_denunciar_no_trabalho_4_por_folha.pdf", "Panfleto: onde denunciar no trabalho", "Os canais de denúncia e de acolhimento com QR code, quatro por folha, para imprimir e cortar.",
     "direitos", "imprimir", ["papel"], pdf=True, tags="panfleto imprimir qr code")
item("kit-pode", "/arquivos/Kit_pode_ou_nao.pdf", "Kit Pode ou não pode?", "Roteiro, placas, cartas de dobrar, placar e a página dos canais de denúncia.", "direitos", "imprimir", ["papel"], pdf=True, tags="kit imprimir pdf")

# Bolso e direitos sociais
item("j14", "/jogos#j14", "Régua do Imposto de Renda", "Arraste até o seu salário e veja se você paga, paga menos ou não paga mais.", "bolso", "calc", ["celular"], dest=True,
     tags="imposto de renda ir isenção 5 mil salário")
item("j17", "/jogos#j17", "Programas na sua vida", "Bolsa Família, SAMU, Farmácia Popular, ProUni, Pé-de-Meia: marque os que você já usou e veja de quando é cada um.",
     "bolso", "teste", ["celular"], dest=True, tags="programas sociais bolsa família samu farmácia popular prouni pé-de-meia")
item("j15", "/jogos#j15", "Linha do tempo", "Ponha em ordem sete conquistas, do SAMU à isenção do IR.", "bolso", "jogo", ["celular"], tags="linha do tempo conquistas samu ir")

# Eleições 2026
item("viramos", "/viramos", "Viramos", "Lula eleito com 51,79% dos votos válidos. A história da campanha em 10 telas e as mensagens que chegaram depois.",
     "eleicoes", "leitura", dest=True, tags="eleição 2026 resultado virada lula obrigado")
item("apuracao", "/apuracao", "Apuração", "Os números oficiais do TSE, por estado, do 1º e do 2º turno.", "eleicoes", "dados", dest=True, tags="apuração tse resultado estado votos")
item("pesquisas", "/pesquisas", "Pesquisas do 2º turno", "A média das pesquisas na reta final e como elas se compararam com a urna.", "eleicoes", "dados", tags="pesquisas datafolha quaest média")
item("jogos", "/jogos", "Games Vira-Voto", "Os 17 jogos curtos da eleição de 2026: show, quiz, baralho, mapa da virada e mais, com fonte em cada resposta.",
     "eleicoes", "jogo", ["celular"], tags="games vira-voto fliperama jogos eleição")
item("j1", "/jogos#j1", "Show do Vira-Voto", "Dez perguntas em escada, com duas ajudas. Errou, acabou.", "eleicoes", "jogo", ["celular", "grupo"], tags="show perguntas")
item("quiz", "/quiz", "Quiz", "32 perguntas rápidas, de três opções, com a fonte de cada resposta.", "eleicoes", "jogo", ["celular"], tags="quiz perguntas")
item("baralho", "/baralho", "Baralho Vira-Voto", "As 52 cartas da banquinha, com roleta, placar, explicação e pergunta de conversa.", "eleicoes", "jogo", ["grupo", "celular"], tags="baralho cartas banquinha tablet")
item("baralho-pdf", "/arquivos/Baralho_Vira-Voto_imprimir.pdf", "Baralho para imprimir", "As 52 cartas em A4, para recortar e jogar sem internet.", "eleicoes", "imprimir", ["papel"], pdf=True, tags="baralho imprimir pdf cartas")
item("j11", "/jogos#j11", "Mapa do 1º turno", "Quem venceu em cada estado? Adivinhe e pinte o mapa do Brasil.", "eleicoes", "jogo", ["celular"], tags="mapa estados 1º turno")
item("j12", "/jogos#j12", "O tamanho da virada", "Quantos votos separaram os dois? E quantos ficaram em casa? Veja em barras e bolinhas.", "eleicoes", "jogo", ["celular"], tags="votos abstenção virada")
item("j9", "/jogos#j9", "Radar da virada", "Onde mobilizar e onde persuadir: treine com resultados reais e faça a conta do seu lugar.", "eleicoes", "jogo", ["celular"], tags="radar mobilizar persuadir")
item("j7", "/jogos#j7", "Desarma a desculpa", "“Não vou votar porque...” Escolha a pergunta que abre a conversa.", "eleicoes", "jogo", ["celular"], tags="desculpa abstenção conversa")
item("cartilha", "/cartilha", "Cartilha Vira-Voto", "Como conversar e ajudar alguém a votar, em 4 minutos. Com áudio e Libras.", "eleicoes", "leitura", tags="cartilha conversa libras áudio")
item("apostila", "/apostila", "Apostila de argumentos", "Bolso, 6x1, saúde, fome, escola, mulheres: fatos com fonte e resposta pronta.", "eleicoes", "leitura", tags="apostila argumentos")
item("conversar", "/jogos#conversar", "Como virar voto numa conversa", "Sete passos e o que pode e não pode.", "eleicoes", "leitura", tags="conversa passos")
item("guia", "/guia", "Guia da banquinha", "Pontos, horários, o que levar e o que dizer.", "eleicoes", "leitura", tags="banquinha guia rua")
item("ja-votou", "/ja-votou", "Disseram que você já votou?", "O que fazer na seção eleitoral.", "eleicoes", "leitura", tags="seção eleitoral já votou")
item("j5", "/jogos#j5", "Plano de domingo", "Hora, caminho e companhia em um minuto.", "eleicoes", "ferramenta", ["celular"], tags="plano domingo votar")
item("kit", "/kit", "Kit de postagens", "Stories, posts, Reels e textos prontos, com texto alternativo.", "eleicoes", "leitura", tags="kit postagens stories reels")
item("roteiros", "/roteiros", "Roteiros para vídeo", "Nove roteiros curtos, com teleprompter.", "eleicoes", "leitura", tags="roteiros vídeo teleprompter")
item("materiais", "/jogos#materiais", "Todos os materiais da campanha", "Baralho, cartazes, cartilha, apostila, carrosséis, áudios e vídeos, livres para copiar e imprimir.", "eleicoes", "imprimir", ["papel"], tags="materiais baixar imprimir")

# Participe: campanhas e canais de fora do site (não são órgãos públicos: dizemos quem organiza)
item("bets", "https://betsnuncamais.com.br/", "#BetsNuncaMais: abaixo-assinado contra a volta das bets",
     "A MP 1.394/2026, de 25/9, proibiu as apostas de quota fixa. No STF, a associação das empresas de apostas pede a suspensão da MP (ADI 8027); o relator, ministro Luiz Fux, fez audiência pública em 3/11 e, em 8/11, a pedido da PGR, suspendeu os processos sobre a MP nas outras instâncias até o STF decidir. O julgamento ainda não tem data. O abaixo-assinado pede que a proibição continue, o fim do patrocínio das bets e tratamento público para quem se viciou. Pede nome, e-mail e CPF.",
     "bolso", "campanha", externo=True, quem="Organiza: Instituto Conhecimento Liberta. Conferido em 9/11/2026.",
     tags="bets apostas jogo vício abaixo-assinado petição stf participe campanha")
item("antirracista", "https://whatsapp.com/channel/0029Vb92L295Ui2P899ACd1k", "Exército Antirracista",
     "Canal de mobilização antirracista no WhatsApp, que distribui “missões”. Cerca de 21 mil seguidores em 2/11/2026.",
     "direitos", "canal", externo=True, quem="Canal de militância, não é órgão público. Para denunciar racismo: Disque 100 e delegacia (veja Onde denunciar).",
     tags="racismo antirracista canal whatsapp mobilização participe campanha")
item("indigenas", "https://linktr.ee/exercitodospovosindigenas", "Exército dos Povos Indígenas",
     "Canal no WhatsApp criado em 28/10/2026 por representantes de povos indígenas, com denúncias, campanhas e a lista das terras indígenas que aguardam homologação. Mais de 90 mil membros um dia depois, segundo a CartaCapital (29/10/2026).",
     "direitos", "canal", externo=True, quem="Inspirado no Exército do Lula, de André Janones (Rede-MG). Canal de militância, não é órgão público.",
     tags="indígenas terras indígenas demarcação homologação canal whatsapp participe campanha")

ITENS = {x["id"]: x for x in I}
TEMA = {t["id"]: t for t in TEMAS}

# páginas do site (slug do endereço) → item; usado na trilha, no menu e no carimbo da ronda
PAGINA_ITEM = {x["href"].strip("/"): x["id"] for x in I if x["href"].startswith("/") and "#" not in x["href"] and not x["pdf"]}
# endereços antigos que redirecionam para um jogo de /jogos: contam no carimbo do tema do jogo
ATALHOS = {"6x1": "j4", "ir": "j14", "programas": "j17", "boato": "j2", "quemdisse": "j16", "show": "j1", "desculpa": "j7", "plano": "j5",
           "conversar": "conversar", "materiais": "materiais", "debate": "checagem", "obrigado": "viramos"}
# páginas sem tema (aparecem na busca, sem trilha de tema)
SOLTAS = {"acessibilidade": "Acessibilidade", "semana-2026-10-17": None}

# como jogar (página /jogar): ordem dos grupos e os itens de cada um
JOGAR = [
    ("telao", "No telão, com a plateia", "Para palestra, aula, SIPAT ou assembleia: o jogo aparece no telão e cada pessoa responde pelo celular, pelo QR code, sem cadastro.",
     ["saude-mental", "roleta-saude", "pode-ou-nao", "sala"]),
    ("grupo", "Em grupo ou na roda", "Para praça, sindicato, escola ou roda de conversa: uma pessoa conduz e o grupo responde junto.",
     ["praca", "roleta-saude", "pode-ou-nao", "quem-cobrar", "roleta", "baralho", "j1"]),
    ("celular", "No celular, sozinho", "Rápidos, de 1 a 5 minutos. Cada resposta traz a fonte.",
     ["vota-como-voce", "quem-cobrar", "j2", "j16", "j6", "j3", "j13", "j4", "j14", "j17", "j15", "saude-mental", "roleta", "quiz", "j1", "j11", "j12", "j9", "j7"]),
    ("papel", "No papel, sem internet", "Kits em A4 colorido: roteiro, cartas, placas e placar.",
     ["kits-sm", "kit-roleta", "kit-pode", "baralho-pdf", "mapa-cobrar", "cartaz-den", "materiais"]),
]

# o que você quer fazer? (atalhos da página inicial)
INTENCOES = [
    dict(ic="pessoa", tema="congresso", t="Ver como vota quem me representa", d="Teste de 5 minutos com votações reais", href="/vota-como-voce"),
    dict(ic="cruzar", tema="congresso", t="Cruzar os dados do meu estado", d="Bancada, urna, eleitos e ciência", href="/cruzar"),
    dict(ic="fatos", tema="fatos", t="Checar uma mensagem que recebi", d="O que diz o zap e o que dizem os números", href="/familia"),
    dict(ic="denuncia", tema="direitos", t="Denunciar ou buscar apoio", d="O canal certo para cada caso, com QR code", href="/denuncie"),
    dict(ic="telao", tema="trabalho", t="Jogar com um grupo ou no telão", d="Palestra, aula, roda ou praça", href="/jogar#telao"),
    dict(ic="imprimir", tema="eleicoes", t="Imprimir um material", d="Kits, cartazes e panfletos em A4", href="/jogar#papel"),
]


def itens_do_tema(tid):
    """Itens do tema: primeiro os principais (na ordem do catálogo), depois os que também aparecem nele."""
    return [x for x in I if x["tema"] == tid] + [x for x in I if tid in x["mais"] and x["tema"] != tid]
