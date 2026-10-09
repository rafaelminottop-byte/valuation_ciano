// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 20
//  Temas: Resolução CVM 175 (estrutura de classes/subclasses,
//  segregação patrimonial); limites de concentração por emissor
//  e por modalidade de ativo; tipos de fundos (classificação);
//  regras gerais de funcionamento; margem em derivativos.
//  Escritas do zero a partir de conhecimento padrão da CGA.
// ============================================================
window.QUESTOES.push(

  // ===== CVM 175 - ESTRUTURA DE CLASSES E SUBCLASSES =====
  { topico:"Regulação e Fundos",
    enunciado:"Sobre a estrutura de fundos de investimento trazida pela Resolução CVM 175, é correto afirmar que:",
    alternativas:[
      "O fundo deixou de existir como entidade jurídica; cada classe de cotas agora é registrada como um CNPJ próprio e independente.",
      "O fundo é a entidade registrada na CVM (um único CNPJ), podendo conter uma ou mais classes de cotas, e cada classe pode ter subclasses que representam diferentes condições de custo, prazo ou público, sem segregação patrimonial entre subclasses da mesma classe.",
      "Cada classe de cotas responde apenas pelas obrigações de suas próprias subclasses, mas todas as classes de um mesmo fundo compartilham a integralidade do patrimônio entre si.",
      "As subclasses têm patrimônio segregado entre si, mas as classes de um mesmo fundo não têm segregação patrimonial entre elas."],
    correta:1,
    explicacao:"Na CVM 175, o fundo é a entidade (um único CNPJ) e pode ter uma ou mais CLASSES de cotas; cada classe tem segregação patrimonial em relação às demais classes do mesmo fundo (como se fossem 'fundos' distintos para fins de responsabilidade). Dentro de uma classe pode haver SUBCLASSES, que representam variações de custos, prazos ou público-alvo, mas compartilham o mesmo patrimônio da classe (não há segregação patrimonial entre subclasses).",
    macete:"Fundo = 1 CNPJ. Classe = patrimônio segregado entre si. Subclasse = mesmo patrimônio da classe (só varia custo/prazo/público), SEM segregação entre subclasses." },

  { topico:"Regulação e Fundos",
    enunciado:"Um fundo constituído sob a CVM 175 possui uma classe com subclasses 'A' (taxa de administração maior, com remuneração de distribuição embutida) e 'B' (taxa de administração menor, sem remuneração de distribuição). Do ponto de vista patrimonial, o resultado da carteira dessa classe:",
    alternativas:[
      "É apurado separadamente para cada subclasse, pois cada uma tem patrimônio próprio.",
      "É apurado de forma única para a classe (mesma carteira/patrimônio), sendo as diferenças entre subclasses tratadas via taxas e encargos distintos, não por segregação de ativos.",
      "É apurado de forma única para o fundo inteiro, incluindo todas as classes existentes.",
      "Depende de decisão do administrador a cada aniversário do fundo."],
    correta:1,
    explicacao:"Subclasses de uma mesma classe compartilham a mesma carteira de ativos (o mesmo patrimônio); o que difere entre elas são taxas, encargos e condições comerciais (ex.: remuneração de distribuidor embutida na taxa), refletidos no valor da cota de cada subclasse, mas não uma segregação de ativos.",
    macete:"Subclasses = mesma carteira, cotas com preços diferentes por causa de taxas/encargos diferentes. Não existe 'pedaço' de ativo por subclasse." },

  // ===== LIMITES DE CONCENTRAÇÃO POR EMISSOR =====
  { topico:"Regulação e Fundos",
    enunciado:"Em relação aos limites de concentração por emissor aplicáveis a fundos de investimento (regra geral, fora dos casos de exceção previstos na regulação, como fundos exclusivos ou para investidores qualificados/profissionais com regras próprias), o limite de concentração por emissor privado (não estatal) tende a ser:",
    alternativas:[
      "Mais restritivo quando o emissor é o próprio administrador, gestor ou partes a eles relacionadas, do que em relação a emissores não relacionados.",
      "Idêntico independentemente de o emissor ser parte relacionada ao administrador/gestor ou não.",
      "Mais permissivo quando o emissor é parte relacionada ao administrador ou gestor, por já haver relação de confiança.",
      "Inexistente para títulos públicos federais, mas também inexistente para qualquer emissor privado."],
    correta:0,
    explicacao:"A regulação impõe limites mais restritivos de concentração quando o emissor dos ativos é o próprio administrador, gestor, ou partes a eles ligadas, exatamente para mitigar conflito de interesses. Para emissores não relacionados, os limites gerais de concentração por emissor (percentual do PL do fundo) se aplicam, mas de forma menos restritiva do que para partes relacionadas.",
    macete:"Parte relacionada ao administrador/gestor = limite MAIS apertado (conflito de interesse). Título público federal = sem limite de concentração." },

  { topico:"Regulação e Fundos",
    enunciado:"Sobre o limite de concentração por MODALIDADE de ativo financeiro (ex.: limites para aplicação em cotas de fundos, em ativos no exterior, em determinadas classes de risco), é correto afirmar que esse tipo de limite:",
    alternativas:[
      "Controla o percentual do PL do fundo que pode estar alocado em determinado TIPO/categoria de ativo, independentemente de quantos emissores distintos compõem essa posição.",
      "É equivalente ao limite de concentração por emissor, apenas com nome diferente.",
      "Aplica-se somente a fundos de ações, não existindo para fundos de renda fixa ou multimercado.",
      "Não pode ser combinado com o limite de concentração por emissor dentro da mesma carteira."],
    correta:0,
    explicacao:"O limite por modalidade de ativo é uma dimensão distinta do limite por emissor: ele restringe o percentual do patrimônio que pode estar em determinada categoria/modalidade de ativo (por exemplo, cotas de outros fundos, ativos no exterior, ativos de determinado risco de crédito), independentemente de estar concentrado em um único emissor ou pulverizado entre vários. Os dois limites (por emissor e por modalidade) coexistem e se aplicam simultaneamente à mesma carteira.",
    macete:"Por emissor = quanto num único nome. Por modalidade = quanto naquele TIPO de ativo (fundos, exterior, etc.), somando todos os emissores daquele tipo. Os dois valem ao mesmo tempo." },

  // ===== TIPOS DE FUNDOS (CLASSIFICAÇÃO) =====
  { topico:"Regulação e Fundos",
    enunciado:"Considerando a classificação dos fundos de investimento quanto à composição da carteira (renda fixa, ações, multimercado e cambial), um fundo que deve manter, no mínimo, 80% da carteira em ativos relacionados diretamente ou sintetizados via derivativos ao fator de risco que dá nome à classe (ex.: moeda estrangeira), é classificado como:",
    alternativas:[
      "Fundo de Renda Fixa.",
      "Fundo de Ações.",
      "Fundo Cambial.",
      "Fundo Multimercado."],
    correta:2,
    explicacao:"Fundos Cambiais devem ter no mínimo 80% da carteira em ativos relacionados, direta ou sinteticamente (via derivativos), à variação de preços de moeda estrangeira ou à variação de taxa de juros associada a moedas estrangeiras (cupom cambial). Fundos de Renda Fixa exigem 80% em ativos relacionados a fator de risco de juros/índice de preços; Fundos de Ações exigem 67% em ações/ativos relacionados; Multimercado não tem compromisso de concentração em um único fator de risco, combinando várias classes de ativos.",
    macete:"Renda Fixa e Cambial = mínimo 80% no fator de risco correspondente. Ações = mínimo 67%. Multimercado = sem concentração obrigatória em 1 fator — combina vários." },

  { topico:"Regulação e Fundos",
    enunciado:"Um fundo classificado como 'Ações' deve manter, no mínimo, qual percentual da carteira em ações, bônus/recibos de subscrição, cotas de fundos de ações e BDRs (ou ativos equivalentes), conforme a regra geral de composição dessa classe?",
    alternativas:[
      "50%.",
      "67%.",
      "80%.",
      "95%."],
    correta:1,
    explicacao:"A classe 'Ações' exige o mínimo de 67% do patrimônio líquido em ações à vista, bônus ou recibos de subscrição, certificados de depósito de ações, cotas de fundos de ações/ETFs de ações e BDRs (ou ativos equivalentes representativos desses). Esse limiar (dois terços) é o que diferencia essa classe das demais.",
    macete:"Ações = 67% mínimo (dois terços). É o número mais 'quebrado' da lista — decore separado dos 80% de renda fixa/cambial." },

  // ===== MARGEM EM DERIVATIVOS =====
  { topico:"Derivativos",
    enunciado:"No contexto de operações com derivativos negociados em bolsa (ex.: contratos futuros), a MARGEM DE GARANTIA depositada pelo investidor tem a função principal de:",
    alternativas:[
      "Antecipar o pagamento do prêmio da opção ao vendedor da posição.",
      "Servir como garantia financeira para cobrir eventuais perdas decorrentes de oscilações desfavoráveis na posição, mitigando o risco de inadimplência (risco de contraparte/liquidação).",
      "Substituir o ajuste diário, eliminando a necessidade de liquidação financeira das perdas e ganhos ao longo do contrato.",
      "Ser devolvida integralmente ao investidor apenas no vencimento do contrato, independentemente do resultado das posições."],
    correta:1,
    explicacao:"A margem de garantia é um valor (em dinheiro ou ativos aceitos pela clearing) depositado para cobrir o risco de que o investidor não honre eventuais perdas na posição — ela mitiga o risco de contraparte/liquidação do sistema. Ela NÃO substitui o ajuste diário (que é a liquidação financeira diária dos ganhos/perdas); os dois mecanismos coexistem e se complementam. A margem pode ser movimentada (chamada adicional ou liberação) conforme a exposição de risco da posição varia, não ficando 'travada' até o vencimento.",
    macete:"Margem = garantia contra risco de inadimplência/contraparte. Ajuste diário = liquidação diária de ganhos/perdas. Os dois existem juntos, um não substitui o outro." },

  { topico:"Derivativos",
    enunciado:"Sobre a exigência de margem em operações com derivativos, é correto afirmar que o valor de margem requerido para uma posição:",
    alternativas:[
      "É fixo e igual para todos os ativos-objeto, independentemente da volatilidade histórica ou do risco da posição.",
      "É calculado com base no risco da posição (considerando volatilidade, liquidez e cenários de estresse do ativo-objeto), podendo aumentar em períodos de maior volatilidade de mercado.",
      "Só é exigido em operações de venda (posições vendidas), nunca em posições compradas.",
      "É devolvida ao investidor assim que a posição gera lucro no ajuste diário do dia."],
    correta:1,
    explicacao:"A margem requerida é dimensionada pelo risco da posição — normalmente calculada por metodologias que consideram volatilidade histórica/implícita, liquidez do ativo e cenários de estresse (ex.: metodologias de margem por cenários da clearing). Em momentos de maior volatilidade de mercado, as clearings costumam elevar as exigências de margem para todas as posições sensíveis àquele risco, e não apenas para posições vendidas — posições compradas alavancadas (como em futuros) também exigem margem.",
    macete:"Margem varia com o RISCO (volatilidade/liquidez/estresse), não é valor fixo. Sobe quando o mercado fica mais volátil. Vale para compra e venda de contratos futuros." },

  // ===== FI-INFRA x SUFIXO "CRÉDITO PRIVADO" (denominação e divulgação) =====
  { topico:"Regulação e Fundos",
    enunciado:"Uma classe tipificada como Renda Fixa, com debêntures incentivadas, CRI e cotas de FIDC ligados a infraestrutura, superará 50% do patrimônio em ativos de emissores privados. A denominação preliminar traz 'Investimento em Infraestrutura' e o material destaca a isenção tributária para pessoa física, sem detalhar condições do benefício nem riscos de concentração e liquidez. A providência compatível com a tipificação e a divulgação é:",
    alternativas:[
      "acrescentar o sufixo 'Crédito Privado' à denominação, preservar a expressão 'Investimento em Infraestrutura' e manter o destaque tributário já previsto.",
      "manter a denominação vinculada à infraestrutura, dispensar o sufixo 'Crédito Privado' e revisar o material de divulgação do produto.",
      "tratar a classe como Renda Fixa – Crédito Privado, evidenciar os riscos de concentração e liquidez e dispensar o regime de infraestrutura na denominação.",
      "manter a denominação de infraestrutura e revisar o material, reservando ao regulamento os riscos de concentração e liquidez."],
    correta:1,
    explicacao:"O FI-Infra é DISPENSADO do sufixo 'Crédito Privado', mas deve MANTER a denominação vinculada à infraestrutura (regime próprio). Essa dispensa não elimina o risco de crédito da carteira. Por isso o material de divulgação PRECISA ser revisado: o destaque do benefício tributário tem de vir acompanhado das condições para sua manutenção e dos riscos relevantes (concentração, liquidez). A alternativa D é sedutora, mas erra ao RETIRAR do material de divulgação justamente os riscos que precisam ser evidenciados ao investidor (reservá-los só ao regulamento não basta).",
    macete:"FI-Infra: mantém 'infraestrutura', dispensa 'Crédito Privado' — mas o material de divulgação deve mostrar riscos e condições do benefício fiscal (não esconder no regulamento)." },

  // ===== DISPENSAS DE TAXA DE PERFORMANCE POR PÚBLICO-ALVO (FIF) =====
  { topico:"Regulação e Fundos",
    enunciado:"Uma classe de cotas de Fundo de Investimento Financeiro (FIF) prevê expressamente em seu regulamento as dispensas admitidas em razão do público-alvo. Sobre as dispensas relativas à taxa de performance, é correto afirmar:",
    alternativas:[
      "as classes destinadas exclusivamente a investidores qualificados ficam dispensadas de observar integralmente as regras de cobrança e de método de cálculo da taxa de performance.",
      "as classes destinadas exclusivamente a investidores profissionais ficam dispensadas de observar as regras relativas aos critérios de cobrança e ao método de cálculo da taxa de performance.",
      "as dispensas independem de previsão no regulamento, decorrendo automaticamente do público-alvo da classe.",
      "não há qualquer dispensa em razão do público-alvo, aplicando-se as mesmas regras a todas as classes."],
    correta:1,
    explicacao:"Desde que expressamente previsto no regulamento, as classes/subclasses destinadas EXCLUSIVAMENTE a investidores PROFISSIONAIS ficam dispensadas de observar tanto os critérios de cobrança quanto o método de cálculo da taxa de performance (dispensa ampla). As destinadas a investidores QUALIFICADOS têm dispensa apenas PARCIAL (restrita a alguns critérios) — por isso a alternativa que lhes atribui dispensa integral está errada. As dispensas NÃO são automáticas: dependem de previsão expressa no regulamento. E existe, sim, tratamento distinto conforme o público-alvo.",
    macete:"Taxa de performance: profissional = dispensa AMPLA; qualificado = dispensa PARCIAL. Sempre depende de previsão no regulamento (não é automática)." }

);
