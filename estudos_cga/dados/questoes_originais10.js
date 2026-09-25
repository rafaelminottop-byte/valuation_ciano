// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 10
//  Tema: distribuição normal (regra empírica 68-95-99,7) aplicada
//  a tracking error / retornos. Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Estatística e Risco",
    enunciado:"Assumindo que os retornos ativos de uma carteira seguem distribuição normal, o percentual esperado de observações dentro do intervalo de UM desvio-padrão em torno da média é de aproximadamente:",
    alternativas:["68%","95%","99,7%","50%"],
    correta:0,
    explicacao:"Pela regra empírica da normal (68-95-99,7): ±1σ ≈ 68%, ±2σ ≈ 95%, ±3σ ≈ 99,7%. Como o intervalo é de 1 desvio-padrão, a resposta é ≈ 68%. O tracking error é justamente o desvio-padrão do retorno ativo.",
    macete:"68-95-99,7 para 1σ-2σ-3σ. 'Um desvio-padrão' → 68%. O 95% é 2σ (pegadinha)." },

  { topico:"Estatística e Risco",
    enunciado:"Numa distribuição normal, o intervalo que concentra aproximadamente 95% das observações corresponde a:",
    alternativas:["±1 desvio-padrão","±2 desvios-padrão (aprox. 1,96σ)","±3 desvios-padrão","±0,5 desvio-padrão"],
    correta:1,
    explicacao:"Cerca de 95% das observações caem dentro de ±2 desvios-padrão (mais precisamente ±1,96σ) da média. ±1σ cobre ~68% e ±3σ cobre ~99,7%.",
    macete:"95% ≈ ±2σ (exatos 1,96σ). É o número usado em VaR a 95%. Não confunda com 1σ (68%)." },

  { topico:"Estatística e Risco",
    enunciado:"Uma carteira tem tracking error (desvio-padrão do retorno ativo) de 3% ao ano e retorno ativo médio de 1%. Assumindo normalidade, o intervalo que contém cerca de 95% dos retornos ativos é aproximadamente:",
    alternativas:[
      "de −2% a +4% (±1σ)",
      "de −5% a +7% (±2σ)",
      "de −8% a +10% (±3σ)",
      "de 0% a +1%"],
    correta:1,
    explicacao:"95% ≈ ±2σ. Com média 1% e σ = 3%: 1% ± (2×3%) = 1% ± 6% → de −5% a +7%. O intervalo de ±1σ (−2% a +4%) cobre ~68%, e ±3σ (−8% a +10%) cobre ~99,7%.",
    macete:"Monte média ± k·σ. Para 95% use k=2. Aqui: 1% ± 2×3% = −5% a +7%." }

);
