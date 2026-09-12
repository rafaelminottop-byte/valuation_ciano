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
CACHE_FILE = CACHE_DIR / "ibov_ciclo_v3.json"
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
            "p0": vals[i0], "p1": vals[i1], "amp": amp, "meses": i1 - i0,
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

    # --- Projeção: upside e tempo estimados, pela estatística das ALTAS passadas ---
    # Frame: a perna de alta atual = do último FUNDO (pivô L) até agora.
    proj = None
    import statistics as _st
    fundos = [(i, t) for i, t in piv if t == "L"]
    altas_hist = [l for l in legs if l["tipo"] == "alta"]
    if fundos and len(altas_hist) >= 3:
        i_fundo = fundos[-1][0]
        preco_fundo = vals[i_fundo]
        amp_atual = (atual - preco_fundo) / preco_fundo * 100
        meses_atual = (n - 1) - i_fundo
        # histórico: altas MODERNAS (pós-2008; as dos anos 90/2000 tinham inflação
        # residual e amplitudes de +300/+700% que não se repetem) anteriores à atual
        hist = [l for l in altas_hist if "2008-01" <= l["de"] < datas[i_fundo][:7]]
        amps = sorted(l["amp"] for l in hist)
        durs = sorted(l["meses"] for l in hist)
        if amps and durs:
            amp_med, amp_max = _st.median(amps), max(amps)
            dur_med, dur_max = _st.median(durs), max(durs)
            alvo_med = preco_fundo * (1 + amp_med / 100)
            alvo_max = preco_fundo * (1 + amp_max / 100)
            up_med = (alvo_med / atual - 1) * 100
            up_max = (alvo_max / atual - 1) * 100
            madura = amp_atual >= amp_med or meses_atual >= dur_med
            if up_med <= 2:
                upside_txt = (f"Limitado. A alta (+{amp_atual:.0f}%) já superou a amplitude típica das "
                              f"altas modernas (+{amp_med:.0f}%). Upside adicional só num ciclo forte "
                              f"(~+{up_max:.0f}%, alvo ~{_fmt(alvo_max)}).")
            else:
                upside_txt = (f"~+{up_med:.0f}% até a amplitude típica (alvo ~{_fmt(alvo_med)}); "
                              f"num ciclo forte, até +{up_max:.0f}% (~{_fmt(alvo_max)}).")
            if meses_atual >= dur_max:
                tempo_txt = (f"{meses_atual} meses — já é a alta mais LONGA da era moderna "
                             f"(máx anterior {dur_max:.0f}m). Madura/tardia.")
            elif meses_atual >= dur_med:
                tempo_txt = (f"{meses_atual} meses — acima da duração típica ({dur_med:.0f}m); restam "
                             f"~{dur_max - meses_atual:.0f}m até o ciclo mais longo já visto ({dur_max:.0f}m).")
            else:
                tempo_txt = f"{meses_atual} meses — restam ~{dur_med - meses_atual:.0f}m até a duração típica ({dur_med:.0f}m)."
            veredito = ("Madura / tardia" if meses_atual >= dur_max
                        else "Avançada" if (amp_atual >= amp_med or meses_atual >= dur_med)
                        else "Jovem")
            proj = {
                "veredito": veredito, "upside_txt": upside_txt, "tempo_txt": tempo_txt,
                "desde": datas[i_fundo][:7], "fundo": preco_fundo,
                "amp_atual": amp_atual, "meses_atual": meses_atual,
                "amp_hist_med": amp_med, "amp_hist_max": amp_max,
                "dur_hist_med": dur_med, "dur_hist_max": dur_max,
                "alvo_med": alvo_med, "alvo_max": alvo_max,
                "upside_med": up_med, "upside_max": up_max,
                "restante_meses_med": dur_med - meses_atual,
                "restante_meses_max": dur_max - meses_atual,
                "madura": madura,
            }

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
        "projecao": proj,
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
        p = d.get("projecao")
        if p:
            print(f"PROJEÇÃO: alta atual +{p['amp_atual']:.0f}% em {p['meses_atual']}m "
                  f"(desde {p['desde']}, fundo {_fmt(p['fundo'])})")
            print(f"  altas históricas: mediana +{p['amp_hist_med']:.0f}%/{p['dur_hist_med']:.0f}m, "
                  f"máx +{p['amp_hist_max']:.0f}%/{p['dur_hist_max']:.0f}m")
            print(f"  UPSIDE até alvo mediano: {p['upside_med']:+.0f}% (~{_fmt(p['alvo_med'])}) | "
                  f"até alvo máx: {p['upside_max']:+.0f}% (~{_fmt(p['alvo_max'])})")
            print(f"  TEMPO restante estimado: {p['restante_meses_med']:.0f}m (mediana) a "
                  f"{p['restante_meses_max']:.0f}m (máx) | madura={p['madura']}")
        print("pernas:", len(d["legs"]), "| pivôs:", len(d["pivos"]))
        for l in d["legs"][-6:]:
            print(f"  {'ALTA ' if l['tipo']=='alta' else 'BAIXA'} {l['de']}->{l['ate']} {l['amp']:+.0f}%")
