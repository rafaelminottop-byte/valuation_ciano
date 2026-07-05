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


def rankear_qualidade(
    df: pd.DataFrame,
    peso_solidez: float = 0.5,
    peso_qualidade: float = 0.5,
    liquidez_minima: float = 0.0,
) -> pd.DataFrame:
    """Calcula os pilares e o score final para cada empresa e ordena por score.

    Exige as colunas do Fundamentus processadas (roic, roe, margem_ebit,
    div_liq_patrim, liquidez_corrente, p_ebit, ev_ebit). Empresas com EBIT não
    positivo (P/EBIT <= 0, tipicamente bancos) ou com dados faltando saem.
    """
    total = peso_solidez + peso_qualidade
    if total <= 0:
        peso_solidez, peso_qualidade = 0.5, 0.5
        total = 1.0

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
        solidez = score_solidez(
            div_liq_ebit, _num(row.get("div_liq_patrim")), _num(row.get("liquidez_corrente"))
        )
        qualidade = score_qualidade(
            _num(row.get("roic")), _num(row.get("roe")), _num(row.get("margem_ebit"))
        )
        if solidez is None or qualidade is None:
            continue

        score = round((peso_solidez * solidez + peso_qualidade * qualidade) / total, 2)
        linhas.append(
            {
                "ticker": str(row["ticker"]).upper(),
                "score": score,
                "solidez": solidez,
                "qualidade": qualidade,
                "div_liq_ebit": round(div_liq_ebit, 2) if div_liq_ebit is not None else None,
                "roic_pct": round(_num(row.get("roic")) * 100, 1),
                "roe_pct": round(_num(row.get("roe")) * 100, 1),
                "margem_ebit_pct": round(_num(row.get("margem_ebit")) * 100, 1),
            }
        )

    out = pd.DataFrame(linhas)
    if not out.empty:
        out = out.sort_values("score", ascending=False).reset_index(drop=True)
    return out
