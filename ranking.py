"""
Ranking qualitativo objetivo das empresas (pilares de solidez e qualidade),
a partir dos indicadores do Fundamentus.

- Pilar 1 (Solidez / baixo risco a juros): Dív.Líq/EBIT, Dív.Líq/Patrimônio,
  Liquidez Corrente. A Dív.Líq/EBIT é derivada de EV/EBIT − P/EBIT.
- Pilar 2 (Qualidade do negócio): ROIC, ROE, Margem EBIT.

Cada indicador vira uma nota 0–10 por faixas fixas; os pilares são médias
ponderadas e o score final é a média ponderada dos dois pilares.

Bancos e empresas sem EBIT positivo ficam de fora (os indicadores de margem/
retorno não se aplicam), coerente com o modelo de valuation por EBIT.
"""

import math

import pandas as pd

from valuation_engine import CENARIOS_PADRAO, calcular_valuation_completo


def _num(v):
    """Converte para float finito ou devolve None."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def nota_div_liq_ebit(x: float) -> float:
    if x < 0:
        return 10.0  # caixa líquido
    for limite, nota in [(1, 9), (2, 8), (3, 6), (4, 4), (5, 2)]:
        if x < limite:
            return float(nota)
    return 0.0


def nota_div_liq_patrim(x: float) -> float:
    if x < 0:
        return 10.0
    for limite, nota in [(0.5, 8), (1, 6), (2, 4), (3, 2)]:
        if x < limite:
            return float(nota)
    return 0.0


def nota_liquidez_corrente(x: float) -> float:
    for limite, nota in [(2, 10), (1.5, 8), (1, 6), (0.8, 4)]:
        if x >= limite:
            return float(nota)
    return 2.0


def _nota_pct(frac: float) -> float:
    """Nota para ROIC/ROE (recebe fração, ex.: 0.20 = 20%)."""
    p = frac * 100
    for limite, nota in [(20, 10), (15, 8), (10, 6), (5, 4), (0, 2)]:
        if p >= limite:
            return float(nota)
    return 0.0


def nota_margem_ebit(frac: float) -> float:
    p = frac * 100
    for limite, nota in [(25, 10), (15, 8), (8, 6), (3, 4)]:
        if p >= limite:
            return float(nota)
    return 2.0


def score_solidez(div_liq_ebit, div_liq_patrim, liquidez_corrente) -> float | None:
    if div_liq_ebit is None or div_liq_patrim is None or liquidez_corrente is None:
        return None
    return round(
        0.50 * nota_div_liq_ebit(div_liq_ebit)
        + 0.25 * nota_div_liq_patrim(div_liq_patrim)
        + 0.25 * nota_liquidez_corrente(liquidez_corrente),
        2,
    )


def score_qualidade(roic, roe, margem_ebit) -> float | None:
    if roic is None or roe is None or margem_ebit is None:
        return None
    notas = [_nota_pct(roic), _nota_pct(roe), nota_margem_ebit(margem_ebit)]
    return round(sum(notas) / len(notas), 2)


def nota_upside(upside_pct: float) -> float:
    """Nota para o upside do valuation (quanto maior o desconto, maior a nota)."""
    for limite, nota in [(200, 10), (100, 8), (50, 6), (20, 4), (0, 2)]:
        if upside_pct >= limite:
            return float(nota)
    return 0.0


# Peso relativo de cada categoria no score final (ajustável pelo usuário).
# Grupos: Solidez, Qualidade e Upside (valuation). Padrão dá ~1/3 para cada.
PESOS_PADRAO = {
    "div_liq_ebit": 30.0,
    "div_liq_patrim": 10.0,
    "liquidez_corrente": 10.0,
    "roic": 20.0,
    "roe": 15.0,
    "margem_ebit": 15.0,
    "upside": 50.0,
}
GRUPO_SOLIDEZ = ("div_liq_ebit", "div_liq_patrim", "liquidez_corrente")
GRUPO_QUALIDADE = ("roic", "roe", "margem_ebit")


def _media_ponderada(notas: dict, pesos: dict, chaves) -> float | None:
    total = sum(pesos.get(k, 0.0) for k in chaves)
    if total <= 0:
        return None
    return round(sum(pesos.get(k, 0.0) * notas[k] for k in chaves) / total, 2)


def rankear_qualidade(
    df: pd.DataFrame,
    pesos: dict = None,
    liquidez_minima: float = 0.0,
    tma: float = None,
    retorno_alvo: float = None,
    cenarios: dict = None,
    anos_fase_1: int = None,
    anos_fase_2: int = None,
) -> pd.DataFrame:
    """Calcula as notas de cada categoria e o score (média ponderada por ``pesos``).

    ``pesos`` mapeia cada categoria (div_liq_ebit, div_liq_patrim,
    liquidez_corrente, roic, roe, margem_ebit, upside) a um peso relativo;
    ausentes usam PESOS_PADRAO. O ``upside`` vem do valuation (cenário
    intermediário), calculado com as premissas passadas. Exige as colunas do
    Fundamentus processadas. Empresas com EBIT não positivo (bancos) ou dados
    faltando saem. Ordena por score.
    """
    pesos = {**PESOS_PADRAO, **(pesos or {})}
    cenarios = cenarios if cenarios is not None else CENARIOS_PADRAO

    linhas = []
    for _, row in df.iterrows():
        p_ebit = _num(row.get("p_ebit"))
        ev_ebit = _num(row.get("ev_ebit"))
        if p_ebit is None or p_ebit <= 0:  # exclui EBIT não-positivo / bancos
            continue

        liquidez = _num(row.get("liquidez"))
        if liquidez_minima > 0 and (liquidez is None or liquidez < liquidez_minima):
            continue

        div_liq_ebit = (ev_ebit - p_ebit) if ev_ebit is not None else None
        div_liq_patrim = _num(row.get("div_liq_patrim"))
        liquidez_corrente = _num(row.get("liquidez_corrente"))
        roic = _num(row.get("roic"))
        roe = _num(row.get("roe"))
        margem = _num(row.get("margem_ebit"))
        preco = _num(row.get("preco_atual"))
        ebit_por_acao = _num(row.get("ebit_por_acao"))
        if None in (div_liq_ebit, div_liq_patrim, liquidez_corrente, roic, roe, margem):
            continue
        if preco is None or preco <= 0 or ebit_por_acao is None or ebit_por_acao <= 0:
            continue

        res = calcular_valuation_completo(
            ticker=str(row["ticker"]),
            ebit_atual=ebit_por_acao,
            acoes_em_circulacao=1.0,
            preco_atual=preco,
            tma=tma,
            retorno_alvo=retorno_alvo,
            cenarios=cenarios,
            anos_fase_1=anos_fase_1,
            anos_fase_2=anos_fase_2,
        )
        nomes = list(res["resultados"].keys())
        ref = "intermediario" if "intermediario" in res["resultados"] else nomes[len(nomes) // 2]
        upside_pct = res["resultados"][ref].upside_percentual

        notas = {
            "div_liq_ebit": nota_div_liq_ebit(div_liq_ebit),
            "div_liq_patrim": nota_div_liq_patrim(div_liq_patrim),
            "liquidez_corrente": nota_liquidez_corrente(liquidez_corrente),
            "roic": _nota_pct(roic),
            "roe": _nota_pct(roe),
            "margem_ebit": nota_margem_ebit(margem),
            "upside": nota_upside(upside_pct),
        }
        score = _media_ponderada(notas, pesos, notas.keys())
        if score is None:  # todos os pesos zerados
            continue

        linhas.append(
            {
                "ticker": str(row["ticker"]).upper(),
                "score": score,
                "solidez": _media_ponderada(notas, pesos, GRUPO_SOLIDEZ),
                "qualidade": _media_ponderada(notas, pesos, GRUPO_QUALIDADE),
                "upside_pct": round(upside_pct, 1),
                "div_liq_ebit": round(div_liq_ebit, 2),
                "roic_pct": round(roic * 100, 1),
                "roe_pct": round(roe * 100, 1),
                "margem_ebit_pct": round(margem * 100, 1),
            }
        )

    out = pd.DataFrame(linhas)
    if not out.empty:
        out = out.sort_values("score", ascending=False).reset_index(drop=True)
    return out
