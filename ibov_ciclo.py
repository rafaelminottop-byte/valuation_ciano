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
CACHE_FILE = CACHE_DIR / "ibov_ciclo_v5.json"
# Antes do Plano Real (jul/1994) o Ibov estava em outra moeda (hiperinflação),
# com valores minúsculos que distorcem a análise. Começamos em 1995.
DATA_INICIAL = "1995-01-01"
CACHE_TTL_SEGUNDOS = 24 * 3600  # 24h


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
            # retornos de 12 meses da PRÓPRIA série moderna (pós-2008) -> ritmo realista.
            # (annualizar pernas curtas de alta dá taxas absurdas; o retorno anual do
            #  índice é a base honesta para projetar fins de ano.)
            from datetime import date as _date
            base_i = next((k for k, s in enumerate(serie) if s["data"] >= "2008-01-01"), 0)
            ret12 = [(vals[k] / vals[k - 12] - 1) * 100 for k in range(max(12, base_i), n)]
            g_base = _st.median(ret12) if ret12 else 0.0            # ano típico
            g_forte = (_st.quantiles(ret12, n=4)[2] if len(ret12) >= 4 else max(ret12)) \
                if ret12 else 0.0                                    # ano forte (~p75)
            ultima = _date.fromisoformat(datas[-1])
            anos_proj = []
            for ano in (2027, 2028):
                alvo_dez = _date(ano, 12, 1)
                meses_frente = (alvo_dez.year - ultima.year) * 12 + (alvo_dez.month - ultima.month)
                if meses_frente <= 0:
                    continue
                base = atual * (1 + g_base / 100) ** (meses_frente / 12)
                forte = atual * (1 + g_forte / 100) ** (meses_frente / 12)
                anos_proj.append({
                    "ano": ano, "meses_frente": meses_frente,
                    "base": base, "forte": forte,
                    "up_base": (base / atual - 1) * 100, "up_forte": (forte / atual - 1) * 100,
                })
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
                "g_anual_base": g_base, "g_anual_forte": g_forte,
                "anos": anos_proj,
            }

    # --- Anatomia dos topos: o que o Ibov fez depois de cada topo historico ---
    import statistics as _st2
    anatomia = []
    for i, t in piv:
        if t != "H":
            continue
        pv = vals[i]
        def _ret(k):
            return (vals[i + k] / pv - 1) * 100 if i + k < n else None
        low = min(vals[i:])
        qmax = (low / pv - 1) * 100
        rec = next((k - i for k in range(i + 1, n) if vals[k] >= pv), None)
        anatomia.append({
            "topo": datas[i][:7], "nivel": pv,
            "r3": _ret(3), "r6": _ret(6), "r12": _ret(12),
            "queda_max": qmax, "recup_meses": rec,
            "atual": i == piv[-1][0] and t == "H",
        })
    # medianas dos topos passados (exclui o topo mais recente se for o atual)
    passados = [a for a in anatomia if not a["atual"]]
    def _medi(campo):
        xs = [a[campo] for a in passados if a[campo] is not None]
        return _st2.median(xs) if xs else None
    anatomia_med = {
        "r3": _medi("r3"), "r6": _medi("r6"), "r12": _medi("r12"),
        "queda_max": _medi("queda_max"), "recup_meses": _medi("recup_meses"),
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
        "anatomia_topos": anatomia,
        "anatomia_medianas": anatomia_med,
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


# ------------------------------------------------------------------------------
# Maturidade do mercado por DOIS eixos objetivos, via MM200 semanal:
#  - ESTICAMENTO: distância do preço à média de 200 semanas (fundos ficam
#    abaixo da linha; topos, bem acima).
#  - TEMPO: meses desde o último FUNDO MAIOR — definido como a queda a >=15%
#    abaixo da MM200 (filtra pausas rasas/laterais tipo 2011 e 2022).
# ------------------------------------------------------------------------------
CACHE_MATUR = CACHE_DIR / "ibov_maturidade_v2.json"
FUNDO_MAIOR_LIMITE = -15.0  # % abaixo da MM200 para contar como virada de ciclo


def _coletar_maturidade() -> dict:
    try:
        h = yf.Ticker("^BVSP").history(period="max", interval="1wk")["Close"].dropna()
        if h is None or h.empty or len(h) < 220:
            return {"erro": "Série semanal do Ibov insuficiente."}
        h.index = pd.to_datetime([d.date() for d in h.index])
        ma = h.rolling(200).mean()
        dist = ((h / ma) - 1) * 100
        d = dist.dropna()

        # FUNDOS MAIORES: cada episódio em que a distância ficou <= -15%; o fundo é
        # o ponto mais profundo. Um novo episódio só começa depois que o preço VOLTA
        # acima da MM200 (dist >= 0) — senão um bear longo e oscilante viraria vários
        # fundos. Assim cada bear conta como um fundo só (o mais profundo).
        fundos = []
        ativo, prof, data_prof = False, None, None
        for dt, v in d.items():
            if v <= FUNDO_MAIOR_LIMITE:
                if not ativo or v < prof:
                    ativo, prof, data_prof = True, float(v), dt
            elif ativo and v >= 0:
                fundos.append({"data": data_prof.strftime("%Y-%m"), "prof": round(prof, 1)})
                ativo = False
        if ativo:
            fundos.append({"data": data_prof.strftime("%Y-%m"), "prof": round(prof, 1)})

        # Agrupa fundos a menos de 24 meses (mesmo bear) e fica com o mais profundo,
        # para não contar repiques do meio de um bear longo como fundos distintos.
        def _mm(a, b):
            pa, pb = pd.Period(a, "M"), pd.Period(b, "M")
            return (pb.year - pa.year) * 12 + (pb.month - pa.month)
        grupos = []
        for f in fundos:
            if grupos and _mm(grupos[-1][-1]["data"], f["data"]) < 24:
                grupos[-1].append(f)
            else:
                grupos.append([f])
        fundos = [min(g, key=lambda x: x["prof"]) for g in grupos]

        # Queda desde o topo dos últimos 12 meses (52 semanas) — mostra quanto o
        # mercado já corrigiu, para o esticamento não dar impressão de "caríssimo"
        # quando a bolsa já caiu bastante do pico.
        pico52 = float(h.tail(52).max())
        queda_desde_topo = round((float(h.iloc[-1]) / pico52 - 1) * 100, 1)

        hoje = d.index[-1]
        meses = None
        if fundos:
            uf = pd.Period(fundos[-1]["data"], "M")
            meses = (hoje.year - uf.year) * 12 + (hoje.month - uf.month)

        # intervalos (meses) entre fundos maiores -> noção de "idade típica" do ciclo
        def _m(a, b):
            pa, pb = pd.Period(a, "M"), pd.Period(b, "M")
            return (pb.year - pa.year) * 12 + (pb.month - pa.month)
        inter = [_m(fundos[k - 1]["data"], fundos[k]["data"]) for k in range(1, len(fundos))]
        import statistics as _st
        inter_med = int(_st.median(inter)) if inter else None
        inter_max = int(max(inter)) if inter else None

        # percentis da distância (desde 2003, sem o lixo hiperinflacionário dos 90s)
        dd = d[d.index >= pd.Timestamp("2003-01-01")]
        p25, med, p75 = (float(dd.quantile(q)) for q in (0.25, 0.5, 0.75))

        return {
            "dist_atual": round(float(d.iloc[-1]), 1),
            "queda_desde_topo": queda_desde_topo,
            "ibov": round(float(h.iloc[-1])), "ma200": round(float(ma.iloc[-1])),
            "meses_desde_fundo": meses,
            "fundo_atual": fundos[-1] if fundos else None,
            "fundos": fundos,
            "inter_med": inter_med, "inter_max": inter_max,
            "p25": round(p25, 0), "med": round(med, 0), "p75": round(p75, 0),
            "erro": None,
        }
    except Exception as e:  # noqa: BLE001
        return {"erro": f"Falha ao calcular maturidade (MM200): {e}"}


def buscar_maturidade(usar_cache: bool = True) -> dict:
    if usar_cache and CACHE_MATUR.exists():
        try:
            if time.time() - CACHE_MATUR.stat().st_mtime < CACHE_TTL_SEGUNDOS:
                return json.loads(CACHE_MATUR.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    dados = _coletar_maturidade()
    if not dados.get("erro"):
        try:
            CACHE_DIR.mkdir(exist_ok=True)
            CACHE_MATUR.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
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
