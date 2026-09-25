// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 18
//  Temas: classe com responsabilidade limitada e PL negativo;
//  ALM x goals-based x asset-only em plano de benefícios.
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== RESPONSABILIDADE LIMITADA + PL NEGATIVO =====
  { topico:"Regulação e Fundos",
    enunciado:"Uma classe com sufixo 'Responsabilidade Limitada' apura patrimônio líquido negativo. O encaminhamento COMPATÍVEL com a responsabilidade limitada é:",
    alternativas:[
      "Convocar assembleia para deliberar aporte proporcional dos cotistas.",
      "Fechar a classe para resgates, cancelar os pedidos pendentes e preparar plano de resolução para deliberação.",
      "Manter resgates em fila e permitir novas subscrições condicionadas à recomposição do patrimônio.",
      "Preservar a amortização já programada enquanto o plano é elaborado."],
    correta:1,
    explicacao:"Com responsabilidade limitada, o cotista não pode ser obrigado a cobrir PL negativo. A conduta é conter as movimentações (fechar resgates, cancelar pendências, suspender amortização e vedar novas subscrições) e elaborar plano de resolução. Forçar aporte viola a responsabilidade limitada; pagar amortização/resgate com PL negativo é incompatível.",
    macete:"Resp. limitada + PL negativo = NÃO cobra aporte. Congela movimentações + plano de resolução. Não paga amortização com PL negativo." },

  // ===== ALM x GOALS-BASED x ASSET-ONLY =====
  { topico:"Regulação e Fundos",
    enunciado:"Uma fundação fechada administra plano de benefícios com superávit atuarial recorrente. Sobre a gestão da carteira, o encaminhamento correto é:",
    alternativas:[
      "Tratar toda a carteira por goals-based, hierarquizando as obrigações como metas.",
      "Manter o Asset-Liability Management (ALM) como matriz da carteira, inclusive para excedentes e reservas, ajustando o orçamento de risco.",
      "Aplicar ALM aos benefícios e goals-based ao excedente, com governança própria e segregada.",
      "Otimizar o excedente por asset-only, deslocando os passivos para condição secundária."],
    correta:1,
    explicacao:"Em plano de benefícios, a carteira existe para honrar passivos atuariais, então o ALM é a matriz de toda a carteira. O superávit não é patrimônio livre: segue sujeito a revisão atuarial, evolução dos pagamentos, contribuições e solvência. O excedente pode ajustar o orçamento de risco, mas não muda a arquitetura da decisão. Segmentar o excedente com governança própria retira patrimônio da governança do plano.",
    macete:"Plano de benefícios = ALM é a matriz. Superávit muda o orçamento de risco, não a arquitetura. Excedente NÃO é patrimônio livre." },

  { topico:"Performance e Risco",
    enunciado:"A principal diferença entre as abordagens ASSET-ONLY e ASSET-LIABILITY MANAGEMENT (ALM) na alocação de ativos é que o ALM:",
    alternativas:[
      "Ignora as obrigações e foca apenas em maximizar o retorno dos ativos.",
      "Considera explicitamente os passivos/obrigações, casando ativos e obrigações (adequado a planos de benefícios e seguradoras).",
      "Só pode ser usado em fundos de ações.",
      "Elimina completamente o risco de mercado."],
    correta:1,
    explicacao:"O ALM gere a carteira em função dos passivos (casamento ativo-obrigação), sendo adequado a planos de benefícios, seguradoras e previdência. O asset-only foca apenas nos ativos (risco-retorno), sem tratar as obrigações como referência central.",
    macete:"ALM = olha os PASSIVOS (casa ativo-obrigação). Asset-only = só os ATIVOS. Plano de benefícios pede ALM." }

);
