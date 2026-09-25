// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 6
//  Temas: curva spot / ETTJ (e formato I-II-III), Treynor com
//  tabela, e análise de estilo (returns-based x holdings-based).
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== CURVA SPOT / ETTJ =====
  { topico:"Renda Fixa",
    enunciado:"A curva de juros SPOT (à vista) é corretamente descrita como:",
    alternativas:[
      "A curva das taxas de títulos com cupom, ponderadas pelo prazo.",
      "A curva das taxas zero-cupom para diferentes prazos de vencimento.",
      "A curva das taxas forward implícitas apenas.",
      "A curva de dividendos esperados das ações."],
    correta:1,
    explicacao:"A curva spot é a curva das taxas ZERO-CUPOM (uma taxa para cada prazo, sem pagamentos intermediários). Títulos com cupom precisam ser 'desmontados' (stripping) em fluxos zero-cupom para compor a curva. As forward são derivadas das spot.",
    macete:"Curva SPOT = curva ZERO-CUPOM. Se falar em 'títulos com cupom', desconfie — spot é sem cupom." },

  { topico:"Renda Fixa",
    enunciado:"Sobre o traçado da curva de juros spot de referência, considere:\nI. A curva base é referenciada em títulos públicos federais.\nII. A curva spot utiliza apenas títulos com cupom.\nIII. Aspectos de liquidez e risco de crédito influenciam os spreads sobre a curva base.\nEstá correto apenas o que se afirma em:",
    alternativas:["II e III","I, II e III","I e III","I e II"],
    correta:2,
    explicacao:"I é verdadeira (a curva base/livre de risco usa títulos públicos). II é FALSA (a spot é zero-cupom, não 'apenas com cupom'). III é verdadeira (liquidez e crédito afetam spreads). Logo, corretas: I e III. Atalho: como II é falsa, elimine toda alternativa que a contenha.",
    macete:"Em 'I/II/III', ache a afirmativa claramente FALSA (aqui a II) e elimine todas as combinações que a incluem." },

  { topico:"Renda Fixa",
    enunciado:"A relação entre uma taxa spot de 2 anos (s2), a spot de 1 ano (s1) e a taxa forward de 1 ano daqui a 1 ano (f) é dada por:",
    alternativas:[
      "(1+s2)² = (1+s1) × (1+f)",
      "s2 = (s1 + f) / 2 exatamente",
      "(1+s2) = (1+s1) × (1+f)",
      "f = s2 − s1 sempre"],
    correta:0,
    explicacao:"Por não-arbitragem, aplicar 2 anos na spot de 2 anos deve equivaler a aplicar 1 ano na spot de 1 ano e reinvestir 1 ano à forward: (1+s2)² = (1+s1)×(1+f). A média simples é apenas uma aproximação grosseira.",
    macete:"Forward sai da spot por não-arbitragem: (1+s2)² = (1+s1)×(1+f). É composto, não média simples." },

  // ===== TREYNOR (cálculo com tabela) =====
  { topico:"Performance e Risco",
    enunciado:"Um fundo tem retorno de 14%, desvio-padrão de 25% e beta de 1,15; a taxa livre de risco é 4%. O Índice de Treynor do fundo é aproximadamente:",
    alternativas:["0,40","0,087","0,10","0,56"],
    correta:1,
    explicacao:"Treynor = (Rp − Rf) / β = (0,14 − 0,04) / 1,15 = 0,10 / 1,15 ≈ 0,087. Cuidado: 0,40 é o Sharpe [(0,14−0,04)/0,25], colocado como distrator.",
    macete:"Treynor divide por BETA; Sharpe divide por DESVIO-PADRÃO. Se a tabela dá os dois, é teste de denominador." },

  { topico:"Performance e Risco",
    enunciado:"A diferença entre o Índice de Treynor e o Índice de Sharpe está em que:",
    alternativas:[
      "Treynor usa o desvio-padrão e Sharpe usa o beta.",
      "Treynor usa o beta (risco sistemático) e Sharpe usa o desvio-padrão (risco total).",
      "Ambos usam o beta, mudando só o numerador.",
      "Treynor ignora a taxa livre de risco."],
    correta:1,
    explicacao:"Ambos têm o mesmo numerador (Rp − Rf). O denominador difere: Treynor usa beta (risco sistemático), adequado a carteiras diversificadas; Sharpe usa desvio-padrão (risco total).",
    macete:"Mesmo numerador (Rp−Rf). Treynor ÷ beta; Sharpe ÷ desvio-padrão. Só muda o denominador." },

  // ===== ANÁLISE DE ESTILO =====
  { topico:"Renda Variável",
    enunciado:"A análise de estilo baseada em RETORNOS (returns-based) caracteriza-se por:",
    alternativas:[
      "Analisar os ativos que efetivamente compõem a carteira do gestor.",
      "Uma regressão dos retornos do fundo contra índices de estilo, em que o termo de erro representa o retorno de seleção do gestor.",
      "Uma tabela de correlação entre os ativos da carteira.",
      "Análise fundamentalista de cada ativo detido pelo fundo."],
    correta:1,
    explicacao:"A análise baseada em retornos (Sharpe) regride os retornos do fundo sobre índices de estilo: a parte explicada indica a exposição a estilo, e o resíduo (erro) é atribuído à seleção (habilidade do gestor). Olhar os ativos detidos é a abordagem baseada em carteira (holdings-based).",
    macete:"Returns-based = regressão dos RETORNOS; resíduo = seleção. Olhar os ATIVOS da carteira = holdings-based." },

  { topico:"Renda Variável",
    enunciado:"A principal diferença entre a análise de estilo baseada em CARTEIRA (holdings-based) e a baseada em RETORNOS (returns-based) é que a baseada em carteira:",
    alternativas:[
      "Usa regressão dos retornos contra índices de estilo.",
      "Examina diretamente os ativos que compõem a carteira, exigindo transparência das posições.",
      "Não consegue identificar o estilo do gestor.",
      "Dispensa qualquer informação sobre a carteira."],
    correta:1,
    explicacao:"A holdings-based olha diretamente as posições detidas pelo fundo (precisa de transparência/dados da carteira). A returns-based infere o estilo apenas a partir da série de retornos, via regressão, sem precisar conhecer as posições.",
    macete:"Holdings-based olha as POSIÇÕES (precisa de transparência). Returns-based infere pelos RETORNOS (regressão)." }

);
