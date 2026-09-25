// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 11
//  Temas: contagem de STRIPS (cupons semestrais + principal) e
//  cálculo da convexidade aproximada (pegadinha do Δy²).
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== CONTAGEM DE STRIPS =====
  { topico:"Renda Fixa",
    enunciado:"Um T-Bond norte-americano com vencimento em 30 anos e cupons semestrais será decomposto em STRIPS. Quantos títulos zero-cupom (STRIPS) são necessários para reproduzir integralmente seus fluxos?",
    alternativas:["30","60","61","31"],
    correta:2,
    explicacao:"Cupons semestrais em 30 anos = 30 × 2 = 60 strips de cupom, mais 1 strip do principal = 61. Esquecer o principal leva a 60; assumir cupom anual leva a 31/30.",
    macete:"STRIPS = (anos × 2) cupons + 1 principal. 30 anos → 60 + 1 = 61. Nunca esqueça o '+1'." },

  { topico:"Renda Fixa",
    enunciado:"Uma T-Note de 5 anos, com pagamentos semestrais de cupom, é transformada em STRIPS. O número total de títulos zero-cupom resultantes é:",
    alternativas:["5","10","11","6"],
    correta:2,
    explicacao:"5 anos × 2 cupons por ano = 10 strips de cupom, mais 1 strip do principal = 11 no total.",
    macete:"Semestral: cupons = anos × 2. Some 1 do principal. 5 anos → 10 + 1 = 11." },

  // ===== CONVEXIDADE APROXIMADA =====
  { topico:"Renda Fixa",
    enunciado:"Um título prefixado sem opção embutida tem preço inicial de R$ 1.000,00. Após redução de 100 bps no yield, o preço vai a R$ 1.050,00; após elevação de 100 bps, recua a R$ 962,00. A convexidade aproximada é:",
    alternativas:["12,00","120,00","1,20","88,00"],
    correta:1,
    explicacao:"Convexidade ≈ (P− + P+ − 2·P0) / (P0 · Δy²) = (1.050 + 962 − 2.000) / (1.000 × 0,01²) = 12 / 0,1 = 120. Dividir por Δy (não Δy²) daria 1,20 (pegadinha); a amplitude 1.050−962 = 88 não é convexidade.",
    macete:"Convexidade ≈ (P− + P+ − 2P0) / (P0·Δy²). O pulo do gato é o Δy AO QUADRADO." },

  { topico:"Renda Fixa",
    enunciado:"No cálculo da convexidade aproximada pela sensibilização de preços, o erro mais comum que subestima grosseiramente o resultado é:",
    alternativas:[
      "Usar os dois cenários de choque (queda e alta).",
      "Dividir por Δy em vez de Δy² (esquecer de elevar a variação do yield ao quadrado).",
      "Subtrair duas vezes o preço inicial.",
      "Dividir pelo preço inicial."],
    correta:1,
    explicacao:"A fórmula usa (Δy)² no denominador. Esquecer o quadrado (dividir por Δy) reduz o resultado em um fator enorme — por exemplo, transforma 120 em 1,20. Os demais passos citados estão corretos.",
    macete:"Esqueceu o quadrado do Δy? O resultado 'encolhe' (120 vira 1,20). Sempre Δy² no denominador." }

);
