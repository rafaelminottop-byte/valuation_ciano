"""
Fonte de dados do mercado americano (via Yahoo Finance / yfinance).

Análogo ao fundamentus_scraper.py, mas para ações dos EUA: em vez de uma tabela
única (que não existe para o mercado americano), parte de um universo curado
(data/tickers_eua.json) e busca, ticker a ticker, o que o valuation Ciano precisa:

  - preço atual;
  - fluxo por ação: EBIT/ação para empresas normais; para BANCOS (que não têm
    EBIT), o lucro líquido por ação — mesma decisão dos bancos da B3;
  - dívida líquida / EBIT (para filtrar empresas alavancadas, cujo valuation por
    EBIT superestima a ação);
  - dividendo médio de 3 anos (DY), reaproveitando a lógica de dividendos.py.

As premissas do valuation são as de PREMISSAS_EUA (TMA em dólar = 10% a.a.).
Cada ticker é uma chamada de rede lenta (demonstrativos), então há cache local
com TTL. A primeira montagem demora; as seguintes vêm do cache.
"""

import json
import math
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

from dividendos import _media_proventos_3anos, dy_medio_3anos
from valuation_engine import PREMISSAS_EUA, calcular_valuation_completo

UNIVERSO_PATH = Path(__file__).resolve().parent / "data" / "tickers_eua.json"
CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "mercado_eua.json"
CACHE_TTL_SEGUNDOS = 12 * 60 * 60  # 12 horas

# Filtros padrão de qualidade (o valuation por EBIT distorce nesses casos):
#  - alavancagem: EBIT pertence a credores + acionistas; com muita dívida, o
#    "justo" por ação sai inflado.
#  - P/EBIT anômalo: múltiplo < ~3 gera upside irreal (mesmo alerta do screener B3).
DIV_LIQ_EBIT_MAX_PADRAO = 3.0
P_EBIT_MINIMO_PADRAO = 3.0


def carregar_universo() -> list[dict]:
    """Lê o universo curado de empresas americanas (ticker, nome, setor, base)."""
    if not UNIVERSO_PATH.exists():
        return []
    return json.loads(UNIVERSO_PATH.read_text(encoding="utf-8"))


def buscar_ticker_eua(ticker: str) -> dict:
    """Busca um ticker americano avulso no Yahoo Finance, pronto para o valuation.

    Deriva o fluxo por ação: EBIT/ação para empresas normais; se a linha de EBIT
    não existir no demonstrativo (típico de bancos), usa o lucro líquido, como os
    bancos da B3. Levanta ValueError se faltar preço/ações ou não houver fluxo
    positivo (o modelo Ciano pressupõe EBIT/lucro positivo e crescente).
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("Informe um ticker (ex.: AAPL, MSFT, JPM).")
    tk = yf.Ticker(ticker)
    fin = tk.financials
    fluxo, serie = _linha_demonstrativo(fin, ["EBIT", "Operating Income"])
    base = "EBIT"
    if fluxo is None:  # sem linha de EBIT -> provável banco: usa o lucro líquido
        fluxo, serie = _linha_demonstrativo(fin, ["Net Income"])
        base = "Lucro"
    if fluxo is None or fluxo <= 0:
        raise ValueError(
            f"{ticker}: sem EBIT nem lucro positivo no Yahoo Finance "
            "(o modelo só se aplica a EBIT positivo)."
        )
    fi = tk.fast_info
    preco = float(fi.last_price) if getattr(fi, "last_price", None) else None
    acoes = getattr(fi, "shares", None)
    info = tk.info or {}
    if not acoes:
        acoes = info.get("sharesOutstanding")
    if not preco or preco <= 0 or not acoes:
        raise ValueError(f"{ticker}: preço ou nº de ações indisponível no Yahoo Finance.")
    anos = sorted(serie)
    # LPA (lucro líquido por ação) para as lentes reversas. Para banco o próprio
    # fluxo já é o lucro; senão, lê a linha de Net Income.
    if base == "Lucro":
        lucro = fluxo
    else:
        lucro, _ = _linha_demonstrativo(fin, ["Net Income"])
    lpa = (lucro / float(acoes)) if lucro is not None else None
    return {
        "ticker": ticker,
        "nome": info.get("longName") or info.get("shortName") or ticker,
        "preco_atual": preco,
        "ebit_por_acao": fluxo / float(acoes),
        "lpa": lpa,
        "base_calculo": base,
        "fluxo_crescente": len(anos) >= 2 and serie[anos[-1]] > serie[anos[0]],
    }


def _linha_demonstrativo(fin, nomes):
    """(valor mais recente, série {ano: valor}) da 1a linha encontrada, ou (None, {})."""
    if fin is None or getattr(fin, "empty", True):
        return None, {}
    for nome in nomes:
        if nome in fin.index:
            s = fin.loc[nome].dropna()
            if len(s):
                serie = {c.year: float(v) for c, v in s.items()}
                return serie[max(serie)], serie
    return None, {}


def _buscar_um(ticker: str, base_calculo: str) -> dict:
    """Busca no yfinance os dados brutos (estáveis) de um ticker. Preço à parte."""
    try:
        tk = yf.Ticker(ticker)
        if base_calculo == "Lucro":  # bancos: lucro líquido no lugar do EBIT
            fluxo, serie = _linha_demonstrativo(tk.financials, ["Net Income"])
        else:
            fluxo, serie = _linha_demonstrativo(tk.financials, ["EBIT", "Operating Income"])
        fi = tk.fast_info
        preco = float(fi.last_price)
        acoes = getattr(fi, "shares", None)
        info = None
        if not acoes:
            info = tk.info or {}
            acoes = info.get("sharesOutstanding")
        if info is None:
            info = tk.info or {}
        divida = info.get("totalDebt") or 0.0
        caixa = info.get("totalCash") or 0.0
        media_div = _media_proventos_3anos(tk.dividends)
        anos = sorted(serie)
        return {
            "preco": preco,
            "fluxo_total": fluxo,
            "acoes": float(acoes) if acoes else None,
            "div_liquida": float(divida) - float(caixa),
            "media_div_3a": media_div,
            "fluxo_crescente": len(anos) >= 2 and serie[anos[-1]] > serie[anos[0]],
            "ts": time.time(),
        }
    except Exception as e:
        return {"erro": str(e)[:100], "ts": time.time()}


def _carregar_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _salvar_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def _montar_registro(u: dict, bruto: dict) -> dict | None:
    """Transforma os dados brutos + universo numa linha pronta para o valuation."""
    if bruto.get("erro"):
        return None
    preco = bruto.get("preco")
    fluxo = bruto.get("fluxo_total")
    acoes = bruto.get("acoes")
    if not preco or preco <= 0 or fluxo is None or not acoes or acoes <= 0:
        return None
    fluxo_por_acao = fluxo / acoes
    # Para bancos (base 'Lucro'), "dívida líquida" é depósito/funding, não
    # alavancagem operacional — o índice não é comparável, então fica vazio.
    eh_banco = u.get("base_calculo") == "Lucro"
    div_liq_ebit = None if eh_banco else ((bruto["div_liquida"] / fluxo) if fluxo > 0 else None)
    dy = dy_medio_3anos(bruto.get("media_div_3a"), preco)
    return {
        "ticker": u["ticker"],
        "nome": u.get("nome"),
        "setor": u.get("setor"),
        "citacoes": u.get("citacoes", 0),
        "base_calculo": u.get("base_calculo", "EBIT"),
        "preco_atual": preco,
        "fluxo_total": fluxo,
        "ebit_por_acao": fluxo_por_acao,
        "p_ebit": preco / fluxo_por_acao if fluxo_por_acao > 0 else None,
        "div_liq_ebit": div_liq_ebit,
        "dy_medio_3a": dy,
        "fluxo_crescente": bruto.get("fluxo_crescente", False),
    }


def buscar_dados_eua(
    tickers: list[str] = None,
    usar_cache: bool = True,
    ttl_segundos: float = CACHE_TTL_SEGUNDOS,
    progresso=None,
) -> pd.DataFrame:
    """Busca os dados do universo americano (ou de ``tickers``) prontos p/ valuation.

    Usa cache local por ticker (TTL). ``progresso`` é um callback opcional
    ``(feitos, total)`` para a barra de progresso do app. Empresas com fluxo/
    preço inválido saem. Devolve um DataFrame.
    """
    universo = {u["ticker"]: u for u in carregar_universo()}
    alvos = tickers or list(universo)
    cache = _carregar_cache() if usar_cache else {}
    agora = time.time()

    registros = []
    total = len(alvos)
    alterou = False
    for i, t in enumerate(alvos, 1):
        u = universo.get(t, {"ticker": t})
        bruto = cache.get(t)
        if not (usar_cache and bruto and (agora - bruto.get("ts", 0)) < ttl_segundos):
            bruto = _buscar_um(t, u.get("base_calculo", "EBIT"))
            cache[t] = bruto
            alterou = True
        reg = _montar_registro(u, bruto)
        if reg is not None:
            registros.append(reg)
        if progresso:
            progresso(i, total)
    if usar_cache and alterou:
        _salvar_cache(cache)

    return pd.DataFrame(registros)


def rankear_eua(
    df: pd.DataFrame,
    div_liq_ebit_max: float = DIV_LIQ_EBIT_MAX_PADRAO,
    p_ebit_minimo: float = P_EBIT_MINIMO_PADRAO,
    apenas_crescente: bool = False,
    tma: float = None,
    retorno_alvo: float = None,
    cenarios: dict = None,
) -> pd.DataFrame:
    """Roda o valuation Ciano (premissas em dólar) sobre ``df`` de buscar_dados_eua.

    Aplica os filtros de qualidade que evitam o upside-fantasma:
      - ``div_liq_ebit_max``: exclui empresas muito alavancadas (0 = sem filtro).
        Bancos (base 'Lucro') não têm dívida líquida/EBIT comparável e passam.
      - ``p_ebit_minimo``: exclui múltiplos anômalos que geram upside irreal.
      - ``apenas_crescente``: se True, mantém só as com fluxo crescente na série.
    Ordena por upside (cenário intermediário). Função pura (não acessa a rede).
    """
    tma = tma if tma is not None else PREMISSAS_EUA["tma"]
    retorno_alvo = retorno_alvo if retorno_alvo is not None else PREMISSAS_EUA["retorno_alvo_pl"]

    linhas = []
    for _, r in df.iterrows():
        preco = r.get("preco_atual")
        fluxo_acao = r.get("ebit_por_acao")
        if not preco or preco <= 0 or not fluxo_acao or fluxo_acao <= 0:
            continue
        p_ebit = r.get("p_ebit")
        if p_ebit_minimo > 0 and (p_ebit is None or p_ebit < p_ebit_minimo):
            continue
        dl_ebit = r.get("div_liq_ebit")
        eh_banco = r.get("base_calculo") == "Lucro"
        if div_liq_ebit_max > 0 and not eh_banco:
            if dl_ebit is None or dl_ebit > div_liq_ebit_max:
                continue
        if apenas_crescente and not r.get("fluxo_crescente"):
            continue

        res = calcular_valuation_completo(
            ticker=str(r["ticker"]), ebit_atual=fluxo_acao, acoes_em_circulacao=1.0,
            preco_atual=preco, tma=tma, retorno_alvo=retorno_alvo, cenarios=cenarios,
        )
        i = res["resultados"]["intermediario"]
        dy = r.get("dy_medio_3a")
        linhas.append({
            "ticker": r["ticker"],
            "nome": r.get("nome"),
            "setor": r.get("setor"),
            "upside_pct": round(i.upside_percentual, 1),
            "veredito": res["veredito"],
            "preco": round(preco, 2),
            "justo": round(i.valuation_final_por_acao, 2),
            "div_liq_ebit": round(dl_ebit, 2) if dl_ebit is not None else None,
            "p_ebit": round(p_ebit, 1) if p_ebit is not None else None,
            "dy_medio_3a_pct": round(dy * 100, 2) if dy is not None else None,
            "base": r.get("base_calculo"),
            "crescente": bool(r.get("fluxo_crescente")),
            "citacoes": int(r.get("citacoes") or 0),
        })

    out = pd.DataFrame(linhas)
    if not out.empty:
        out = out.sort_values("upside_pct", ascending=False).reset_index(drop=True)
    return out
