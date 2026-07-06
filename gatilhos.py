"""
Gatilhos técnicos: avisa quando o preço de uma ação chega perto da média
móvel (por padrão a média de 200 semanas — MM200 no gráfico semanal).

O histórico de preços vem do Yahoo Finance (yfinance), já que o Fundamentus
só expõe o preço atual. A lógica de distância à média é pura (testável sem
rede); o download fica isolado.
"""

import pandas as pd

PERIODOS_PADRAO = 200        # 200 candles semanais = MM200 semanal
TOLERANCIA_PADRAO = 5.0      # % de proximidade que dispara o gatilho


def _distancia_media(precos: pd.Series, periodos: int) -> dict | None:
    """Distância (%) do último preço até a média móvel de ``periodos`` candles.

    Devolve None se não houver candles suficientes para a média.
    """
    precos = precos.dropna()
    if len(precos) < periodos:
        return None
    preco = float(precos.iloc[-1])
    media = float(precos.rolling(periodos).mean().iloc[-1])
    if not media:
        return None
    return {
        "preco": round(preco, 2),
        "media": round(media, 2),
        "distancia_pct": round((preco / media - 1) * 100, 1),
    }


def baixar_fechamento_semanal(ticker: str, anos: int = 8) -> pd.Series:
    """Série de fechamentos semanais (ajustados) do ticker da B3, via Yahoo."""
    import yfinance as yf

    df = yf.download(
        f"{ticker.strip().upper()}.SA",
        period=f"{anos}y",
        interval="1wk",
        progress=False,
        auto_adjust=True,
    )
    if df is None or df.empty or "Close" not in df:
        return pd.Series(dtype=float)
    return df["Close"].squeeze().dropna()


def avaliar_gatilhos(
    tickers,
    periodos: int = PERIODOS_PADRAO,
    tolerancia_pct: float = TOLERANCIA_PADRAO,
) -> pd.DataFrame:
    """Para cada ticker, calcula a distância à média e sinaliza os que estão
    dentro de ``tolerancia_pct`` (em módulo). Ordena pelos mais próximos."""
    linhas = []
    for t in tickers:
        t = str(t).strip().upper()
        if not t:
            continue
        try:
            precos = baixar_fechamento_semanal(t)
        except Exception:  # noqa: BLE001 - rede/fonte pode falhar por ticker
            precos = pd.Series(dtype=float)
        dados = _distancia_media(precos, periodos)
        if dados is None:
            linhas.append(
                {"ticker": t, "preco": None, "media": None, "distancia_pct": None,
                 "alerta": "histórico insuficiente"}
            )
            continue
        na_media = abs(dados["distancia_pct"]) <= tolerancia_pct
        linhas.append({"ticker": t, **dados, "alerta": "🎯 na média" if na_media else ""})

    out = pd.DataFrame(linhas)
    if not out.empty:
        out["_abs"] = out["distancia_pct"].abs()
        out = out.sort_values("_abs", na_position="last").drop(columns="_abs").reset_index(drop=True)
    return out
