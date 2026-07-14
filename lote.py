"""
Avaliação de várias empresas de uma vez (busca em lote).

Recebe uma lista de empresas já com os dados brutos (preço, fluxo por ação e LPA)
e roda o valuation Ciano em cada uma pelos DOIS métodos — sobre o EBIT e sobre o
lucro líquido —, devolvendo uma tabela comparável.

Marca ``alavancada`` quando as duas óticas divergem: sinal de que o EBIT vai em
boa parte para credores e o preço justo por EBIT está superestimado (ver lentes.py).
Ordena pelo upside do LPA, que é a leitura confiável nesses casos.
"""

import pandas as pd

from lentes import leitura_reversa
from valuation_engine import calcular_valuation_completo


def separar_tickers(texto: str) -> list[str]:
    """Extrai tickers de um texto livre (vírgula, espaço, ponto-e-vírgula ou quebra de linha)."""
    if not texto:
        return []
    bruto = texto.replace(",", " ").replace(";", " ").replace("\n", " ").replace("\t", " ")
    vistos, saida = set(), []
    for t in bruto.split():
        t = t.strip().upper()
        if t and t not in vistos:
            vistos.add(t)
            saida.append(t)
    return saida


def avaliar_lote(
    empresas: list[dict],
    cenarios: dict,
    tma: float,
    retorno_alvo: float = None,
    anos_fase_1: int = None,
    anos_fase_2: int = None,
    cenario_ref: str = "intermediario",
) -> pd.DataFrame:
    """Avalia cada empresa pelos dois métodos e devolve a tabela do lote.

    ``empresas``: lista de dicts com ticker, preco_atual, ebit_por_acao, lpa (opcional)
    e base_calculo (opcional). Função pura — não acessa a rede.
    """
    linhas = []
    for e in empresas:
        preco = e.get("preco_atual")
        fluxo = e.get("ebit_por_acao")
        if not preco or preco <= 0 or not fluxo or fluxo <= 0:
            continue
        comuns = dict(
            acoes_em_circulacao=1.0, preco_atual=preco, tma=tma, retorno_alvo=retorno_alvo,
            cenarios=cenarios, anos_fase_1=anos_fase_1, anos_fase_2=anos_fase_2,
        )
        res_ebit = calcular_valuation_completo(ticker=e["ticker"], ebit_atual=fluxo, **comuns)
        ref = cenario_ref if cenario_ref in res_ebit["resultados"] else list(res_ebit["resultados"])[0]
        r_ebit = res_ebit["resultados"][ref]

        lpa = e.get("lpa")
        r_lpa = None
        alavancada = False
        tma_lucro = tma_ebit = None
        if lpa and lpa > 0:
            res_lpa = calcular_valuation_completo(ticker=e["ticker"], ebit_atual=lpa, **comuns)
            r_lpa = res_lpa["resultados"][ref]
            lr = leitura_reversa(preco, fluxo, lpa, cenarios[ref], tma, retorno_alvo)
            alavancada = lr["alavancada"]
            tma_lucro, tma_ebit = lr["tma_lucro"], lr["tma_ebit"]

        linhas.append({
            "ticker": e["ticker"],
            "nome": e.get("nome"),
            "preco": round(preco, 2),
            "justo_lpa": round(r_lpa.valuation_final_por_acao, 2) if r_lpa else None,
            "upside_lpa": round(r_lpa.upside_percentual, 1) if r_lpa else None,
            # TMA implícita: o retorno anual que o mercado exige para pagar o preço de
            # hoje. Pelo lucro costuma ser sensata; pelo EBIT, quando dispara, denuncia
            # que o EBIT não é do acionista (dívida).
            "tma_lpa_pct": round(tma_lucro * 100, 1) if tma_lucro is not None else None,
            "justo_ebit": round(r_ebit.valuation_final_por_acao, 2),
            "upside_ebit": round(r_ebit.upside_percentual, 1),
            "tma_ebit_pct": round(tma_ebit * 100, 1) if tma_ebit is not None else None,
            "alavancada": "⚠️" if alavancada else "",
            "base": e.get("base_calculo", "EBIT"),
            "veredito": res_ebit["veredito"],
        })

    df = pd.DataFrame(linhas)
    if df.empty:
        return df
    # Ordena pelo upside do LPA (leitura confiável); quem não tem LPA vai pelo EBIT.
    df["_ordem"] = df["upside_lpa"].fillna(df["upside_ebit"])
    return df.sort_values("_ordem", ascending=False).drop(columns="_ordem").reset_index(drop=True)
