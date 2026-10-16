"""
Setor de cada ação da B3 — o Fundamentus não traz essa informação, então
buscamos no Yahoo (ticker + '.SA') e guardamos um mapa em cache (data/setores_b3.json).

Padroniza nos mesmos 11 setores do mercado americano (em inglês, como o Yahoo
devolve), para a tela traduzir e filtrar igual ao screener dos EUA.
A 1ª montagem é lenta (uma chamada por ticker); depois vem tudo do cache.
"""
import json
import socket
import time
from pathlib import Path

import yfinance as yf

MAPA_PATH = Path(__file__).resolve().parent / "data" / "setores_b3.json"


def _forcar_ipv4():
    _orig = socket.getaddrinfo
    socket.getaddrinfo = lambda h, p, *a, **k: [x for x in _orig(h, p, socket.AF_INET, *a[1:], **k)]


def carregar_mapa() -> dict:
    if MAPA_PATH.exists():
        try:
            return json.loads(MAPA_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _salvar_mapa(mapa: dict) -> None:
    try:
        MAPA_PATH.parent.mkdir(exist_ok=True)
        MAPA_PATH.write_text(json.dumps(mapa, ensure_ascii=False, indent=0), encoding="utf-8")
    except OSError:
        pass


def garantir_setores(tickers, progresso=None) -> dict:
    """Devolve {ticker: setor} para os tickers pedidos, buscando no Yahoo só os
    que faltam no cache e persistindo o resultado."""
    mapa = carregar_mapa()
    faltam = [t for t in tickers if t not in mapa]
    if faltam:
        _forcar_ipv4()
        for i, t in enumerate(faltam, 1):
            setor = None
            try:
                info = yf.Ticker(f"{t}.SA").info or {}
                setor = info.get("sector")
            except Exception:  # noqa: BLE001
                setor = None
            mapa[t] = setor or "—"
            if progresso:
                progresso(i, len(faltam))
            time.sleep(0.05)
        _salvar_mapa(mapa)
    return {t: mapa.get(t, "—") for t in tickers}


if __name__ == "__main__":
    # Pré-aquece o cache com todos os tickers líquidos do Fundamentus.
    from fundamentus_scraper import baixar_tabela_fundamentus
    df = baixar_tabela_fundamentus()
    tks = list(df["ticker"].astype(str).str.upper().unique())
    print(f"buscando setor de {len(tks)} tickers da B3...")
    m = garantir_setores(tks, progresso=lambda f, t: print(f"  {f}/{t}", end="\r") if f % 25 == 0 else None)
    import collections
    c = collections.Counter(m.values())
    print("\npronto. setores:")
    for s, n in c.most_common():
        print(f"  {n:3d}  {s}")
