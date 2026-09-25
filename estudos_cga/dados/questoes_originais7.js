// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 7
//  Tema: VaR (nível de confiança/significância) e VaR x CVaR.
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  { topico:"Estatística e Risco",
    enunciado:"O nível de significância associado a um VaR calculado com 97,5% de confiança é:",
    alternativas:["97,5%","2,5%","95%","1%"],
    correta:1,
    explicacao:"Significância = 1 − nível de confiança = 1 − 0,975 = 2,5%. É a probabilidade de a perda exceder o VaR no horizonte considerado.",
    macete:"Significância = 1 − confiança. Confiança + significância sempre somam 100%." },

  { topico:"Estatística e Risco",
    enunciado:"Sobre a interpretação do nível de confiança do VaR, é correto afirmar que quanto MAIOR o nível de confiança (ex.: passar de 95% para 99%):",
    alternativas:[
      "Menor o valor do VaR, pois considera menos cenários.",
      "Maior o valor do VaR, pois passa a cobrir perdas mais extremas.",
      "O VaR não se altera.",
      "O VaR se torna exato."],
    correta:1,
    explicacao:"Aumentar a confiança (95% → 99%) desloca o corte para a cauda mais extrema da distribuição, elevando o valor do VaR (a perda 'até a qual' você confia é maior). Nível de confiança maior = VaR maior.",
    macete:"Mais confiança → VaR MAIOR (corta mais na cauda). 99% de VaR > 95% de VaR para a mesma carteira." },

  { topico:"Estatística e Risco",
    enunciado:"A principal limitação do VaR, corrigida pelo CVaR (Expected Shortfall), é que o VaR:",
    alternativas:[
      "Não considera a taxa livre de risco.",
      "Não informa o tamanho da perda quando esta excede o próprio VaR.",
      "Só pode ser calculado para ações.",
      "É sempre maior que a perda real."],
    correta:1,
    explicacao:"O VaR diz até quanto se perde com dada confiança, mas NÃO informa a magnitude das perdas na cauda além desse ponto. O CVaR (Expected Shortfall) mede justamente a perda média nos cenários que excedem o VaR.",
    macete:"VaR = 'até quanto' (o limite). CVaR = 'e se passar, quanto em média' (a cauda além do VaR)." },

  { topico:"Estatística e Risco",
    enunciado:"Uma carteira tem VaR de 1 dia a 99% igual a R$ 2 milhões e CVaR (Expected Shortfall) de R$ 3 milhões no mesmo nível. A leitura correta é:",
    alternativas:[
      "Em 99% dos dias a perda será de exatamente R$ 2 milhões.",
      "Nos 1% de piores dias, a perda esperada é de cerca de R$ 3 milhões (média além do VaR).",
      "A perda máxima possível é R$ 3 milhões.",
      "O CVaR é sempre menor que o VaR."],
    correta:1,
    explicacao:"Com 99% de confiança a perda não excede R$ 2 mi (VaR). Nos 1% de piores dias, a perda MÉDIA esperada é o CVaR = R$ 3 mi. O CVaR é, por construção, maior ou igual ao VaR (olha a cauda além dele).",
    macete:"CVaR ≥ VaR sempre. CVaR = perda média nos piores cenários (além do VaR); não é 'perda máxima'." }

);
