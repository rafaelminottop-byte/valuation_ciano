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


# ---------------------------------------------------------------------------
# Estudo: IFIX x média de 200 dias x NTN-B 10 anos
# O Yahoo não tem o histórico do índice IFIX; usamos o XFIX11 (ETF que o replica,
# desde nov/2020, proventos reinvestidos). Amostra curta: leitura é indício, não regra.
# ---------------------------------------------------------------------------
CACHE_ESTUDO = Path(__file__).resolve().parent / ".cache" / "fii_estudo_v1.pkl"
HORIZONTES = (63, 126, 252)   # ~3, 6 e 12 meses em pregões
FAIXAS = [(-99, -8, "mais de 8% abaixo"), (-8, -3, "3% a 8% abaixo"), (-3, 3, "perto (±3%)"),
          (3, 8, "3% a 8% acima"), (8, 99, "mais de 8% acima")]


def _ntnb_10a_historico() -> pd.Series:
    """Taxa da NTN-B (Tesouro IPCA+) com vencimento mais próximo de 10 anos, por dia."""
    import macro
    r = requests.get(macro.URL_TESOURO_TAXAS, headers=macro.HEADERS, timeout=90)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.content.decode("latin1")), sep=";")
    df = df[df["Tipo Titulo"] == "Tesouro IPCA+"].copy()
    df["d"] = pd.to_datetime(df["Data Base"], format="%d/%m/%Y")
    df["v"] = pd.to_datetime(df["Data Vencimento"], format="%d/%m/%Y")
    df["t"] = df["Taxa Compra Manha"].astype(str).str.replace(",", ".").astype(float)
    df["dist"] = ((df["v"] - df["d"]).dt.days / 365.25 - 10).abs()
    return df.sort_values("dist").groupby("d")["t"].first().sort_index()


def estudo_ifix(forcar: bool = False) -> dict:
    if not forcar and CACHE_ESTUDO.exists() and time.time() - CACHE_ESTUDO.stat().st_mtime < TTL:
        try:
            return pd.read_pickle(CACHE_ESTUDO)
        except Exception:
            pass
    import yfinance as yf
    px = yf.download("XFIX11.SA", start="2020-01-01", progress=False, auto_adjust=True)["Close"].squeeze().dropna()
    if px.empty:
        raise RuntimeError("Yahoo não devolveu o XFIX11.")
    ntnb = _ntnb_10a_historico()
    d = pd.DataFrame({"preco": px})
    d["mm200"] = px.rolling(200).mean()
    d["dist"] = (px / d["mm200"] - 1) * 100
    d["ntnb"] = ntnb.reindex(px.index).ffill()
    for h in HORIZONTES:
        d[f"r{h}"] = (px.shift(-h) / px - 1) * 100
    v = d.dropna(subset=["dist"])

    # toques: 1º dia em que o preço entra a ±1,5% da média (sem toque nos 20 pregões anteriores)
    t = v["dist"].abs() <= 1.5
    ep = t & ~t.shift(1, fill_value=False).rolling(20).max().fillna(0).astype(bool)
    toques = v[ep].copy()
    toques["veio"] = ["de cima" if a > 0 else "de baixo" for a in v["dist"].shift(20)[ep]]

    faixas = []
    for a, b, nome in FAIXAS:
        s = v[(v["dist"] >= a) & (v["dist"] < b)]
        faixas.append({"Distância da média": nome, "Dias": len(s),
                       **{f"{h // 21} meses": s[f"r{h}"].mean() for h in HORIZONTES}})

    sem = d[["preco", "ntnb"]].resample("W").last().dropna()
    mes = d[["preco", "ntnb"]].resample("ME").last().dropna()
    out = {
        "serie": d, "toques": toques, "faixas": pd.DataFrame(faixas),
        "base": {f"{h // 21} meses": float(v[f"r{h}"].mean()) for h in HORIZONTES},
        "corr_sem": float((sem["preco"].pct_change() * 100).corr(sem["ntnb"].diff())),
        "corr_mes": float((mes["preco"].pct_change() * 100).corr(mes["ntnb"].diff())),
        "hoje": v.iloc[-1],
    }
    try:
        CACHE_ESTUDO.parent.mkdir(exist_ok=True)
        pd.to_pickle(out, CACHE_ESTUDO)
    except OSError:
        pass
    return out
