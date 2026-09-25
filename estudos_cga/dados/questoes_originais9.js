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
    macete:"Retorno excedente = R(portfólio, pesos do portfólio) − R(benchmark, pesos do benchmark). Nunca cruze os pesos." }

);
