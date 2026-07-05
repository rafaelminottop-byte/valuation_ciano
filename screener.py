"""
Screener: roda o valuation em todas as ações da tabela do Fundamentus e
devolve um ranking de oportunidades (por upside no cenário de referência).

Ignora empresas sem EBIT positivo (P/EBIT <= 0), para as quais o modelo por
EBIT não se aplica.
"""

import math

import pandas as pd

from valuation_engine import CENARIOS_PADRAO, calcular_valuation_completo

# P/EBIT abaixo disto costuma indicar EBIT distorcido (não-recorrente) ou preço
# deprimido; o upside fica irreal. Não excluímos por padrão — só sinalizamos.
LIMITE_ALERTA_PEBIT = 2.0


def rodar_screener(
    df: pd.DataFrame,
    tma: float = None,
    retorno_alvo: float = None,
    cenarios: dict = None,
    anos_fase_1: int = None,
    anos_fase_2: int = None,
    liquidez_minima: float = 0.0,
    crescimento_minimo: float = None,
    pebit_minimo: float = 0.0,
    alerta_pebit: float = LIMITE_ALERTA_PEBIT,
) -> pd.DataFrame:
    """Calcula o valuation de cada ticker de ``df`` e devolve um DataFrame
    ordenado por upside (decrescente) no cenário de referência.

    ``df`` deve ter as colunas ``ticker``, ``preco_atual`` e ``ebit_por_acao``
    (como as que ``fundamentus_scraper._processar_tabela`` produz).

    - ``liquidez_minima``: filtra ações pouco negociadas (coluna ``liquidez``);
      sem isso o topo do ranking costuma ser lixo de tickers ilíquidos.
    - ``crescimento_minimo``: fração (ex.: 0.0). Como o modelo pressupõe EBIT
      crescente, filtra empresas com crescimento de receita em 5 anos abaixo
      do mínimo (coluna ``cresc_receita_5a``, proxy do crescimento do EBIT).
      Empresas sem esse dado são excluídas quando o filtro está ativo.
    - ``pebit_minimo``: P/EBIT mínimo. Um P/EBIT muito baixo (< ~1) costuma ser
      anomalia (EBIT inflado por evento não-recorrente ou preço deprimido) e o
      modelo projeta upsides irreais. Filtrar por um piso (ex.: 3) limpa o topo.
    """
    cenarios = cenarios if cenarios is not None else CENARIOS_PADRAO
    nomes = list(cenarios.keys())
    ref = "intermediario" if "intermediario" in cenarios else nomes[len(nomes) // 2]

    linhas = []
    for _, row in df.iterrows():
        try:
            preco = float(row["preco_atual"])
            ebit_por_acao = float(row["ebit_por_acao"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (math.isfinite(preco) and preco > 0):
            continue
        if not (math.isfinite(ebit_por_acao) and ebit_por_acao > 0):
            continue

        try:
            p_ebit = float(row["p_ebit"])
        except (KeyError, TypeError, ValueError):
            p_ebit = None
        if pebit_minimo > 0 and (p_ebit is None or not math.isfinite(p_ebit) or p_ebit < pebit_minimo):
            continue

        liquidez = row.get("liquidez") if hasattr(row, "get") else None
        try:
            liquidez = float(liquidez)
        except (TypeError, ValueError):
            liquidez = None
        if liquidez_minima > 0 and (liquidez is None or not math.isfinite(liquidez) or liquidez < liquidez_minima):
            continue

        crescimento = row.get("cresc_receita_5a") if hasattr(row, "get") else None
        try:
            crescimento = float(crescimento)
        except (TypeError, ValueError):
            crescimento = None
        if crescimento_minimo is not None and (
            crescimento is None or not math.isfinite(crescimento) or crescimento < crescimento_minimo
        ):
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
        r = res["resultados"][ref]
        linhas.append(
            {
                "ticker": res["ticker"],
                "alerta": "⚠️ P/EBIT baixo"
                if (p_ebit is not None and math.isfinite(p_ebit) and p_ebit < alerta_pebit)
                else "",
                "preco_atual": round(preco, 2),
                "p_ebit": round(p_ebit, 2) if p_ebit is not None and math.isfinite(p_ebit) else None,
                "veredito": res["veredito"],
                "upside_pct": round(r.upside_percentual, 1),
                "valuation": round(r.valuation_final_por_acao, 2),
                "cresc_receita_5a_pct": round(crescimento * 100, 1) if crescimento is not None and math.isfinite(crescimento) else None,
                "liquidez": liquidez,
            }
        )

    out = pd.DataFrame(linhas)
    if not out.empty:
        out = out.sort_values("upside_pct", ascending=False).reset_index(drop=True)
    return out
