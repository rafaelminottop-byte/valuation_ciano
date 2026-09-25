// Feed de cartas resumidas. Cada carta é resumida manualmente (Claude lê o PDF
// e escreve aqui). Campos:
//   id, gestora, titulo, data (AAAA-MM-DD), categoria, url (PDF original),
//   tese (frase-resumo), bullets [], ativos [], tags []
// A flag "lida" é controlada pelo app (salva no localStorage), não precisa vir aqui.
window.CARTAS = [
  {
    id: "verde-mm-2026-08",
    gestora: "Verde Asset",
    titulo: "Relatório de Gestão — Verde FIF Multimercado (Ago/2026)",
    data: "2026-08-31",
    categoria: "Multimercado",
    url: "https://www.verdeasset.com.br/public/files/rel_gestao/158094/Verde-REL-2026_08.pdf",
    tese: "Trajetória fiscal preocupante nos países desenvolvidos deve manter juros longos pressionados; ouro e prata são peças-chave do portfólio. No Brasil, ciclo eleitoral aguado e mais competitivo faz a bolsa reprecificar para cima.",
    bullets: [
      "Agosto positivo: +1,98% no mês, +10,33% em 2026 (CDI +9,33%). Ganhos em ouro, prata, bolsa global e trading; perdas marginais em juro real americano e crédito.",
      "Quatro forças que guiam o cenário: (i) conflito EUA-Irã e petróleo; (ii) sinais do novo chairman do Fed, Kevin Warsh (tom mais duro em Jackson Hole); (iii) pressão fiscal/de demanda sobre juros longos nos desenvolvidos; (iv) ciclo de investimento em IA.",
      "O secretário Bessent tentou intervir na parte longa da curva americana, mas a Verde vê baixa chance de sucesso dado o déficit fiscal e as emissões para financiar capex de IA — mercados enfraqueceram o dólar e beneficiaram ouro/prata.",
      "Diagnóstico estrutural: fiscal dos desenvolvidos sem apetite político de ajuste → saída via mais inflação ou repressão financeira (talvez já um 1º sinal). Ouro e prata ganham papel central.",
      "Brasil: ciclo eleitoral em fase aguda e caótica, eleição mais competitiva do que o consenso assumia; bolsa ensaiou alta relevante a partir de meados de agosto. Ainda veem prêmio de risco interessante e mantêm posições compradas em opções; aumentaram renda variável."
    ],
    ativos: ["Ouro", "Prata", "Bolsa global", "Opções de bolsa BR", "Juro real (EUA/BR)"],
    tags: ["multimercado", "macro", "ouro", "prata", "fiscal", "eleições 2026", "Warsh"]
  },
  {
    id: "kinea-2026-08",
    gestora: "Kinea",
    titulo: "Carta do Gestor — “A Hora do Pesadelo” (Ago/2026)",
    data: "2026-08-31",
    categoria: "Multimercado",
    url: "https://www.kinea.com.br/wp-content/uploads/2026/09/Carta-do-Gestor-Prev-Multimercado-2026-08.pdf",
    tese: "Decisões do passado que assombram o presente: a dívida brasileira, o fiscal americano e o prêmio de energia herdado do impasse com o Irã — problemas que crescem só com o tempo passando e exigem ação, não heroísmo.",
    bullets: [
      "Metáfora do filme “A Hora do Pesadelo”: como Freddy Krueger, a dívida age enquanto o país “dorme” — não precisa de nova decisão para crescer, basta o tempo passar. Adiar é escolher pagar mais caro.",
      "Brasil: aproxima-se de mais um ciclo eleitoral com trajetória de dívida que precisa ser enfrentada nesta eleição; para mantê-la sob controle pagamos um dos juros reais mais altos do mundo (a “cafeína” que evita o colapso imediato mas cobra preço crescente).",
      "O problema não é só nosso: a trajetória fiscal dos EUA e décadas de relações conturbadas com Irã e Rússia (refletidas nos preços de energia) seguem pressionando a ponta longa da curva.",
      "Saída (como no filme): não um gesto heroico, mas a decisão objetiva de interromper o mecanismo que alimenta o problema — desarmar a “bomba fiscal”.",
      "Performance: no mês o fundo praticamente empatou com o CDI (~1,07% vs 1,09%), com maior consumo de risco vindo de despesas/caixa; ganhos marginais em ações e commodities."
    ],
    ativos: ["Dívida/juros BR", "Treasuries (juros longos EUA)", "Energia/petróleo", "Ações", "Commodities"],
    tags: ["multimercado", "macro", "âncora fiscal", "eleições 2026", "juros reais", "energia"]
  },
  {
    id: "verde-acoes-2026-08",
    gestora: "Verde Asset",
    titulo: "Relatório de Gestão — Verde AM Ações (Ago/2026)",
    data: "2026-08-30",
    categoria: "Ações",
    url: "https://www.verdeasset.com.br/public/files/rel_gestao/118/Acoes-REL-2026_08.pdf",
    tese: "Com pouca mudança no global (petróleo ~US$90, Fed sem alta, 10y em 4,7%), a bolsa brasileira oscilou com resultados e eleição; a gestão usou o caixa para dobrar apostas de alta convicção a preços estressados.",
    bullets: [
      "Mês de leve queda: -0,06% (Ibov -0,33%), +3,20% em 2026 e +15,32% em 12 meses. IBOV fechou neutro mas recuperou 7% desde o piso no meio do mês; small caps chegaram ao menor valor em mais de um ano antes de recuperar.",
      "Gatilho local: melhora da oposição nas pesquisas eleitorais após forte saída de capital estrangeiro na 1ª metade do mês.",
      "Petrobras: posição importante com hedges na curva de petróleo — aposta em geração de caixa e dividendos com crack spreads elevados por mais tempo e boa produção.",
      "Usaram o caixa para dobrar a aposta em nomes de alta convicção (Equatorial, Sabesp, BTG) a preços “extremamente estressados”, concentrando mais o portfólio.",
      "Maiores contribuições: Petrobras e Tenda (+); Smartfit e Equatorial (-). Maiores posições atuais: Equatorial, Petrobras e BTG."
    ],
    ativos: ["Equatorial", "Petrobras", "BTG", "Sabesp", "Tenda", "Smartfit"],
    tags: ["ações Brasil", "elétricas", "Petrobras", "eleições 2026", "alta convicção"]
  },
  {
    id: "squadra-1s26",
    gestora: "Squadra",
    titulo: "Carta Squadra 1º semestre 2026",
    data: "2026-08-20",
    categoria: "Ações",
    url: "https://www.squadrainvest.com.br/wp-content/uploads/2026/08/Squadra_Carta_1S26.pdf",
    tese: "Carta franca sobre um “vale de performance”: anos difíceis para ativos de risco brasileiros e onda histórica de resgates na indústria; a Squadra reconhece seu maior erro (Hapvida) e adota “postura de guerra”.",
    bullets: [
      "Contexto duro: juros altos, ruídos macro/políticos, competição da renda fixa isenta, fracassos corporativos alavancados e a valorização extraordinária da bolsa americana levaram a desilusão e resgates — a gestão ativa vive uma das maiores ondas de resgates de sua história (casas fechando, virando family office ou sendo absorvidas).",
      "Performance: em 2025 o Long-Biased subiu 11,5% (Ibov +34,0%); no 1º sem/2026 os fundos caíram -5,1% (LB) e -6,2% (LO), com Ibov +6,8%. Reconhecem que ficou aquém e não pretendem “suavizar o fato”.",
      "Maior erro da história: Hapvida, que arranhou o histórico e custou caro ao capital dos cotistas.",
      "“Postura de guerra”: intensificar rotinas, reuniões, pesquisas de campo e interações com empresas; reduzir ao mínimo a tolerância com premissas pouco verificadas e trabalhos medianos — não esperar passivamente por reversão à média.",
      "Convicção: 18 anos de casa, sociedade coesa, base de cotistas de longo prazo e conhecimento acumulado (long e short) como vantagem competitiva. Citam Pinker: “Disasters are instant, improvements are gradual.”"
    ],
    ativos: ["Hapvida (maior erro assumido)", "Carteira concentrada de ações brasileiras (long e short)"],
    tags: ["value investing", "franqueza", "vale de performance", "Hapvida", "resgates", "postura de guerra"]
  },
  {
    id: "dynamo-128",
    gestora: "Dynamo",
    titulo: "Carta Dynamo 128 — “Os Serendipitistas”",
    data: "2026-04-06",
    categoria: "Ações",
    url: "https://www.dynamo.com.br/wp-content/uploads/2026/04/Carta-Dynamo-128.pdf",
    tese: "Continuação sobre “consequências não intencionais”, agora as positivas — a serendipidade: como desvios acidentais geram grandes descobertas e negócios, e o que isso ensina sobre opcionalidade e curiosidade na gestão.",
    bullets: [
      "Depois de tratar das consequências não intencionais negativas (foco em preservar patrimônio), a carta explora as positivas — mais por curiosidade intelectual, já que “evitar perdas” tem prioridade sobre “explorar opcionalidades”.",
      "Exemplos na ciência: penicilina, raio-X (Roentgen), reação anafilática (Richet, Nobel 1913) e a Dramamine — a medicina é especialmente rica em descobertas inesperadas.",
      "Exemplos nos negócios: Post-it (3M), forno de micro-ondas, e pivôs famosos — Slack (nasceu do fracasso do jogo Glitch, vendida à Salesforce por US$27,7 bi), YouTube (era um site de encontros) e Instagram (era um app de check-in).",
      "Lição: grandes sucessos frequentemente estão “afastados das intenções iniciais” — valor está em manter opcionalidade e reconhecer o desvio promissor, não em planos lineares.",
      "Prática Dynamo: cultivam conversas informais e abertas com gente de áreas diversas (esportistas, enxadristas, cientistas) — “verdadeiros encontros serendipitosos”. Carta de 06/04/2026."
    ],
    ativos: ["Carta de reflexão (sem teses de ações específicas nesta edição)"],
    tags: ["filosofia de investimento", "serendipidade", "opcionalidade", "complexidade", "value investing"]
  },
  {
    id: "kinea-2025-12",
    gestora: "Kinea",
    titulo: "Carta do Gestor — Reflexões de Fim de Ano (Dez/2025)",
    data: "2025-12-31",
    categoria: "Multimercado",
    url: "https://www.kinea.com.br/wp-content/uploads/2026/01/Carta-do-Gestor-Prev-Multimercado-2025-12.pdf",
    tese: "Retrospectiva reflexiva celebrando 10 anos dos multimercados (~155% do CDI); 2025 exigiu resiliência de processo, ouro foi o destaque, e 2026 chega com fiscal expansionista + afrouxamento monetário nos EUA.",
    bullets: [
      "Balanço da década: em 2026 os multimercados Kinea (Apolo, Chronos, Atlas, Zeus) completam 10 anos, com ~155% do CDI desde o início e rápida recuperação de perdas (mesmo em 2020 entregaram 93% do CDI). Filosofia do “multimercado moderno 2.0”: combinar macro + micro + temático.",
      "Início de 2025 cauteloso com o Brasil: governo com postura fiscal insuficiente e déficits gêmeos difíceis de financiar num cenário de dólar mais forte. Resiliência de processo foi testada no 1º semestre (temas ligados à cadeia de valor de IA).",
      "Virada no 2º semestre: após o “Liberation Day” ajustaram o portfólio. Ouro foi o principal destaque do ano (dólar mais fraco, compras de bancos centrais e busca por reserva de valor num mundo fragmentado).",
      "Bolsa Brasil: bom crescimento de lucros em utilities (Equatorial, Sabesp, Copel) e bancos (Itaú, Bradesco, BTG, Nubank) + melhor humor global deram suporte. No juro local, início de ciclo de cortes abriu oportunidades.",
      "Visão 2026: nos EUA, combinação de política fiscal expansionista e afrouxamento monetário, com troca na presidência do Fed prevista para maio e impulso da “Big Beautiful Bill”. Postura: formular “as perguntas certas” (cita Rilke), com disciplina e paciência."
    ],
    ativos: ["Ouro", "Equatorial", "Sabesp", "Copel", "Itaú", "Bradesco", "BTG", "Nubank", "Juro local BR"],
    tags: ["multimercado", "macro", "ouro", "10 anos", "Fed", "utilities", "bancos"]
  },
  {
    id: "dahlia-3ps-2025-05",
    gestora: "Dahlia Capital",
    titulo: "Carta — “Os três P’s dos investimentos” (Mai/2025)",
    data: "2025-05-13",
    categoria: "Multimercado",
    url: "https://acionista.com.br/wp-content/uploads/2025/05/13052025-DahliaOs-tres-Ps-dos-investimentos.pdf",
    tese: "Apresenta a lente dos “três P’s” (Profits, Policy, Positioning) e argumenta que o ciclo de alta de juros pode ter acabado — cenário construtivo para a bolsa brasileira nos meses seguintes.",
    bullets: [
      "Framework dos 3 P’s: Profits (lucro das empresas, maior explicador da performance no médio/longo prazo), Policy (política econômica/juros, que define o múltiplo) e Positioning (posicionamento dos investidores, componente de curto prazo). Esta carta foca em Policy.",
      "Copom subiu a Selic +50 bps para 14,75%, mas o comunicado passou a ver um balanço de riscos mais equilibrado (queda de commodities, desaceleração global) — sinal de que o ciclo de aperto pode ter chegado ao fim.",
      "Externo: incerteza tarifária dos EUA torna o Fed mais prudente (juros altos por mais tempo), enquanto outros BCs ficam mais acomodatícios; queda do petróleo reforça a desinflação global.",
      "Mercado já precifica início de cortes de juros no fim de 2025, acelerando em 2026.",
      "Dois modelos próprios de “regime de mercado” apontam cenário positivo para a bolsa brasileira nos meses seguintes — historicamente (desde 2010), o melhor regime para o Ibovespa é a manutenção da Selic após um ciclo de alta."
    ],
    ativos: ["Ibovespa", "Selic / juros BR", "Commodities", "Petróleo"],
    tags: ["multimercado", "Profits-Policy-Positioning", "Selic", "regime de mercado", "didático"]
  },
  {
    id: "verde-mm-2025-09",
    gestora: "Verde Asset",
    titulo: "Relatório de Gestão — Verde FIF Multimercado (Set/2025)",
    data: "2025-09-30",
    categoria: "Multimercado",
    url: "https://www.verdeasset.com.br/public/files/rel_gestao/158094/Verde-REL-2025_09.pdf",
    tese: "Cenário global de dólar fraco + Fed cortando juros favorece diversificação para fora do dólar, inflação e ações; no Brasil, o “acelerador fiscal com freio monetário” favorece o Real e desfavorece ações.",
    bullets: [
      "Setembro positivo: fundo +1,99% no mês (vs CDI +1,22%), acumulando +12,00% em 2025 (CDI +10,35%). Ganhos distribuídos em bolsa Brasil, ouro, cripto e crédito local; perdas marginais em juro real (Brasil e EUA).",
      "Macro EUA: combinação incomum de inflação em alta (tarifas), crescimento robusto (ciclo de investimento em IA) e emprego fraco. Pressão política sobre o Fed sugere ciclo de cortes de juros mais longo.",
      "Conclusão global: cenário favorece exposição à diversificação do dólar, à inflação e a ações. MSCI Emerging Markets subiu no 9º mês consecutivo.",
      "Brasil: BC sinalizando postura mais dura e aprovação da isenção de IR até R$5 mil ilustram o modelo “acelerador fiscal com freio monetário” — tende a favorecer o Real e desfavorecer ações.",
      "Posicionamento: aumentou marginalmente ações BR; comprado em juro real local; reduziu juro real EUA e comprado em inflação implícita; comprado em Euro, Renminbi, Ouro e Real; manteve cripto e crédito high yield local/global."
    ],
    ativos: ["Bolsa Brasil", "Ouro", "Cripto", "Juro real BR", "Euro", "Renminbi", "Real", "Crédito high yield"],
    tags: ["multimercado", "macro", "Fed", "dólar fraco", "âncora fiscal", "ouro", "cripto"]
  },
  {
    id: "verde-acoes-2025-07",
    gestora: "Verde Asset",
    titulo: "Relatório de Gestão — Verde AM Ações (Jul/2025)",
    data: "2025-07-31",
    categoria: "Ações",
    url: "https://www.verdeasset.com.br/public/files/rel_gestao/118/Acoes-REL-2025_07.pdf",
    tese: "Realização da bolsa em julho (tarifas dos EUA + conflito com o Judiciário) abriu prêmio de risco em ações domésticas; fundo aproveitou para aumentar levemente a posição comprada, rumo ao neutro.",
    bullets: [
      "Mês fraco: fundo -5,21% em julho (Ibovespa -4,17%), mas acumula +14,56% em 2025 (Ibov +10,63%). Bolsa continuou a realização iniciada em junho.",
      "Gatilhos: tarifas de importação dos EUA a produtos brasileiros e escalada do conflito com o Judiciário → saída de estrangeiros, IBOV -4,2%, juros +36 bps na NTN-B 35 e BRL -3,1%.",
      "Small caps sofreram mais (SMLL -6,4%); Vale (+1,5%, dolarizada, expectativa de estímulo na China) amenizou o índice. Melhores contribuições: commodities; piores: teses sensíveis a juros.",
      "Ação da gestão: com abertura do prêmio de risco, aumentaram levemente a posição comprada, aproximando-se do neutro, já que o excesso de otimismo eleitoral nos preços se dissipou. Ainda preferem bond proxies a cíclicas domésticas e commodities, preservando caixa.",
      "Maiores contribuições em julho: Petrobras e Vale (+); Smartfit e Rumo (-). Maiores posições atuais: Equatorial, Energisa, Copel, Itaú e BTG."
    ],
    ativos: ["Equatorial", "Energisa", "Copel", "Itaú", "BTG", "Petrobras", "Vale", "Smartfit", "Rumo"],
    tags: ["ações Brasil", "bond proxies", "elétricas", "prêmio de risco", "tarifas EUA"]
  },
  {
    id: "atmos-33",
    gestora: "Atmos",
    titulo: "Carta Atmos 33 — “De um povo heróico o brado retumbante” (ref. 2025.1)",
    data: "2025-07-01",
    categoria: "Ações",
    url: "https://www.atmoscapital.com.br/documentos/cartas/Carta-Atmos-33.pdf",
    tese: "Ensaio sobre o ciclo histórico brasileiro de ruptura → anistia → reintegração, e como a falta de âncora fiscal e institucional mina a confiança — com a lição de que investir é atravessar o tempo sem sucumbir.",
    bullets: [
      "Tese central: o Brasil raramente resolve conflitos pela institucionalização, preferindo o “esquecimento” — do Tenentismo aos impeachments de Collor (1992) e Dilma (2016), o padrão é ruptura, anistia e reintegração dos derrotados.",
      "Percorre a história (Vargas, Estado Novo, JK e “50 anos em 5”, ditadura, Nova República) para mostrar democracias frágeis onde cada avanço institucional vem com um retrocesso.",
      "Lição fiscal: democracias se consolidam quando as finanças públicas ganham âncora — exemplos da Revolução Gloriosa inglesa (1688) e de Hamilton federalizando as dívidas nos EUA (1790). Reformas fiscais avançam por pactos e concessões.",
      "Leitura de 2025: democracia mais resiliente que em 1945, mas ainda frágil — partidos pulverizados, pactos fiscais instáveis e ruído que mina a confiança. Falta liderança que articule presente e futuro (à la JK ou FHC).",
      "Mensagem ao investidor: “investir é aceitar o desconforto certo, seguir sem sucumbir e nunca morrer no meio da travessia” — não se trata de vencer o mercado, mas de atravessar o tempo com ele e chegar inteiro do outro lado."
    ],
    ativos: ["Carta de reflexão macro-institucional (sem teses de ações específicas nesta edição)"],
    tags: ["macro Brasil", "âncora fiscal", "instituições", "história", "filosofia de investimento"]
  },
  {
    id: "squadra-1s25",
    gestora: "Squadra",
    titulo: "Carta Squadra 1º semestre 2025",
    data: "2025-08-21",
    categoria: "Ações",
    url: "https://www.squadrainvest.com.br/wp-content/uploads/2025/08/Squadra_Carta_1S25.pdf",
    tese: "Reafirmação da disciplina e do foco em ações brasileiras de qualidade a valuations atrativos, com portfólio concentrado, análise bottom-up profunda e humildade para reconhecer erros de análise.",
    bullets: [
      "Montanha-russa: os fundos caíram forte no 2º sem/2024 e se recuperaram no 1º sem/2025. Acumulado jul/24–jun/25 modesto: +9,5% (Long-Biased) e +8,6% (Long-Only). Em 2024 o LB caiu 20,5%; no 1S25 subiu 30,7%.",
      "Princípios revisitados: time estável (meta de zero turnover, sócios juntos há +17 anos), foco exclusivo em equities Brasil (vantagem competitiva vem da profundidade de análise, não de investir em Nvidia) e obsessão por teses short (contabilidade agressiva, negócios em decadência).",
      "Filosofia: foco no processo e não no resultado de curto prazo — “Time will tell”. Cita Graham, Peter Lynch e a ideia de controlar-se no próprio jogo.",
      "Portfólio long concentrado em empresas de qualidade com valuation atrativo (a “boia”); nesta carta dividem a carteira em categorias de negócios com métricas simplificadas.",
      "Destaque para alocação de capital das investidas: aquisições inorgânicas bem-sucedidas e programas de buyback que elevaram o valor intrínseco por ação. Admitem também erros de análise em algumas posições.",
      "Voltaram a montar um portfólio short de tamanho moderado no 1S25, após período de baixa exposição vendida."
    ],
    ativos: ["Carteira long concentrada de empresas brasileiras de qualidade (empresas específicas discutidas por categoria na carta)"],
    tags: ["value investing", "disciplina", "bottom-up", "buyback", "short", "equities Brasil"]
  },
  {
    id: "dynamo-126",
    gestora: "Dynamo",
    titulo: "Carta Dynamo 126 — “Proxymidade”",
    data: "2025-07-10",
    categoria: "Ações",
    url: "https://www.dynamo.com.br/wp-content/uploads/2025/07/Carta-Dynamo-126.pdf",
    tese: "Crítica ao poder desproporcional das empresas de aconselhamento de voto (proxy advisors, como a ISS) nas assembleias, e defesa do acionista que age como dono de verdade.",
    bullets: [
      "Tema central: a atuação das PAFs (proxy advisory firms) — empresas que recomendam como investidores devem votar em assembleias. A Dynamo vê distorções nesse mercado.",
      "Resgata a história de Bob Monks (falecido em abr/2025), fundador da ISS em 1985, cujo propósito original era fazer os donos das empresas “sentirem e agirem como donos” — um contraste com o que a indústria virou.",
      "Usa o caso Eletrobras (abr/2025): a companhia publicou carta pública criticando a recomendação da ISS, que daria a um grupo com ~10% do capital o direito de eleger 43% do conselho — uma assimetria vista como incomum.",
      "Argumento de fundo: recomendações automáticas e padronizadas de voto enfraquecem a análise caso a caso e podem prejudicar o valor de longo prazo das companhias.",
      "Mensagem ao cotista: defesa da ação coletiva e responsável dos acionistas na construção de consensos em assembleias, em vez da terceirização acrítica do voto."
    ],
    ativos: ["ELET3/ELET6 (Eletrobras, citada como caso)"],
    tags: ["governança corporativa", "proxy advisors", "ISS", "assembleias", "value investing"]
  }
];
