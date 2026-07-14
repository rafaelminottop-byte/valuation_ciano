"""
Leitura reversa do valuation — "o que o preço de hoje já embute".

Em vez de perguntar "qual o preço justo?", pergunta na ordem inversa:
- ``crescimento_implicito``: fixada a TMA, qual crescimento perpétuo do lucro o
  preço atual embute (modelo de Gordon sobre o LPA).
- ``tma_implicita_lucro``: fixado um crescimento, qual TMA o mercado exige para
  o preço atual, pela ótica do LUCRO (fórmula fechada de Gordon).
- ``tma_implicita_ebit``: idem, mas pela ótica do EBIT (resolvido no motor Ciano
  por bissecção).

A razão ``tma_implicita_ebit / tma_implicita_lucro`` é um detector de
alavancagem: perto de 1, o EBIT pertence ao acionista e as duas óticas
convergem (empresa pouco endividada); muito acima de ~2, a dívida distorce o
EBIT e a leitura por EBIT (e o upside que ela gera) não é confiável — use o lucro.
"""

from valuation_engine import PREMISSAS_PADRAO, calcular_valuation_completo

# Acima desta razão entre as TMAs implícitas, considera-se que a alavancagem
# distorce o método por EBIT (as óticas divergem).
RAZAO_ALAVANCAGEM = 2.0


def crescimento_implicito(preco: float, lpa: float, tma: float) -> float | None:
    """Crescimento perpétuo do lucro embutido no preço (Gordon: P = LPA(1+g)/(TMA-g)).

    Resolve g: g = (P·TMA − LPA) / (P + LPA). Devolve None sem lucro positivo.
    """
    if not preco or preco <= 0 or lpa is None or lpa <= 0:
        return None
    return (preco * tma - lpa) / (preco + lpa)


def tma_implicita_lucro(preco: float, lpa: float, crescimento: float) -> float | None:
    """TMA que o preço implica pela ótica do lucro (Gordon): TMA = LPA(1+g)/P + g."""
    if not preco or preco <= 0 or lpa is None or lpa <= 0:
        return None
    return lpa * (1 + crescimento) / preco + crescimento


def tma_implicita_ebit(
    ebit_por_acao: float,
    preco: float,
    cenario: dict,
    retorno_alvo: float = None,
    tma_max: float = 6.0,
) -> float | None:
    """TMA que faz o valuation por EBIT (motor Ciano) igualar o preço atual.

    ``cenario`` = {crescimento_fase_1, crescimento_fase_2}. Bissecção em [2%, tma_max].
    Devolve None se nem ``tma_max`` derrubar o valor justo até o preço (sinal de
    EBIT muito grande frente ao preço — tipicamente empresa muito alavancada).
    """
    if not preco or preco <= 0 or not ebit_por_acao or ebit_por_acao <= 0:
        return None
    retorno_alvo = retorno_alvo if retorno_alvo is not None else PREMISSAS_PADRAO["retorno_alvo_pl"]

    def justo(tma: float) -> float:
        r = calcular_valuation_completo(
            ticker="_", ebit_atual=ebit_por_acao, acoes_em_circulacao=1.0,
            preco_atual=preco, tma=tma, retorno_alvo=retorno_alvo, cenarios={"c": cenario},
        )
        return r["resultados"]["c"].valuation_final_por_acao

    lo, hi = 0.02, tma_max
    if justo(hi) > preco:  # nem a TMA máxima derruba o justo até o preço
        return None
    for _ in range(70):
        meio = (lo + hi) / 2
        if justo(meio) > preco:
            lo = meio
        else:
            hi = meio
    return (lo + hi) / 2


def leitura_reversa(
    preco: float,
    ebit_por_acao: float,
    lpa: float,
    cenario: dict,
    tma: float,
    retorno_alvo: float = None,
) -> dict:
    """Consolida as lentes reversas para uma empresa.

    Devolve {crescimento_implicito, tma_lucro, tma_ebit, razao, alavancada}.
    ``razao`` = tma_ebit/tma_lucro (None se alguma faltar); ``alavancada`` True
    quando a razão passa de RAZAO_ALAVANCAGEM (ou tma_ebit não converge).
    """
    g_perp = cenario.get("crescimento_fase_2", 0.0)
    tma_lucro = tma_implicita_lucro(preco, lpa, g_perp)
    tma_ebit = tma_implicita_ebit(ebit_por_acao, preco, cenario, retorno_alvo)
    razao = (tma_ebit / tma_lucro) if (tma_ebit and tma_lucro) else None
    alavancada = (tma_ebit is None) or (razao is not None and razao > RAZAO_ALAVANCAGEM)
    return {
        "crescimento_implicito": crescimento_implicito(preco, lpa, tma),
        "tma_lucro": tma_lucro,
        "tma_ebit": tma_ebit,
        "razao": razao,
        "alavancada": alavancada,
    }
