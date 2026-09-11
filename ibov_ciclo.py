"""
Ciclo do Ibovespa — leitura de ciclos de mercado a partir da série longa.

Fonte: Yahoo Finance (^BVSP), mensal, desde os anos 90. Detecta os topos e
fundos maiores (extremos numa janela), separa o CICLO GRANDE (secular) do
CICLO PEQUENO (perna atual) e mede o "esticamento" vs a média longa — sem
prometer "mediana de ciclo", que é métrica frágil.

Cache local com TTL (a série mensal muda devagar).
"""

import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "ibov_ciclo_v2.json"
# Antes do Plano Real (jul/1994) o Ibov estava em outra moeda (hiperinflação),
# com valores minúsculos que distorcem a análise. Começamos em 1995.
DATA_INICIAL = "1995-01-01"
CACHE_TTL_SEGUNDOS = 6 * 3600  # 6h


def _pivos(vals: list[float], N: int = 9) -> list[tuple[int, str]]:
    """Topos (H) e fundos (L) como extremos numa janela de +/- N meses."""
    marks: list[tuple[int, str]] = []
    for i in range(len(vals)):
        w = vals[max(0, i - N): i + N + 1]
        if vals[i] == max(w):
            marks.append((i, "H"))
        elif vals[i] == min(w):
            marks.append((i, "L"))
    piv: list[tuple[int, str]] = []
    for i, t in marks:
        if piv and piv[-1][1] == t:
            if (t == "H" and vals[i] > vals[piv[-1][0]]) or (t == "L" and vals[i] < vals[piv[-1][0]]):
                piv[-1] = (i, t)
        else:
            piv.append((i, t))
    return piv


def _fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


def _analisar(serie: list[dict]) -> dict:
    vals = [s["valor"] for s in serie]
    datas = [s["data"] for s in serie]
    n = len(vals)
    atual = vals[-1]
    ath = max(vals)
    piv = _pivos(vals, N=9)

    # pernas entre pivôs
    legs = []
    for k in range(1, len(piv)):
        i0, _ = piv[k - 1]
        i1, _ = piv[k]
        amp = (vals[i1] - vals[i0]) / vals[i0] * 100
        legs.append({
            "de": datas[i0][:7], "ate": datas[i1][:7],
            "p0": vals[i0], "p1": vals[i1], "amp": amp,
            "tipo": "alta" if amp >= 0 else "baixa",
        })

    # ciclo pequeno: do último pivô até agora
    peq = {}
    if piv:
        i0, t0 = piv[-1]
        amp = (atual - vals[i0]) / vals[i0] * 100
        peq = {
            "tipo": "alta" if t0 == "L" else "baixa",
            "desde": datas[i0][:7], "preco_pivo": vals[i0], "amp": amp,
            "meses": n - 1 - i0,
        }

    # esticamento vs média longa (24 meses)
    janela = min(24, n)
    media_longa = sum(vals[-janela:]) / janela
    desvio = (atual - media_longa) / media_longa * 100

    # narrativas
    na_maxima = atual >= ath * 0.99
    if na_maxima:
        grande = ("Em MÁXIMA HISTÓRICA — alta secular em rompimento, sem resistência acima. "
                  f"({_fmt(atual)} pts).")
    else:
        grande = (f"Alta secular. Está a {(atual/ath-1)*100:.0f}% da máxima histórica "
                  f"(~{_fmt(ath)}); acima disso é céu aberto.")

    if peq:
        seta = "⬆️ Alta" if peq["tipo"] == "alta" else "⬇️ Baixa"
        pequeno = (f"{seta} desde {peq['desde']} ({_fmt(peq['preco_pivo'])}): "
                   f"{peq['amp']:+.0f}% até ~{_fmt(atual)}, em ~{peq['meses']} meses.")
    else:
        pequeno = "Sem pivô recente detectado."

    est_nota = ("muito esticado — movimento maduro" if desvio > 15
                else "esticado" if desvio > 7
                else "próximo da média" if desvio > -7
                else "abaixo da média — barato")

    return {
        "serie": serie,
        "atual": atual,
        "ath": ath,
        "pivos": [{"data": datas[i], "valor": vals[i], "tipo": t} for i, t in piv],
        "legs": legs,
        "grande": grande,
        "pequeno": pequeno,
        "esticamento": {"media": media_longa, "desvio_pct": desvio, "nota": est_nota},
        "erro": None,
    }


def _coletar() -> dict:
    try:
        h = yf.Ticker("^BVSP").history(period="max", interval="1mo")
        if h is None or h.empty:
            return {"erro": "Yahoo não retornou dados do ^BVSP."}
        fech = h["Close"].dropna()
        serie = [{"data": d.strftime("%Y-%m-%d"), "valor": float(v)} for d, v in fech.items()]
        serie = [s for s in serie if s["data"] >= DATA_INICIAL]  # remove era pré-Real
        if len(serie) < 60:
            return {"erro": "Série do Ibovespa muito curta."}
        return _analisar(serie)
    except Exception as e:  # noqa: BLE001
        return {"erro": f"Falha ao buscar/analisar o Ibovespa: {e}"}


def buscar_ciclo_ibov(usar_cache: bool = True) -> dict:
    if usar_cache and CACHE_FILE.exists():
        try:
            if time.time() - CACHE_FILE.stat().st_mtime < CACHE_TTL_SEGUNDOS:
                return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    dados = _coletar()
    if not dados.get("erro"):
        try:
            CACHE_DIR.mkdir(exist_ok=True)
            CACHE_FILE.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    return dados


if __name__ == "__main__":
    d = buscar_ciclo_ibov(usar_cache=False)
    if d.get("erro"):
        print("ERRO:", d["erro"])
    else:
        print("atual:", _fmt(d["atual"]), "| ath:", _fmt(d["ath"]))
        print("GRANDE:", d["grande"])
        print("PEQUENO:", d["pequeno"])
        print("esticamento:", f"{d['esticamento']['desvio_pct']:+.0f}%", d["esticamento"]["nota"])
        print("pernas:", len(d["legs"]), "| pivôs:", len(d["pivos"]))
        for l in d["legs"][-6:]:
            print(f"  {'ALTA ' if l['tipo']=='alta' else 'BAIXA'} {l['de']}->{l['ate']} {l['amp']:+.0f}%")
