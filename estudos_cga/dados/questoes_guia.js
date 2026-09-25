// ============================================================
//  QUESTÕES BASEADAS NO GUIA DE REVISÃO CGA (Blocos 1 a 4)
//  Somadas ao banco de questões (window.QUESTOES).
// ============================================================
window.QUESTOES.push(

  // ===== RENDA VARIÁVEL =====
  { topico:"Renda Variável",
    enunciado:"Uma gestão que busca retorno absoluto, independentemente de um benchmark, podendo usar posições long/short e derivativos, é classificada como:",
    alternativas:["Passiva","Ativa relativa","Agnóstica (total return)","Indexação pura"],
    correta:2,
    explicacao:"A gestão agnóstica/total return foca no resultado absoluto, sem comparação relativa a um índice. A passiva replica o benchmark; a ativa busca alfa relativo ao benchmark.",
    macete:"'Retorno absoluto, sem benchmark' = agnóstica/total return. Passiva replica; ativa bate o índice." },

  { topico:"Renda Variável",
    enunciado:"Sobre os métodos de indexação, a FULL REPLICATION caracteriza-se por:",
    alternativas:["Selecionar um subconjunto representativo por estratos","Comprar todos os ativos do índice nas mesmas proporções, com máxima precisão e custo alto","Usar modelos de fatores para montar uma carteira menor","Eliminar o tracking error por meio de derivativos"],
    correta:1,
    explicacao:"Full replication compra todos os componentes do índice nas proporções corretas: precisão máxima, porém custo alto e dificuldade com ativos ilíquidos. Amostragem estratificada e otimização usam carteiras menores.",
    macete:"Full replication = compra TUDO (máxima precisão, maior custo). Amostragem/otimização = carteira menor." },

  { topico:"Renda Variável",
    enunciado:"Uma carteira long-short cujas exposições comprada e vendida se equilibram, resultando em beta próximo de zero, é chamada de:",
    alternativas:["Market neutral","Long only","Enhanced indexing","Buy-and-hold"],
    correta:0,
    explicacao:"Quando long e short se equilibram, a carteira fica market neutral: o retorno depende da seleção relativa dos ativos, não da direção do mercado.",
    macete:"Beta ≈ 0 numa long-short = market neutral. Ganha na seleção, não na direção do mercado." },

  { topico:"Renda Variável",
    enunciado:"Na integração de aspectos ASG (ESG) ao valuation por fluxo de caixa descontado, é comum que empresas com riscos ASG elevados apresentem:",
    alternativas:["Menor custo de capital","Maior custo de capital, reduzindo o valor presente dos fluxos","Fluxos de caixa garantidos","Isenção de análise de governança"],
    correta:1,
    explicacao:"Riscos ASG altos elevam o custo de capital (taxa de desconto) e/ou reduzem premissas de crescimento e margem, diminuindo o valor. Abordagens: integração no DCF, exclusão setorial ou best-in-class.",
    macete:"Risco ASG alto → custo de capital maior → valor menor. ASG entra como ajuste de risco no DCF." },

  { topico:"Renda Variável",
    enunciado:"Entre as classificações por tracking error, a INDEXAÇÃO REFORÇADA (enhanced indexing) caracteriza-se por:",
    alternativas:["Tracking error mínimo, replicando o índice fielmente","Tracking error baixo: base passiva com pequenos desvios táticos buscando alfa marginal","Tracking error alto, com desvios relevantes","Ausência total de benchmark"],
    correta:1,
    explicacao:"Enhanced indexing parte de uma base passiva e adiciona pequenos desvios táticos (TE baixo) para gerar alfa marginal, ficando entre a indexação pura e a gestão ativa.",
    macete:"TE: pura (mínimo) < enhanced (baixo) < ativa (alto). Enhanced = passiva 'turbinada' com pequenos desvios." },

  // ===== RENDA FIXA =====
  { topico:"Renda Fixa",
    enunciado:"A estratégia de imunização MAIS conservadora, que monta uma carteira cujos fluxos coincidem exatamente com as obrigações futuras, eliminando risco de reinvestimento e de taxa, é:",
    alternativas:["Contingent immunization","Cash-flow matching","Butterfly","Constant mix"],
    correta:1,
    explicacao:"O cash-flow matching casa exatamente os fluxos (cupons + principal) com as obrigações, eliminando risco de reinvestimento e de taxa. É a forma mais conservadora de imunização.",
    macete:"'Mais conservadora' + 'fluxo casa com obrigação' = cash-flow matching. Elimina reinvestimento E taxa." },

  { topico:"Renda Fixa",
    enunciado:"Uma curva de juros INVERTIDA (taxas curtas maiores que as longas) costuma sinalizar:",
    alternativas:["Expectativa de alta de juros e aquecimento","Expectativa de queda de juros / recessão","Ausência de prêmio de prazo","Mercado perfeitamente eficiente"],
    correta:1,
    explicacao:"A inversão (curtas > longas) tipicamente antecipa queda de juros futura e/ou recessão. A curva normal (ascendente) é a mais comum, refletindo prêmio por prazo.",
    macete:"Curva invertida (curta > longa) = mercado prevê QUEDA de juros / recessão." },

  { topico:"Renda Fixa",
    enunciado:"O Yield to Worst (YTW) de um título com opções embutidas é definido como:",
    alternativas:["A média entre YTM, YTC e YTP","O maior valor entre YTM, YTC e YTP","O menor valor entre YTM, YTC e YTP","Igual ao current yield"],
    correta:2,
    explicacao:"O YTW é o menor rendimento entre YTM, YTC e YTP — representa o cenário mais conservador para o investidor, considerando o pior desfecho das opções.",
    macete:"Worst = pior para o investidor = o MENOR dos yields. Nunca é média nem o maior." },

  { topico:"Renda Fixa",
    enunciado:"Um Treasury STRIPS é caracterizado por ser um título:",
    alternativas:["De cupom zero, resultado da separação de cupons e principal","De curtíssimo prazo com pagamento de cupom mensal","Corporativo de alto risco","Indexado à inflação americana"],
    correta:0,
    explicacao:"STRIPS resultam da separação (stripping) dos cupons e do principal de um Treasury, negociados individualmente como títulos de cupom zero.",
    macete:"STRIPS = 'fatiar' o título em cupom zero. 'Strip' de cupons e principal negociados separadamente." },

  { topico:"Renda Fixa",
    enunciado:"A Teoria da Preferência pela Liquidez afirma que a curva de juros tende a se inclinar para cima porque:",
    alternativas:["O mercado sempre espera queda de juros","Investidores exigem um prêmio para carregar títulos de prazos mais longos","Os títulos curtos têm mais risco de crédito","A inflação é sempre decrescente"],
    correta:1,
    explicacao:"Segundo a preferência pela liquidez, prazos mais longos embutem mais incerteza/risco de mercado, exigindo prêmio — o que inclina a curva para cima independentemente das expectativas de juros.",
    macete:"Preferência pela liquidez = prêmio por prazo. Prazo mais longo pede mais prêmio → curva sobe." },

  { topico:"Renda Fixa",
    enunciado:"Uma estratégia de curva BUTTERFLY tem como característica:",
    alternativas:["Apostar apenas na queda do nível geral das taxas","Posições em três pontos da curva apostando em mudança de curvatura, neutra ao nível","Comprar somente títulos de curto prazo","Eliminar o risco de crédito"],
    correta:1,
    explicacao:"O butterfly usa três vértices (curto, médio, longo) para apostar em mudança de CURVATURA, sendo neutro ao nível geral das taxas. Steepening/flattening apostam na inclinação.",
    macete:"Butterfly = 3 pontos da curva, aposta na CURVATURA (neutro ao nível). Steepening/flattening = inclinação." },

  // ===== PERFORMANCE E RISCO =====
  { topico:"Performance e Risco",
    enunciado:"O retorno TIME-WEIGHTED (ponderado pelo tempo) é a medida mais adequada para avaliar o gestor porque:",
    alternativas:["Reflete a experiência do investidor com aportes e resgates","Isola o efeito de aportes/resgates, encadeando os subperíodos","Considera apenas o fluxo inicial","É sempre maior que o money-weighted"],
    correta:1,
    explicacao:"O time-weighted encadeia os retornos entre fluxos de caixa, isolando o efeito de aportes/resgates que o gestor não controla. O money-weighted (TIR) reflete a experiência do investidor.",
    macete:"Avaliar o GESTOR = time-weighted (isola aportes). Experiência do INVESTIDOR = money-weighted (TIR)." },

  { topico:"Performance e Risco",
    enunciado:"Qual medida de desempenho ajustada ao risco utiliza apenas o desvio-padrão dos retornos NEGATIVOS (downside)?",
    alternativas:["Sharpe","Treynor","Sortino","Information Ratio"],
    correta:2,
    explicacao:"O Índice de Sortino usa o desvio-padrão apenas dos retornos abaixo de um alvo (downside), penalizando somente a volatilidade indesejada. Sharpe usa risco total; Treynor usa beta.",
    macete:"Só downside = Sortino. Sharpe = risco total; Treynor = beta; IR = tracking error." },

  { topico:"Performance e Risco",
    enunciado:"O Information Ratio (IR) é calculado como:",
    alternativas:["Retorno excedente ÷ desvio-padrão total","Retorno ativo (vs. benchmark) ÷ tracking error","Retorno excedente ÷ beta","Alfa ÷ desvio-padrão negativo"],
    correta:1,
    explicacao:"IR = retorno ativo (carteira − benchmark) ÷ tracking error. Mede a eficiência da gestão ativa por unidade de risco ativo assumido.",
    macete:"IR = retorno ATIVO ÷ tracking error. É o 'Sharpe da gestão ativa' (mede risco ativo)." },

  { topico:"Performance e Risco",
    enunciado:"A duration EFFECTIVE é a medida mais apropriada para títulos que possuem:",
    alternativas:["Fluxos de caixa perfeitamente fixos","Opcionalidade embutida, como pré-pagamento ou call","Prazo inferior a um ano","Cupom zero"],
    correta:1,
    explicacao:"A effective duration mede a variação de preço sob choques de taxa considerando que os fluxos podem mudar — adequada a títulos com opcionalidade embutida (call, pré-pagamento). Para fluxos fixos usa-se a modificada.",
    macete:"Opção embutida (call/pré-pagamento) → effective duration. Fluxo fixo → modificada." },

  { topico:"Performance e Risco",
    enunciado:"A Perda Esperada de uma exposição de crédito é dada pela fórmula:",
    alternativas:["PD + LGD + EAD","PD × LGD × EAD","LGD ÷ EAD","1 − PD"],
    correta:1,
    explicacao:"Perda Esperada = PD (probabilidade de default) × LGD (perda dado o default) × EAD (exposição no default). Note que LGD = 1 − taxa de recuperação.",
    macete:"Perda Esperada = PD × LGD × EAD (multiplica os três). E LGD = 1 − recuperação." },

  { topico:"Performance e Risco",
    enunciado:"A estratégia CONSTANT MIX, que mantém proporções fixas entre classes (ex.: 60/40) rebalanceando periodicamente, é considerada:",
    alternativas:["Pró-cíclica, como o CPPI","Contrária/anti-cíclica: compra o que caiu e vende o que subiu","Idêntica ao buy-and-hold","Livre de risco"],
    correta:1,
    explicacao:"O constant mix rebalanceia de volta aos pesos-alvo, comprando o ativo que caiu e vendendo o que subiu — comportamento contrário/anti-cíclico, oposto ao CPPI (que compra na alta).",
    macete:"Constant mix = contrária (compra o que caiu). CPPI = pró-cíclica (compra o que subiu)." },

  // ===== REGULAÇÃO E FUNDOS =====
  { topico:"Regulação e Fundos",
    enunciado:"Segundo as obrigações na estrutura de um fundo, a responsabilidade pela GUARDA dos ativos, liquidação de operações e conciliação da posição é do:",
    alternativas:["Administrador","Gestor","Custodiante","Distribuidor"],
    correta:2,
    explicacao:"O custodiante guarda os ativos, liquida operações e concilia a posição. O administrador é o responsável legal perante a CVM; o gestor toma as decisões de investimento.",
    macete:"Guarda + liquida + concilia = custodiante. Decide = gestor; responde à CVM = administrador." },

  { topico:"Regulação e Fundos",
    enunciado:"Para ser classificado como Fundo de Renda Fixa, o fundo deve manter, no mínimo:",
    alternativas:["50% em ações","67% em ações","80% em ativos do fator de risco renda fixa","100% em títulos públicos"],
    correta:2,
    explicacao:"Fundos de Renda Fixa devem ter no mínimo 80% da carteira em ativos ligados ao fator de risco de renda fixa (juros e/ou índices de preços). Fundos de Ações exigem no mínimo 67% em ações.",
    macete:"Renda Fixa = mínimo 80% no fator de risco RF. Ações = mínimo 67%." },

  { topico:"Regulação e Fundos",
    enunciado:"Sobre a tributação de fundos (CVM 175, Anexo I), o mecanismo de 'come-cotas' consiste em:",
    alternativas:["Cobrança de IR apenas no resgate","Antecipação semestral de IR na fonte (maio e novembro)","Isenção total de imposto de renda","Taxa fixa de 15% mensal"],
    correta:1,
    explicacao:"O come-cotas é a antecipação semestral de IR na fonte (maio e novembro) em fundos de RF/multimercado. Fundos de ações não têm come-cotas (15% apenas no resgate).",
    macete:"Come-cotas = antecipação de IR em maio e novembro (RF/multimercado). Ações não têm." },

  { topico:"Regulação e Fundos",
    enunciado:"As CLASSES RESTRITAS de fundos, sob a Resolução CVM 175, destinam-se a:",
    alternativas:["Qualquer investidor de varejo","Exclusivamente investidores qualificados/profissionais, com regras mais flexíveis","Somente pessoas jurídicas","Fundos garantidos pelo governo"],
    correta:1,
    explicacao:"Classes restritas são destinadas a investidores qualificados/profissionais e têm regras mais flexíveis quanto a ativos elegíveis, concentração e alavancagem, dado o perfil mais sofisticado.",
    macete:"Restrita = restrita a quem entende mais (qualificado/profissional) → regras mais flexíveis." },

  { topico:"Regulação e Fundos",
    enunciado:"Sobre os encargos de um fundo de investimento, é correto afirmar que:",
    alternativas:["Incluem livremente qualquer despesa decidida pelo gestor","Seguem um rol taxativo previsto na regulação (custódia, auditoria, CVM, corretagem)","São a mesma coisa que a taxa de administração","Não podem ser debitados do fundo"],
    correta:1,
    explicacao:"Os encargos seguem um rol taxativo (custódia, auditoria, taxa CVM, corretagem etc.), são debitados diretamente do fundo e são distintos da taxa de administração/performance.",
    macete:"Encargos = rol TAXATIVO (lista fechada). Não é 'qualquer despesa' e não se confunde com taxa de adm." }

);
