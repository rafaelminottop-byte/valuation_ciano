// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - reforço dos tópicos fracos
//  Escritas do zero a partir de conhecimento padrão da CGA.
//  Somadas ao banco (window.QUESTOES).
// ============================================================
window.QUESTOES.push(

  // ===== FINANÇAS / MAT. FINANCEIRA =====
  { topico:"Finanças",
    enunciado:"Um investidor aplica R$ 10.000 por 2 anos a uma taxa de 10% ao ano em juros compostos. O montante final será:",
    alternativas:["R$ 12.000,00","R$ 12.100,00","R$ 11.000,00","R$ 12.210,00"],
    correta:1,
    explicacao:"VF = 10.000 × (1,10)² = 10.000 × 1,21 = R$ 12.100. Em juros simples seria 10.000 × (1+0,10×2) = R$ 12.000 — a diferença (R$ 100) é o juro sobre juro.",
    macete:"Composto é potência: VF = VP×(1+i)^n. A opção 'redonda' (12.000) é o juro simples — geralmente a pegadinha." },

  { topico:"Finanças",
    enunciado:"Dois projetos mutuamente exclusivos têm a mesma TIR, mas fluxos de caixa com perfis diferentes. Para decidir entre eles, a ferramenta mais adequada é:",
    alternativas:["Escolher qualquer um, pois a TIR é igual","Comparar o VPL a uma taxa de desconto relevante","Escolher o de menor payback sempre","Comparar apenas o investimento inicial"],
    correta:1,
    explicacao:"Quando há conflito ou empate de TIR entre projetos mutuamente exclusivos, o VPL é o critério decisivo, pois mede a criação de valor em termos absolutos à taxa de desconto apropriada. A TIR pode enganar por causa da escala e do perfil temporal dos fluxos.",
    macete:"Na dúvida entre projetos, quem manda é o VPL. A TIR engana em escala e perfil de fluxo." },

  { topico:"Finanças",
    enunciado:"Uma taxa nominal de 12% ao ano com capitalização mensal equivale a uma taxa efetiva anual de aproximadamente:",
    alternativas:["12,00%","12,68%","1,00%","12,36%"],
    correta:1,
    explicacao:"A taxa mensal é 12%/12 = 1% a.m. A efetiva anual = (1,01)¹² − 1 ≈ 12,68%. A capitalização mais frequente eleva a taxa efetiva acima da nominal.",
    macete:"Nominal ÷ períodos = taxa do período; depois eleve à potência. Efetiva > nominal quando capitaliza mais vezes." },

  // ===== ECONOMIA =====
  { topico:"Economia",
    enunciado:"No regime de metas de inflação, quando o Banco Central eleva a taxa básica de juros (Selic), o efeito esperado sobre a economia é:",
    alternativas:["Estímulo ao consumo e ao crédito","Contração da demanda agregada e desaceleração da inflação","Aumento imediato do PIB","Desvalorização automática da moeda local"],
    correta:1,
    explicacao:"Juros mais altos encarecem o crédito e desestimulam consumo e investimento, contraindo a demanda agregada e, com defasagem, reduzindo a pressão inflacionária. Tende inclusive a atrair capital externo e valorizar a moeda (não desvalorizar).",
    macete:"Juro sobe → freia demanda → segura inflação (e tende a valorizar a moeda). Política monetária contracionista." },

  { topico:"Economia",
    enunciado:"Um país apresenta déficit em conta corrente no balanço de pagamentos. Isso significa, em termos gerais, que:",
    alternativas:["O país exportou mais bens e serviços do que importou","O país está enviando ao exterior mais recursos (por bens, serviços e rendas) do que recebendo","O país necessariamente está em recessão","As reservas internacionais aumentaram"],
    correta:1,
    explicacao:"Déficit em conta corrente indica que as saídas (importações, remessas de renda etc.) superam as entradas. Esse déficit precisa ser financiado pela conta financeira (entrada de capitais/investimentos externos).",
    macete:"Déficit em conta corrente = sai mais do que entra; financia-se com entrada de capital (conta financeira)." },

  { topico:"Economia",
    enunciado:"Se a taxa de juros doméstica é maior que a externa, pela paridade descoberta da taxa de juros, o mercado tende a esperar que a moeda local:",
    alternativas:["Se valorize continuamente","Se deprecie no futuro, compensando o diferencial de juros","Fique fixa por decisão do Banco Central","Tenha juros irrelevantes para o câmbio"],
    correta:1,
    explicacao:"Pela paridade descoberta, um diferencial de juros a favor do país é compensado por uma expectativa de depreciação futura da moeda — caso contrário haveria arbitragem. Relaciona diretamente juros e câmbio esperado.",
    macete:"Juro doméstico maior → expectativa de DEPRECIAÇÃO futura da moeda (senão seria arbitragem de graça)." },

  // ===== DERIVATIVOS =====
  { topico:"Derivativos",
    enunciado:"Um investidor compra uma opção de compra (call) com prêmio de R$ 2 e strike de R$ 50. No vencimento, a ação está a R$ 58. O resultado bruto por ação (desconsiderando o prêmio) e o lucro líquido são, respectivamente:",
    alternativas:["R$ 8 e R$ 6","R$ 8 e R$ 8","R$ 6 e R$ 4","R$ 0 e −R$ 2"],
    correta:0,
    explicacao:"A call dá direito de comprar a R$ 50 algo que vale R$ 58: valor intrínseco = R$ 8. Descontando o prêmio pago (R$ 2), o lucro líquido é R$ 6. Se a ação fechasse abaixo de R$ 50, a call viraria pó e a perda seria só o prêmio.",
    macete:"Call: intrínseco = preço − strike (se positivo). Lucro líquido = intrínseco − prêmio pago." },

  { topico:"Derivativos",
    enunciado:"Um produtor rural que venderá sua safra daqui a 3 meses e teme queda de preço deve, para se proteger no mercado futuro:",
    alternativas:["Comprar contratos futuros da commodity","Vender contratos futuros da commodity (hedge de venda)","Comprar opções de compra apenas","Não fazer nada, pois o futuro não protege"],
    correta:1,
    explicacao:"Quem tem o ativo físico e teme queda faz hedge de VENDA: vende contratos futuros, travando o preço. Se o preço cair, a perda no físico é compensada pelo ganho na posição vendida em futuros.",
    macete:"Tem o ativo e teme QUEDA → VENDE futuro (hedge de venda). Vai comprar e teme ALTA → compra futuro." },

  { topico:"Derivativos",
    enunciado:"Sobre a grega VEGA de uma opção, é correto afirmar que ela mede a sensibilidade do prêmio a variações:",
    alternativas:["No preço do ativo-objeto","Na volatilidade implícita","Na passagem do tempo","Na taxa de juros"],
    correta:1,
    explicacao:"Vega mede a sensibilidade do prêmio à volatilidade. Delta mede sensibilidade ao preço do ativo; Theta ao tempo; Rho à taxa de juros. Maior volatilidade eleva o prêmio de calls e puts.",
    macete:"Vega = Volatilidade. Delta = preço; Theta = tempo; Rho = juros. Associe pela inicial." },

  // ===== ÉTICA E REGULAÇÃO =====
  { topico:"Ética e Regulação",
    enunciado:"Um gestor recebe informação relevante ainda não divulgada ao mercado sobre uma companhia e a utiliza para negociar ações antes da divulgação. Essa conduta configura:",
    alternativas:["Suitability inadequado","Uso indevido de informação privilegiada (insider trading)","Marcação a mercado","Front running de ordem de cliente"],
    correta:1,
    explicacao:"Negociar com base em informação relevante não pública é insider trading, prática vedada. Front running é diferente: usar a informação de uma ordem de cliente para negociar antes dela.",
    macete:"Informação relevante não pública = insider trading. Se for na frente da ORDEM do cliente = front running." },

  { topico:"Ética e Regulação",
    enunciado:"O dever de suitability obriga o profissional a:",
    alternativas:["Garantir rentabilidade ao cliente","Verificar a adequação do produto ao perfil, aos objetivos e à situação financeira do cliente","Vender sempre o produto de maior taxa","Divulgar informação privilegiada a todos os clientes"],
    correta:1,
    explicacao:"Suitability é o dever de adequar a recomendação ao perfil do investidor (objetivos, situação financeira e conhecimento). Não existe garantia de rentabilidade, e a recomendação não pode ser guiada pelo interesse de quem vende.",
    macete:"Suitability = produto certo para o cliente certo. Ninguém garante rentabilidade — se a opção prometer isso, é falsa." },

  { topico:"Ética e Regulação",
    enunciado:"A prática de comprar/vender ativos no fim do período de avaliação apenas para melhorar artificialmente a foto da carteira divulgada é conhecida como:",
    alternativas:["Window dressing","Chinese wall","Rebalanceamento","Best execution"],
    correta:0,
    explicacao:"Window dressing é 'maquiar' a carteira na data de divulgação para parecer mais atraente, distorcendo a avaliação. É uma das limitações/manipulações que afetam medidas de desempenho.",
    macete:"Window dressing = 'maquiar a vitrine' na data da foto. Manipula a aparência da carteira." },

  // ===== ESTATÍSTICA E RISCO =====
  { topico:"Estatística e Risco",
    enunciado:"Uma carteira tem retorno esperado de 12% e desvio-padrão de 20%. Com a taxa livre de risco em 6%, o Índice de Sharpe é:",
    alternativas:["0,60","0,30","0,90","1,20"],
    correta:1,
    explicacao:"Sharpe = (12% − 6%) / 20% = 6/20 = 0,30. Mede o retorno excedente por unidade de risco total (desvio-padrão).",
    macete:"Sharpe = (retorno − CDI) ÷ desvio-padrão. Primeiro o excedente, depois divide pelo risco total." },

  { topico:"Estatística e Risco",
    enunciado:"Sobre a diversificação de uma carteira, é correto afirmar que ela reduz principalmente o:",
    alternativas:["Risco sistemático (de mercado)","Risco não sistemático (específico/diversificável)","Retorno esperado","Beta da carteira para zero"],
    correta:1,
    explicacao:"A diversificação elimina o risco específico (não sistemático) de cada ativo. O risco sistemático (de mercado) não é diversificável e é justamente o remunerado pelo prêmio de risco no CAPM.",
    macete:"Diversificação mata o risco ESPECÍFICO. O sistemático (mercado) não some — e é o único remunerado." },

  { topico:"Estatística e Risco",
    enunciado:"Um ativo com distribuição de retornos que apresenta 'caudas mais gordas' que a normal (excesso de curtose) implica que:",
    alternativas:["Eventos extremos são menos prováveis que o previsto pela normal","Eventos extremos são mais prováveis que o previsto pela normal, subestimando o risco de cauda","A média dos retornos é sempre negativa","O desvio-padrão é zero"],
    correta:1,
    explicacao:"Excesso de curtose (leptocurtose) significa caudas mais gordas: eventos extremos ocorrem com mais frequência do que a distribuição normal prevê. Por isso, medidas como o VaR paramétrico (que assume normalidade) tendem a subestimar o risco de cauda.",
    macete:"Cauda gorda = evento extremo mais frequente. VaR normal SUBESTIMA esse risco de cauda." },

  { topico:"Estatística e Risco",
    enunciado:"Dois ativos têm correlação igual a +1. Ao combiná-los numa carteira, o desvio-padrão resultante será:",
    alternativas:["Sempre zero","A média ponderada dos desvios-padrão (sem benefício de diversificação)","Menor que o de qualquer ativo isolado","Impossível de calcular"],
    correta:1,
    explicacao:"Com correlação +1 não há benefício de diversificação: o risco da carteira é a média ponderada dos riscos individuais. O ganho de diversificação só aparece quando a correlação é menor que 1.",
    macete:"ρ = +1 → zero diversificação (risco = média ponderada). Só há ganho quando ρ < 1." }

);
