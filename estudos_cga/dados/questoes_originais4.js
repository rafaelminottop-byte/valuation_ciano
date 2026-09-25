// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 4
//  Tema: estruturas de carteira em RF (barbell/ladder/bullet),
//  convexidade e imunização. Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Renda Fixa",
    enunciado:"Três carteiras imunizadas têm a MESMA duration. Diante de movimentos PARALELOS (alta e baixa) nas taxas de juros, a ordem DECRESCENTE de performance esperada é:",
    alternativas:[
      "Barbell, Ladder e Bullet.",
      "Bullet, Ladder e Barbell.",
      "Ladder, Bullet e Barbell.",
      "Bullet, Barbell e Ladder."],
    correta:0,
    explicacao:"Com a mesma duration, quem manda em choque paralelo é a convexidade. Barbell tem a maior convexidade, ladder intermediária e bullet a menor. Maior convexidade = melhor desempenho (cai menos na alta, sobe mais na baixa). Logo: Barbell > Ladder > Bullet.",
    macete:"Choque PARALELO → ganha quem tem mais convexidade: Barbell > Ladder > Bullet." },

  { topico:"Renda Fixa",
    enunciado:"Uma carteira BARBELL, que concentra vencimentos em prazos muito curtos e muito longos, comparada a uma BULLET de mesma duration, apresenta:",
    alternativas:[
      "Menor convexidade","Maior convexidade","Convexidade idêntica","Convexidade negativa"],
    correta:1,
    explicacao:"O barbell 'espalha' os fluxos nos extremos da curva, o que eleva a convexidade em relação ao bullet (concentrado num único ponto). Por isso o barbell tende a se sair melhor em deslocamentos paralelos de taxa.",
    macete:"Barbell = pontas espalhadas = MAIS convexidade que o bullet (concentrado). Ladder fica no meio." },

  { topico:"Renda Fixa",
    enunciado:"A vantagem de convexidade de uma carteira BARBELL sobre uma BULLET de mesma duration é mais confiável quando:",
    alternativas:[
      "A curva de juros muda de inclinação (steepening/flattening)","Os deslocamentos das taxas são paralelos","A curva muda de curvatura","Há default dos emissores"],
    correta:1,
    explicacao:"A superioridade do barbell por convexidade pressupõe deslocamentos PARALELOS da curva. Se a curva muda de inclinação ou curvatura, o bullet pode superar o barbell — a vantagem deixa de ser garantida.",
    macete:"Barbell só é 'garantidamente melhor' em choque PARALELO. Mudou inclinação/curvatura? Bullet pode ganhar." },

  { topico:"Renda Fixa",
    enunciado:"Uma carteira LADDER (escada), com vencimentos distribuídos uniformemente ao longo da curva, tem como característica principal:",
    alternativas:[
      "Concentrar todo o risco num único vértice","Distribuir vencimentos de forma uniforme, facilitando o reinvestimento gradual e diluindo o risco de reinvestimento",
      "Eliminar completamente o risco de crédito","Ter convexidade maior que o barbell"],
    correta:1,
    explicacao:"A ladder distribui os vencimentos uniformemente: a cada período vence uma parcela que é reinvestida, diluindo o risco de reinvestimento e o timing de taxa. Sua convexidade fica entre a do bullet (menor) e a do barbell (maior).",
    macete:"Ladder = escada de vencimentos uniformes → reinvestimento gradual. Convexidade fica ENTRE bullet e barbell." }

);
