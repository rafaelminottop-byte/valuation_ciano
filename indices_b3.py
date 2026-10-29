"""
Composição dos índices da B3 (carteira teórica), direto da fonte oficial.

Busca os componentes de IBOV, SMLL (Small Caps) e IFIX (fundos imobiliários)
pela API pública da B3. É a fonte autoritativa — a carteira muda só nas
reavaliações trimestrais, então o cache é longo (24h), com degradação
elegante (se a B3 cair, devolve o último dado bom).
"""
import base64
import json
import time
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "indices_b3.json"
CACHE_TTL = 24 * 60 * 60  # 24h
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"),
           "Accept": "application/json"}

INDICES = {"IBOV": "Ibovespa", "SMLL": "Small Caps", "IFIX": "Fundos imobiliários (IFIX)"}


def _buscar_b3(indice: str) -> list:
    payload = {"language": "pt-br", "pageNumber": 1, "pageSize": 200, "index": indice, "segment": "1"}
    b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    url = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/{b64}"
    r = requests.get(url, headers=HEADERS, timeout=25, verify=False)
    r.raise_for_status()
    res = r.json().get("results", [])
    tickers = [str(x.get("cod", "")).strip().upper() for x in res if x.get("cod")]
    return sorted(set(tickers))


def _carregar_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {}


def componentes(indice: str, usar_cache: bool = True) -> dict:
    """Devolve {tickers, fonte, aviso?} para um índice (IBOV/SMLL/IFIX)."""
    indice = indice.upper()
    cache = _carregar_cache()
    entrada = cache.get(indice)
    if usar_cache and entrada and (time.time() - entrada.get("ts", 0) < CACHE_TTL):
        return {"tickers": entrada["tickers"], "fonte": "B3 (carteira teórica)", "cacheado": True}
    try:
        tickers = _buscar_b3(indice)
        if len(tickers) < 10:  # coleta quebrada
            raise RuntimeError(f"Carteira {indice} veio curta demais ({len(tickers)}).")
    except Exception as e:  # noqa: BLE001
        if entrada and entrada.get("tickers"):
            return {"tickers": entrada["tickers"], "fonte": "B3 (carteira teórica)",
                    "aviso": "B3 indisponível agora; usando a última carteira salva."}
        return {"tickers": [], "fonte": "B3", "erro": f"Falha ao buscar a carteira {indice}: {e}"}

    cache[indice] = {"tickers": tickers, "ts": time.time()}
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    return {"tickers": tickers, "fonte": "B3 (carteira teórica)"}


if __name__ == "__main__":
    for idx in INDICES:
        d = componentes(idx, usar_cache=False)
        print(idx, "->", len(d.get("tickers", [])), "tickers", d.get("aviso") or d.get("erro") or "")
