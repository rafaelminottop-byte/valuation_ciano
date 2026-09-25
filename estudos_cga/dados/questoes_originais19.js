// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 19
//  Temas: curva de juros (bull/bear flattener/steepener);
//  atribuição de desempenho (gestão ativa x estilo);
//  atribuição setorial (efeito de alocação - Brinson);
//  prazo de enquadramento de classe aberta de FIF.
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== CURVA DE JUROS: BULL/BEAR x FLATTENER/STEEPENER =====
  { topico:"Renda Fixa",
    enunciado:"Um gestor aposta que as taxas de juros de longo prazo vão aumentar, e que o movimento será acompanhado por uma alta ainda maior nas taxas de curto prazo. O movimento esperado da curva de juros é:",
    alternativas:[
      "Bear flattener, se as taxas de curto prazo aumentarem com maior rapidez.",
      "Bear flattener, se as taxas de curto prazo aumentarem com menor rapidez.",
      "Bull flattener, se as taxas de curto prazo aumentarem com maior rapidez.",
      "Bull flattener, se as taxas de curto prazo aumentarem com menor rapidez."],
    correta:0,
    explicacao:"Na renda fixa, 'bull' = queda de taxas (preço do título sobe) e 'bear' = alta de taxas (preço cai) — convenção oposta à de ações. Como as taxas longas sobem, o cenário é necessariamente 'bear'. 'Flattener' (achatamento) ocorre quando o vértice curto sobe MAIS rápido que o longo, reduzindo o spread longo-curto. Logo: taxas subindo (bear) + curto subindo mais rápido que o longo (flattening) = bear flattener.",
    macete:"Bull = taxa CAI. Bear = taxa SOBE. Flattener = curto anda MAIS que o longo. Steepener = curto anda MENOS (ou cai) vs. o longo." },

  // ===== ATRIBUIÇÃO DE DESEMPENHO: GESTÃO ATIVA x ESTILO =====
  { topico:"Performance e Risco",
    enunciado:"Um patrocinador quer decompor o resultado de uma carteira entre a parcela explicada pela gestão ativa do gestor e a parcela associada ao estilo representado pelo benchmark adotado, usando: Retorno de mercado = 10%; Retorno do portfólio = 13%; Retorno do benchmark = 12,50%. A atribuição de desempenho em relação à gestão ativa e ao estilo foi de, respectivamente:",
    alternativas:[
      "2,50% e 0,50%.",
      "3% e 0,50%.",
      "0,50% e 3%.",
      "0,50% e 2,50%."],
    correta:3,
    explicacao:"Gestão ativa = retorno do portfólio − retorno do benchmark = 13% − 12,50% = 0,50% (o que o gestor agregou além do benchmark). Estilo = retorno do benchmark − retorno de mercado = 12,50% − 10% = 2,50% (o que já vinha da simples exposição ao benchmark/estilo, sem decisão ativa). Confirma-se somando as duas parcelas: 0,50% + 2,50% = 3,00% = portfólio − mercado (o excesso total, não uma parcela isolada).",
    macete:"Gestão ativa = Portfólio − Benchmark. Estilo = Benchmark − Mercado. As duas somadas fecham o excesso total (Portfólio − Mercado)." },

  // ===== ATRIBUIÇÃO SETORIAL (BRINSON - EFEITO DE ALOCAÇÃO) =====
  { topico:"Performance e Risco",
    enunciado:"Num modelo de atribuição de performance (Brinson) que decompõe o retorno adicional de uma carteira por grupos/setores, o efeito de ALOCAÇÃO setorial (sem medir a habilidade de seleção de papéis dentro de cada grupo) é calculado por:",
    alternativas:[
      "Σ [(peso da carteira no setor) × (retorno do setor na carteira − retorno do setor no benchmark)].",
      "Σ [(peso da carteira no setor − peso do benchmark no setor) × (retorno do setor no benchmark − retorno total do benchmark)].",
      "Σ [(peso do benchmark no setor) × (retorno do setor na carteira − retorno total da carteira)].",
      "Σ [(retorno da carteira no setor − retorno do benchmark no setor) × peso do benchmark no setor]."],
    correta:1,
    explicacao:"O efeito de alocação (setorial) isola o impacto de sobre/subponderar um setor frente ao benchmark, SEM misturar o efeito de escolha de papéis dentro do setor. Por isso usa a diferença de PESOS (carteira − benchmark) multiplicada pela diferença entre o retorno do setor NO BENCHMARK e o retorno total do benchmark — sempre usando o retorno setorial do benchmark (nunca da carteira), o que neutraliza o efeito de seleção. Somando a contribuição de todos os setores chega-se ao efeito de alocação total.",
    macete:"Alocação = (peso carteira − peso benchmark) × (retorno SETOR no BENCHMARK − retorno TOTAL do benchmark). Sempre retorno do benchmark, nunca da carteira — isso isola de seleção." },

  // ===== PRAZO DE ENQUADRAMENTO - CLASSE ABERTA DE FIF =====
  { topico:"Regulação e Fundos",
    enunciado:"Na constituição de uma nova classe ABERTA de Fundo de Investimento Financeiro (FIF), o enquadramento da carteira aos limites de concentração por emissor e por modalidade de ativo não precisa ocorrer de forma integral já no primeiro momento de funcionamento. O prazo máximo permitido para que a classe passe a respeitar esses limites é de:",
    alternativas:[
      "180 dias, a contar da data de encerramento da distribuição.",
      "180 dias, a contar da data da primeira integralização de cotas.",
      "60 dias, a contar da data de encerramento da distribuição.",
      "60 dias, a contar da data da primeira integralização de cotas."],
    correta:3,
    explicacao:"As classes de FIF têm prazos máximos distintos conforme o tipo: classes ABERTAS têm 60 dias, a contar da data da primeira integralização de cotas; classes FECHADAS têm 180 dias, a contar da data de encerramento da distribuição. Como o enunciado trata de uma classe aberta, aplica-se a primeira regra.",
    macete:"Aberta = 60 dias da 1ª integralização. Fechada = 180 dias do encerramento da distribuição. Não misture prazo de um tipo com o marco temporal do outro." }

);
