// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 14
//  Tema: cálculo do Índice M² (Modigliani). Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Performance e Risco",
    enunciado:"Uma carteira tem Índice de Sharpe de 0,8. A taxa livre de risco é 4% e o desvio-padrão do mercado é 15%. O Índice M² (Modigliani) da carteira é:",
    alternativas:["12,0%","16,0%","19,0%","8,0%"],
    correta:1,
    explicacao:"M² = Rf + Sharpe × σ_mercado = 4% + 0,8 × 15% = 4% + 12% = 16%. Traduz o Sharpe numa escala de retorno comparável ao mercado.",
    macete:"M² = Rf + Sharpe × σ_MERCADO. Multiplica pelo desvio do mercado e SOMA o Rf no fim." },

  { topico:"Performance e Risco",
    enunciado:"Um analista calcula Sharpe × σ_mercado = 9% para uma carteira, com taxa livre de risco de 5%. Ao reportar o Índice M², o valor correto é:",
    alternativas:["9,0%","14,0%","5,0%","4,0%"],
    correta:1,
    explicacao:"M² = Rf + (Sharpe × σ_mercado) = 5% + 9% = 14%. O erro comum é reportar apenas os 9% (esquecendo de somar a taxa livre de risco).",
    macete:"Não esqueça de SOMAR o Rf. M² = Rf + Sharpe×σ_mercado; parar em Sharpe×σ_mercado é a pegadinha." },

  { topico:"Performance e Risco",
    enunciado:"Sobre o Índice M² (Modigliani), é correto afirmar que:",
    alternativas:[
      "É expresso em unidades de risco, como o Sharpe.",
      "Expressa o desempenho ajustado ao risco em termos de RETORNO (%), comparável ao mercado, ajustando a carteira à volatilidade do mercado.",
      "Usa o beta no lugar do desvio-padrão.",
      "Ignora a taxa livre de risco."],
    correta:1,
    explicacao:"O M² deriva do Sharpe, mas expressa o resultado em RETORNO percentual (mais intuitivo), ajustando a carteira à mesma volatilidade do mercado. Usa desvio-padrão (não beta) e inclui a taxa livre de risco.",
    macete:"M² = o Sharpe 'traduzido' em % de retorno comparável ao mercado. Usa desvio-padrão, não beta." }

);
