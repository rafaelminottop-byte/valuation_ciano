// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 12
//  Tema: diversificação internacional e o papel da correlação
//  na redução do risco da carteira. Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Estatística e Risco",
    enunciado:"Um gestor adiciona ações estrangeiras de risco individual ELEVADO, porém com baixa correlação com o mercado doméstico, a uma carteira de ações locais. O efeito mais provável sobre a carteira é:",
    alternativas:[
      "Aumento do risco total, pois as ações estrangeiras são voláteis.",
      "Redução da dispersão dos retornos (risco total), pela baixa correlação.",
      "Nenhum efeito, pois só o risco individual importa.",
      "Eliminação completa do risco de mercado."],
    correta:1,
    explicacao:"O que reduz o risco de uma carteira é a correlação entre os ativos, não o risco isolado de cada um. Ativos de baixa correlação (como ações estrangeiras) reduzem a variância total mesmo sendo individualmente arriscados. A diversificação não elimina o risco sistemático/de mercado.",
    macete:"O que importa é a CORRELAÇÃO, não o risco isolado do ativo. Baixa correlação → menos dispersão na carteira." },

  { topico:"Estatística e Risco",
    enunciado:"No cálculo da variância de uma carteira de dois ativos (w = peso de cada ativo, σ = desvio-padrão de cada ativo, ρ = correlação entre eles), o termo que captura o benefício da diversificação e depende da correlação (ρ) é:",
    alternativas:[
      "w1²σ1²",
      "2·w1·w2·ρ·σ1·σ2",
      "w2²σ2²",
      "σ1 + σ2"],
    correta:1,
    explicacao:"O termo cruzado 2·w1·w2·ρ·σ1·σ2 depende de ρ: quanto menor a correlação, menor esse termo e menor a variância da carteira. Os termos w1²σ1² e w2²σ2² são as variâncias individuais ponderadas.",
    macete:"O ganho de diversificação está no termo cruzado (com ρ). ρ menor → variância da carteira menor." },

  { topico:"Estatística e Risco",
    enunciado:"Sobre a diversificação internacional, é INCORRETO afirmar que:",
    alternativas:[
      "Ativos estrangeiros costumam ter baixa correlação com o mercado local, reduzindo o risco da carteira.",
      "O risco cambial pode ser um fator adicional a considerar.",
      "Adicionar qualquer ativo estrangeiro sempre elimina o risco sistemático da carteira.",
      "O benefício depende da correlação, não apenas do risco individual do ativo."],
    correta:2,
    explicacao:"A afirmação incorreta é que se 'elimina o risco sistemático': a diversificação reduz o risco específico/total e adiciona, inclusive, um novo fator sistemático estrangeiro (e risco cambial). O risco de mercado não é eliminado por diversificação.",
    macete:"Diversificação NÃO elimina risco sistemático. E atenção: investir fora adiciona risco cambial." }

);
