// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 15
//  Temas: TWRR x MWRR (cálculo e interpretação do timing) e
//  VaR com escala temporal (regra da raiz do tempo). Do zero.
// ============================================================
window.QUESTOES.push(

  // ===== TWRR x MWRR =====
  { topico:"Performance e Risco",
    enunciado:"Um ativo rende, em três períodos consecutivos, +10%, +10% e −8%. O Retorno Ponderado no Tempo (TWRR) acumulado é aproximadamente:",
    alternativas:["+12,0%","+11,3%","+12,2%","−8,0%"],
    correta:1,
    explicacao:"TWRR encadeia os retornos: (1,10)(1,10)(0,92) − 1 = 1,1132 − 1 ≈ 11,3%. Ignora aportes/resgates, medindo o desempenho do ativo/gestor.",
    macete:"TWRR = multiplica os (1+retorno) de cada período e subtrai 1. Ignora fluxos do investidor." },

  { topico:"Performance e Risco",
    enunciado:"Ao comparar o desempenho de um fundo, verificou-se que o MWRR (retorno ponderado pelo dinheiro) do investidor ficou ABAIXO do TWRR do fundo. A interpretação correta é:",
    alternativas:[
      "O gestor teve desempenho ruim no período.",
      "O timing dos fluxos de caixa do investidor foi desfavorável (aportou mais antes de períodos ruins).",
      "O investidor teve timing favorável.",
      "TWRR e MWRR são sempre iguais."],
    correta:1,
    explicacao:"MWRR < TWRR indica que o timing dos aportes/resgates do investidor prejudicou seu resultado (mais capital exposto nos piores momentos). O TWRR mede o gestor; o MWRR mede a experiência do investidor. MWRR > TWRR indicaria timing favorável.",
    macete:"MWRR < TWRR → timing RUIM do investidor. MWRR > TWRR → timing BOM. TWRR = gestor; MWRR = investidor." },

  { topico:"Performance e Risco",
    enunciado:"Qual medida de retorno é a mais adequada para avaliar a HABILIDADE do gestor, isolando o efeito de aportes e resgates feitos pelo investidor?",
    alternativas:[
      "MWRR (retorno ponderado pelo dinheiro / TIR)",
      "TWRR (retorno ponderado pelo tempo)",
      "Current yield",
      "Retorno nominal simples"],
    correta:1,
    explicacao:"O TWRR encadeia os retornos entre fluxos de caixa, isolando o efeito de aportes/resgates que o gestor não controla — por isso é o mais adequado para avaliar o gestor. O MWRR (TIR) reflete a experiência do investidor.",
    macete:"Avaliar GESTOR = TWRR (isola fluxos). Avaliar experiência do INVESTIDOR = MWRR (TIR)." },

  // ===== VaR COM ESCALA TEMPORAL =====
  { topico:"Estatística e Risco",
    enunciado:"O VaR diário de uma carteira é R$ 20.000. Assumindo retornos independentes, o VaR para 16 dias úteis é aproximadamente:",
    alternativas:["R$ 320.000","R$ 80.000","R$ 5.000","R$ 20.000"],
    correta:1,
    explicacao:"VaR escala pela raiz do tempo: VaR(t) = VaR_diário × √t = 20.000 × √16 = 20.000 × 4 = R$ 80.000. Multiplicar por 16 (R$ 320.000) é o erro clássico de usar t em vez de √t.",
    macete:"VaR(período) = VaR_diário × √t. Para 16 dias: ×4 (não ×16). Sempre RAIZ do tempo." },

  { topico:"Estatística e Risco",
    enunciado:"Calcule o VaR mensal (21 dias úteis) de 99% (Z = 2,33) de uma carteira de R$ 2.000.000, cujo desvio-padrão diário dos retornos é 1,5%:",
    alternativas:["R$ 69.900","R$ 320.310","R$ 1.466.100","R$ 15.255"],
    correta:1,
    explicacao:"VaR = Z × σ × √t × Valor = 2,33 × 0,015 × √21 × 2.000.000. √21 ≈ 4,583. 2,33 × 0,015 = 0,03495; × 4,583 ≈ 0,16017; × 2.000.000 ≈ R$ 320.310. O VaR diário (sem √t) seria ~R$ 69.900 (distrator).",
    macete:"VaR = Z × σ × √t × Valor. Monte na ordem e não esqueça o √t (aqui √21 ≈ 4,58)." }

);
