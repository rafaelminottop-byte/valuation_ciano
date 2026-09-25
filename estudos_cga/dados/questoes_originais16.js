// ============================================================
//  QUESTÕES ORIGINAIS (autorais) - lote 16
//  Tema: alavancagem em fundos (venda a descoberto) e o contraste
//  com hedge/gestão de liquidez. Escritas do zero.
// ============================================================
window.QUESTOES.push(

  { topico:"Renda Variável",
    enunciado:"Entre as operações de um fundo de investimento, a que MAIS provavelmente configura uma forma de alavancagem é:",
    alternativas:[
      "Realização de operações compromissadas.",
      "Venda a descoberto de ativos.",
      "Contratação de contratos a termo de moeda para proteção cambial.",
      "Compra de títulos públicos federais."],
    correta:1,
    explicacao:"A venda a descoberto cria exposição econômica a um ativo sem possuí-lo, ampliando o risco em relação ao capital próprio — é inerentemente alavancagem. As demais não caracterizam necessariamente alavancagem: compromissadas são gestão de liquidez, o termo de moeda pode ser hedge, e a compra de títulos públicos é simples alocação.",
    macete:"Venda a descoberto = SEMPRE alavancagem (exposição sem ter o ativo). Termo pode ser hedge; compromissada é liquidez." },

  { topico:"Renda Variável",
    enunciado:"Um mesmo contrato a termo de moeda pode ou não ser considerado alavancagem porque:",
    alternativas:[
      "Ele é sempre alavancagem, independentemente do uso.",
      "Depende do uso: como PROTEÇÃO (hedge) reduz risco; como exposição adicional/especulativa, gera alavancagem.",
      "Ele nunca gera alavancagem.",
      "Só gera alavancagem se for de renda fixa."],
    correta:1,
    explicacao:"O termo de moeda pode reduzir risco (hedge de uma exposição existente) ou ampliá-lo (nova exposição especulativa). Por isso não é 'necessariamente' alavancagem — diferente da venda a descoberto, que assume exposição sem possuir o ativo.",
    macete:"Derivativo pode ser hedge OU alavancagem, conforme o uso. Se protege exposição existente, não alavanca." }

);
