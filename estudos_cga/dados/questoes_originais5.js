// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 5
//  Temas: Macaulay x modified duration (÷ vs × por (1+YTM)) e
//  duration de título zero-cupom / imunização. Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Renda Fixa",
    enunciado:"Sobre a relação entre Macaulay duration e modified duration, é correto afirmar que a modified é obtida:",
    alternativas:[
      "Multiplicando a Macaulay por (1 + YTM).",
      "Dividindo a Macaulay por (1 + YTM).",
      "Somando o YTM à Macaulay.",
      "Ignorando o YTM, pois ele não afeta a modified."],
    correta:1,
    explicacao:"Modified duration = Macaulay ÷ (1 + YTM). É a conversão do prazo médio (em anos) numa medida de sensibilidade percentual do preço. Por isso a modified SEMPRE depende do YTM.",
    macete:"Modified = Macaulay ÷ (1+YTM). É DIVIDIR, nunca multiplicar. E o YTM sempre entra." },

  { topico:"Renda Fixa",
    enunciado:"Uma equipe precisa padronizar dois conceitos: (i) o prazo médio econômico dos fluxos e (ii) a sensibilidade aproximada do preço a pequenas variações de taxa. A associação correta é:",
    alternativas:[
      "(i) modified duration e (ii) Macaulay duration.",
      "(i) Macaulay duration e (ii) modified duration.",
      "(i) e (ii) são ambos a Macaulay duration.",
      "(i) e (ii) independem do YTM."],
    correta:1,
    explicacao:"Macaulay mede o prazo médio ponderado dos fluxos (em anos); modified mede a sensibilidade percentual do preço a variações de taxa. A modified se relaciona ao YTM (modified = Macaulay ÷ (1+YTM)).",
    macete:"Macaulay = TEMPO (anos). Modified = SENSIBILIDADE (%). Não troque os papéis." },

  { topico:"Renda Fixa",
    enunciado:"Assinale a alternativa INCORRETA sobre duration:",
    alternativas:[
      "A Macaulay duration é expressa em unidades de tempo (anos).",
      "A modified duration aproxima a variação percentual do preço para pequenas mudanças na taxa.",
      "O YTM não interfere na leitura da modified duration.",
      "A modified duration deriva da Macaulay pela divisão por (1 + YTM)."],
    correta:2,
    explicacao:"A afirmação incorreta é que 'o YTM não interfere': a modified = Macaulay ÷ (1+YTM), portanto o YTM interfere diretamente. As demais estão corretas.",
    macete:"Cuidado com o enunciado 'INCORRETA'. A pegadinha clássica é dizer que o YTM não afeta a modified — afeta, sim." },

  { topico:"Renda Fixa",
    enunciado:"Um investidor está short (vendido) em um título público ZERO-CUPOM de 10 anos. Para imunizar a carteira, o ideal é comprar um papel:",
    alternativas:[
      "De duration de 10 anos, imunizando independentemente de alterações na curva de juros.",
      "Com duration menor que 10 anos se a curva fechar.",
      "Com duration maior que 10 anos se a curva abrir.",
      "De 10 anos, mas apenas se não houver qualquer alteração na curva."],
    correta:0,
    explicacao:"Num título zero-cupom, a duration é sempre igual ao prazo (todo o fluxo está no vencimento) e não varia com a curva. Comprar outro zero-cupom de 10 anos casa a duration de forma perfeita, imunizando independentemente de movimentos na curva.",
    macete:"Zero-cupom: duration = prazo, sempre. Casou o prazo, imunizou — e isso independe da curva." },

  { topico:"Renda Fixa",
    enunciado:"Comparado a um título COM cupom de mesmo prazo, um título ZERO-CUPOM tem duration:",
    alternativas:[
      "Menor, pois antecipa fluxos.",
      "Igual ao seu prazo até o vencimento (a maior possível para aquele prazo).",
      "Sempre igual a 1 ano.",
      "Negativa."],
    correta:1,
    explicacao:"O zero-cupom concentra todo o fluxo no vencimento, então sua duration é igual ao prazo — a máxima para aquele vencimento. Títulos com cupom antecipam parte dos fluxos e têm duration menor que o prazo.",
    macete:"Zero-cupom tem a MAIOR duration para o prazo (= prazo). Cupom antecipa fluxo → duration menor que o prazo." }

);
