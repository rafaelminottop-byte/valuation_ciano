"""Constrói data/multiplos_historicos.json: quanto o mercado pagou de P/L (lucro 12m) por setor,
e como o P/L varia com o juro real (NTN-B 10a). Rodar à mão de vez em quando (não roda no app).

Uso:  py scripts/construir_multiplos.py <precos.pkl>
  precos.pkl = (PC, PA, VOL, shares): fechamentos mensais, ajustados, volume e nº de ações por CNPJ.
Dados: CVM (lucro anual, com defasagem de publicação), Yahoo (preço), painel do preditor (NTN-B).
Limites: só empresas vivas (viés de sobrevivência); 150 maiores por mês; 1 papel por empresa;
nº de ações = o mais recente (escala calibrada contra o P/L atual do Fundamentus).
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import setores_b3  # noqa: E402

PL_MAX = 60  # descarta P/L absurdo (lucro quase zero)


def construir(pkl: str) -> dict:
    PC, PA, VOL, shares = pd.read_pickle(pkl)
    PC.index = pd.PeriodIndex(PC.index, freq="M")
    cache = json.load(open(RAIZ / "data" / "cvm_dre_historico.json", encoding="utf-8"))
    emp, tick = cache["empresas"], cache["tickers"]
    sec = setores_b3.carregar_mapa()
    F = pd.read_pickle(sorted((RAIZ / ".cache").glob("fundamentus_v*.pkl"))[-1]).set_index("ticker")
    rows = []
    for t, c in tick.items():
        if t not in PC.columns or c not in emp or c not in shares or t not in sec:
            continue
        anos = {int(a): v for a, v in emp[c]["anos"].items()}
        sh = shares[c][max(shares[c])]
        lu = anos.get(max(anos), {}).get("lucro")
        if t in F.index and F.at[t, "p_l"] > 0 and lu and lu > 0 and PC[t].dropna().size:
            pnow = PC[t].dropna().iloc[-1]  # o Yahoo às vezes traz ações em milhares: escolhe a escala certa
            sh *= min((1, 1e3, 1e6, 1e-3), key=lambda f: abs(np.log(pnow * sh * f / lu / F.at[t, "p_l"])))
        for m in PC.index:
            ult = m.year - 1 if m.month >= 4 else m.year - 2
            v, p = anos.get(ult), PC.at[m, t]
            if v is None or not (p == p and p > 0):
                continue
            l = v.get("lucro")
            mc = p * sh
            rows.append((m, c, sec[t], mc, mc / l if l and l > 0 else np.nan))
    D = pd.DataFrame(rows, columns=["m", "c", "setor", "mc", "pl"])
    D = D.sort_values(["m", "c", "mc"]).groupby(["m", "c"]).tail(1)
    D = D[D.groupby("m").mc.rank(ascending=False) <= 150]
    a = D[(D.pl > 0) & (D.pl < PL_MAX)]

    setores = {}
    for s, g in a.groupby("setor"):
        if len(g) >= 150 and s.strip():
            q = g.pl.quantile([.25, .5, .75])
            setores[s] = {"p25": round(q[.25], 1), "p50": round(q[.5], 1), "p75": round(q[.75], 1), "obs": int(len(g))}
    q = a.pl.quantile([.25, .5, .75])
    mercado = {"p25": round(q[.25], 1), "p50": round(q[.5], 1), "p75": round(q[.75], 1), "obs": int(len(a))}

    painel = pd.DataFrame(json.load(open(sorted((RAIZ / ".cache").glob("preditor_painel_v*.json"))[-1], encoding="utf-8")))
    painel["m"] = pd.PeriodIndex(painel.per, freq="M")
    M = a.groupby("m").pl.median().rename("pl")
    J = pd.concat([M, painel.set_index("m")[["ntnb"]]], axis=1).dropna()
    J["ey"] = 100 / J.pl  # lucro/preço em %
    b, a0 = np.polyfit(J.ntnb, J.ey, 1)
    res = J.ey - (a0 + b * J.ntnb)
    juro = {"a": round(a0, 3), "b": round(b, 3),
            "res_p25": round(res.quantile(.25), 3), "res_p75": round(res.quantile(.75), 3),
            "corr_pl_ntnb": round(J.pl.corr(J.ntnb), 2), "meses": int(len(J)),
            "de": str(J.index[0]), "ate": str(J.index[-1])}
    return {"gerado_em": str(pd.Timestamp.today().date()), "mercado": mercado, "setores": setores, "juro_real": juro}


if __name__ == "__main__":
    out = construir(sys.argv[1])
    (RAIZ / "data" / "multiplos_historicos.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
