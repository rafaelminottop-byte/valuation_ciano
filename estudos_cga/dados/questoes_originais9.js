// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 9
//  Tema: cálculo do retorno excedente (portfólio x benchmark),
//  base da atribuição de desempenho. Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Performance e Risco",
    enunciado:"Uma carteira tem 50% em Renda Variável (retorno 10%) e 50% em Renda Fixa (retorno 4%). O benchmark tem 40% em RV (retorno 9%) e 60% em RF (retorno 5%). O retorno EXCEDENTE da carteira é:",
    alternativas:["1,40%","0,60%","2,00%","0,40%"],
    correta:3,
    explicacao:"Carteira = 0,50×10% + 0,50×4% = 5% + 2% = 7,0%. Benchmark = 0,40×9% + 0,60×5% = 3,6% + 3,0% = 6,6%. Excedente = 7,0% − 6,6% = 0,40%. Cada lado usa os seus próprios pesos.",
    macete:"Cada lado com SEUS pesos: some (peso×retorno) no portfólio e no benchmark, depois subtraia." },

  { topico:"Performance e Risco",
    enunciado:"Um portfólio aloca 60% em ações (retorno 12%), 30% em renda fixa (retorno 6%) e 10% em caixa (retorno 1%). O benchmark aloca 50% em ações (retorno 10%), 40% em renda fixa (retorno 7%) e 10% em caixa (retorno 1%). O retorno excedente do portfólio é:",
    alternativas:["1,20%","0,90%","2,10%","0,30%"],
    correta:0,
    explicacao:"Portfólio = 0,60×12% + 0,30×6% + 0,10×1% = 7,2% + 1,8% + 0,1% = 9,1%. Benchmark = 0,50×10% + 0,40×7% + 0,10×1% = 5,0% + 2,8% + 0,1% = 7,9%. Excedente = 9,1% − 7,9% = 1,20%.",
    macete:"Monte os dois retornos totais (média ponderada com os pesos de cada lado) e subtraia. Não misture pesos." },

  { topico:"Performance e Risco",
    enunciado:"No cálculo do retorno excedente para atribuição de desempenho, o erro mais comum é:",
    alternativas:[
      "Usar os pesos do benchmark também para o retorno do portfólio (misturar os pesos).",
      "Somar os retornos sem ponderar por peso.",
      "Aplicar a média ponderada corretamente em cada lado.",
      "Subtrair o retorno do portfólio do benchmark na ordem certa."],
    correta:0,
    explicacao:"O erro clássico é misturar os pesos: cada lado (portfólio e benchmark) deve usar os SEUS próprios pesos. Usar o peso de um com o retorno do outro gera os distratores típicos da questão.",
    macete:"Retorno excedente = R(portfólio, pesos do portfólio) − R(benchmark, pesos do benchmark). Nunca cruze os pesos." },

  // ===== SELEÇÃO DE GESTORES: UNIVERSO INICIAL =====
  { topico:"Performance e Risco",
    enunciado:"Na etapa INICIAL de seleção de gestores para um mandato de renda variável, o objetivo é delimitar de forma ampla quais profissionais poderiam, em tese, cumprir o papel definido no portfólio, deixando análises mais aprofundadas de adequação e comparação para fases posteriores. Ao definir esse universo inicial de gestores viáveis com base no estilo, o processo deve EVITAR:",
    alternativas:[
      "excluir gestores com baixo desempenho ajustado ao risco.",
      "identificar o benchmark de referência.",
      "utilizar classificações de terceiros para encontrar gestores que possam atender ao mandato.",
      "identificar os fatores de risco por meio da análise dos retornos."],
    correta:0,
    explicacao:"Na etapa inicial o foco é CONSTRUIR um universo amplo de gestores potenciais compatíveis com o estilo/papel no portfólio, SEM ainda filtrar por histórico de performance — isso é refinamento de fases posteriores. Identificar o benchmark é essencial para definir o papel do gestor; usar classificações de terceiros é forma eficiente de compor o universo inicial; e a análise dos retornos ajuda a avaliar fatores de risco e estilo. Portanto, EXCLUIR gestores por desempenho ajustado ao risco já nesta etapa ampla é o que se deve evitar (é prematuro).",
    macete:"Universo inicial de gestores = amplo, por estilo/papel. Filtrar por performance ajustada ao risco vem DEPOIS — fazer isso na largada é o erro." },

  // ===== ÍNDICE M² (MODIGLIANI) - CÁLCULO =====
  { topico:"Performance e Risco",
    enunciado:"Uma carteira tem Índice de Sharpe igual a 1,2, com taxa livre de risco de 3% ao ano e desvio-padrão da carteira de mercado de 12%. Qual é o Índice M² (de Modigliani) dessa carteira?",
    alternativas:[
      "12,0%.",
      "15,0%.",
      "17,4%.",
      "20,4%."],
    correta:2,
    explicacao:"O M² (Modigliani) traduz o Sharpe numa escala percentual comparável à do mercado: M² = Rf + (Sharpe × σ do mercado). Como a expressão entre colchetes do M² é o próprio Índice de Sharpe: M² = 3% + (1,2 × 12%) = 3% + 14,4% = 17,4%.",
    macete:"M² = Rf + Sharpe × σ(mercado). Aqui: 3% + 1,2×12% = 17,4%. É o Sharpe 'vestido' de retorno percentual." },

  // ===== IR x SHARPE x M² (distinção entre as medidas) =====
  { topico:"Performance e Risco",
    enunciado:"Sobre indicadores de performance, considere: I. O Information Ratio é o índice ideal quando se deseja comparar determinado investimento a um benchmark. II. O Índice de Sharpe considera o risco TOTAL da carteira. III. O índice M² do ativo A pode ser calculado como: [E(Rc) − Rf] / σ. Está correto o que se afirma apenas em:",
    alternativas:[
      "I e II.",
      "II e III.",
      "I e III.",
      "III."],
    correta:0,
    explicacao:"I (correta): o Information Ratio = retorno ativo / risco ativo (Rport − Rbench) / TE — é a medida própria para comparar com um benchmark. II (correta): o Sharpe usa o desvio-padrão no denominador, ou seja, risco TOTAL. III (errada): a fórmula [E(Rc) − Rf]/σ é a do ÍNDICE DE SHARPE, não do M². O M² é Rf + Sharpe × σ(mercado). Logo, apenas I e II estão corretas.",
    macete:"IR → compara com benchmark (risco ativo). Sharpe → risco TOTAL (σ). Cuidado: [E(Rc)−Rf]/σ é Sharpe, NÃO M² (M² = Rf + Sharpe×σmercado)." },

  // ===== ATRIBUIÇÃO DE DESEMPENHO: EFEITO SETORIAL (ALOCAÇÃO) =====
  { topico:"Performance e Risco",
    enunciado:"Atribuição de desempenho de um Fundo Multimercado, por grupo (setor). Grupo 1: peso do fundo 62,5%, peso do benchmark 50,0%, retorno do setor no benchmark 8,64%. Grupo 2: 25,0% / 33,3% / 5,92%. Grupo 3: 12,5% / 16,7% / 2,47%. Qual o retorno adicional gerado pela ATRIBUIÇÃO SETORIAL (efeito alocação)?",
    alternativas:[
      "0,485%.",
      "0,600%.",
      "0,291%.",
      "0,578%."],
    correta:0,
    explicacao:"Retorno total do benchmark = 0,50×8,64 + 0,333×5,92 + 0,167×2,47 ≈ 6,705%. Efeito setorial = Σ (peso_fundo − peso_benchmark) × (retorno_setorial_benchmark − retorno_total_benchmark) = (0,625−0,500)×(8,64−6,705) + (0,250−0,333)×(5,92−6,705) + (0,125−0,167)×(2,47−6,705) ≈ 0,242 + 0,065 + 0,178 = 0,485%. Esse efeito mede só a decisão de ALOCAÇÃO entre grupos (não a escolha de papéis dentro de cada grupo).",
    macete:"Efeito alocação = Σ (peso fundo − peso bench) × (retorno do setor no bench − retorno total do bench). Usa retornos do BENCHMARK, não do fundo." },

  // ===== BENCHMARK CUSTOMIZADO (CARTEIRA MULTI-CLASSE) =====
  { topico:"Performance e Risco",
    enunciado:"Um gestor administra um fundo multimercado que investe predominantemente em ações de empresas com boas práticas ESG e mantém parcela relevante da carteira em crédito privado. Para refletir adequadamente a estratégia e a composição do fundo, o benchmark mais adequado é:",
    alternativas:[
      "o Ibovespa.",
      "o IMA-B 5.",
      "o Índice de Sustentabilidade Empresarial (ISE).",
      "um benchmark customizado."],
    correta:3,
    explicacao:"Como o fundo tem exposição relevante a DUAS classes distintas (ações ESG e crédito privado), nenhum índice isolado representa bem a estratégia: o Ibovespa só captura ações amplas, o IMA-B 5 só títulos públicos indexados à inflação e o ISE só ações ESG. O correto é um benchmark CUSTOMIZADO, combinando indicadores representativos de cada classe presente na carteira.",
    macete:"Carteira multi-classe → nenhum índice único serve. Benchmark customizado = mistura de índices ponderada pela composição real." },

  // ===== VaR PARAMÉTRICO - CÁLCULO (99%, horizonte) =====
  { topico:"Estatística e Risco",
    enunciado:"Uma posição concentrada vale R$ 3.000.000, com desvio-padrão diário dos retornos de 5%, horizonte de 5 dias úteis e nível de confiança de 99% (fator de confiança 2,58). Qual o Value at Risk (VaR) dessa posição?",
    alternativas:[
      "R$ 134.720,00.",
      "R$ 177.340,00.",
      "R$ 657.400,26.",
      "R$ 865.358,31."],
    correta:3,
    explicacao:"VaR = valor × (Z × σ_diário × √dias) = 3.000.000 × (2,58 × 0,05 × √5) = 3.000.000 × (2,58 × 0,05 × 2,2361) ≈ 3.000.000 × 0,28845 = R$ 865.358,31. O √5 (não o 5) é o que escala o risco para o horizonte de 5 dias.",
    macete:"VaR = Valor × Z × σ × √dias. 99% → Z = 2,58. Não esqueça a RAIZ dos dias (√5, não 5)." },

  // ===== CPPI: CÁLCULO DO PISO (FLOOR) =====
  { topico:"Renda Variável",
    enunciado:"Um investidor quer preservar um patamar mínimo de patrimônio mesmo em estresse do mercado acionário, mantendo parte em renda variável (estratégia CPPI). O portfólio vale R$ 150.000,00, com metade em ações e metade em ativos livres de risco, e o coeficiente (multiplicador m) da regra de rebalanceamento é 1,5. O valor mínimo (piso) da carteira será de:",
    alternativas:[
      "R$ 50.000,00.",
      "R$ 75.000,00.",
      "R$ 100.000,00.",
      "R$ 225.000,00."],
    correta:2,
    explicacao:"No CPPI (Constant Proportion Portfolio Insurance): Exposição em ações = m × (Total de Ativos − Piso). As ações valem metade de R$ 150.000 = R$ 75.000. Então 75.000 = 1,5 × (150.000 − Piso) → 150.000 − Piso = 50.000 → Piso = R$ 100.000,00. O piso é o nível a partir do qual a exposição a risco cai a zero.",
    macete:"CPPI: Ações = m × (Total − Piso). Isola o Piso: Piso = Total − (Ações/m) = 150.000 − 75.000/1,5 = 100.000." },

  // ===== GESTÃO NEUTRA (MARKET NEUTRAL / LONG-SHORT) =====
  { topico:"Renda Variável",
    enunciado:"Um gestor estrutura uma estratégia sem assumir posição direcional em relação ao mercado: monta a carteira com posições compradas e vendidas em ativos correlacionados, de forma que o resultado dependa principalmente da DIFERENÇA de desempenho entre os ativos, e não do movimento geral do mercado. Essa gestão é denominada:",
    alternativas:[
      "neutra.",
      "agnóstica.",
      "passiva.",
      "ativa."],
    correta:0,
    explicacao:"A gestão NEUTRA (market neutral) busca reduzir/eliminar a exposição direcional ao mercado, combinando posições compradas e vendidas para que o retorno venha da diferença entre os ativos (alfa), não da direção do mercado (beta ≈ 0). A passiva replica um índice; a ativa busca superar um benchmark com decisões discricionárias; a agnóstica é flexível, sem viés predefinido de setores/estilos.",
    macete:"Neutra = long/short com beta ~0: ganha na DIFERENÇA entre ativos, não na direção do mercado. Passiva = replica; ativa = bate o índice." },

  // ===== ANÁLISE TÉCNICA: SINAL LOCALIZADO (NÚCLEO x SATÉLITE) =====
  { topico:"Renda Variável",
    enunciado:"Fundo multimercado: núcleo indexado ao MSCI World (ainda acima da MM50) e satélite tático de small caps referenciado ao Russell 2000. O Russell 2000 perdeu suporte, fechou ABAIXO da MM50 e teve aumento de volume na queda; o VIX subiu. A política exige exposição próxima ao benchmark. A decisão de alocação deve:",
    alternativas:[
      "reduzir a exposição do satélite de small caps, pois o sinal técnico negativo ficou concentrado na sua referência operacional (Russell 2000).",
      "reduzir o núcleo indexado ao MSCI World, pois a alta do VIX antecipa a deterioração global antes da perda da MM50.",
      "substituir o satélite de small caps por ETF do Nasdaq 100, pois empresas maiores reduzem o risco capturado pela alta do VIX.",
      "zerar a exposição global em renda variável, pois a perda de suporte no Russell 2000 confirma que o VIX já se transmitiu ao mercado amplo."],
    correta:0,
    explicacao:"O sinal técnico negativo (perda de suporte, fechamento abaixo da MM50 e volume alto na queda) está LOCALIZADO na referência do satélite (Russell 2000) — logo, a resposta disciplinada é reduzir o satélite de small caps. A alta do VIX reflete maior volatilidade esperada nas opções do S&P 500, mas não substitui a leitura técnica do MSCI World (ainda acima da MM50) nem autoriza, sozinha, mexer no núcleo. Trocar por Nasdaq 100 apenas desloca o problema; zerar a RV global transforma um sinal localizado em decisão ampla sem confirmação técnica equivalente no núcleo.",
    macete:"Sinal técnico localizado → resposta localizada. Russell abaixo da MM50 = corta o satélite small caps. VIX subindo não é motivo para mexer no núcleo ainda saudável." },

  // ===== SAR PARABÓLICO / STOP MÓVEL + AJUSTE DE BETA =====
  { topico:"Renda Variável",
    enunciado:"Uma classe multimercado mantém sobrepeso em uma ação do índice de referência (financiado por caixa) e usa o SAR Parabólico como stop móvel da posição comprada. Após alta prolongada, o ativo fecha ABAIXO do nível do SAR e também abaixo da MM20. A política exige manter a exposição direcional próxima ao benchmark e permite usar futuro do índice para ajuste de beta. A execução que preserva disciplina técnica e risco relativo é:",
    alternativas:[
      "vender a ação sinalizada pelo SAR, recompondo a exposição direcional com futuro do índice para preservar o beta do mandato.",
      "manter a ação até o rebalanceamento periódico, evitando transformar o acionamento do stop em aumento de tracking error.",
      "inverter a posição na ação, pois o SAR indicou Stop-and-Reverse e o fechamento abaixo da MM20 confirmou a virada.",
      "vender a ação e manter o caixa, pois o disparo do stop móvel invalida a recomposição de beta até novo sinal de compra."],
    correta:0,
    explicacao:"O stop móvel deve RETIRAR o risco específico da posição que perdeu o parâmetro técnico (a ação), mas isso NÃO significa reduzir a exposição direcional da classe, que a política exige próxima ao benchmark. Logo: vende-se a ação sinalizada pelo SAR (disciplina técnica) e recompõe-se o beta com FUTURO DO ÍNDICE (mantém a exposição ampla autorizada). Manter a ação subordina o stop ao receio de tracking error; inverter extrapola o SAR e muda a natureza do mandato; manter caixa confunde um stop específico com redução ampla de risco de renda variável.",
    macete:"Stop técnico tira a AÇÃO (risco específico), mas o beta do mandato se mantém com FUTURO do índice. Vender sem recompor beta = mudar o mandato sem querer." }

);
