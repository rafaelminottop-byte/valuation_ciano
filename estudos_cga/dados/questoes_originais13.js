// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 13
//  Tema: estratégias de hedge funds (merger arbitrage, distressed,
//  global macro, event-driven, market neutral). Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Renda Variável",
    enunciado:"A estratégia de hedge fund que aposta em tendências macroeconômicas — juros, câmbio, commodities e dívida soberana —, com abordagem top-down por país/região, é a:",
    alternativas:["Merger arbitrage","Global Macro","Distressed securities","Market neutral"],
    correta:1,
    explicacao:"Global Macro atua sobre variáveis macroeconômicas (juros, câmbio, commodities, países), de forma top-down. Não se baseia em eventos corporativos — isso é a família Event-Driven.",
    macete:"Global Macro = MACRO (juros/câmbio/commodities/países). Evento corporativo é Event-Driven, não Global Macro." },

  { topico:"Renda Variável",
    enunciado:"Um hedge fund compra ações de uma empresa-alvo de aquisição, que negociam com desconto em relação ao preço ofertado, apostando na conclusão do negócio. Essa estratégia é:",
    alternativas:["Global Macro","Merger arbitrage","Distressed securities","Long-short setorial"],
    correta:1,
    explicacao:"Merger arbitrage captura o diferencial entre o preço de mercado e o preço anunciado em operações de fusão/aquisição, assumindo o risco de o negócio não se concretizar. É uma estratégia Event-Driven.",
    macete:"Diferencial preço de mercado × preço anunciado em M&A = merger arbitrage (sub-tipo de event-driven)." },

  { topico:"Renda Variável",
    enunciado:"A estratégia que consiste em adquirir títulos ou ações de companhias em dificuldade financeira ou em processo de reestruturação/recuperação é chamada de:",
    alternativas:["Distressed securities","Global Macro","Market neutral","Indexação reforçada"],
    correta:0,
    explicacao:"Distressed securities investe em ativos de empresas em crise/reestruturação, buscando ganho na recuperação ou no processo (inclusive judicial). Também é uma estratégia da família Event-Driven.",
    macete:"'Empresa em dificuldade/reestruturação' = distressed securities. Também é event-driven." },

  { topico:"Renda Variável",
    enunciado:"As estratégias merger arbitrage e distressed securities pertencem, ambas, à família de estratégias:",
    alternativas:["Global Macro","Event-Driven (dirigida por eventos)","Indexação pura","Renda fixa passiva"],
    correta:1,
    explicacao:"Merger arbitrage (fusões/aquisições) e distressed (reestruturações) exploram EVENTOS corporativos específicos — por isso são classificadas como Event-Driven. Global Macro, por outro lado, atua em variáveis macroeconômicas.",
    macete:"Merger arbitrage + distressed = Event-Driven (eventos corporativos). Global Macro é outra família (macro)." },

  { topico:"Renda Variável",
    enunciado:"Sobre estratégias de hedge funds, assinale a associação INCORRETA:",
    alternativas:[
      "Merger arbitrage — diferencial de preço em fusões e aquisições.",
      "Distressed securities — ativos de empresas em dificuldade/reestruturação.",
      "Global Macro — atuação principal em eventos corporativos (cisões, incorporações, recuperações judiciais).",
      "Market neutral — carteira long-short com beta próximo de zero."],
    correta:2,
    explicacao:"A associação incorreta é a do Global Macro: sua atuação é em variáveis MACROeconômicas (juros, câmbio, commodities), e não em eventos corporativos — estes caracterizam o Event-Driven. As demais associações estão corretas.",
    macete:"Pegadinha clássica: descrever Global Macro como 'eventos corporativos'. Isso é Event-Driven — troca de rótulo." }

);
