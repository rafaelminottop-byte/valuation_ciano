"""
Agregado de EBIT e Lucro líquido por universo (Ibovespa, Small Caps) e por setor.

Pergunta que responde: os lucros/EBIT das empresas da bolsa, no conjunto, estão
subindo ou caindo ano a ano? Soma os valores absolutos (R$) de uma CESTA FIXA
(só empresas com série completa no período), para que a comparação ano-a-ano seja
honesta e imune ao problema de "base baixa" que distorce CAGRs percentuais.

Fonte: demonstrativo anual do Yahoo Finance (mesma do módulo crescimento).
Cache próprio por ticker (guarda a série anual, não só o CAGR).
"""
import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

import crescimento as _cr

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "agregado_lucros.json"
CACHE_TTL = 7 * 24 * 60 * 60  # 7 dias

_SETOR_PT = {
    "Basic Materials": "Commodities/Materiais", "Energy": "Petróleo/Gás",
    "Financial Services": "Bancos/Financeiro", "Utilities": "Elétricas/Saneamento",
    "Consumer Defensive": "Consumo básico", "Consumer Cyclical": "Varejo/Consumo cíclico",
    "Industrials": "Indústria", "Real Estate": "Imobiliário/Construção",
    "Communication Services": "Comunicação", "Healthcare": "Saúde", "Technology": "Tecnologia",
}


def _setores() -> dict:
    try:
        return json.loads((Path(__file__).resolve().parent / "data" / "setores_b3.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _serie_anual(ticker: str) -> dict:
    """{ano: {'ebit': x, 'lucro': y}} em R$, a partir do income statement anual."""
    t = yf.Ticker(f"{ticker.strip().upper()}.SA")
    fin = t.income_stmt
    if fin is None or fin.empty:
        return {}
    cols = sorted(fin.columns)  # mais antigo -> recente
    ebit = _cr._linha(fin, _cr._LINHAS_EBIT, cols)
    lucro = _cr._linha(fin, _cr._LINHAS_LUCRO, cols)
    out = {}
    for i, c in enumerate(cols):
        ano = c.year
        e = ebit[i] if i < len(ebit) else None
        l = lucro[i] if i < len(lucro) else None
        out[ano] = {"ebit": (None if (e is None or e != e) else float(e)),
                    "lucro": (None if (l is None or l != l) else float(l))}
    return out


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


def coletar_series(tickers, usar_cache: bool = True, progresso=None) -> dict:
    """{ticker: {ano: {ebit, lucro}}} para a lista, com cache por ticker."""
    cache = _carregar_cache()
    agora = time.time()
    res, total = {}, len(tickers)
    for i, tk in enumerate(tickers):
        tk = tk.strip().upper()
        ent = cache.get(tk)
        if usar_cache and ent and (agora - ent.get("ts", 0) < CACHE_TTL):
            serie = ent["serie"]
        else:
            try:
                serie = _serie_anual(tk)
            except Exception:  # noqa: BLE001
                serie = (ent or {}).get("serie") or {}
            cache[tk] = {"serie": serie, "ts": agora}
        res[tk] = {int(a): v for a, v in serie.items()}
        if progresso:
            progresso((i + 1) / total, tk)
    _salvar_cache(cache)
    return res


def _cesta_fixa(series: dict, anos: list) -> list:
    """Tickers com EBIT e lucro não-nulos em TODOS os anos do período (comparação justa)."""
    cesta = []
    for tk, serie in series.items():
        if all(serie.get(a) and serie[a].get("ebit") is not None
               and serie[a].get("lucro") is not None for a in anos):
            cesta.append(tk)
    return cesta


def _anos_comuns(series: dict, n: int = 4) -> list:
    """Os n anos mais recentes com cobertura razoável entre os tickers."""
    from collections import Counter
    cont = Counter()
    for serie in series.values():
        for a in serie:
            cont[a] += 1
    if not cont:
        return []
    anos = sorted(a for a, c in cont.items() if c >= max(5, 0.4 * len(series)))
    return anos[-n:]


def agregar(tickers, usar_cache: bool = True, n_anos: int = 4, progresso=None) -> dict:
    """Agregado (soma R$) de EBIT e lucro ano a ano, da cesta fixa, + quebra por setor."""
    series = coletar_series(tickers, usar_cache=usar_cache, progresso=progresso)
    anos = _anos_comuns(series, n=n_anos)
    if not anos:
        return {"erro": "sem dados suficientes", "anos": [], "ebit": [], "lucro": []}
    cesta = _cesta_fixa(series, anos)
    setores = _setores()

    ebit_tot = {a: 0.0 for a in anos}
    lucro_tot = {a: 0.0 for a in anos}
    por_setor = {}  # setor -> {ano: {ebit, lucro}}, cesta fixa própria do setor
    setor_tickers = {}
    for tk in cesta:
        s = series[tk]
        for a in anos:
            ebit_tot[a] += s[a]["ebit"]
            lucro_tot[a] += s[a]["lucro"]
        setor = _SETOR_PT.get(setores.get(tk, ""), "Outros")
        setor_tickers.setdefault(setor, []).append(tk)

    for setor, tks in setor_tickers.items():
        agg = {a: {"ebit": 0.0, "lucro": 0.0} for a in anos}
        for tk in tks:
            for a in anos:
                agg[a]["ebit"] += series[tk][a]["ebit"]
                agg[a]["lucro"] += series[tk][a]["lucro"]
        por_setor[setor] = {"anos": anos, "n": len(tks),
                            "ebit": [agg[a]["ebit"] for a in anos],
                            "lucro": [agg[a]["lucro"] for a in anos]}

    def _var(serie):
        return None if len(serie) < 2 or serie[-2] == 0 else (serie[-1] / serie[-2] - 1) * 100

    ebit_list = [ebit_tot[a] for a in anos]
    lucro_list = [lucro_tot[a] for a in anos]
    return {
        "erro": None, "anos": anos, "n_cesta": len(cesta), "n_total": len(tickers),
        "ebit": ebit_list, "lucro": lucro_list,
        "var_ebit": _var(ebit_list), "var_lucro": _var(lucro_list),
        "por_setor": por_setor,
    }
