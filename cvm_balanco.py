"""Caixa e dívida bruta das companhias abertas, ano a ano, da DFP da CVM (balanço consolidado).

Serve para montar o valor da empresa (EV = valor de mercado + dívida líquida) no passado e
calcular EV/EBIT histórico. Contas: 1.01.01 (caixa e equivalentes), 1.01.02 (aplicações financeiras),
2.01.04 (empréstimos, financiamentos e debêntures — circulante) e 2.02.01 (idem — não circulante).
Limites: arrendamentos entram só quando a empresa os classifica nessas contas; bancos não se aplicam.
Cache: data/cvm_divida_historico.json  ({cnpj: {ano: {"caixa": x, "divida": y}}}, em R$).
Atualizar: ``py -c "import cvm_balanco as c; c.construir_cache()"``.
"""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pandas as pd

from cvm_historico import ANO_INICIAL, URL_DFP, _num, _requests

ARQ = Path(__file__).resolve().parent / "data" / "cvm_divida_historico.json"
_CONTAS = {"1.01.01": "caixa", "1.01.02": "caixa", "2.01.04": "divida", "2.02.01": "divida"}


def _ler_balanco(ano: int, req) -> dict:
    r = req.get(URL_DFP.format(ano=ano), timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    out: dict = {}
    for arq in (f"dfp_cia_aberta_BPA_con_{ano}.csv", f"dfp_cia_aberta_BPP_con_{ano}.csv"):
        df = pd.read_csv(z.open(arq), sep=";", encoding="latin1", decimal=",",
                         dtype={"CNPJ_CIA": str, "CD_CONTA": str})
        ordem = df["ORDEM_EXERC"].str.upper().str.replace("Ú", "U", regex=False)
        df = df[ordem.str.startswith("ULT") & df["CD_CONTA"].isin(list(_CONTAS))]
        for _, x in df.iterrows():
            v = _num(x["VL_CONTA"])
            if v is None:
                continue
            esc = 1000.0 if str(x["ESCALA_MOEDA"]).upper().startswith("MIL") else 1.0
            d = out.setdefault(x["CNPJ_CIA"], {})
            campo = _CONTAS[x["CD_CONTA"]]
            d[campo] = d.get(campo, 0.0) + v * esc
    return out


def construir_cache(ano_final: int | None = None) -> dict:
    import time

    req = _requests()
    ano_final = ano_final or time.localtime().tm_year
    emp: dict = {}
    for ano in range(ANO_INICIAL, ano_final + 1):
        try:
            for cnpj, d in _ler_balanco(ano, req).items():
                emp.setdefault(cnpj, {})[str(ano)] = {k: round(v) for k, v in d.items()}
        except Exception:  # noqa: BLE001 - ano corrente pode não existir ainda
            continue
    ARQ.write_text(json.dumps(emp, ensure_ascii=False), encoding="utf-8")
    return emp


def carregar() -> dict:
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def divida_liquida(cnpj: str, ano: int, dados: dict | None = None) -> float | None:
    """Dívida bruta − caixa e aplicações do fim do ano, em R$. None se não houver o balanço."""
    d = ((dados if dados is not None else carregar()).get(cnpj) or {}).get(str(ano))
    if not d:
        return None
    return d.get("divida", 0.0) - d.get("caixa", 0.0)
