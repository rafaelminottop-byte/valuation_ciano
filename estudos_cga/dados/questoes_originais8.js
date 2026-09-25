// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 8
//  Temas: amostragem estratificada (nº de células x tracking
//  error; limitação da não-correlação entre fatores) e os três
//  componentes da avaliação de desempenho. Escritas do zero.
// ============================================================
window.QUESTOES.push(

  // ===== AMOSTRAGEM ESTRATIFICADA =====
  { topico:"Renda Variável",
    enunciado:"Numa estratégia de amostragem estratificada, aumentar o número de células (estratos) na estrutura tende a produzir, como principal benefício:",
    alternativas:[
      "Aumento do risco de tracking, em troca de flexibilidade.",
      "Redução do risco de tracking (tracking error), pois cada célula fica mais homogênea e representa melhor o índice.",
      "Aumento dos custos de transação como sinal de diversificação.",
      "Eliminação total do risco de mercado."],
    correta:1,
    explicacao:"Mais células deixam cada estrato mais homogêneo e específico, melhorando a representação do índice e reduzindo o desvio de retorno frente ao benchmark (menor tracking error). Custo maior não é 'benefício', e o risco de mercado não é eliminado.",
    macete:"Mais células = mais aderência ao índice = MENOS tracking error. Custo não é benefício." },

  { topico:"Renda Variável",
    enunciado:"A principal limitação CONCEITUAL da amostragem estratificada como método de indexação é que ela:",
    alternativas:[
      "Exige que todas as ações do índice tenham alta liquidez.",
      "Assume, implicitamente, que os fatores de risco (setor, capitalização, P/L) não são correlacionados entre si.",
      "Só pode ser usada em índices de renda fixa.",
      "Garante tracking error igual a zero."],
    correta:1,
    explicacao:"A estratificação trata as células como se as covariâncias entre os fatores fossem nulas — ou seja, supõe fatores não correlacionados, o que não reflete a realidade (há correlação relevante entre eles). Exigir liquidez de todas as ações é característica da full replication, não da amostragem.",
    macete:"Limitação da estratificada = supor fatores NÃO correlacionados (covariância ≈ 0). Liquidez total é problema da full replication." },

  { topico:"Renda Variável",
    enunciado:"Compare os métodos de indexação. A FULL REPLICATION difere da AMOSTRAGEM ESTRATIFICADA principalmente porque:",
    alternativas:[
      "A full replication usa uma carteira menor baseada em fatores.",
      "A full replication compra todos os ativos do índice, exigindo liquidez ampla e incorrendo em custo alto, enquanto a estratificada usa um subconjunto representativo por estratos.",
      "A amostragem estratificada replica o índice com máxima precisão e custo zero.",
      "Ambas eliminam o tracking error."],
    correta:1,
    explicacao:"Full replication compra todos os componentes (máxima precisão, mas custo alto e dependência de liquidez). A estratificada seleciona um subconjunto representativo por células, reduzindo custo com tracking error moderado. A otimização, por sua vez, usa modelos de fatores.",
    macete:"Full replication = compra TUDO (precisa liquidez, custa caro). Estratificada = amostra por células (custo menor, TE moderado)." },

  // ===== TRÊS COMPONENTES DA AVALIAÇÃO DE DESEMPENHO =====
  { topico:"Performance e Risco",
    enunciado:"Os três componentes essenciais de um sistema completo de avaliação de desempenho de carteiras são:",
    alternativas:[
      "Benchmarking, atribuição de desempenho e avaliação de desempenho.",
      "Medição de desempenho, atribuição de desempenho e avaliação de desempenho.",
      "Medição de desempenho, atribuição de desempenho e controle de risco.",
      "Medição de desempenho, análise de risco e avaliação de desempenho."],
    correta:1,
    explicacao:"São: (1) medição de desempenho (quanto rendeu), (2) atribuição de desempenho (por que rendeu — as fontes/decisões) e (3) avaliação de desempenho (foi habilidade ou sorte — competência do gestor). Benchmarking e controle de risco são apoios/disciplinas relacionadas, não os três pilares.",
    macete:"Os 3 'M-A-A': Medir → Atribuir → Avaliar. 'Benchmarking' ou 'controle de risco' na lista = distrator." },

  { topico:"Performance e Risco",
    enunciado:"Numa avaliação de desempenho, a etapa que busca separar HABILIDADE de SORTE, julgando a competência do gestor, é a:",
    alternativas:[
      "Medição de desempenho","Atribuição de desempenho","Avaliação de desempenho (appraisal)","Marcação a mercado"],
    correta:2,
    explicacao:"A avaliação (appraisal) julga se o resultado veio de habilidade ou acaso, usando medidas ajustadas ao risco e significância estatística. A medição calcula o retorno; a atribuição identifica as fontes/decisões.",
    macete:"Habilidade x sorte = etapa de AVALIAÇÃO (appraisal). Medir = quanto; Atribuir = por quê; Avaliar = skill ou sorte." }

);
