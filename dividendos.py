"""
Dividendo médio dos últimos 3 anos (para o ranking), via Yahoo Finance.

O Fundamentus só expõe o Dividend Yield atual; para a média histórica usamos o
yfinance (histórico de proventos por ação, ticker ``XXXX3.SA``). Calculamos a
média anual dos proventos nos 3 últimos anos-calendário completos e, a partir do
preço atual, o DY médio de 3 anos (fração). Como cada ticker é uma chamada de
rede (lenta), guardamos um cache local com TTL — o cache guarda o valor em R$
(estável); o yield é recalculado com o preço do momento a cada consulta.
"""

import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "dividendos.json"
CACHE_TTL_SEGUNDOS = 24 * 60 * 60  # 24 horas


def _media_proventos_3anos(dividendos: pd.Series, hoje: pd.Timestamp = None) -> float | None:
    """Média anual dos proventos por ação nos 3 últimos anos-calendário completos.

    ``dividendos`` é a série do yfinance (índice = datas, valor = R$/ação). Usa
    os anos (ano_atual-3, -2, -1), ignorando o ano corrente (incompleto) e o
    fuso horário do índice. Devolve None se não houver nenhum provento na janela.
    """
    if dividendos is None or len(dividendos) == 0:
        return None
    hoje = hoje if hoje is not None else pd.Timestamp.now()
    anos = [hoje.year - 3, hoje.year - 2, hoje.year - 1]
    por_ano = {a: 0.0 for a in anos}
    for data, valor in dividendos.items():
        if data.year in por_ano:
            por_ano[data.year] += float(valor)
    total = sum(por_ano.values())
    if total <= 0:
        return None
    return total / len(anos)


def dy_medio_3anos(media_proventos: float, preco: float) -> float | None:
    """DY médio (fração) = proventos médios anuais / preço atual."""
    if media_proventos is None or preco is None or preco <= 0:
        return None
    return media_proventos / preco


def _media_via_yfinance(ticker: str) -> float | None:
    """Baixa o histórico de proventos do ticker (.SA) e devolve a média 3a em R$."""
    try:
        serie = yf.Ticker(f"{ticker.upper()}.SA").dividends
        return _media_proventos_3anos(serie)
    except Exception:
        return None


def _carregar_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _salvar_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def buscar_dy_medio_3anos(
    precos: dict,
    usar_cache: bool = True,
    ttl_segundos: float = CACHE_TTL_SEGUNDOS,
) -> dict:
    """Devolve {ticker: dy_3a_fracao} (ou None) para os tickers em ``precos``.

    ``precos`` mapeia ticker -> preço atual (do Fundamentus), usado para o yield.
    Só bate no yfinance nos tickers ausentes/vencidos no cache; guarda a média em
    R$ (estável) e recalcula o DY com o preço passado. Passe ``usar_cache=False``
    para forçar a atualização de todos.
    """
    cache = _carregar_cache() if usar_cache else {}
    agora = time.time()
    resultado = {}
    alterou = False
    for ticker, preco in precos.items():
        t = str(ticker).upper()
        entrada = cache.get(t)
        if not (usar_cache and entrada and (agora - entrada.get("ts", 0)) < ttl_segundos):
            entrada = {"media_rs": _media_via_yfinance(t), "ts": agora}
            cache[t] = entrada
            alterou = True
        resultado[t] = dy_medio_3anos(entrada.get("media_rs"), preco)
    if usar_cache and alterou:
        _salvar_cache(cache)
    return resultado
