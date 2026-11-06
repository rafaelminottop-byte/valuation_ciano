// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 23
//  Bloco OFICIAL mais pesado da prova (15/45) e ponto fraco:
//  Tributação de fundos (come-cotas, tabela regressiva de IR,
//  IOF, FII, ETF, isentos) e Investimentos no Exterior
//  (BDR, ADR, Lei 14.754/2023, offshore, diversificação).
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== TABELA REGRESSIVA DE IR (fundos de longo prazo) =====
  { topico:"Tributação",
    enunciado:"Um investidor resgata cotas de um fundo de RENDA FIXA de longo prazo após mantê-las por 800 dias. Qual a alíquota de Imposto de Renda aplicável sobre o rendimento no resgate?",
    alternativas:["22,5%", "20%", "17,5%", "15%"],
    correta:3,
    explicacao:"A tabela regressiva de IR dos fundos de longo prazo (e da renda fixa em geral) é: até 180 dias 22,5%; de 181 a 360 dias 20%; de 361 a 720 dias 17,5%; ACIMA de 720 dias 15%. Como 800 > 720, a alíquota é a mínima: 15%. Quanto mais tempo aplicado, menor o imposto.",
    macete:"Tabela regressiva: 22,5 / 20 / 17,5 / 15. Vira 15% só DEPOIS de 720 dias (2 anos). Prazo maior = imposto menor." },

  // ===== COME-COTAS: quando tem e alíquota =====
  { topico:"Tributação",
    enunciado:"Sobre o mecanismo de \"come-cotas\" na tributação de fundos de investimento, é correto afirmar que:",
    alternativas:[
      "incide semestralmente (maio e novembro) em fundos de renda fixa, à alíquota de 15% nos de longo prazo e 20% nos de curto prazo.",
      "incide mensalmente sobre todos os fundos, inclusive os de ações.",
      "é cobrado apenas no resgate, substituindo a tabela regressiva.",
      "aplica-se aos fundos de ações à alíquota de 15% a cada semestre."],
    correta:0,
    explicacao:"O come-cotas é a antecipação semestral do IR, no último dia útil de MAIO e NOVEMBRO, pela MENOR alíquota de cada tipo de fundo: 15% nos fundos de longo prazo e 20% nos de curto prazo. No resgate, completa-se o imposto conforme a tabela regressiva. FUNDOS DE AÇÕES NÃO TÊM come-cotas (só pagam 15% no resgate).",
    macete:"Come-cotas = antecipação em maio e novembro: 15% (LP) / 20% (CP). Fundo de AÇÕES não tem come-cotas." },

  // ===== FUNDO DE AÇÕES: tributação =====
  { topico:"Tributação",
    enunciado:"Um Fundo de Investimento em Ações (mínimo de 67% da carteira em ações) tem tributação de IR caracterizada por:",
    alternativas:[
      "15% sobre o rendimento, apenas no resgate, sem come-cotas.",
      "tabela regressiva de 22,5% a 15%, conforme o prazo.",
      "come-cotas de 20% em maio e novembro.",
      "isenção total de IR para pessoa física."],
    correta:0,
    explicacao:"O fundo de ações tem tributação simples: alíquota única de 15% sobre o rendimento, cobrada SOMENTE no resgate, sem come-cotas e sem tabela regressiva. É uma das vantagens tributárias desse tipo de fundo — o imposto não é antecipado semestralmente.",
    macete:"Fundo de AÇÕES: 15% fixo, só no resgate, sem come-cotas. Simples assim." },

  // ===== IOF regressivo (<30 dias) =====
  { topico:"Tributação",
    enunciado:"Um investidor aplica em um fundo de renda fixa e resgata em 20 dias. Além do IR, sobre esse resgate incide:",
    alternativas:[
      "IOF regressivo, que vai de 96% a 0% do rendimento e zera a partir do 30º dia.",
      "IOF fixo de 0,38% sobre o valor aplicado.",
      "nenhum tributo além do IR.",
      "IOF de 20% sobre o rendimento, independentemente do prazo."],
    correta:0,
    explicacao:"O IOF incide sobre resgates em MENOS de 30 dias, por tabela regressiva que começa em 96% do rendimento (1 dia) e cai até 0% no 30º dia. A partir do 30º dia não há mais IOF — só o IR. O IOF incide ANTES do IR e sobre o rendimento.",
    macete:"IOF 'morde' só nos primeiros 30 dias (96% → 0%). Passou de 30 dias, zero IOF." },

  // ===== FII: isenção de dividendos PF =====
  { topico:"Tributação",
    enunciado:"Os rendimentos (dividendos) distribuídos por um Fundo de Investimento Imobiliário (FII) a uma pessoa física são ISENTOS de Imposto de Renda, desde que cumpridas condições. Qual condição abaixo é uma delas?",
    alternativas:[
      "O cotista pessoa física não pode deter 10% ou mais das cotas do fundo.",
      "O fundo deve ter menos de 50 cotistas.",
      "O cotista deve manter as cotas por mais de 720 dias.",
      "O fundo não pode ser negociado em bolsa."],
    correta:0,
    explicacao:"A isenção de IR sobre os rendimentos distribuídos de FII à PF exige: (1) cotas negociadas EXCLUSIVAMENTE em bolsa/balcão organizado; (2) fundo com no mínimo 50 cotistas; e (3) o cotista beneficiário NÃO pode deter 10% ou mais das cotas (nem receber 10%+ dos rendimentos). ATENÇÃO: a isenção é só sobre os RENDIMENTOS distribuídos — o GANHO DE CAPITAL na venda das cotas é tributado em 20%.",
    macete:"FII isento p/ PF: ≥50 cotistas, negociado em bolsa, cotista <10%. Mas ganho na VENDA da cota = 20%." },

  // ===== Ativos isentos para PF =====
  { topico:"Tributação",
    enunciado:"Para a pessoa física, qual dos seguintes investimentos tem rendimento ISENTO de Imposto de Renda?",
    alternativas:[
      "Debêntures incentivadas (de infraestrutura), LCI e LCA.",
      "CDB e Tesouro Selic.",
      "Fundo multimercado de longo prazo.",
      "Debêntures comuns (não incentivadas)."],
    correta:0,
    explicacao:"São isentos de IR para a PF: LCI, LCA, CRI, CRA, debêntures INCENTIVADAS (de infraestrutura, Lei 12.431), poupança e dividendos de ações. CDB, Tesouro Direto, fundos comuns e debêntures comuns seguem a tabela regressiva (22,5% a 15%).",
    macete:"Isentos p/ PF: LCI/LCA/CRI/CRA, debênture INCENTIVADA, poupança, dividendo. 'Incentivada' é a palavra-chave." },

  // ===== ETF de ações x ETF de renda fixa =====
  { topico:"Tributação",
    enunciado:"Sobre a tributação de ETFs (fundos de índice) negociados em bolsa, é correto afirmar:",
    alternativas:[
      "O ETF de ações é tributado a 15% no resgate/venda; o ETF de renda fixa segue uma tabela própria por prazo médio (15% a 25%).",
      "Ambos são isentos de IR para pessoa física.",
      "Ambos seguem a mesma tabela regressiva de 22,5% a 15%.",
      "O ETF de ações tem come-cotas semestral de 15%."],
    correta:0,
    explicacao:"O ETF de AÇÕES é tributado a 15% sobre o ganho (no resgate ou venda em bolsa), sem come-cotas. Já o ETF de RENDA FIXA tem tabela própria, baseada no prazo médio da carteira: 25% (até 180 dias), 20% (181 a 720) e 15% (acima de 720) — alíquotas diferentes da tabela dos fundos comuns. Não confundir os dois.",
    macete:"ETF de ações = 15% fixo. ETF de renda fixa = tabela PRÓPRIA (25/20/15) pelo prazo médio. São regimes diferentes." },

  // ===== Fundo de curto x longo prazo (classificação tributária) =====
  { topico:"Tributação",
    enunciado:"A classificação de um fundo como de \"curto prazo\" ou \"longo prazo\", para fins tributários, depende:",
    alternativas:[
      "do prazo médio da carteira de títulos: até 365 dias é curto prazo; acima de 365 dias é longo prazo.",
      "do tempo que o cotista mantém a aplicação.",
      "do patrimônio líquido do fundo.",
      "da classificação ANBIMA do fundo."],
    correta:0,
    explicacao:"A classificação tributária depende do PRAZO MÉDIO da carteira do fundo (não do tempo do cotista): prazo médio igual ou inferior a 365 dias = fundo de CURTO prazo (come-cotas 20%, tabela 22,5%/20%); prazo médio superior a 365 dias = LONGO prazo (come-cotas 15%, tabela 22,5% a 15%). É uma característica do fundo, não do investidor.",
    macete:"Curto x longo prazo = PRAZO MÉDIO DA CARTEIRA (corte em 365 dias), não o tempo do cotista." },

  // ===== INVESTIMENTOS NO EXTERIOR =====

  // ===== BDR =====
  { topico:"Investimentos no Exterior",
    enunciado:"Um BDR (Brazilian Depositary Receipt) é melhor descrito como:",
    alternativas:[
      "um certificado negociado no Brasil que representa valores mobiliários (ações) emitidos por empresas no exterior.",
      "uma ação de empresa brasileira negociada em bolsa dos Estados Unidos.",
      "um título de dívida emitido pelo governo brasileiro no exterior.",
      "um fundo cambial que investe em moedas estrangeiras."],
    correta:0,
    explicacao:"O BDR é um certificado de depósito, negociado na B3, lastreado em valores mobiliários (geralmente ações) emitidos por empresas NO EXTERIOR. Permite ao investidor brasileiro ter exposição a empresas estrangeiras (Apple, Google etc.) sem enviar recursos para fora. O inverso — ação brasileira negociada lá fora — é o ADR (American Depositary Receipt).",
    macete:"BDR = empresa de FORA negociada AQUI. ADR = empresa BR negociada LÁ (EUA). O 'B' do BDR é o país onde se negocia (Brasil)." },

  // ===== ADR =====
  { topico:"Investimentos no Exterior",
    enunciado:"A Petrobras tem recibos de suas ações negociados na Bolsa de Nova York (NYSE). Esses recibos são:",
    alternativas:[
      "ADRs (American Depositary Receipts).",
      "BDRs (Brazilian Depositary Receipts).",
      "ETFs internacionais.",
      "debêntures conversíveis."],
    correta:0,
    explicacao:"Recibos de ações de empresas brasileiras (ou de outros países) negociados em bolsa dos Estados Unidos são ADRs — American Depositary Receipts. É o espelho do BDR: o ADR leva a empresa estrangeira para o mercado americano; o BDR traz a empresa estrangeira para o mercado brasileiro.",
    macete:"ADR = negociado na AMÉRICA (EUA). Empresa BR com ação em NY = ADR. É o inverso do BDR." },

  // ===== Lei 14.754/2023 - aplicações no exterior PF =====
  { topico:"Investimentos no Exterior",
    enunciado:"Desde a Lei 14.754/2023, os rendimentos de aplicações financeiras no exterior detidas diretamente por pessoa física residente no Brasil passaram a ser tributados:",
    alternativas:[
      "a uma alíquota única de 15%, apurados anualmente na Declaração de Ajuste Anual.",
      "pela tabela progressiva do carnê-leão (até 27,5%), mensalmente.",
      "com isenção total, por já serem tributados no país de origem.",
      "pela tabela regressiva de 22,5% a 15%, conforme o prazo."],
    correta:0,
    explicacao:"A Lei 14.754/2023 (vigente a partir de 2024) unificou a tributação das aplicações financeiras no exterior da PF em uma alíquota ÚNICA de 15%, apurada ANUALMENTE na declaração. Antes, dependia do tipo (ganho de capital ou carnê-leão progressivo). A lei também criou a tributação automática anual dos lucros de entidades controladas no exterior (offshore), mesmo sem distribuição.",
    macete:"Lei 14.754/23: aplicação no exterior PF = 15% único, anual. Offshore = tributação anual do lucro mesmo sem distribuir." },

  // ===== Offshore (controlada no exterior) =====
  { topico:"Investimentos no Exterior",
    enunciado:"Sobre as entidades controladas no exterior (\"offshore\") de pessoas físicas, após a Lei 14.754/2023:",
    alternativas:[
      "os lucros passam a ser tributados anualmente a 15%, ainda que não distribuídos ao cotista no Brasil.",
      "continuam tributados apenas quando o lucro é efetivamente distribuído ao Brasil.",
      "são isentas de tributação no Brasil.",
      "são tributadas pela tabela regressiva conforme o prazo de permanência."],
    correta:0,
    explicacao:"Uma das principais mudanças da Lei 14.754/2023 foi acabar com o diferimento (adiamento) do imposto nas offshore de PF: os lucros apurados passam a ser tributados ANUALMENTE a 15%, mesmo que fiquem retidos na estrutura (sem distribuição ao Brasil). Antes, só se tributava quando o dinheiro voltava — o que permitia adiar o imposto indefinidamente.",
    macete:"Offshore pós-2024: acabou o diferimento. Tributa o lucro todo ano (15%), distribuindo ou não." },

  // ===== Diversificação internacional =====
  { topico:"Investimentos no Exterior",
    enunciado:"O principal benefício de incluir ativos internacionais em uma carteira brasileira, do ponto de vista de gestão de risco, é:",
    alternativas:[
      "reduzir o risco total da carteira pela baixa correlação entre mercados, diversificando o risco específico do país.",
      "eliminar completamente o risco de mercado da carteira.",
      "garantir retorno superior ao mercado doméstico em qualquer cenário.",
      "isentar a carteira de tributação."],
    correta:0,
    explicacao:"A diversificação internacional reduz o risco total porque os mercados de diferentes países não são perfeitamente correlacionados — quando o Brasil vai mal, outros mercados podem ir bem, suavizando a volatilidade da carteira. Diminui a exposição ao risco específico do país (Brasil), mas NÃO elimina o risco de mercado global nem garante retorno superior. Adiciona também a variável do risco cambial.",
    macete:"Exterior diversifica o risco-país (correlação baixa reduz a volatilidade). Não elimina risco de mercado e traz risco cambial junto." },

  // ===== Exposição cambial / hedge =====
  { topico:"Investimentos no Exterior",
    enunciado:"Um fundo que investe em ações nos EUA mas faz HEDGE cambial integral (\"dólar travado\") tem como característica:",
    alternativas:[
      "o retorno depende apenas do desempenho das ações, neutralizando a variação do dólar.",
      "o retorno soma o desempenho das ações mais a variação do dólar.",
      "o investidor fica exposto somente à variação cambial.",
      "a ausência de qualquer risco de mercado."],
    correta:0,
    explicacao:"Com hedge cambial integral, o fundo neutraliza a variação do dólar: o retorno para o cotista reflete basicamente o DESEMPENHO DAS AÇÕES lá fora, sem o efeito da moeda. Num fundo SEM hedge (\"dólar cheio\"), o retorno seria a soma do desempenho das ações MAIS a variação do dólar. O hedge troca a exposição cambial por um custo (o do próprio hedge).",
    macete:"Hedge cambial = tira o dólar da conta (só o ativo conta). Sem hedge = ativo + variação do dólar." }

);
