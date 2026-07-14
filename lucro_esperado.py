"""
Expectativa de lucro (consenso de analistas) e suas REVISÕES.

É o indicador que o autor do relatório acompanha: *"a mediana da expectativa de
lucro para os próximos 12 meses"*. Ele mesmo o classifica como **atrasado** — o
valor de hoje diz pouco. O que informa é a **direção da revisão**: as expectativas
estão sendo cortadas ou elevadas? (No texto: *"pararam de cair e receberam
revisões positivas"*.)

Fonte: Yahoo Finance (``eps_trend``), que dá a estimativa de LPA do próximo ano
como está hoje e como estava há 7, 30, 60 e 90 dias — de graça, para B3 e EUA.

Índice de revisão: cada empresa é normalizada pela própria estimativa de 90 dias
atrás (= 100) e tiramos a MEDIANA da cesta em cada instante. Assim o índice não é
dominado por quem tem lucro grande, e o número é lido direto: 103 = a expectativa
de lucro da cesta subiu 3% em 90 dias.
"""

import json
import time
from pathlib import Path
from statistics import median

import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_VERSAO = 1
CACHE_FILE = CACHE_DIR / f"lucro_esperado_v{CACHE_VERSAO}.json"
CACHE_TTL_SEGUNDOS = 24 * 60 * 60  # 24h (consenso muda devagar)

# Instantes do eps_trend, do mais antigo para o mais recente.
JANELAS = [("90daysAgo", "90d atrás"), ("60daysAgo", "60d"), ("30daysAgo", "30d"),
           ("7daysAgo", "7d"), ("current", "hoje")]
PERIODO_ALVO = "+1y"  # lucro esperado do próximo ano (proxy dos "próximos 12 meses")


def _valido(x) -> bool:
    """Descarta ausentes e zeros (o Yahoo usa 0.0 para 'sem estimativa')."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return False
    return v == v and v > 0  # v == v descarta NaN


def expectativa_ticker(ticker: str) -> dict | None:
    """Estimativa de LPA do próximo ano e como ela estava nas últimas janelas.

    Devolve {ticker, valores: {janela: lpa}, revisao_90d_pct, n_analistas} ou
    None se o Yahoo não tiver consenso utilizável para o papel.
    """
    try:
        tk = yf.Ticker(ticker)
        trend = tk.eps_trend
        if trend is None or getattr(trend, "empty", True) or PERIODO_ALVO not in trend.index:
            return None
        linha = trend.loc[PERIODO_ALVO]
        valores = {chave: float(linha[chave]) for chave, _ in JANELAS
                   if chave in linha.index and _valido(linha[chave])}
        if "current" not in valores or "90daysAgo" not in valores:
            return None
        revisao = (valores["current"] / valores["90daysAgo"] - 1) * 100

        n_analistas = None
        try:
            est = tk.earnings_estimate
            if est is not None and not est.empty and PERIODO_ALVO in est.index:
                n_analistas = int(est.loc[PERIODO_ALVO]["numberOfAnalysts"])
        except Exception:  # noqa: BLE001 - dado opcional
            pass

        return {"ticker": ticker, "valores": valores, "revisao_90d_pct": revisao,
                "n_analistas": n_analistas}
    except Exception:  # noqa: BLE001
        return None


def indice_revisao(expectativas: list[dict]) -> dict:
    """Índice de revisão do lucro esperado (mediana da cesta, base 100 = 90d atrás).

    Função pura. Devolve {valor, serie, n_empresas, pct_revisao_positiva}:
    - ``valor``: o índice hoje (ex.: 103 = expectativa 3% acima de 90 dias atrás);
    - ``serie``: os 5 pontos da trajetória (90d → hoje), para o gráfico;
    - ``pct_revisao_positiva``: quantas empresas da cesta tiveram revisão para cima
      (medida de "amplitude" — se é generalizado ou concentrado).
    """
    uteis = [e for e in expectativas if e and "90daysAgo" in e["valores"]]
    if not uteis:
        return {"valor": None, "serie": [], "n_empresas": 0, "pct_revisao_positiva": None}

    serie = []
    for chave, rotulo in JANELAS:
        # cada empresa vira um índice base 100 na própria estimativa de 90d atrás
        relativos = [
            e["valores"][chave] / e["valores"]["90daysAgo"] * 100
            for e in uteis if chave in e["valores"]
        ]
        if relativos:
            serie.append({"data": rotulo, "valor": median(relativos)})

    positivas = sum(1 for e in uteis if e["revisao_90d_pct"] > 0)
    return {
        "valor": serie[-1]["valor"] if serie else None,
        "serie": serie,
        "n_empresas": len(uteis),
        "pct_revisao_positiva": 100 * positivas / len(uteis),
    }


def _carregar_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def buscar_indice_revisao(
    tickers: list[str],
    usar_cache: bool = True,
    ttl_segundos: float = CACHE_TTL_SEGUNDOS,
    progresso=None,
) -> dict:
    """Monta o índice de revisão para a cesta de ``tickers`` (com cache local)."""
    cache = _carregar_cache() if usar_cache else {}
    if usar_cache and cache.get("ts") and (time.time() - cache["ts"]) < ttl_segundos:
        if cache.get("chave") == sorted(tickers):
            return cache["indice"]

    expectativas = []
    for i, t in enumerate(tickers, 1):
        e = expectativa_ticker(t)
        if e:
            expectativas.append(e)
        if progresso:
            progresso(i, len(tickers))

    indice = indice_revisao(expectativas)
    if usar_cache:
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps({"ts": time.time(), "chave": sorted(tickers), "indice": indice},
                       ensure_ascii=False),
            encoding="utf-8",
        )
    return indice
