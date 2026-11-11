"""
Panorama de FIIs — tabela do Fundamentus (fii_resultado.php).

Entrega, por segmento: quantos fundos, P/VP mediano, dividend yield mediano e
liquidez — para mostrar onde está o desconto e onde o yield paga mais.
Cache local de 24h (mesmo padrão do fundamentus_scraper).
"""
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.fundamentus.com.br/fii_resultado.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
CACHE = Path(__file__).resolve().parent / ".cache" / "fii_v1.pkl"
TTL = 24 * 3600

# Filtros mínimos para o panorama não ser contaminado por fundo morto/sem negócio.
LIQUIDEZ_MIN = 200_000   # R$/dia
PVP_MIN, PVP_MAX = 0.2, 3.0


def _num(s: pd.Series) -> pd.Series:
    """'1.234,56' / '12,3%' -> float (percentual vira fração)."""
    t = s.astype(str).str.strip()
    pct = t.str.contains("%")
    t = t.str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.replace("%", "", regex=False)
    n = pd.to_numeric(t, errors="coerce")
    return n.where(~pct, n / 100)


def baixar(forcar: bool = False) -> pd.DataFrame:
    if not forcar and CACHE.exists() and time.time() - CACHE.stat().st_mtime < TTL:
        try:
            return pd.read_pickle(CACHE)
        except Exception:
            pass
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = "iso-8859-1"
    # thousands=None: mantém o texto cru ("1.234", "5,60") e a conversão é nossa
    df = pd.read_html(StringIO(r.text), thousands=None)[0].astype(str)
    ren = {}
    for c in df.columns:
        k = c.lower()
        ren[c] = ("Cotacao" if k.startswith("cota") else "Vacancia" if k.startswith("vac")
                  else "Imoveis" if k.startswith("qtd") else c)
    df = df.rename(columns=ren)
    for c in ["Cotacao", "FFO Yield", "Dividend Yield", "P/VP", "Valor de Mercado", "Liquidez",
              "Imoveis", "Cap Rate", "Vacancia"]:
        if c in df.columns:
            df[c] = _num(df[c])
    df = df.rename(columns={"Dividend Yield": "DY"})
    try:
        CACHE.parent.mkdir(exist_ok=True)
        df.to_pickle(CACHE)
    except OSError:
        pass
    return df


def filtrar(df: pd.DataFrame) -> pd.DataFrame:
    """Só fundos com negociação real e P/VP plausível."""
    d = df[(df["Liquidez"] >= LIQUIDEZ_MIN) & df["P/VP"].between(PVP_MIN, PVP_MAX)]
    return d[d["DY"] > 0].copy()


def por_segmento(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("Segmento").agg(
        Fundos=("Papel", "count"),
        PVP=("P/VP", "median"),
        DY=("DY", "median"),
        Liquidez=("Liquidez", "sum"),
        Valor=("Valor de Mercado", "sum"),
    ).reset_index()
    return g.sort_values("Valor", ascending=False)


def resumo(df: pd.DataFrame) -> dict:
    return {"fundos": len(df), "pvp": float(df["P/VP"].median()),
            "dy": float(df["DY"].median()),
            "abaixo_vp": float((df["P/VP"] < 1).mean())}
