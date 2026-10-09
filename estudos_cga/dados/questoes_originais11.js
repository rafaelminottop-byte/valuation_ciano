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
    macete:"Esqueceu o quadrado do Δy? O resultado 'encolhe' (120 vira 1,20). Sempre Δy² no denominador." },

  // ===== DEFINIÇÃO DE STRIPS =====
  { topico:"Renda Fixa",
    enunciado:"As STRIPS são definidas como:",
    alternativas:[
      "títulos negociáveis e zero cupom emitidos pelo governo.",
      "títulos negociáveis e zero cupom emitidos por instituições financeiras.",
      "recibos negociáveis e emitidos por instituições financeiras que dão direito a uma fração de um título emitido pelo governo.",
      "recibos não negociáveis emitidos por instituições financeiras que dão direito a um pagamento de principal e de juros de um título emitido pelo governo."],
    correta:2,
    explicacao:"STRIPS são RECIBOS, ou seja, não são títulos de crédito em si, mas instrumentos que dão direito a um ativo (ou fração de ativo) depositado em um custodiante. São emitidos por INSTITUIÇÕES FINANCEIRAS (não pelo governo) e são NEGOCIÁVEIS. Cada STRIP dá direito a uma fração (um fluxo isolado) de um título emitido pelo governo. 'Não negociáveis' (alt. D) e 'emitidos pelo governo' (alt. A) são os erros clássicos.",
    macete:"STRIPS = recibo negociável, emitido por instituição financeira, sobre uma fração de um título do governo. Não é o governo que emite, e SÃO negociáveis." },

  // ===== REPO (REPURCHASE AGREEMENT) =====
  { topico:"Renda Fixa",
    enunciado:"Sobre os Repurchase Agreements (Repos), considere as afirmativas: I. O vendedor recompra os títulos em uma data posterior. II. O valor da recompra deve ser menor que o valor original da venda. III. Equivale a uma venda à vista combinada com uma opção de compra. Está correto apenas o que se afirma em:",
    alternativas:[
      "I.",
      "I e II.",
      "III.",
      "I, II e III."],
    correta:0,
    explicacao:"I (correta): o Repo é um acordo em que o vendedor recompra os títulos em data posterior — financiamento de posição lastreado em títulos. II (errada): o valor de recompra é MAIOR que o da venda, pois a diferença embute os juros da operação (a taxa de repo). III (errada): o Repo é um COMPROMISSO firme de recompra (obrigação), não uma opção; portanto equivale a uma venda à vista combinada com um CONTRATO A TERMO, não com uma opção de compra.",
    macete:"Repo: recompra em data futura (I ✓), por valor MAIOR (juros embutidos), e é compromisso firme = venda à vista + termo (não opção)." },

  // ===== TIPS (TREASURY INFLATION-PROTECTED SECURITIES) =====
  { topico:"Renda Fixa",
    enunciado:"Sobre os TIPS (Treasury Inflation-Protected Securities), considere as afirmativas: I. O principal varia anualmente. II. A taxa de cupom é fixa. III. Se houver deflação, o principal é protegido e tem como trava o valor de face do título. Está correto o que se afirma apenas em:",
    alternativas:[
      "I e II.",
      "II e III.",
      "III.",
      "I, II e III."],
    correta:1,
    explicacao:"I (errada): o principal dos TIPS é corrigido DIARIAMENTE, com base na taxa diária do índice CPI-U — não anualmente. II (correta): os TIPS pagam cupom a uma taxa FIXA; o valor do cupom em dólares varia porque incide sobre o principal corrigido, mas a TAXA é fixa. III (correta): no vencimento, o investidor recebe o maior valor entre o principal corrigido pelo CPI-U e o valor de face original — essa trava protege contra deflação.",
    macete:"TIPS: principal corrigido DIÁRIO pelo CPI-U (não anual), cupom de taxa FIXA, e no vencimento paga o MAIOR entre corrigido e valor de face (trava anti-deflação)." },

  // ===== STRIP DE PRINCIPAL x NOTE INTEIRA (casamento de fluxo) =====
  { topico:"Renda Fixa",
    enunciado:"Uma instituição tem um único desembolso previsto para daqui a 10 anos, sem pagamentos intermediários. Pode comprar uma Treasury Note inteira (10 anos, cupom semestral) ou instrumentos oriundos de Treasury STRIPS, alinhando a escolha ao fluxo do passivo. A carteira será marcada a mercado até o vencimento. A recomendação deve indicar que:",
    alternativas:[
      "priorizar a Treasury Note inteira; a conversão gera 20 instrumentos de cupom e 1 de principal, e os cupons antes do passivo podem ser reinvestidos para compor o valor do desembolso.",
      "priorizar o strip de principal; a conversão gera 20 instrumentos de cupom e 1 de principal, e a ausência de cupons intermediários reduz reinvestimento, sem afastar o risco de preço.",
      "priorizar o strip de principal; a conversão gera 10 instrumentos de cupom e 1 de principal, e a ausência de cupons intermediários reduz reinvestimento, sem afastar o risco de preço.",
      "priorizar a Treasury Note inteira; a conversão gera 10 instrumentos de cupom e 1 de principal, e os cupons antes do passivo podem ser reinvestidos para compor o valor do desembolso."],
    correta:1,
    explicacao:"Como o passivo é ÚNICO e não há pagamentos intermediários, o ideal é o STRIP DE PRINCIPAL com vencimento casado ao desembolso: um zero-cupom com fluxo único na data certa, evitando cupons antes da hora e a necessidade de reinvesti-los (risco de reinvestimento). A Note de 10 anos tem cupons SEMESTRAIS, então sua conversão gera 10×2 = 20 strips de cupom + 1 de principal (21 no total) — por isso '10 instrumentos de cupom' está errado. Atenção: o strip de principal reduz reinvestimento, mas NÃO elimina o risco de PREÇO, pois a carteira segue marcada a mercado até o vencimento.",
    macete:"Passivo único e distante → strip de PRINCIPAL casado (zero-cupom, sem reinvestimento). Note 10 anos semestral = 20 cupons + 1 principal. Reduz reinvestimento, mas o risco de preço (MaM) continua." },

  // ===== ESTRATÉGIA DE CURVA: FLATTENING (achatamento) =====
  { topico:"Renda Fixa",
    enunciado:"Com o fim próximo dos estímulos do Fed, um gestor prevê a seguinte movimentação da curva de juros americana: as taxas dos vértices curtos/intermediários (2 a 10 anos) SOBEM, enquanto a taxa do vértice longo (30 anos) CAI — ou seja, a curva se achata. Para obter vantagem com esse cenário, a estratégia e a negociação do gestor deverão ser:",
    alternativas:[
      "flattening, comprando títulos de 2-10 anos e vendendo títulos de 30 anos.",
      "flattening, vendendo títulos de 2-10 anos e comprando títulos de 30 anos.",
      "steepening, comprando títulos de 2-10 anos e vendendo títulos de 30 anos.",
      "steepening, vendendo títulos de 2-10 anos e comprando títulos de 30 anos."],
    correta:1,
    explicacao:"A curva achatando (flattening) = juros curtos/médios SOBEM e o juro longo CAI. Como preço e taxa andam em sentidos opostos: nos títulos de 2-10 anos a taxa sobe → preço CAI → o gestor deve VENDER (ou ficar vendido) nesses vértices; no título de 30 anos a taxa cai → preço SOBE → o gestor deve COMPRAR o longo. Logo: estratégia de flattening, vendendo 2-10 anos e comprando 30 anos.",
    macete:"Flattening = curto sobe, longo cai. Preço anda ao contrário da taxa: VENDE o que a taxa sobe (2-10a) e COMPRA o que a taxa cai (30a)." },

  // ===== BEAR STEEPENING: BULLET x BARBELL (imunização, mesmo passivo) =====
  { topico:"Renda Fixa",
    enunciado:"Três carteiras imunizadas para o MESMO passivo de vencimento único são comparadas: (I) concentrada no entorno do prazo do compromisso (bullet); (II) distribuída ao longo da curva (ladder); (III) combina posições curtas e longas com baixa presença no intermediário (barbell). Cenário: taxas sobem +10 pb no vértice curto, +35 pb no intermediário e +90 pb no longo. Qual conclusão deve constar do relatório?",
    alternativas:[
      "Bear steepening; a alta mais intensa no vértice longo prejudica mais a carteira com maior exposição a esse prazo, favorecendo a estrutura concentrada no entorno do passivo (bullet).",
      "Bear steepening; a alta mais intensa no vértice longo favorece a estrutura de posições curtas e longas (barbell), em razão de sua maior convexidade.",
      "Bull steepening; a alta menos intensa no vértice curto favorece a estrutura concentrada no entorno do passivo, por reduzir a exposição aos vencimentos longos.",
      "Bull steepening; a alta mais intensa no vértice longo favorece a barbell, pois a maior convexidade prevalece sobre o efeito duration."],
    correta:0,
    explicacao:"Taxas SOBEM em todos os vértices (logo é 'bear'), com alta mais forte no longo → a inclinação aumenta → BEAR STEEPENING ('bull' é incompatível com alta de juros). Em movimentos de MUDANÇA DE INCLINAÇÃO (não paralelos), o efeito DURATION predomina sobre a convexidade, porque a variação do vértice longo tem impacto maior no preço. Entre carteiras imunizadas para o mesmo passivo, a BULLET (concentrada no prazo do compromisso) tem melhor desempenho relativo, por ter menor exposição ao vértice longo que a barbell. A maior convexidade da barbell não compensa num movimento não paralelo com alta mais forte nas taxas longas.",
    macete:"Juros sobem + longo sobe mais = BEAR STEEPENING. Em movimento não paralelo, duration manda (não a convexidade). Bullet > barbell quando o longo é o mais castigado." },

  // ===== SPREAD DURATION x DURATION (efeito de preço combinado) =====
  { topico:"Renda Fixa",
    enunciado:"Carteira Global Income: 40% em Treasury Note (duration modificada 6,0) e 60% em high-yield bond (duration modificada 4,0 e spread duration 5,0). Cenário: a curva do Tesouro cai 50 pb (paralela) e o spread de crédito do high-yield sobe 120 pb, sem default. Qual o efeito de preço aproximado na carteira (antes de cupom e impostos)?",
    alternativas:[
      "Ganho de ~2,40%; a alocação em high-yield deve ser mantida, pois a queda da curva livre de risco explica o efeito do cenário.",
      "Perda de ~1,20%; o spread do high-yield deve ser tratado como o principal fator de risco do cenário, apesar da queda da curva livre de risco.",
      "Perda de ~2,40%; o efeito da abertura de spread deve ser medido sem considerar o ganho de taxa do high-yield.",
      "Perda de ~4,00%; o efeito líquido do high-yield deve ser aplicado integralmente à carteira, sem ponderar pela posição em Treasury Note."],
    correta:1,
    explicacao:"Treasury Note: queda de 50 pb × duration 6,0 = +3,00%. High-yield: a queda de 50 pb na taxa livre de risco × duration 4,0 = +2,00%, mas a abertura de 120 pb no spread × spread duration 5,0 = −6,00% → efeito líquido do HY = −4,00%. Carteira: 0,40 × (+3,00%) + 0,60 × (−4,00%) = +1,20% − 2,40% = −1,20%. Mesmo com a curva caindo, a abertura de spread DOMINA o cenário — por isso é inadequado ler o HY só pela queda de taxa ou pelo current yield.",
    macete:"HY tem DOIS fatores: duration (taxa livre) e spread duration (crédito). Efeito = −ΔTaxa×Dur − ΔSpread×SprDur. Aqui: +3% (TN×40%) e −4% (HY×60%) = −1,20%." },

  // ===== KEY RATE DURATION: 3 CARTEIRAS, MOVIMENTO NÃO PARALELO =====
  { topico:"Renda Fixa",
    enunciado:"Três carteiras com mesmo valor presente e mesma duration agregada (8,0) para um passivo de 8 anos. Key rate durations nos vértices de 2, 8 e 14 anos: Carteira A = 1,0; 6,0; 1,0 (bullet). Carteira B = 2,5; 3,0; 2,5 (ladder). Carteira C = 3,5; 1,0; 3,5 (barbell). Cenário adverso: altas de 10, 30 e 90 pb nos respectivos vértices. A política prioriza a MENOR perda estimada no cenário não paralelo. Qual decisão registrar?",
    alternativas:[
      "Selecionar a Carteira A, pois sua perda estimada é de 2,80%, menor que a de B e C; a vantagem de convexidade da C é mais relevante em deslocamentos paralelos.",
      "Selecionar a Carteira C, pois sua perda estimada é de 3,80% e a maior convexidade dos ativos curtos e longos favorece a carteira no cenário adverso.",
      "Selecionar a Carteira B, pois sua perda estimada é de 3,40% e a distribuição escalonada é a melhor combinação de exposições.",
      "Tratar as três como equivalentes, pois a mesma duration agregada (8,0) permite estimar a perda pelo vértice intermediário, resultando em ~2,40%."],
    correta:0,
    explicacao:"A perda em movimento não paralelo é a soma (key rate duration × variação do vértice). A: 1,0×0,10 + 6,0×0,30 + 1,0×0,90 = 2,80%. B: 2,5×0,10 + 3,0×0,30 + 2,5×0,90 = 3,40%. C: 3,5×0,10 + 1,0×0,30 + 3,5×0,90 = 3,80%. A Carteira A (bullet) tem a MENOR perda porque concentra a sensibilidade no vértice de 8 anos (que subiu só 30 pb) e quase não se expõe ao vértice de 14 anos (que subiu 90 pb). A duration agregada igual NÃO torna as carteiras equivalentes num movimento não paralelo — a distribuição por vértice é que decide.",
    macete:"Movimento não paralelo → perda = Σ (key rate duration × Δvértice). Duration agregada igual não basta. Concentrar longe do vértice que mais sobe (bullet) protege." },

  // ===== DURATION + CONVEXIDADE: ESTIMATIVA DE PREÇO NO ESTRESSE =====
  { topico:"Renda Fixa",
    enunciado:"Carteira Turmalina RF, estresse de alta PARALELA de 200 pb (Δy = 0,02), sem derivativos. Composição atual: 55% Ativo A (duration modificada 4,0; convexidade 30) e 45% Ativo B (duration modificada 8,0; convexidade 110). Uma proposta desloca para 70% A e 30% B. A política prioriza a MENOR perda estimada no cenário de alta. Qual conclusão?",
    alternativas:[
      "Adotar a proposta 70/30, pois a perda estimada cai de 10,28% para 9,32%; a composição atual preserva maior ganho em queda de taxas, mas sofre mais na alta.",
      "Manter a composição atual, pois sua maior convexidade reduz a perda para 9,32%, enquanto a proposta amplia para 10,28%.",
      "Manter a composição atual, pois a perda de 10,28% é compensada pelo maior ganho potencial em cenário de baixa, atendendo à política de menor perda no estresse.",
      "Tratar as composições como equivalentes, pois a redução de duration na proposta compensa a menor convexidade, mantendo a perda próxima de 10,00%."],
    correta:0,
    explicacao:"Efeito de preço ≈ −DurMod×Δy + ½×Convexidade×Δy². Atual: DurMod = 0,55×4,0 + 0,45×8,0 = 5,80; Conv = 0,55×30 + 0,45×110 = 66,0 → ΔP = −5,80×0,02 + 0,5×66×0,02² = −0,116 + 0,0132 = −10,28%. Proposta: DurMod = 0,70×4,0 + 0,30×8,0 = 5,20; Conv = 0,70×30 + 0,30×110 = 54,0 → ΔP = −5,20×0,02 + 0,5×54×0,02² = −0,104 + 0,0108 = −9,32%. A proposta reduz a duration e, com isso, a perda no estresse de alta (de 10,28% para 9,32%). A convexidade maior da atual ajudaria numa QUEDA de taxa, mas a política prioriza a menor perda na ALTA.",
    macete:"ΔP ≈ −DurMod×Δy + ½·Conv·Δy². Menos duration = menos perda na alta. Convexidade só 'salva' na queda — não é o critério quando o cenário prioritário é a alta." }

);
