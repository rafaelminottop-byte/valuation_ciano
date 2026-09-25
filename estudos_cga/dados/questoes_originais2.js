// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 2
//  Reforço dos blocos de maior peso: RF, RV, Performance e Regulação.
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== RENDA FIXA =====
  { topico:"Renda Fixa",
    enunciado:"Um título prefixado tem duration modificada de 5,5. Diante de uma expectativa de QUEDA de 0,80 ponto percentual na taxa de juros, o preço deve variar aproximadamente:",
    alternativas:["Cair 4,4%","Subir 4,4%","Subir 0,55%","Permanecer estável"],
    correta:1,
    explicacao:"ΔP% ≈ −DM × Δi = −5,5 × (−0,80%) = +4,4%. Queda de juros eleva o preço dos prefixados; a duration modificada estima a magnitude.",
    macete:"Juro cai → preço sobe. ΔP% ≈ −DM × Δtaxa; o sinal negativo com queda vira alta de preço." },

  { topico:"Renda Fixa",
    enunciado:"Entre dois títulos com a mesma duration, aquele que possui MAIOR convexidade tende a:",
    alternativas:["Perder mais valor quando os juros sobem","Ganhar mais quando os juros caem e perder menos quando sobem","Ter comportamento idêntico ao outro","Não sofrer efeito de variação de juros"],
    correta:1,
    explicacao:"Para uma mesma duration, maior convexidade é vantajosa: o preço sobe mais na queda de juros e cai menos na alta. Por isso investidores pagam um leve prêmio por convexidade.",
    macete:"Mais convexidade = mais 'sorte': sobe mais na queda, cai menos na alta (para a mesma duration)." },

  { topico:"Renda Fixa",
    enunciado:"Um gestor acredita que a curva de juros vai se ACHATAR (as taxas longas cairão em relação às curtas). A estratégia coerente com essa visão é:",
    alternativas:["Steepening","Flattening","Butterfly neutro","Aumentar caixa apenas"],
    correta:1,
    explicacao:"Apostar no estreitamento do spread longo-curto é uma estratégia de flattening (ex.: comprar títulos longos e/ou vender curtos). Steepening é a aposta oposta (curva mais inclinada).",
    macete:"FLATtening = curva mais 'flat' (achatada). Steepening = mais inclinada. O nome já diz a aposta." },

  { topico:"Renda Fixa",
    enunciado:"Um título é negociado com yield to maturity de 9%, mas possui uma cláusula de call que, se exercida, resultaria em yield to call de 7,5%. Para um investidor avaliar o pior cenário, a medida relevante é:",
    alternativas:["Current yield","Yield to maturity","Yield to worst (7,5%)","Yield spread"],
    correta:2,
    explicacao:"O yield to worst é o menor entre YTM, YTC e YTP. Aqui, YTW = 7,5% (o YTC), representando o cenário mais conservador para o investidor caso o emissor exerça o call.",
    macete:"Yield to WORST = o MENOR dos yields (YTM/YTC/YTP). É sempre o cenário mais conservador." },

  { topico:"Renda Fixa",
    enunciado:"Uma seguradora precisa honrar um pagamento fixo daqui a 7 anos e quer eliminar completamente o risco de reinvestimento e de taxa de juros. A estratégia mais adequada é:",
    alternativas:["Comprar um título de curtíssimo prazo e rolar","Cash-flow matching com um título cujo fluxo coincida com a obrigação","Gestão ativa buscando alfa","Constant mix 60/40"],
    correta:1,
    explicacao:"O cash-flow matching casa exatamente o fluxo do ativo com a obrigação futura, eliminando risco de reinvestimento e de taxa — a forma mais conservadora de imunização, ideal para passivos determinados.",
    macete:"Quer eliminar TUDO (reinvestimento + taxa) para um passivo certo → cash-flow matching (casa fluxo com obrigação)." },

  // ===== RENDA VARIÁVEL =====
  { topico:"Renda Variável",
    enunciado:"Um fundo indexado ao Ibovespa apresenta tracking error elevado em relação ao índice. Isso indica que o fundo:",
    alternativas:["Está replicando o índice com alta fidelidade","Está se desviando bastante do comportamento do índice","Tem custo zero","Superou o índice com certeza"],
    correta:1,
    explicacao:"Tracking error mede o desvio de retorno frente ao benchmark. Num fundo que se propõe indexado, TE elevado é ruim: sinaliza baixa aderência ao índice (o objetivo era minimizá-lo).",
    macete:"Tracking error = tamanho do desvio ao benchmark. Fundo indexado quer TE baixo; TE alto = pouca aderência." },

  { topico:"Renda Variável",
    enunciado:"Uma gestora monta uma carteira comprada em ações baratas e vendida em ações caras, equilibrando as exposições de modo que o beta líquido fique próximo de zero. Essa estratégia é:",
    alternativas:["Long only value","Long-short market neutral","Indexação pura","Buy-and-hold"],
    correta:1,
    explicacao:"Long-short com beta líquido ~0 é market neutral: o retorno vem da seleção relativa (o spread entre as pontas), com baixa dependência da direção do mercado.",
    macete:"Long + short com beta ≈ 0 = market neutral. O lucro vem do spread entre as pontas, não da direção do mercado." },

  { topico:"Renda Variável",
    enunciado:"No estilo de gestão VALUE, o gestor busca principalmente ações que:",
    alternativas:["Tenham alto crescimento de receita, mesmo caras","Estejam baratas frente aos seus fundamentos (baixo P/L, P/VP)","Sejam de empresas recém-listadas","Paguem zero dividendo por definição"],
    correta:1,
    explicacao:"O estilo value procura ações descontadas em relação aos fundamentos (múltiplos baixos como P/L e P/VP). O estilo growth foca em empresas com alto potencial de crescimento, geralmente com múltiplos mais altos.",
    macete:"Value = barato (múltiplo baixo). Growth = crescimento (múltiplo alto). Value caça desconto." },

  { topico:"Renda Variável",
    enunciado:"Na integração ASG via fluxo de caixa descontado, uma companhia com forte passivo ambiental e governança fraca tende a ser avaliada com:",
    alternativas:["Menor taxa de desconto e maior valor","Maior taxa de desconto (mais risco) e/ou fluxos ajustados para baixo","Isenção de análise de risco","Valor idêntico a uma empresa sem esses riscos"],
    correta:1,
    explicacao:"Riscos ASG elevados aumentam o custo de capital (taxa de desconto) e podem reduzir premissas de crescimento/margem, resultando em menor valor presente. É a lógica da integração ASG no valuation.",
    macete:"Risco ASG alto → taxa de desconto maior → valor menor. ASG ruim encarece o capital." },

  // ===== PERFORMANCE E RISCO =====
  { topico:"Performance e Risco",
    enunciado:"Dois fundos têm o mesmo Índice de Sharpe. O Fundo A, porém, é bem diversificado e o Fundo B é concentrado. Para comparar o desempenho ajustado ao risco SISTEMÁTICO, a medida mais apropriada é:",
    alternativas:["Sharpe","Treynor","Desvio-padrão","Current yield"],
    correta:1,
    explicacao:"Treynor usa o beta (risco sistemático) no denominador, sendo mais adequado para carteiras bem diversificadas, onde o risco específico já foi eliminado. Sharpe usa o risco total.",
    macete:"Falou em risco SISTEMÁTICO / carteira diversificada → Treynor (beta). Risco total → Sharpe (desvio)." },

  { topico:"Performance e Risco",
    enunciado:"Um fundo entregou retorno de 14%, com beta 1,2, num mercado que rendeu 11% e taxa livre de risco de 5%. O alfa de Jensen do fundo é:",
    alternativas:["+1,8%","−1,8%","+3,0%","0%"],
    correta:0,
    explicacao:"Retorno esperado (CAPM) = 5% + 1,2×(11%−5%) = 5% + 7,2% = 12,2%. Alfa = 14% − 12,2% = +1,8%. Alfa positivo indica geração de valor acima do previsto para o risco assumido.",
    macete:"Alfa = retorno real − CAPM. Primeiro monte o CAPM [Rf + β(Rm−Rf)], depois subtraia do retorno obtido." },

  { topico:"Performance e Risco",
    enunciado:"O Information Ratio de um fundo ativo é baixo, apesar de um bom retorno ativo. A explicação mais provável é:",
    alternativas:["O tracking error foi muito alto (muito risco ativo para o retorno obtido)","O beta foi negativo","O fundo é livre de risco","O benchmark não existe"],
    correta:0,
    explicacao:"IR = retorno ativo ÷ tracking error. Se o retorno ativo é bom mas o IR é baixo, o denominador (tracking error) foi alto: o gestor assumiu muito risco ativo para o retorno que gerou.",
    macete:"IR = retorno ativo ÷ tracking error. IR baixo com bom retorno = tracking error alto (muito risco ativo)." },

  { topico:"Performance e Risco",
    enunciado:"Para um título com opção de pré-pagamento embutida (cujos fluxos mudam conforme a taxa), a medida de sensibilidade de preço mais apropriada é a:",
    alternativas:["Duration de Macaulay","Duration modificada","Effective duration","Current yield"],
    correta:2,
    explicacao:"A effective duration considera que os fluxos podem mudar sob choques de taxa, sendo apropriada a títulos com opcionalidade (call, pré-pagamento). A modificada assume fluxos fixos e não captura esse efeito.",
    macete:"Tem opção embutida (call/pré-pagamento) → effective duration. Fluxo fixo → modificada." },

  // ===== REGULAÇÃO E FUNDOS (CVM 175) =====
  { topico:"Regulação e Fundos",
    enunciado:"Em um fundo de investimento, a responsabilidade por tomar as decisões de compra e venda de ativos da carteira é do:",
    alternativas:["Administrador","Gestor","Custodiante","Auditor independente"],
    correta:1,
    explicacao:"O gestor é o responsável pelas decisões de investimento/alocação. O administrador responde legalmente perante a CVM e supervisiona; o custodiante guarda os ativos e liquida operações.",
    macete:"Decisão de comprar/vender = GESTOR. Responsável legal/CVM = administrador. Guarda = custodiante." },

  { topico:"Regulação e Fundos",
    enunciado:"Um investidor resgata cotas de um fundo de renda fixa de longo prazo após 200 dias da aplicação. A alíquota de IR aplicável, pela tabela regressiva, é:",
    alternativas:["22,5%","20,0%","17,5%","15,0%"],
    correta:1,
    explicacao:"Na tabela regressiva de longo prazo: até 180 dias 22,5%; de 181 a 360 dias 20%; de 361 a 720 dias 17,5%; acima de 720 dias 15%. Com 200 dias (entre 181 e 360), a alíquota é 20%.",
    macete:"Tabela regressiva LP: 180/360/720 dias → 22,5% / 20% / 17,5% / 15%. Ache a faixa do prazo primeiro." },

  { topico:"Regulação e Fundos",
    enunciado:"O mecanismo de 'come-cotas' NÃO se aplica a qual tipo de fundo?",
    alternativas:["Fundos de renda fixa de longo prazo","Fundos multimercado","Fundos de ações","Fundos de curto prazo"],
    correta:2,
    explicacao:"Fundos de ações não têm come-cotas; a tributação (15%) ocorre apenas no resgate. O come-cotas é a antecipação semestral (maio e novembro) que incide sobre fundos de RF e multimercado.",
    macete:"Fundo de AÇÕES não tem come-cotas (15% só no resgate). Come-cotas = RF e multimercado (maio/novembro)." },

  { topico:"Regulação e Fundos",
    enunciado:"Para ser classificado como Fundo de Ações, a carteira deve manter, no mínimo, o seguinte percentual em ações e ativos relacionados:",
    alternativas:["50%","67%","80%","95%"],
    correta:1,
    explicacao:"Fundos de Ações exigem no mínimo 67% em ações e ativos ligados ao mercado acionário. (Fundos de Renda Fixa exigem no mínimo 80% no fator de risco de renda fixa.)",
    macete:"Ações = mínimo 67%. Renda Fixa = mínimo 80%. Não troque os dois números." }

);
