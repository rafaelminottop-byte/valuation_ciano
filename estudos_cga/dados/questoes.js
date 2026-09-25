// ============================================================
//  BANCO DE QUESTÕES - CGA (ANBIMA)
//  Como adicionar uma questão: copie um bloco { ... } e edite.
//    topico     -> mesmo nome usado nas fórmulas (para filtrar)
//    enunciado  -> a pergunta
//    alternativas -> array de textos (A, B, C, D...)
//    correta    -> índice da correta (0=A, 1=B, 2=C, 3=D)
//    explicacao -> por que é a correta / por que as outras erram
//    macete     -> dica curta para memorizar / não cair na pegadinha
// ============================================================

window.QUESTOES = [
  // ---------- ÉTICA E REGULAÇÃO ----------
  {
    topico: "Ética e Regulação",
    enunciado: "A separação entre a área de gestão de recursos de terceiros e a tesouraria da instituição, visando evitar conflito de interesses, é conhecida como:",
    alternativas: ["Suitability", "Chinese Wall (barreira de informação)", "Marcação a mercado", "Best execution"],
    correta: 1,
    explicacao: "Chinese Wall é a segregação de atividades para evitar conflito de interesses e uso indevido de informação. Suitability é adequação ao perfil; MaM é precificação de ativos.",
    macete: "Muro chinês = separa áreas. Se a questão fala em 'segregar/barreira entre áreas', é Chinese Wall."
  },
  {
    topico: "Ética e Regulação",
    enunciado: "O princípio da marcação a mercado (MaM) tem como principal objetivo:",
    alternativas: ["Aumentar a rentabilidade do fundo", "Reduzir a tributação dos cotistas", "Evitar a transferência de riqueza entre cotistas", "Garantir liquidez diária"],
    correta: 2,
    explicacao: "A MaM avalia os ativos a preço de mercado diariamente, evitando que aplicações/resgates a preços defasados transfiram riqueza entre cotistas.",
    macete: "MaM = evitar transferência de riqueza entre cotistas. É a resposta 'padrão' do objetivo da MaM."
  },

  // ---------- RENDA FIXA ----------
  {
    topico: "Renda Fixa",
    enunciado: "Um título de renda fixa possui duration modificada de 4. Se a taxa de juros de mercado subir 1 ponto percentual, o preço do título deverá, aproximadamente:",
    alternativas: ["Subir 4%", "Cair 4%", "Cair 0,25%", "Permanecer estável"],
    correta: 1,
    explicacao: "ΔP% ≈ −DM × Δi = −4 × 1% = −4%. Duration modificada mede a queda percentual aproximada do preço para +1 p.p. na taxa.",
    macete: "ΔPreço% ≈ −DM × Δtaxa. Juro sobe → preço cai. Multiplique a DM pela variação em p.p."
  },
  {
    topico: "Renda Fixa",
    enunciado: "Sobre a convexidade de um título prefixado, é correto afirmar que:",
    alternativas: ["É sempre negativa para o investidor", "Faz o preço cair mais do que o previsto pela duration quando os juros sobem", "Beneficia o investidor: o preço cai menos e sobe mais do que a duration prevê", "Não afeta a relação preço-taxa"],
    correta: 2,
    explicacao: "A convexidade positiva (típica de bonds sem opção) é um termo de 2ª ordem favorável: para uma mesma variação de juros, o ganho de preço é maior e a perda é menor do que a estimativa linear da duration.",
    macete: "Convexidade positiva é amiga do investidor: cai menos, sobe mais do que a duration prevê."
  },
  {
    topico: "Renda Fixa",
    enunciado: "Se a taxa de juros exigida pelo mercado é MAIOR que a taxa de cupom de um título, ele será negociado:",
    alternativas: ["Com ágio (acima do valor de face)", "Ao par (igual ao valor de face)", "Com deságio (abaixo do valor de face)", "Não é possível determinar"],
    correta: 2,
    explicacao: "Quando a taxa de mercado > cupom, o valor presente dos fluxos cai abaixo do valor de face: o título é negociado com deságio. O oposto gera ágio.",
    macete: "Taxa de mercado > cupom → DESágio (preço cai). Taxa < cupom → ágio. Preço e taxa andam em sentidos opostos."
  },

  // ---------- ESTATÍSTICA E RISCO ----------
  {
    topico: "Estatística e Risco",
    enunciado: "O Índice de Sharpe difere do Índice de Treynor principalmente porque:",
    alternativas: ["Sharpe usa o beta e Treynor usa o desvio-padrão", "Sharpe usa risco total (desvio-padrão) e Treynor usa risco sistemático (beta)", "Ambos usam beta", "Sharpe não considera o ativo livre de risco"],
    correta: 1,
    explicacao: "Sharpe = (Rp−Rf)/σ (risco total). Treynor = (Rp−Rf)/β (risco sistemático). Treynor é mais adequado para carteiras bem diversificadas.",
    macete: "SHarpe = deSvio-padrão (risco total). Treynor = beTa (risco sistemático). A inicial ajuda a lembrar."
  },
  {
    topico: "Estatística e Risco",
    enunciado: "Dois ativos com correlação igual a −1 são combinados numa carteira. Sobre o risco (desvio-padrão), pode-se afirmar que:",
    alternativas: ["Não há benefício de diversificação", "É possível, teoricamente, montar uma carteira com risco zero", "O risco é a média simples dos riscos", "O risco sempre aumenta"],
    correta: 1,
    explicacao: "Com ρ = −1 os movimentos são perfeitamente opostos; existe uma combinação de pesos que anula a variância da carteira (risco zero teórico). Quanto menor ρ, maior o ganho de diversificação.",
    macete: "ρ = −1 → risco zero teórico. Quanto menor a correlação, maior o ganho de diversificação."
  },
  {
    topico: "Estatística e Risco",
    enunciado: "O VaR (Value at Risk) de 1 dia a 99% de uma carteira é R$ 1 milhão. A interpretação correta é:",
    alternativas: ["A perda máxima possível é sempre R$ 1 milhão", "Há 99% de chance de perder exatamente R$ 1 milhão", "Em 1% dos dias, espera-se perda superior a R$ 1 milhão", "O ganho esperado é de R$ 1 milhão"],
    correta: 2,
    explicacao: "VaR 99% significa que, com 99% de confiança, a perda não excede R$ 1 mi; nos 1% de piores dias a perda tende a ser maior. O VaR NÃO diz o tamanho dessa perda extra (isso é o CVaR/Expected Shortfall).",
    macete: "VaR diz o 'até quanto' no dia bom; NÃO diz o tamanho da perda no dia ruim (isso é o CVaR)."
  },
  {
    topico: "Estatística e Risco",
    enunciado: "O Alfa de Jensen positivo de um fundo indica que o gestor:",
    alternativas: ["Assumiu risco excessivo", "Obteve retorno acima do previsto pelo CAPM para o risco assumido", "Teve desempenho igual ao benchmark", "Reduziu a volatilidade da carteira"],
    correta: 1,
    explicacao: "α = Rp − [Rf + β(Rm−Rf)]. Alfa positivo = retorno acima do esperado pelo CAPM dado o beta, sinal de geração de valor pela gestão ativa.",
    macete: "Alfa > 0 = bateu o que o CAPM previa para aquele risco. Alfa é a 'nota' da gestão ativa."
  },

  // ---------- RENDA VARIÁVEL ----------
  {
    topico: "Renda Variável",
    enunciado: "Pelo Modelo de Gordon, uma ação pagará dividendo de R$ 2,00 no próximo ano, o custo de capital próprio é 12% e o crescimento perpétuo dos dividendos é 4%. O preço justo é:",
    alternativas: ["R$ 16,67", "R$ 25,00", "R$ 50,00", "R$ 12,50"],
    correta: 1,
    explicacao: "P = D1/(k−g) = 2/(0,12−0,04) = 2/0,08 = R$ 25,00. Exige k > g e crescimento constante.",
    macete: "Gordon: P = D1 ÷ (k − g). Use o dividendo do PRÓXIMO ano (D1) e lembre: só vale se k > g."
  },
  {
    topico: "Renda Variável",
    enunciado: "No CAPM, o coeficiente beta (β) mede:",
    alternativas: ["O risco total do ativo", "O risco específico (diversificável) do ativo", "O risco sistemático, ou seja, a sensibilidade ao mercado", "A rentabilidade histórica do ativo"],
    correta: 2,
    explicacao: "Beta mede o risco sistemático (não diversificável), a sensibilidade do ativo aos movimentos do mercado. O risco específico é eliminado pela diversificação e não é remunerado.",
    macete: "Beta = risco sistemático (de mercado). Só esse é remunerado; o específico some na diversificação."
  },

  // ---------- DERIVATIVOS ----------
  {
    topico: "Derivativos",
    enunciado: "Pela paridade put-call (mesmo strike e vencimento), a relação correta é:",
    alternativas: ["C − P = S − VP(K)", "C + P = S + K", "C − P = K − S", "C + S = P + VP(K)"],
    correta: 0,
    explicacao: "Da paridade C + VP(K) = P + S, isolando: C − P = S − VP(K). Relação de não arbitragem entre call, put, ativo à vista e VP do strike.",
    macete: "Guarde a base: C + VP(K) = P + S. Qualquer variação é só isolar os termos dessa igualdade."
  },
  {
    topico: "Derivativos",
    enunciado: "O delta de uma opção de compra (call) pode assumir valores no intervalo:",
    alternativas: ["Entre −1 e 0", "Entre 0 e 1", "Entre −1 e 1", "Sempre igual a 1"],
    correta: 1,
    explicacao: "O delta da call varia de 0 (muito fora do dinheiro) a 1 (muito dentro do dinheiro). O delta da put varia de −1 a 0.",
    macete: "Call: delta de 0 a +1. Put: delta de −1 a 0. Comprou call, delta positivo; comprou put, negativo."
  },

  // ---------- ECONOMIA ----------
  {
    topico: "Economia",
    enunciado: "Na ótica da despesa, o PIB é dado por C + I + G + (X − M). O termo (X − M) representa:",
    alternativas: ["O consumo das famílias", "Os investimentos das empresas", "As exportações líquidas (balança comercial)", "Os gastos do governo"],
    correta: 2,
    explicacao: "(X − M) = exportações menos importações = exportações líquidas. C é consumo, I investimento, G gastos do governo.",
    macete: "PIB = C + I + G + (X − M). O parêntese (X − M) é sempre 'exportações líquidas'."
  },
  {
    topico: "Economia",
    enunciado: "Segundo a relação de Fisher, se a taxa nominal é 10% a.a. e a inflação é 4% a.a., a taxa real aproximada é:",
    alternativas: ["6,00%", "5,77%", "14,00%", "2,50%"],
    correta: 1,
    explicacao: "i_real = (1,10/1,04) − 1 ≈ 5,77%. Não é a simples subtração 10%−4%=6%, que serve apenas como aproximação grosseira.",
    macete: "Fisher: taxa real = (1+nominal)/(1+inflação) − 1. NÃO é subtrair; se a opção 'redonda' (6%) aparecer, é pegadinha."
  },

  // ---------- FINANÇAS ----------
  {
    topico: "Finanças",
    enunciado: "Um investimento rende 1% ao mês em juros compostos. A taxa equivalente anual é:",
    alternativas: ["12,00%", "12,68%", "10,00%", "1,00%"],
    correta: 1,
    explicacao: "(1+i_ano) = (1,01)^12 = 1,1268 → 12,68% a.a. A taxa proporcional (12%) subestima o efeito dos juros compostos.",
    macete: "Equivalência composta é potência: (1+i)^n. A resposta 'redonda' (12%) é a proporcional — quase sempre a errada."
  }
];
