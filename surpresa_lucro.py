"""
Surpresa de resultados — as empresas vêm batendo ou frustrando o consenso?

Complementa lucro_esperado.py (que mede a REVISÃO das estimativas, com janela de
90 dias). Aqui olhamos para trás: cada trimestre, o Yahoo (``earnings_dates``)
traz o EPS estimado antes do balanço e o EPS reportado — a diferença é a
"surpresa". Como o histórico vai a ~2 anos, este indicador já nasce longo.

Índice de surpresa da B3: em cada data de balanço, a MEDIANA da surpresa (%) das
empresas da cesta que reportaram por volta daquela data (agrupadas por mês).
Mediana para não ser dominada por uma única empresa com surpresa gigante.
"""

import json
import time
from pathlib import Path
from statistics import median

import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
# v2: passou a guardar as linhas estimado x realizado. v3: corrigida a leitura da
# coluna Surprise(%) (ja vem em %, nao multiplicar por 100).
CACHE_VERSAO = 3
CACHE_FILE = CACHE_DIR / f"surpresa_lucro_v{CACHE_VERSAO}.json"
CACHE_TTL_SEGUNDOS = 24 * 60 * 60  # 24h


# Surpresas alem disso vem de consenso ~zero (a % explode) e sao ruido: aparamos.
LIMITE_SURPRESA = 100.0
# So mostramos um trimestre com pelo menos esta quantidade de empresas (mediana robusta).
MIN_EMPRESAS_TRI = 3


def _num(x):
    try:
        v = float(x)
        return v if v == v else None  # descarta NaN
    except (TypeError, ValueError):
        return None


def _trimestre(data) -> str:
    """'YYYY-Tn' a partir de uma data (agrupa balancos do mesmo trimestre)."""
    return f"{data.year}-T{(data.month - 1) // 3 + 1}"


def surpresas_ticker(ticker: str, limite: int = 24) -> list[dict]:
    """Estimado, reportado e surpresa (%) por balanco de um ticker.

    Devolve [{trimestre, estimado, reportado, surpresa_pct}], surpresa aparada em
    ±LIMITE_SURPRESA, do mais antigo ao mais recente.
    """
    try:
        ed = yf.Ticker(ticker).get_earnings_dates(limit=limite)
    except Exception:
        return []
    if ed is None or ed.empty:
        return []
    col_est = next((c for c in ed.columns if "Estimate" in c), None)
    col_rep = next((c for c in ed.columns if "Reported" in c or "Actual" in c), None)
    saida = []
    for data, linha in ed.iterrows():
        est = _num(linha.get(col_est)) if col_est else None
        rep = _num(linha.get(col_rep)) if col_rep else None
        if est is None or rep is None:
            continue  # so trimestres ja reportados (com os dois valores)
        # A coluna Surprise(%) do get_earnings_dates ja vem em PORCENTAGEM
        # (0,44 = 0,44%, nao 44%). Usamos direto; se faltar, calculamos.
        s = _num(linha.get("Surprise(%)"))
        if s is not None:
            pct = s
        elif est != 0:
            pct = (rep / est - 1) * 100
        else:
            continue
        pct = max(-LIMITE_SURPRESA, min(LIMITE_SURPRESA, pct))  # winsoriza
        saida.append({"trimestre": _trimestre(data), "estimado": est,
                      "reportado": rep, "surpresa_pct": pct})
    saida.sort(key=lambda x: x["trimestre"])
    return saida


def serie_empresa(ticker: str, limite: int = 16) -> list[dict]:
    """LPA estimado x reportado de UMA empresa, por trimestre (para o gráfico individual).

    ``ticker`` já no formato do Yahoo (ex.: 'PETR4.SA' ou 'AAPL'). Devolve
    [{data, estimado, reportado, surpresa_pct}], cronológico.
    """
    return [
        {"data": s["trimestre"], "estimado": s["estimado"],
         "reportado": s["reportado"], "surpresa_pct": s["surpresa_pct"]}
        for s in surpresas_ticker(ticker, limite=limite)
    ]


def indice_surpresa(por_ticker: dict, min_empresas: int = MIN_EMPRESAS_TRI) -> dict:
    """Indice de surpresa da cesta: mediana por trimestre de balanco.

    ``por_ticker`` = {ticker: [surpresas...]}. So entram trimestres com pelo menos
    ``min_empresas`` empresas. Devolve {valor, serie, n_empresas, pct_bateram} —
    valor = mediana do trimestre mais recente valido.
    """
    por_tri = {}
    tickers_ok = set()
    for ticker, surpresas in por_ticker.items():
        if not surpresas:
            continue
        tickers_ok.add(ticker)
        # no maximo uma surpresa por empresa por trimestre (a mais recente)
        vistos = {}
        for s in surpresas:
            vistos[s["trimestre"]] = s["surpresa_pct"]
        for tri, pct in vistos.items():
            por_tri.setdefault(tri, []).append(pct)

    validos = {t: v for t, v in por_tri.items() if len(v) >= min_empresas}
    serie = [{"data": tri, "valor": round(median(vals), 2)}
             for tri, vals in sorted(validos.items())]
    if not serie:
        return {"valor": None, "serie": [], "serie_est_real": [],
                "n_empresas": len(tickers_ok), "pct_bateram": None}

    ultimo = serie[-1]
    vals_ultimo = validos[ultimo["data"]]
    positivas = sum(1 for v in vals_ultimo if v > 0)
    return {
        "valor": ultimo["valor"],
        "serie": serie,
        "serie_est_real": serie_estimado_realizado(por_ticker, min_empresas),
        "n_empresas": len(tickers_ok),
        "pct_bateram": round(100 * positivas / len(vals_ultimo), 0),
    }


def serie_estimado_realizado(por_ticker: dict, min_empresas: int = MIN_EMPRESAS_TRI) -> list[dict]:
    """Duas linhas por trimestre: media do LPA estimado x media do LPA reportado.

    Como as MESMAS empresas alimentam as duas linhas em cada trimestre, o gap
    entre elas e a surpresa agregada (estimado acima = frustrou; abaixo = bateu).
    A media (nao a soma) neutraliza quantas empresas reportaram no trimestre.
    """
    est_tri, rep_tri = {}, {}
    for surpresas in por_ticker.values():
        vistos = {}
        for s in surpresas:
            vistos[s["trimestre"]] = s  # 1 por empresa/trimestre (a mais recente)
        for tri, s in vistos.items():
            est_tri.setdefault(tri, []).append(s["estimado"])
            rep_tri.setdefault(tri, []).append(s["reportado"])

    linhas = []
    for tri in sorted(est_tri):
        if len(est_tri[tri]) < min_empresas:
            continue
        linhas.append({
            "data": tri,
            "estimado": round(sum(est_tri[tri]) / len(est_tri[tri]), 2),
            "reportado": round(sum(rep_tri[tri]) / len(rep_tri[tri]), 2),
        })
    return linhas


def _carregar_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def buscar_indice_surpresa(
    tickers: list[str],
    usar_cache: bool = True,
    ttl_segundos: float = CACHE_TTL_SEGUNDOS,
    progresso=None,
) -> dict:
    """Monta o índice de surpresa para a cesta de ``tickers`` (com cache local)."""
    cache = _carregar_cache() if usar_cache else {}
    if usar_cache and cache.get("ts") and (time.time() - cache["ts"]) < ttl_segundos:
        if cache.get("chave") == sorted(tickers):
            return cache["indice"]

    por_ticker = {}
    for i, t in enumerate(tickers, 1):
        por_ticker[t] = surpresas_ticker(t)
        if progresso:
            progresso(i, len(tickers))

    indice = indice_surpresa(por_ticker)
    if usar_cache:
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps({"ts": time.time(), "chave": sorted(tickers), "indice": indice},
                       ensure_ascii=False),
            encoding="utf-8",
        )
    return indice
