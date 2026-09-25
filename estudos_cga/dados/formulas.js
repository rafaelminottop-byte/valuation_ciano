// ============================================================
//  BASE DE FÓRMULAS E CONCEITOS - CGA (ANBIMA)
//  Como adicionar: copie um bloco { ... } e edite.
//  Campos:
//    topico    -> um dos blocos da prova (usado no filtro)
//    titulo    -> nome curto da fórmula/conceito
//    formula   -> a expressão (use texto simples; ^ p/ potência)
//    descricao -> explicação, variáveis e quando usar
//    tags      -> palavras-chave para a busca
// ============================================================

window.FORMULAS = [
  // ---------- FINANÇAS / MATEMÁTICA FINANCEIRA ----------
  {
    topico: "Finanças",
    titulo: "Valor Presente (VP)",
    formula: "VP = VF / (1 + i)^n",
    descricao: "Traz um valor futuro (VF) a valor de hoje. i = taxa por período, n = nº de períodos. Base de todo desconto de fluxo de caixa.",
    tags: ["desconto", "valor presente", "vp", "juros compostos"]
  },
  {
    topico: "Finanças",
    titulo: "Valor Futuro (VF) - Juros Compostos",
    formula: "VF = VP × (1 + i)^n",
    descricao: "Capitaliza um valor presente. Juros sobre juros. Para juros simples: VF = VP × (1 + i×n).",
    tags: ["capitalização", "juros compostos", "juros simples", "vf"]
  },
  {
    topico: "Finanças",
    titulo: "Taxa Equivalente (composta)",
    formula: "(1 + i_maior) = (1 + i_menor)^q",
    descricao: "Converte taxas entre períodos em regime composto. Ex.: (1+i_ano) = (1+i_mês)^12. q = quantos períodos menores cabem no maior.",
    tags: ["taxa equivalente", "conversão de taxas", "proporcional"]
  },
  {
    topico: "Finanças",
    titulo: "Taxa Real (Fisher)",
    formula: "(1 + i_nominal) = (1 + i_real) × (1 + inflação)",
    descricao: "Relação de Fisher. Isola o ganho real acima da inflação. i_real = (1+i_nom)/(1+infl) − 1. NÃO é só subtrair.",
    tags: ["fisher", "taxa real", "inflação", "nominal"]
  },
  {
    topico: "Finanças",
    titulo: "TIR (Taxa Interna de Retorno)",
    formula: "0 = Σ FC_t / (1 + TIR)^t",
    descricao: "Taxa que zera o VPL. Aceita projeto se TIR > custo de capital. Cuidado com fluxos não convencionais (múltiplas TIRs).",
    tags: ["tir", "irr", "vpl", "análise de projetos"]
  },

  // ---------- RENDA FIXA ----------
  {
    topico: "Renda Fixa",
    titulo: "Duration de Macaulay",
    formula: "D = Σ [ t × (VP do FC_t) ] / Preço",
    descricao: "Prazo médio ponderado dos fluxos pelo valor presente. Medida de tempo (em anos). Quanto maior, maior a sensibilidade a juros.",
    tags: ["duration", "macaulay", "prazo médio", "sensibilidade"]
  },
  {
    topico: "Renda Fixa",
    titulo: "Duration Modificada",
    formula: "DM = Duration / (1 + i)",
    descricao: "Sensibilidade % do preço a variação de 1 p.p. na taxa. ΔPreço% ≈ −DM × Δi. É a principal medida de risco de taxa de juros.",
    tags: ["duration modificada", "sensibilidade", "risco de juros", "dm"]
  },
  {
    topico: "Renda Fixa",
    titulo: "Convexidade",
    formula: "ΔP% ≈ −DM×Δi + ½ × Convexidade × (Δi)^2",
    descricao: "Correção de 2ª ordem da relação preço-taxa. Convexidade positiva favorece o investidor (preço cai menos e sobe mais que o previsto pela duration).",
    tags: ["convexidade", "preço", "taxa de juros"]
  },
  {
    topico: "Renda Fixa",
    titulo: "Preço de um Título (PU)",
    formula: "PU = Σ Cupom / (1+i)^t + VN / (1+i)^n",
    descricao: "Soma dos VPs dos cupons mais o VP do valor de face (VN). Se taxa de mercado > cupom, título negocia com deságio.",
    tags: ["pu", "preço unitário", "cupom", "bond", "deságio", "ágio"]
  },
  {
    topico: "Renda Fixa",
    titulo: "Curva de Juros (ETTJ)",
    formula: "Spot vs Forward",
    descricao: "Estrutura a termo. Taxa forward: (1+s2)^2 = (1+s1)×(1+f). Curva normal (ascendente), invertida (recessão), plana.",
    tags: ["ettj", "curva de juros", "forward", "spot", "estrutura a termo"]
  },

  // ---------- RENDA VARIÁVEL / VALUATION ----------
  {
    topico: "Renda Variável",
    titulo: "Gordon (Dividendos - crescimento constante)",
    formula: "P = D1 / (k − g)",
    descricao: "Preço = próximo dividendo / (custo do capital próprio − crescimento). Válido só se k > g e g constante perpétuo.",
    tags: ["gordon", "dividendos", "ddm", "gemido", "valuation", "perpetuidade"]
  },
  {
    topico: "Renda Variável",
    titulo: "CAPM",
    formula: "E(R) = Rf + β × (Rm − Rf)",
    descricao: "Retorno esperado de um ativo. Rf = livre de risco, β = risco sistemático, (Rm−Rf) = prêmio de mercado. Base do custo de capital próprio.",
    tags: ["capm", "beta", "prêmio de risco", "custo de capital", "risco sistemático"]
  },
  {
    topico: "Renda Variável",
    titulo: "WACC (Custo Médio Ponderado de Capital)",
    formula: "WACC = Ke×(E/V) + Kd×(1−T)×(D/V)",
    descricao: "Custo de capital da empresa. Ke=capital próprio, Kd=dívida, T=imposto, E=equity, D=dívida, V=E+D. Taxa de desconto do FCFF.",
    tags: ["wacc", "custo de capital", "kd", "ke", "fcff", "desconto"]
  },
  {
    topico: "Renda Variável",
    titulo: "Índice P/L (Preço/Lucro)",
    formula: "P/L = Preço da ação / LPA",
    descricao: "Quantos anos de lucro pagam o preço. LPA = lucro por ação. Múltiplo de mercado; comparar com pares do setor.",
    tags: ["p/l", "múltiplos", "lpa", "preço lucro"]
  },

  // ---------- ESTATÍSTICA / RISCO ----------
  {
    topico: "Estatística e Risco",
    titulo: "Retorno Esperado da Carteira",
    formula: "E(Rp) = Σ wi × E(Ri)",
    descricao: "Média ponderada dos retornos esperados pelos pesos (wi). Retorno é linear na carteira; risco NÃO é (por causa da correlação).",
    tags: ["retorno esperado", "carteira", "peso", "média ponderada"]
  },
  {
    topico: "Estatística e Risco",
    titulo: "Variância de Carteira (2 ativos)",
    formula: "σp² = w1²σ1² + w2²σ2² + 2·w1·w2·ρ·σ1·σ2",
    descricao: "Risco da carteira depende da correlação (ρ). Quanto menor ρ, maior o benefício da diversificação. ρ = Cov/(σ1σ2).",
    tags: ["variância", "correlação", "covariância", "diversificação", "risco carteira"]
  },
  {
    topico: "Estatística e Risco",
    titulo: "Índice de Sharpe",
    formula: "Sharpe = (Rp − Rf) / σp",
    descricao: "Retorno excedente por unidade de risco TOTAL (desvio-padrão). Quanto maior, melhor. Usa risco total, não só sistemático.",
    tags: ["sharpe", "retorno ajustado ao risco", "desvio padrão"]
  },
  {
    topico: "Estatística e Risco",
    titulo: "Índice de Treynor",
    formula: "Treynor = (Rp − Rf) / β",
    descricao: "Retorno excedente por unidade de risco SISTEMÁTICO (beta). Adequado para carteiras bem diversificadas.",
    tags: ["treynor", "beta", "risco sistemático"]
  },
  {
    topico: "Estatística e Risco",
    titulo: "Alfa de Jensen",
    formula: "α = Rp − [Rf + β(Rm − Rf)]",
    descricao: "Retorno acima do previsto pelo CAPM. α > 0 indica gestão que agregou valor ajustado ao risco.",
    tags: ["alfa", "jensen", "capm", "geração de valor"]
  },
  {
    topico: "Estatística e Risco",
    titulo: "VaR (Value at Risk) paramétrico",
    formula: "VaR = Z × σ × Valor × √t",
    descricao: "Perda máxima esperada num horizonte e nível de confiança. Z=1,65 (95%) ou 2,33 (99%). NÃO informa a perda além do VaR (isso é o CVaR/Expected Shortfall).",
    tags: ["var", "value at risk", "cvar", "expected shortfall", "risco de mercado"]
  },
  {
    topico: "Estatística e Risco",
    titulo: "Tracking Error",
    formula: "TE = desvio-padrão(Rp − Rbenchmark)",
    descricao: "Volatilidade da diferença de retorno para o benchmark. Information Ratio = (Rp−Rb)/TE, mede retorno ativo por risco ativo.",
    tags: ["tracking error", "information ratio", "benchmark", "risco ativo"]
  },
  {
    topico: "Performance e Risco",
    titulo: "TWR (Retorno Ponderado pelo Tempo)",
    formula: "1 + TWR = (1+r1) × (1+r2) × ... × (1+rn)",
    descricao: "Encadeia os retornos de cada subperíodo (entre aportes/resgates), eliminando o efeito do TIMING e do TAMANHO dos fluxos de caixa do cliente. É a medida correta para avaliar a HABILIDADE DO GESTOR, pois ele não controla quando o cotista aplica ou resgata. É o padrão da indústria (GIPS).",
    tags: ["twr", "time-weighted", "retorno ponderado pelo tempo", "gestor", "gips", "subperíodo", "performance"]
  },
  {
    topico: "Performance e Risco",
    titulo: "MWR (Retorno Ponderado pelo Dinheiro)",
    formula: "0 = Σ FC_t / (1 + MWR)^t   (é a TIR dos fluxos)",
    descricao: "É a própria TIR da carteira: a taxa que zera o valor presente de todos os fluxos (aportes, resgates e valor final). SOFRE influência do timing e do tamanho dos aportes, por isso mede o retorno REAL DO INVESTIDOR (a experiência do cotista), não a habilidade do gestor. Também chamado de retorno ponderado pelo capital / dólar-ponderado.",
    tags: ["mwr", "money-weighted", "dólar ponderado", "retorno do investidor", "tir", "timing", "aporte", "performance"]
  },
  {
    topico: "Performance e Risco",
    titulo: "TWR × MWR (quando divergem)",
    formula: "MWR > TWR se aportou antes de subir; MWR < TWR se aportou antes de cair",
    descricao: "Se os dois são iguais, não houve fluxo relevante no período. Se o cotista aportou pesado logo ANTES de uma alta, o MWR (do investidor) supera o TWR (do gestor); se aportou antes de uma queda, o MWR fica abaixo. Avaliar gestor → TWR. Avaliar resultado do cliente → MWR.",
    tags: ["twr", "mwr", "comparação", "diferença", "timing", "quando usar cada um"]
  },
  {
    topico: "Performance e Risco",
    titulo: "Índice de Sortino",
    formula: "Sortino = (Rp − MAR) / downside deviation",
    descricao: "Variação do Sharpe que pune SOMENTE o risco de queda (desvio abaixo da meta/MAR), IGNORANDO as oscilações positivas. MAR = retorno mínimo aceitável. Um fundo que sobe muito e cai pouco tem Sortino alto mesmo com Sharpe apenas mediano, porque a volatilidade de alta não é penalizada.",
    tags: ["sortino", "downside deviation", "desvio negativo", "mar", "risco de queda", "sharpe"]
  },
  {
    topico: "Performance e Risco",
    titulo: "Índice de Informação (Information Ratio)",
    formula: "IR = (Rp − Rbenchmark) / Tracking Error",
    descricao: "Retorno ATIVO (acima do benchmark) por unidade de risco ATIVO (tracking error). Mede a consistência da gestão ativa em bater o índice. Quanto maior, melhor a relação risco-retorno da estratégia ativa.",
    tags: ["information ratio", "índice de informação", "retorno ativo", "tracking error", "gestão ativa", "benchmark"]
  },
  {
    topico: "Performance e Risco",
    titulo: "Beta (β)",
    formula: "β = Cov(Rp, Rm) / Var(Rm)",
    descricao: "Sensibilidade do ativo/carteira ao mercado (risco sistemático). β=1 acompanha o mercado; β>1 amplifica (mais agressivo); β<1 ameniza (defensivo); β<0 anda ao contrário. É o risco que NÃO se elimina com diversificação e o insumo do CAPM e do Treynor.",
    tags: ["beta", "risco sistemático", "covariância", "capm", "sensibilidade", "mercado"]
  },

  // ---------- DERIVATIVOS ----------
  {
    topico: "Derivativos",
    titulo: "Paridade Put-Call",
    formula: "C + VP(K) = P + S",
    descricao: "Relação sem arbitragem entre call (C), put (P), preço à vista (S) e VP do strike (K). Mesmo strike e vencimento.",
    tags: ["put-call", "paridade", "opções", "arbitragem"]
  },
  {
    topico: "Derivativos",
    titulo: "Preço a Termo (Forward)",
    formula: "F = S × (1 + i)^t",
    descricao: "Preço futuro justo de um ativo sem renda. Com dividendos/custo de carrego, ajusta-se S pelos fluxos. Base do cash-and-carry.",
    tags: ["forward", "termo", "custo de carrego", "cash and carry"]
  },
  {
    topico: "Derivativos",
    titulo: "Gregas - Delta",
    formula: "Δ = ∂Preço da opção / ∂Preço do ativo",
    descricao: "Sensibilidade do prêmio ao preço do ativo. Call: 0 a 1; Put: −1 a 0. Usado no hedge (delta-hedging).",
    tags: ["delta", "gregas", "hedge", "opções", "gamma", "vega", "theta"]
  },

  // ---------- ECONOMIA ----------
  {
    topico: "Economia",
    titulo: "PIB (ótica da despesa)",
    formula: "PIB = C + I + G + (X − M)",
    descricao: "Consumo + Investimento + Gastos do governo + Exportações líquidas. Identidade macroeconômica fundamental.",
    tags: ["pib", "macroeconomia", "demanda agregada", "balança comercial"]
  },
  {
    topico: "Economia",
    titulo: "Paridade Descoberta de Juros",
    formula: "(1+i_doméstico) = (1+i_externo) × (E_esperado/E_atual)",
    descricao: "Relaciona diferencial de juros à expectativa de variação cambial. Base da relação entre juros e câmbio.",
    tags: ["paridade de juros", "câmbio", "juros", "arbitragem cambial"]
  },
  {
    topico: "Economia",
    titulo: "Quantidade da Moeda",
    formula: "M × V = P × Y",
    descricao: "Teoria quantitativa. M=moeda, V=velocidade, P=preços, Y=produto real. Base para relação entre moeda e inflação no longo prazo.",
    tags: ["teoria quantitativa", "moeda", "inflação", "velocidade"]
  },

  // ---------- ÉTICA E REGULAÇÃO ----------
  {
    topico: "Ética e Regulação",
    titulo: "Chinese Wall (Barreira de Informação)",
    formula: "Segregação de atividades",
    descricao: "Separação física/lógica entre gestão de recursos de terceiros e demais atividades (ex.: tesouraria), para evitar conflito de interesse e uso de informação privilegiada.",
    tags: ["chinese wall", "segregação", "conflito de interesse", "compliance", "barreira"]
  },
  {
    topico: "Ética e Regulação",
    titulo: "Suitability",
    formula: "Adequação produto ↔ investidor",
    descricao: "Dever de verificar se o produto é adequado ao perfil, objetivos, situação financeira e conhecimento do cliente antes de recomendar.",
    tags: ["suitability", "perfil", "adequação", "api"]
  },
  {
    topico: "Ética e Regulação",
    titulo: "Marcação a Mercado (MaM)",
    formula: "Ativos a preço de mercado",
    descricao: "Princípio que evita transferência de riqueza entre cotistas. Ativos da carteira avaliados diariamente a valor de mercado, não pela curva.",
    tags: ["marcação a mercado", "mam", "cotização", "transferência de riqueza"]
  }
];
