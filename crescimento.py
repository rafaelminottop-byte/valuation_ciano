"""
Crescimento de resultados (5 anos) por ação da B3 — EBIT, lucro líquido e LPA.

Fonte: demonstrativo anual do Yahoo Finance (income statement), que traz ~5
exercícios. Calcula o CAGR de cada linha (começo→fim) e a direção recente.
Usado pelo Screener (ranking de crescimento) e pela alavanca Lucro dos Cenários.

Cache por ticker (as chamadas do Yahoo são lentas e os balanços mudam só a
cada trimestre), com degradação elegante.
"""
import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "crescimento.json"
CACHE_TTL = 7 * 24 * 60 * 60  # 7 dias

_LINHAS_EBIT = ["EBIT", "Operating Income"]
_LINHAS_LUCRO = ["Net Income", "Net Income Common Stockholders"]
_LINHAS_LPA = ["Diluted EPS", "Basic EPS"]


def _cagr(serie: list):
    """CAGR do mais antigo ao mais recente; None se base/fim não positivos."""
    s = [float(x) for x in serie if x is not None and x == x]
    if len(s) < 2:
        return None
    ini, fim = s[0], s[-1]
    if ini <= 0 or fim <= 0:
        return None
    return round(((fim / ini) ** (1 / (len(s) - 1)) - 1) * 100, 1)


def _linha(fin: pd.DataFrame, nomes: list, cols: list) -> list:
    for nome in nomes:
        if nome in fin.index:
            vals = [fin.loc[nome, c] for c in cols]
            if any(v == v for v in vals):  # tem ao menos um não-NaN
                return [None if (v != v) else float(v) for v in vals]
    return []


def _coletar_ticker(ticker: str) -> dict:
    t = yf.Ticker(f"{ticker.strip().upper()}.SA")
    fin = t.income_stmt
    if fin is None or fin.empty:
        return {"ebit": None, "lucro": None, "lpa": None, "anos": 0}
    cols = sorted(fin.columns)  # datas em ordem crescente (mais antigo -> recente)
    ebit = _linha(fin, _LINHAS_EBIT, cols)
    lucro = _linha(fin, _LINHAS_LUCRO, cols)
    lpa = _linha(fin, _LINHAS_LPA, cols)
    lucro_lim = [v for v in lucro if v is not None]  # ignora anos sem dado (NaN)
    return {"ebit": _cagr(ebit), "lucro": _cagr(lucro), "lpa": _cagr(lpa),
            "lucro_cai": len(lucro_lim) >= 2 and lucro_lim[-1] < lucro_lim[0],
            "anos": len(cols)}


def _media_cagr(d: dict):
    vs = [d[k] for k in ("ebit", "lucro", "lpa") if d.get(k) is not None]
    return round(sum(vs) / len(vs), 1) if vs else None


def _carregar_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {}


def _salvar_cache(cache: dict) -> None:
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def crescimento_lote(tickers, usar_cache: bool = True, progresso=None) -> pd.DataFrame:
    """DataFrame por ticker: cagr de ebit/lucro/lpa (%), média e flag lucro_cai."""
    cache = _carregar_cache()
    linhas, agora = [], time.time()
    total = len(tickers)
    for i, tk in enumerate(tickers):
        tk = tk.strip().upper()
        ent = cache.get(tk)
        if usar_cache and ent and (agora - ent.get("ts", 0) < CACHE_TTL):
            d = ent["dados"]
        else:
            try:
                d = _coletar_ticker(tk)
            except Exception:  # noqa: BLE001
                d = (ent or {}).get("dados") or {"ebit": None, "lucro": None, "lpa": None, "anos": 0}
            cache[tk] = {"dados": d, "ts": agora}
        linhas.append({"ticker": tk, "ebit_cagr": d.get("ebit"), "lucro_cagr": d.get("lucro"),
                       "lpa_cagr": d.get("lpa"), "media_cagr": _media_cagr(d),
                       "lucro_cai": d.get("lucro_cai", False), "anos": d.get("anos", 0)})
        if progresso:
            progresso((i + 1) / total)
    _salvar_cache(cache)
    return pd.DataFrame(linhas)


def crescimento_agregado(tickers, usar_cache: bool = True) -> dict:
    """Resumo do conjunto (ex.: Ibov): CAGR mediano de lucro/LPA e % de empresas
    com lucro caindo — alimenta a alavanca Lucro."""
    df = crescimento_lote(tickers, usar_cache=usar_cache)
    val = df[df["lucro_cagr"].notna()]
    if val.empty:
        return {"lucro_cagr_mediano": None, "lpa_cagr_mediano": None,
                "pct_caindo": None, "n": 0}
    # média APARADA (10% em cada ponta): a média crua é inflada por empresas que
    # saíram de base ~zero (+400% de CAGR); aparar dá uma média honesta.
    vv = sorted(float(x) for x in val["lucro_cagr"].tolist())
    k = max(1, int(len(vv) * 0.1)) if len(vv) >= 5 else 0
    apar = vv[k:len(vv) - k] if k else vv
    medio_apar = round(sum(apar) / len(apar), 1) if apar else None
    return {
        "lucro_cagr_mediano": round(float(val["lucro_cagr"].median()), 1),
        "lucro_cagr_medio": medio_apar,
        "lpa_cagr_mediano": round(float(df["lpa_cagr"].median()), 1) if df["lpa_cagr"].notna().any() else None,
        "pct_caindo": round(float(df["lucro_cai"].mean()) * 100, 0),
        "n": int(len(val)),
    }


if __name__ == "__main__":
    df = crescimento_lote(["WEGE3", "VALE3", "ITUB4", "PRIO3"], usar_cache=False)
    print(df.to_string(index=False))
    print("\nAgregado:", crescimento_agregado(["WEGE3", "VALE3", "ITUB4", "PRIO3"]))
