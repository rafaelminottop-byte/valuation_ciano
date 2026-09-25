// ============================================================
//  TEMAS DIVERSOS — Fé Católica
//  Como adicionar: copie um bloco { ... } e edite.
//    categoria -> agrupa e filtra (ex.: "Sacramentos", "Oração")
//    titulo    -> nome do tema
//    resumo    -> uma frase que aparece em destaque
//    corpo     -> array de parágrafos (cada item = um parágrafo)
//    tags      -> palavras-chave para a busca
// ============================================================

window.TEMAS = [

  // ===================== SACRAMENTOS =====================
  {
    categoria: "Sacramentos",
    titulo: "Os 7 sacramentos",
    resumo: "Sinais eficazes da graça, instituídos por Cristo e confiados à Igreja.",
    corpo: [
      "A Igreja reconhece sete sacramentos, agrupados em três conjuntos. Iniciação cristã: Batismo, Confirmação (Crisma) e Eucaristia. Cura: Penitência (Confissão) e Unção dos Enfermos. Serviço à comunhão: Ordem e Matrimônio.",
      "Cada sacramento é um 'sinal sensível' (água, óleo, pão, palavras) que produz aquilo que significa: comunica a graça de Deus. Por isso se diz que agem 'ex opere operato' — pela própria ação realizada, e não pela santidade de quem os ministra.",
      "Batismo, Confirmação e Ordem imprimem um 'caráter' (marca espiritual permanente) e por isso não se repetem."
    ],
    tags: ["sacramentos", "batismo", "crisma", "confirmação", "eucaristia", "confissão", "penitência", "unção", "ordem", "matrimônio", "graça"]
  },
  {
    categoria: "Sacramentos",
    titulo: "Eucaristia: fonte e ápice",
    resumo: "'Fonte e ápice de toda a vida cristã' (Lumen Gentium 11).",
    corpo: [
      "Na Eucaristia, pela consagração, o pão e o vinho tornam-se verdadeiramente o Corpo e o Sangue de Cristo — mudança que a Igreja chama de transubstanciação: a substância muda, permanecendo as aparências (espécies) de pão e vinho.",
      "É ao mesmo tempo sacrifício (torna presente o único sacrifício da Cruz), presença real e banquete de comunhão. Recomenda-se estar em graça de Deus para comungar; havendo pecado grave, confessa-se antes.",
      "A Missa se estrutura em duas grandes partes: a Liturgia da Palavra e a Liturgia Eucarística."
    ],
    tags: ["eucaristia", "missa", "comunhão", "transubstanciação", "presença real", "sacrifício", "hóstia"]
  },

  // ===================== ORAÇÃO =====================
  {
    categoria: "Oração",
    titulo: "As formas de oração",
    resumo: "Adoração, contrição, ação de graças e súplica — a alma que fala com Deus.",
    corpo: [
      "A tradição distingue quatro finalidades clássicas da oração, lembradas pela sigla ACTS: Adoração (louvar a Deus por ser quem é), Contrição (pedir perdão), Ação de graças (agradecer) e Súplica (pedir).",
      "Quanto ao modo, há a oração vocal (com palavras, como o Pai-Nosso), a meditação (refletir sobre a Palavra, típica do terço e da leitura orante — Lectio Divina) e a contemplação (permanecer em silêncio no amor de Deus).",
      "O próprio Jesus ensinou o modelo de toda oração: o Pai-Nosso, chamado por Tertuliano 'o resumo de todo o Evangelho'."
    ],
    tags: ["oração", "adoração", "contrição", "ação de graças", "súplica", "meditação", "contemplação", "lectio divina"]
  },
  {
    categoria: "Oração",
    titulo: "O Santo Terço",
    resumo: "Meditar a vida de Cristo com Maria, mistério a mistério.",
    corpo: [
      "O terço percorre 20 mistérios divididos em quatro grupos: Gozosos (encarnação e infância), Luminosos (vida pública de Jesus), Dolorosos (paixão e morte) e Gloriosos (ressurreição e glória).",
      "Cada dezena (10 Ave-Marias, com um Pai-Nosso e um Glória) acompanha um mistério, que se procura contemplar enquanto se reza. Não é repetição vazia: as palavras embalam a mente para meditar a cena evangélica.",
      "Tradição dos dias: Gozosos (segunda e sábado), Dolorosos (terça e sexta), Gloriosos (quarta e domingo), Luminosos (quinta)."
    ],
    tags: ["terço", "rosário", "maria", "mistérios", "gozosos", "luminosos", "dolorosos", "gloriosos", "ave-maria"]
  },

  // ===================== ANO LITÚRGICO =====================
  {
    categoria: "Ano Litúrgico",
    titulo: "Os tempos e as cores",
    resumo: "O calendário da Igreja reza a vida de Cristo ao longo do ano.",
    corpo: [
      "O ano litúrgico tem: Advento (preparação para o Natal), Natal, Tempo Comum, Quaresma (preparação para a Páscoa), Tríduo Pascal e Páscoa (que se estende até Pentecostes).",
      "As cores dos paramentos indicam o tempo: roxo (Advento e Quaresma — penitência e espera), branco/dourado (festas de Cristo, Maria e santos não mártires — alegria), vermelho (Espírito Santo, Paixão e mártires — sangue e fogo), verde (Tempo Comum — esperança).",
      "O ano começa no primeiro domingo do Advento, não em 1º de janeiro."
    ],
    tags: ["ano litúrgico", "advento", "quaresma", "páscoa", "pentecostes", "cores", "roxo", "branco", "vermelho", "verde", "tempo comum"]
  },

  // ===================== DOUTRINA =====================
  {
    categoria: "Doutrina",
    titulo: "As virtudes teologais",
    resumo: "Fé, Esperança e Caridade — infundidas por Deus, orientam a alma para Ele.",
    corpo: [
      "As virtudes teologais têm Deus por origem, motivo e objeto direto. Fé: crer em Deus e em tudo o que Ele revelou. Esperança: desejar o Céu e confiar na ajuda da graça. Caridade: amar a Deus sobre todas as coisas e ao próximo por amor a Deus.",
      "São Paulo as reúne: 'Agora permanecem estas três: a fé, a esperança e a caridade. A maior delas, porém, é a caridade' (1Cor 13,13).",
      "Distinguem-se das quatro virtudes cardeais (prudência, justiça, fortaleza e temperança), que se adquirem pelo esforço humano ajudado pela graça."
    ],
    tags: ["virtudes", "teologais", "fé", "esperança", "caridade", "cardeais", "prudência", "justiça", "fortaleza", "temperança"]
  }

];
