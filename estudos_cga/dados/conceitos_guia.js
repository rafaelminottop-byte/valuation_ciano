// ============================================================
//  CONCEITOS DO GUIA DE REVISÃO CGA (Blocos 1 a 4)
//  Estes itens são somados à base de fórmulas (window.FORMULAS).
// ============================================================
window.FORMULAS.push(

  // ===== BLOCO 1 — RENDA VARIÁVEL =====
  { topico:"Renda Variável", titulo:"Estratégias: Passiva × Ativa × Agnóstica (total return)",
    formula:"Passiva → replica | Ativa → alfa | Total return → retorno absoluto",
    descricao:"PASSIVA: replicar benchmark minimizando tracking error e custos (premissa de mercados eficientes). ATIVA: busca retorno acima do benchmark (alfa) via seleção/timing/alocação (existem ineficiências). AGNÓSTICA/TOTAL RETURN: retorno absoluto, independente de benchmark, pode usar long/short e derivativos.",
    tags:["passiva","ativa","agnóstica","total return","alfa","benchmark","estratégia"] },

  { topico:"Renda Variável", titulo:"Fundos de ações indexados",
    formula:"Replicar índice (Ibovespa, IBrX...)",
    descricao:"Buscam replicar o desempenho de um índice. Vantagens: menor custo, transparência e aderência ao mercado. Métrica-chave: tracking error (diferença de retorno entre fundo e índice).",
    tags:["indexado","etf","tracking error","ibovespa","ibrx","passiva"] },

  { topico:"Renda Variável", titulo:"Métodos de indexação (comparação)",
    formula:"Full replication × Amostragem estratificada × Otimização",
    descricao:"FULL REPLICATION: compra todos os ativos nas mesmas proporções — máxima precisão, mas custo alto e difícil com ilíquidos. AMOSTRAGEM ESTRATIFICADA: subconjunto representativo por estratos — reduz custo, tracking error moderado. OTIMIZAÇÃO: modelos de fatores escolhem carteira menor — baixo custo e flexível, mas sujeita a erro de modelo.",
    tags:["full replication","amostragem estratificada","otimização","indexação","tracking error"] },

  { topico:"Renda Variável", titulo:"Long-short e Market Neutral",
    formula:"Compra (long) subavaliados + vende (short) sobrevalorizados",
    descricao:"Lucra com a diferença relativa entre ativos. Quando as posições long e short se equilibram em exposição, é MARKET NEUTRAL: resultado independe da direção do mercado (beta ~0). Long only = apenas posições compradas.",
    tags:["long-short","market neutral","short","venda descoberto","long only"] },

  { topico:"Renda Variável", titulo:"Total Return Equity Swap",
    formula:"Paga retorno total (dividendos + valorização) ↔ recebe taxa (ex.: CDI)",
    descricao:"Contrato em que uma parte paga o retorno total de um ativo/índice e recebe uma taxa fixa/flutuante. Serve para exposição sintética a ações sem deter o ativo, alavancagem, hedge e eficiência tributária/operacional.",
    tags:["total return swap","equity swap","exposição sintética","cdi","derivativo"] },

  { topico:"Renda Variável", titulo:"Estilos de gestão (Value, Growth, Blend)",
    formula:"Value × Growth × Blend/Core (+ large/mid/small cap)",
    descricao:"VALUE: ações baratas frente aos fundamentos. GROWTH: empresas com alto potencial de crescimento. BLEND/CORE: mistura. Recorte adicional por tamanho (large/mid/small cap). O style analysis atribui a performance ao estilo do gestor.",
    tags:["value","growth","blend","core","estilo","large cap","small cap","style analysis"] },

  { topico:"Renda Variável", titulo:"Análise Técnica × Fundamentalista",
    formula:"Preço/volume × Valor intrínseco",
    descricao:"TÉCNICA: foco em padrões de preço/volume históricos (gráficos, indicadores, tendências); premissa de que preços refletem toda informação e se movem em padrões. FUNDAMENTALISTA: foco no valor intrínseco (demonstrações, setor, macro); premissa de que o preço pode divergir do valor justo.",
    tags:["análise técnica","fundamentalista","gráfico","valor intrínseco","tendência"] },

  { topico:"Renda Variável", titulo:"Integração ASG (ESG) no valuation",
    formula:"Ajuste de risco/fluxo de caixa por fatores A-S-G",
    descricao:"Incorpora fatores Ambientais, Sociais e de Governança: maior custo de capital para empresas com riscos ASG altos; ajuste de premissas de crescimento/margens. Abordagens: integração no DCF, exclusão setorial ou best-in-class.",
    tags:["asg","esg","valuation","governança","dcf","best-in-class","exclusão setorial"] },

  { topico:"Renda Variável", titulo:"Classificação por tracking error",
    formula:"Indexação pura → Enhanced → Ativa",
    descricao:"INDEXAÇÃO PURA: TE mínimo, replicar fielmente. INDEXAÇÃO REFORÇADA (enhanced): TE baixo, passiva + pequenos desvios táticos por alfa marginal. GESTÃO ATIVA: TE alto, desvios relevantes buscando alfa significativo.",
    tags:["indexação pura","enhanced indexing","gestão ativa","tracking error","classificação"] },

  { topico:"Renda Variável", titulo:"Ordinárias × Preferenciais (Common × Preferred)",
    formula:"ON: voto | PN: prioridade em dividendos/liquidação",
    descricao:"COMMON (ON): têm voto, dividendos variáveis não garantidos, últimos na fila de liquidação. PREFERRED (PN): geralmente sem voto, dividendos com prioridade (frequentemente fixos), prioridade no reembolso em liquidação.",
    tags:["ordinária","preferencial","common","preferred","voto","dividendo","on","pn"] },

  { topico:"Renda Variável", titulo:"Limitações das medidas de avaliação",
    formula:"Sharpe/alfa/TE não são perfeitos",
    descricao:"Sensíveis ao período; dependem do benchmark escolhido; não capturam risco de cauda; pressupõem normalidade dos retornos; podem sofrer manipulação (window dressing); não isolam sorte de habilidade.",
    tags:["limitações","sharpe","window dressing","risco de cauda","normalidade"] },

  // ===== BLOCO 2 — RENDA FIXA =====
  { topico:"Renda Fixa", titulo:"Imunização de carteiras",
    formula:"Duration(ativos) = Duration(passivos/horizonte)",
    descricao:"Casa a duration entre ativos e passivos (ou horizonte). Protege o valor: o risco de preço é compensado pelo risco de reinvestimento. É a base das estratégias de casamento.",
    tags:["imunização","duration","reinvestimento","casamento","passivo"] },

  { topico:"Renda Fixa", titulo:"Dollar Duration (DV01 / valor monetário)",
    formula:"Sensibilidade em R$ a variação de 100 bps",
    descricao:"Sensibilidade do PREÇO em valor monetário (não percentual) a uma variação de 100 bps na taxa. Uso: somar exposições de instrumentos com valores de mercado diferentes (ex.: montar hedge com derivativos).",
    tags:["dollar duration","dv01","bps","hedge","valor monetário","spread duration"] },

  { topico:"Renda Fixa", titulo:"Cash-flow matching",
    formula:"Fluxos da carteira = obrigações futuras (exato)",
    descricao:"Estratégia de imunização mais conservadora: monta-se carteira cujos fluxos (cupons + principal) coincidem exatamente com as obrigações futuras. Elimina risco de reinvestimento E de taxa.",
    tags:["cash-flow matching","correspondência de fluxo","imunização","conservadora"] },

  { topico:"Renda Fixa", titulo:"Combinações: Contingent immunization & Combination matching",
    formula:"Ativa até um limite → depois imuniza",
    descricao:"CONTINGENT IMMUNIZATION: gestão ativa até um limite de perda pré-definido; ultrapassado, imuniza. COMBINATION MATCHING: parte cash-flow matching + parte imunização clássica.",
    tags:["contingent immunization","combination matching","combinação","imunização"] },

  { topico:"Renda Fixa", titulo:"Swaps de renda fixa",
    formula:"Troca de fluxos: juros (fixa×flutuante), moeda, crédito",
    descricao:"Trocam fluxos de caixa/exposições: swap de taxa de juros (fixa × flutuante), de moeda, de crédito. Usados para alterar duration, fazer hedge ou especular sem negociar o ativo subjacente.",
    tags:["swap","juros","moeda","crédito","duration","hedge"] },

  { topico:"Renda Fixa", titulo:"Formatos da curva de juros",
    formula:"Normal · Invertida · Plana · Humped",
    descricao:"NORMAL/ascendente: longas > curtas (mais comum, prêmio por prazo). INVERTIDA: curtas > longas (sinaliza queda de juros/recessão). PLANA: taxas semelhantes. HUMPED: 'corcova', taxas intermediárias mais altas.",
    tags:["curva","normal","invertida","plana","humped","corcova","ettj"] },

  { topico:"Renda Fixa", titulo:"Teoria da Preferência pela Liquidez",
    formula:"Prêmio por prazo → inclina a curva para cima",
    descricao:"Investidores exigem prêmio para manter títulos mais longos (mais incerteza/risco de mercado). Efeito: inclina naturalmente a curva para cima, independentemente das expectativas de juros futuros.",
    tags:["preferência pela liquidez","prêmio de prazo","estrutura a termo","teoria"] },

  { topico:"Renda Fixa", titulo:"Estratégias na curva: Steepening, Flattening, Butterfly",
    formula:"Aposta em inclinação / achatamento / curvatura",
    descricao:"STEEPENING: aposta que o spread longo-curto aumenta (curva mais inclinada). FLATTENING: aposta que o spread diminui (mais achatada). BUTTERFLY: posições em 3 pontos da curva apostando em mudança de curvatura, neutro ao nível geral.",
    tags:["steepening","flattening","butterfly","curva","spread","curvatura"] },

  { topico:"Renda Fixa", titulo:"Medidas de retorno (yields)",
    formula:"YTW = mín(YTM, YTC, YTP)",
    descricao:"CURRENT YIELD: cupom anual ÷ preço. YTM: TIR de todos os fluxos até o vencimento. YTC: retorno assumindo call na 1ª data. YTP: retorno assumindo exercício da put. YTW: o menor entre YTM/YTC/YTP (mais conservador). YIELD SPREAD: diferença para benchmark de prazo equivalente.",
    tags:["current yield","ytm","ytc","ytp","ytw","yield spread","yield to worst"] },

  { topico:"Renda Fixa", titulo:"Treasuries e STRIPS (EUA)",
    formula:"T-Bill < 1a | T-Note 2-10a | T-Bond >10a | STRIPS = cupom zero",
    descricao:"T-BILL: curtíssimo prazo (até 1 ano), negociado com desconto, sem cupom. T-NOTE: 2 a 10 anos, com cupom. T-BOND: acima de 10 anos, com cupom. STRIPS: separação de cupons e principal em títulos de cupom zero negociados individualmente.",
    tags:["t-bill","t-note","t-bond","strips","treasury","cupom zero","eua"] },

  { topico:"Renda Fixa", titulo:"Commercial Paper e CD (CDB)",
    formula:"CP = dívida curta corporativa | CD = depósito bancário a prazo",
    descricao:"COMMERCIAL PAPER: dívida de curto prazo de empresas não financeiras, sem garantia real, negociada com desconto (capital de giro). CD (Certificate of Deposit): depósito a prazo emitido por bancos; equivalente brasileiro é o CDB.",
    tags:["commercial paper","cd","cdb","depósito a prazo","capital de giro"] },

  { topico:"Renda Fixa", titulo:"Estruturas de títulos",
    formula:"Bullet · Amortizável · Cupom zero · Pós-fixado · Indexado",
    descricao:"BULLET: pagamento único no vencimento. AMORTIZAÇÃO periódica. CUPOM ZERO. Taxa FIXA ou FLUTUANTE (pós-fixada). INDEXADOS a índices de preços.",
    tags:["bullet","amortização","cupom zero","pós-fixado","indexado","estrutura"] },

  { topico:"Renda Fixa", titulo:"Retorno Time-Weighted (TWR)",
    formula:"Encadeia subperíodos entre fluxos de caixa",
    descricao:"Mede a performance do GESTOR isolando o efeito de aportes/resgates. Calculado encadeando os retornos dos subperíodos entre fluxos de caixa. Elimina a distorção do timing de fluxos externos (diferente do money-weighted, que reflete a experiência do investidor).",
    tags:["time-weighted","twr","money-weighted","fluxos externos","performance"] },

  // ===== BLOCO 3 — PERFORMANCE E RISCO =====
  { topico:"Performance e Risco", titulo:"Propriedades de um benchmark válido (7)",
    formula:"SAMURAI-like: especificado, mensurável, não ambíguo...",
    descricao:"Um bom benchmark deve ser: especificado previamente; mensurável; não ambíguo; investível (replicável); apropriado ao estilo; representativo do universo de oportunidades; accountability (o gestor aceita ser avaliado por ele).",
    tags:["benchmark","propriedades","investível","não ambíguo","accountability"] },

  { topico:"Performance e Risco", titulo:"Atribuição Micro de desempenho",
    formula:"Retorno = seleção + alocação setorial + interação",
    descricao:"Decompõe o desempenho frente ao benchmark em: efeito de SELEÇÃO de ativos, efeito de ALOCAÇÃO setorial e efeito de INTERAÇÃO. Modelo de fatores fundamentais atribui retorno a exposições (valor, momento, tamanho, qualidade...).",
    tags:["atribuição","seleção","alocação","interação","fatores","micro"] },

  { topico:"Performance e Risco", titulo:"Atribuição de desempenho em Renda Fixa",
    formula:"Nível + curva + spread + seleção + moeda",
    descricao:"Decompõe o retorno em: efeito de nível de taxa (duration), efeito de formato de curva, efeito de spread de crédito, efeito de seleção de títulos e efeito de moeda (quando aplicável).",
    tags:["atribuição","renda fixa","duration","curva","spread","crédito","moeda"] },

  { topico:"Performance e Risco", titulo:"Medidas ajustadas ao risco (comparação)",
    formula:"Sharpe · Treynor · Jensen · Sortino · Information Ratio",
    descricao:"SHARPE: excedente ÷ desvio-padrão (risco total). TREYNOR: excedente ÷ beta (sistemático). JENSEN (alfa): retorno acima do CAPM. SORTINO: excedente ÷ desvio-padrão negativo (downside). INFORMATION RATIO: retorno ativo ÷ tracking error (risco ativo).",
    tags:["sharpe","treynor","jensen","sortino","information ratio","downside","m2"] },

  { topico:"Performance e Risco", titulo:"Índice M² (M-quadrado / Modigliani)",
    formula:"Retorno da carteira ajustado à volatilidade do mercado",
    descricao:"Deriva do Sharpe: ajusta a carteira à mesma volatilidade do mercado (via mistura com ativo livre de risco) e compara o retorno resultante com o do mercado. Vantagem sobre o Sharpe: resultado em pontos percentuais de retorno, mais intuitivo.",
    tags:["m2","modigliani","sharpe","volatilidade","retorno ajustado"] },

  { topico:"Performance e Risco", titulo:"Tipos de Duration (Macaulay, Modificada, Effective)",
    formula:"Macaulay(anos) · Modificada(% preço) · Effective(opcionalidade)",
    descricao:"MACAULAY: prazo médio ponderado (anos) — conceito-base. MODIFICADA: sensibilidade percentual do preço ao yield — para fluxos fixos. EFFECTIVE: variação de preço em cenários de choque de taxa — para títulos com opcionalidade embutida (ex.: pré-pagamento).",
    tags:["duration","macaulay","modificada","effective","opcionalidade","pré-pagamento"] },

  { topico:"Performance e Risco", titulo:"Derivativos de crédito (CDS, TRS)",
    formula:"CDS: transfere risco de default por prêmio",
    descricao:"CDS (Credit Default Swap): transfere risco de crédito de um ativo de referência mediante prêmio, protege contra default. TOTAL RETURN SWAP de crédito: troca o retorno total de um ativo de crédito por taxa fixa/flutuante. Usos: hedge, especulação, arbitragem de spread.",
    tags:["cds","credit default swap","trs","default","crédito","hedge"] },

  { topico:"Performance e Risco", titulo:"Perda Esperada e LGD",
    formula:"Perda Esperada = PD × LGD × EAD ; LGD = 1 − recuperação",
    descricao:"LGD (Loss Given Default): % da exposição perdido após recuperações (garantias/colaterais). PD = probabilidade de default; EAD = exposição no momento do default. Perda Esperada = PD × LGD × EAD.",
    tags:["lgd","pd","ead","perda esperada","default","recuperação","crédito"] },

  { topico:"Performance e Risco", titulo:"Orçamento de risco (risk budgeting)",
    formula:"Aloca risco tolerável entre estratégias/ativos",
    descricao:"Distribui o 'risco total' tolerável da carteira entre estratégias/ativos/gestores. Define limites de CONTRIBUIÇÃO de risco (não apenas de capital), otimizando a relação risco-retorno.",
    tags:["orçamento de risco","risk budgeting","contribuição de risco","alocação"] },

  { topico:"Performance e Risco", titulo:"Constant Mix × Buy-and-hold × CPPI",
    formula:"Constant Mix = rebalanceia p/ pesos fixos (contrário)",
    descricao:"CONSTANT MIX: mantém proporções fixas (ex.: 60/40), rebalanceando quando desviam — compra o que caiu e vende o que subiu (estratégia contrária/anti-cíclica). Diferente do buy-and-hold (não rebalanceia) e do CPPI (aumenta risco quando sobe).",
    tags:["constant mix","buy and hold","cppi","rebalanceamento","contrária","alocação"] },

  { topico:"Performance e Risco", titulo:"Análise de cenário e stress test",
    formula:"Complementam o VaR",
    descricao:"ANÁLISE DE CENÁRIO simula o desempenho sob condições hipotéticas (choque de juros, crise, alta de commodities). STRESS TEST aplica choques extremos. Ambos complementam o VaR, que não captura bem eventos de cauda.",
    tags:["análise de cenário","stress test","var","choque","cauda"] },

  // ===== BLOCO 4 — REGULAÇÃO E FUNDOS (CVM 175) =====
  { topico:"Regulação e Fundos", titulo:"Obrigações: Administrador, Gestor, Custodiante",
    formula:"Admin (legal) · Gestor (carteira) · Custodiante (ativos)",
    descricao:"ADMINISTRADOR: responsável legal perante a CVM, supervisiona prestadores, compliance geral. GESTOR: decisões de investimento/alocação da carteira. CUSTODIANTE: guarda dos ativos, liquidação de operações, conciliação da posição.",
    tags:["administrador","gestor","custodiante","cvm 175","obrigações","papéis"] },

  { topico:"Regulação e Fundos", titulo:"Fundos de Renda Fixa (limite 80%)",
    formula:"≥ 80% em fator de risco 'renda fixa'",
    descricao:"Mínimo de 80% da carteira em ativos relacionados ao fator de risco renda fixa (juros e/ou índices de preços). Subclassificações: curto prazo, simples, dívida externa, indexados. Fundos de Ações: mín. 67% em ações.",
    tags:["fundo renda fixa","80%","fator de risco","cvm 175","classe"] },

  { topico:"Regulação e Fundos", titulo:"Limites por modalidade e por emissor",
    formula:"Controle de concentração e liquidez",
    descricao:"Regras de concentração (por emissor e por modalidade) e limites de exposição definidos pela Resolução CVM 175 conforme a classe do fundo (Renda Fixa, Ações, Multimercado, Cambial). Objetivo: controlar risco de concentração e liquidez.",
    tags:["limites","emissor","modalidade","concentração","cvm 175"] },

  { topico:"Regulação e Fundos", titulo:"Classes Restritas e Exposição a risco",
    formula:"Restritas = investidor qualificado/profissional",
    descricao:"CLASSES RESTRITAS: exclusivas para investidores qualificados/profissionais, com regras mais flexíveis (ativos elegíveis, concentração, alavancagem). EXPOSIÇÃO A RISCO DE CAPITAL: quanto o fundo pode se expor à variação de ativos de risco, incluindo alavancagem/derivativos, varia por classe e público-alvo.",
    tags:["classes restritas","qualificado","profissional","exposição","alavancagem"] },

  { topico:"Regulação e Fundos", titulo:"Encargos do fundo",
    formula:"Rol taxativo (custódia, auditoria, CVM, corretagem)",
    descricao:"Despesas debitadas diretamente do fundo (custódia, auditoria, taxa CVM, corretagem), DISTINTAS da taxa de administração/performance. Seguem rol taxativo previsto na regulação — não pode debitar o que não estiver na lista.",
    tags:["encargos","despesas","rol taxativo","custódia","auditoria"] },

  { topico:"Regulação e Fundos", titulo:"Tributação de fundos (CVM 175, Anexo I)",
    formula:"LP: 22,5%→15% | CP: 22,5%→20% | Ações: 15% no resgate",
    descricao:"COME-COTAS: IR na fonte semestral (maio e novembro) nos fundos de RF/multimercado. LONGO PRAZO: alíquota regressiva 22,5%→15%. CURTO PRAZO: 22,5%→20%. FUNDOS DE AÇÕES: 15% só no resgate, sem come-cotas. IOF: regressivo para resgates em menos de 30 dias.",
    tags:["tributação","come-cotas","ir","regressiva","fundos de ações","iof","anexo i"] }

);
