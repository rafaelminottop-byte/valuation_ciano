// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 3
//  Temas: papéis dos prestadores, cotas (CVM 175), política de
//  voto / conflito de interesse, Sharpe x Sortino.
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== PAPÉIS DOS PRESTADORES =====
  { topico:"Regulação e Fundos",
    enunciado:"São atribuições típicas do GESTOR de recursos, EXCETO:",
    alternativas:[
      "Negociar, alocar e ratear ordens de compra e venda entre os veículos de investimento.",
      "Enquadrar a carteira aos limites de investimento previstos na regulação e nos documentos do fundo.",
      "Realizar a controladoria e a precificação (cálculo da cota) dos ativos e passivos do fundo.",
      "Exercer o direito de voto decorrente dos ativos da carteira, conforme a política de voto."],
    correta:2,
    explicacao:"Controladoria de ativos/passivos e cálculo da cota são funções do ADMINISTRADOR (controladoria), não do gestor. O gestor decide e movimenta a carteira: negocia/aloca ordens, enquadra limites e exerce direito de voto.",
    macete:"Gestor DECIDE e MOVE a carteira. Se a alternativa fala em controlar/calcular cota/contabilizar, NÃO é do gestor." },

  { topico:"Regulação e Fundos",
    enunciado:"A guarda dos ativos, a liquidação física e financeira das operações e a conciliação da posição da carteira são responsabilidades do:",
    alternativas:["Gestor","Administrador","Custodiante","Distribuidor"],
    correta:2,
    explicacao:"Essas são funções do custodiante. O gestor toma decisões de investimento; o administrador é o responsável legal perante a CVM e pela controladoria/precificação.",
    macete:"Custodiante = guardar, liquidar e conciliar. Palavra 'guarda dos ativos' → custodiante, sempre." },

  // ===== COTAS (CVM 175) =====
  { topico:"Regulação e Fundos",
    enunciado:"Sobre as cotas de fundos de investimento sob a Resolução CVM 175, assinale a afirmativa correta:",
    alternativas:[
      "O regulamento pode prever que a responsabilidade do cotista seja limitada ao valor de suas cotas.",
      "As cotas conferem apenas direitos, nunca obrigações, aos cotistas.",
      "Cotas de classe fechada não podem, em hipótese alguma, ser cedidas ou negociadas.",
      "Cotas de classe aberta são, em regra, transferidas por negociação em mercado organizado."],
    correta:0,
    explicacao:"Uma novidade da CVM 175 é permitir, se o regulamento previr, a responsabilidade LIMITADA do cotista ao valor das cotas. As cotas conferem direitos E obrigações; a classe fechada não tem resgate e sua saída se dá justamente por cessão/negociação; a classe aberta funciona por aplicação/resgate, não por negociação em mercado.",
    macete:"CVM 175: cotista PODE ter responsabilidade limitada. Cotas dão direitos E obrigações (nunca só direitos)." },

  { topico:"Regulação e Fundos",
    enunciado:"Um investidor precisa se desfazer da posição em um fundo de CLASSE FECHADA antes do término do prazo. A forma adequada é:",
    alternativas:[
      "Solicitar o resgate das cotas a qualquer momento.",
      "Ceder ou negociar as cotas a terceiros (inclusive em mercado, se admitido).",
      "Aguardar obrigatoriamente o vencimento, sem alternativa.",
      "Converter as cotas em cotas de classe aberta automaticamente."],
    correta:1,
    explicacao:"Fundos de classe fechada NÃO admitem resgate durante a vigência; a saída ocorre pela cessão/negociação das cotas. Já a classe aberta é a que permite resgate.",
    macete:"Aberta = resgata (sai pelo fundo). Fechada = negocia/cede (sai pelo mercado). Fechada não tem resgate." },

  // ===== POLÍTICA DE VOTO / CONFLITO DE INTERESSE =====
  { topico:"Regulação e Fundos",
    enunciado:"Conforme a política de exercício de direito de voto exigida pelo Código ANBIMA, o voto do gestor é OBRIGATÓRIO em matérias que envolvam:",
    alternativas:[
      "Ativos de emissor com sede social fora do Brasil.",
      "Certificados de depósito de valores mobiliários (ex.: BDRs).",
      "Situações de conflito de interesses.",
      "Assembleias realizadas em local de difícil acesso ou com custo desproporcional."],
    correta:2,
    explicacao:"Situações de conflito de interesses (e matérias que afetem os direitos dos cotistas) são de voto obrigatório. Ativos estrangeiros, certificados de depósito e casos de custo desproporcional costumam estar entre as hipóteses de dispensa/faculdade.",
    macete:"Voto obrigatório = conflito de interesse ou direito do cotista. Ativo estrangeiro/BDR/custo alto = dispensa." },

  { topico:"Ética e Regulação",
    enunciado:"Uma prática que o Código ANBIMA e a regulação buscam evitar por meio da segregação de atividades (Chinese Wall) e da política de conflito de interesses é:",
    alternativas:[
      "A diversificação de carteiras.",
      "O uso de informação de uma área (ex.: tesouraria) em benefício próprio, em prejuízo dos cotistas.",
      "A marcação a mercado dos ativos.",
      "O cálculo diário da cota."],
    correta:1,
    explicacao:"A barreira de informação e as regras de conflito visam impedir que informações ou interesses de uma área contaminem a gestão de recursos de terceiros em prejuízo dos cotistas. Diversificação, marcação a mercado e cálculo de cota são práticas normais/desejáveis.",
    macete:"Chinese Wall/conflito existem para proteger o COTISTA. A resposta é sempre a que descreve prejuízo ao cliente." },

  // ===== SHARPE x SORTINO =====
  { topico:"Performance e Risco",
    enunciado:"Dois fundos têm Índices de Sharpe semelhantes, mas o Fundo A tem Sortino bem maior que o Fundo B. A explicação técnica mais adequada é:",
    alternativas:[
      "O Sharpe trata toda a variação como risco, enquanto o Sortino desconsidera as oscilações positivas, penalizando apenas o desvio abaixo da meta.",
      "As duas métricas sempre convergem quando o retorno médio supera a taxa livre de risco.",
      "O Sortino ignora a taxa livre de risco no cálculo do excedente.",
      "O Sharpe usa o beta e o Sortino usa o desvio-padrão total."],
    correta:0,
    explicacao:"O Sortino usa apenas o desvio NEGATIVO (abaixo da MAR); o Sharpe usa a volatilidade TOTAL. Um fundo com muita 'vol para cima' e pouca 'vol para baixo' tem Sharpe apenas mediano (a alta infla o risco total) mas Sortino elevado (a alta não é punida). O Sharpe não usa beta (esse é o Treynor).",
    macete:"Sharpe pune tudo; Sortino só pune o downside. Muita alta e pouca queda → Sortino >> Sharpe." },

  { topico:"Performance e Risco",
    enunciado:"Uma carteira apresenta várias altas expressivas e poucas quedas suaves. Comparando as métricas de desempenho ajustado ao risco, é esperado que:",
    alternativas:[
      "O Sortino seja penalizado pelas altas expressivas.",
      "O Sharpe seja relativamente menor que o Sortino, pois a alta volatilidade (mesmo positiva) eleva o risco total.",
      "Sharpe e Sortino sejam necessariamente iguais.",
      "Ambos os índices ignorem as quedas suaves."],
    correta:1,
    explicacao:"Como o Sharpe usa a volatilidade total, as altas expressivas aumentam o desvio-padrão e reduzem o Sharpe. O Sortino, que só olha o downside, não pune essas altas, ficando relativamente maior. O Sortino não é penalizado por retornos positivos.",
    macete:"Retorno positivo NUNCA penaliza o Sortino. Se a alternativa disser que a alta prejudica o Sortino, é falsa." }

);
