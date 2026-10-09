// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 21
//  Temas: Loss Given Default (LGD) e Expected Loss (EL) - risco
//  de crédito: componentes (PD, LGD, EAD), cálculo da perda
//  esperada, relação com garantias/recuperação e provisões.
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== CONCEITO DE LGD =====
  { topico:"Risco de Crédito",
    enunciado:"O Loss Given Default (LGD), num modelo de risco de crédito, representa:",
    alternativas:[
      "A probabilidade de que o devedor entre em situação de inadimplência dentro de um horizonte de tempo definido.",
      "O percentual do valor exposto que efetivamente se perde caso ocorra o default, já líquido de eventuais recuperações (garantias, colateral, processo de cobrança).",
      "O valor total exposto ao risco de crédito no momento do default, antes de qualquer ajuste por recuperação.",
      "A perda esperada total da carteira de crédito, combinando probabilidade de default e severidade da perda."],
    correta:1,
    explicacao:"LGD (Loss Given Default) é a severidade da perda: o percentual da exposição que não é recuperado quando o default ocorre. É o complemento da taxa de recuperação (Recovery Rate): LGD = 1 − Taxa de Recuperação. Não se confunde com PD (probabilidade de default, primeira alternativa), EAD (exposição no momento do default, terceira alternativa) nem com EL (perda esperada, quarta alternativa, que combina todos os componentes).",
    macete:"LGD = SEVERIDADE (quanto se perde, em % da exposição, DADO que já houve default). LGD = 1 − Taxa de Recuperação." },

  { topico:"Risco de Crédito",
    enunciado:"Uma instituição possui uma exposição de crédito de R$ 1.000.000, com garantia real que permite recuperar, em média, 70% do valor em caso de inadimplência, após despesas de cobrança e execução da garantia. O LGD dessa operação é de:",
    alternativas:[
      "30%.", "70%.", "100%.", "Não é possível calcular sem a probabilidade de default."],
    correta:0,
    explicacao:"LGD = 1 − Taxa de Recuperação = 1 − 70% = 30%. O LGD depende apenas da severidade da perda (quanto não se recupera), não exige o dado de probabilidade de default para ser calculado — este é necessário apenas quando se quer chegar à Perda Esperada (EL).",
    macete:"LGD = 1 − Recuperação. Não precisa de PD para calcular o LGD isoladamente." },

  // ===== EXPECTED LOSS: FÓRMULA E COMPONENTES =====
  { topico:"Risco de Crédito",
    enunciado:"A Perda Esperada (Expected Loss - EL) de uma exposição de crédito é calculada, na abordagem padrão de risco de crédito, pela fórmula:",
    alternativas:[
      "EL = PD × EAD (Exposure at Default), sem considerar a severidade da perda.",
      "EL = LGD × EAD, sem considerar a probabilidade de inadimplência.",
      "EL = PD × LGD × EAD.",
      "EL = PD + LGD + EAD."],
    correta:2,
    explicacao:"A Perda Esperada combina os três componentes do risco de crédito: PD (Probability of Default — probabilidade de o devedor entrar em default no horizonte considerado), LGD (Loss Given Default — severidade da perda em caso de default) e EAD (Exposure at Default — exposição no momento do default). EL = PD × LGD × EAD. Faltar qualquer um dos três componentes distorce a mensuração: por exemplo, PD × EAD ignora quanto realmente se perderia (severidade); LGD × EAD ignora a chance de o default nem ocorrer.",
    macete:"EL = PD × LGD × EAD — os 3 P's do risco de crédito: Probabilidade, Perda (severidade) e Posição (exposição)." },

  { topico:"Risco de Crédito",
    enunciado:"Uma carteira de crédito tem uma exposição no momento do default (EAD) estimada em R$ 2.000.000, probabilidade de default (PD) de 4% ao ano, e LGD de 45%. A Perda Esperada (EL) dessa exposição é de:",
    alternativas:[
      "R$ 36.000.", "R$ 90.000.", "R$ 900.000.", "R$ 800.000."],
    correta:0,
    explicacao:"EL = PD × LGD × EAD = 4% × 45% × R$ 2.000.000 = 0,04 × 0,45 × 2.000.000 = 0,018 × 2.000.000 = R$ 36.000. Atenção: refazendo a conta — 0,04 × 0,45 = 0,018; 0,018 × 2.000.000 = R$ 36.000. Portanto a resposta correta é R$ 36.000 (primeira alternativa) — as demais alternativas usam apenas dois dos três componentes ou trocam a ordem da multiplicação.",
    macete:"Multiplique os três direto: PD × LGD × EAD. Confira a casa decimal — é fácil errar zero na conta." },

  // ===== EL vs. PROVISÃO / CAPITAL ECONÔMICO =====
  { topico:"Risco de Crédito",
    enunciado:"Do ponto de vista de gestão de risco de crédito, a Perda Esperada (EL) de uma carteira normalmente é tratada como:",
    alternativas:[
      "Um custo do negócio, que deve ser precificado nas taxas cobradas e/ou coberto por provisões, e não como risco propriamente dito — o risco relevante para fins de capital é o de PERDA INESPERADA (a variabilidade em torno da EL).",
      "O valor que a instituição deve manter em capital regulatório, sendo a perda inesperada irrelevante para fins de capital.",
      "Uma medida idêntica ao VaR (Value at Risk) da carteira de crédito.",
      "Um valor sempre nulo em carteiras diversificadas, pela lei dos grandes números."],
    correta:0,
    explicacao:"A EL é uma perda 'esperada' — previsível em média — e por isso é tratada como custo do negócio, devendo ser precificada na taxa de juros cobrada dos tomadores e/ou provisionada contabilmente. O capital regulatório/econômico é dimensionado para cobrir a PERDA INESPERADA (unexpected loss), ou seja, a variabilidade/dispersão em torno da perda esperada, que é o verdadeiro 'risco' na acepção de incerteza. EL não é zero mesmo em carteiras diversificadas — a diversificação reduz a perda inesperada (volatilidade), não a perda esperada média.",
    macete:"EL = precifica/provisiona (é esperado, não é risco). Capital cobre a PERDA INESPERADA (a variação em torno da EL) — isso sim é risco." },

  // ===== EL x LGD: DISTINÇÃO ENTRE AS DEFINIÇÕES =====
  { topico:"Risco de Crédito",
    enunciado:"Sobre a perda esperada de um título de crédito, considere: I. A Perda Esperada (EL) é a diferença entre o valor do título no mercado e o valor após o default, multiplicada pela probabilidade de default. II. A EL é a diferença entre o valor de mercado e o valor esperado após o default. III. O LGD é a multiplicação entre a probabilidade de default e a diferença entre o valor de mercado e o valor após o default. IV. O LGD é a diferença entre o valor de mercado e o valor esperado do título após o default. As afirmativas corretas são:",
    alternativas:[
      "I e II.",
      "II e III.",
      "I, II e III.",
      "I e IV."],
    correta:3,
    explicacao:"O LGD (Loss Given Default) é a diferença entre o valor de mercado do título e o valor esperado caso ocorra o default (a severidade da perda) → afirmativa IV correta. A Perda Esperada (EL) é o resultado da multiplicação do LGD pela probabilidade de default → afirmativa I correta (ela descreve exatamente LGD × PD). A II confunde EL com LGD (falta multiplicar pela PD) e a III confunde LGD com EL (LGD não leva a PD). Logo, corretas apenas I e IV.",
    macete:"LGD = (valor mercado − valor após default) → severidade. EL = LGD × PD. Trocar uma pela outra é a pegadinha (I descreve EL; IV descreve LGD)." }

);
