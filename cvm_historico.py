"""
Histórico anual de EBIT e lucro líquido das companhias abertas, direto dos dados abertos da CVM.

Por que existe: o Yahoo entrega só ~4 anos de balanço e, para várias empresas, em dólar.
A CVM publica a DFP (demonstração anual padronizada) desde 2010, sempre em reais, e dá para
ver o ciclo inteiro (ex.: 2015, quando Petrobras, Vale e Gerdau tiveram EBIT negativo).

Fontes (públicas):
- DFP / DRE consolidada: https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/
- FCA / valores mobiliários (liga o ticker ao CNPJ): https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/

Contas usadas: 3.05 (resultado antes do resultado financeiro e dos tributos = EBIT),
3.06.02 (despesas financeiras) e 3.11 (lucro líquido consolidado). Bancos e seguradoras têm DRE diferente: para eles o EBIT
não faz sentido e o histórico vem marcado como ``financeira``.
"""
from __future__ import annotations

import io
import json
import time
import zipfile
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
ARQ_CACHE = BASE / "data" / "cvm_dre_historico.json"
URL_DFP = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{ano}.zip"
URL_FCA = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_{ano}.zip"
ANO_INICIAL = 2010
VALIDADE_DIAS = 30


def _requests():
    import requests
    try:  # o app força IPv4 em outras fontes; aqui só ajuda quando o IPv6 trava
        import cambio
        cambio._forcar_ipv4()
    except Exception:  # noqa: BLE001
        pass
    return requests


def _num(x) -> float | None:
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def _ler_dfp(ano: int, req) -> list[dict]:
    r = req.get(URL_DFP.format(ano=ano), timeout=240)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_csv(z.open(f"dfp_cia_aberta_DRE_con_{ano}.csv"), sep=";", encoding="latin1",
                     decimal=",", dtype={"CNPJ_CIA": str, "CD_CONTA": str})
    ordem = df["ORDEM_EXERC"].str.upper().str.replace("Ú", "U", regex=False)
    df = df[ordem.str.startswith("ULT") & df["CD_CONTA"].isin(["3.05", "3.11", "3.06.02"])]
    linhas = []
    for _, x in df.iterrows():
        esc = 1000.0 if str(x["ESCALA_MOEDA"]).upper().startswith("MIL") else 1.0
        v = _num(x["VL_CONTA"])
        if v is None:
            continue
        linhas.append({"cnpj": x["CNPJ_CIA"], "nome": x["DENOM_CIA"], "ano": ano,
                       "conta": {"3.05": "ebit", "3.11": "lucro", "3.06.02": "desp_fin"}[x["CD_CONTA"]],
                       "valor": v * esc})
    return linhas


def _mapa_tickers(req) -> dict:
    """{ticker (4 letras+número): cnpj} a partir do FCA mais recente que existir."""
    ano = time.localtime().tm_year
    for a in (ano, ano - 1, ano - 2):
        try:
            r = req.get(URL_FCA.format(ano=a), timeout=240)
            r.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(r.content))
            nome = next(n for n in z.namelist() if "valor_mobiliario" in n)
            df = pd.read_csv(z.open(nome), sep=";", encoding="latin1", dtype=str)
            col_t = next(c for c in df.columns if c.lower().startswith("codigo_negociacao"))
            col_c = next(c for c in df.columns if c.lower().startswith("cnpj"))
            out = {}
            for _, x in df.dropna(subset=[col_t]).iterrows():
                for tk in str(x[col_t]).replace(";", ",").split(","):
                    tk = tk.strip().upper()
                    if tk:
                        out[tk] = x[col_c]
            if out:
                return out
        except Exception:  # noqa: BLE001
            continue
    return {}


def construir_cache(forcar: bool = False, ano_final: int | None = None) -> dict:
    """Baixa DFP/FCA e grava o cache compacto (só EBIT e lucro de cada empresa/ano)."""
    if ARQ_CACHE.exists() and not forcar:
        try:
            c = json.loads(ARQ_CACHE.read_text(encoding="utf-8"))
            if time.time() - c.get("gerado_em", 0) < VALIDADE_DIAS * 86400:
                return c
        except Exception:  # noqa: BLE001
            pass
    req = _requests()
    ano_final = ano_final or time.localtime().tm_year
    emp: dict = {}
    for ano in range(ANO_INICIAL, ano_final + 1):
        try:
            for l in _ler_dfp(ano, req):
                e = emp.setdefault(l["cnpj"], {"nome": l["nome"], "anos": {}})
                e["nome"] = l["nome"]
                e["anos"].setdefault(str(ano), {})[l["conta"]] = l["valor"]
        except Exception:  # noqa: BLE001 - o ano corrente pode ainda não existir
            continue
    cache = {"gerado_em": time.time(), "empresas": emp, "tickers": _mapa_tickers(req)}
    ARQ_CACHE.parent.mkdir(exist_ok=True)
    ARQ_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return cache


def carregar_cache() -> dict:
    """Lê o cache versionado no repositório; só baixa da CVM se ele não existir.

    O arquivo fica no git porque o disco do Streamlit Cloud é efêmero. Para atualizar
    (uma vez por ano, quando saem as DFP novas): ``py -c "import cvm_historico as c; c.construir_cache(True)"``.
    """
    try:
        return json.loads(ARQ_CACHE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return construir_cache(forcar=True)


def historico(ticker: str, cache: dict | None = None) -> dict:
    """{'nome', 'anos': {2011: {'ebit': x, 'lucro': y}, ...}} em R$, ou {} se não achar."""
    c = cache if cache is not None else carregar_cache()
    cnpj = (c.get("tickers") or {}).get(ticker.strip().upper())
    e = (c.get("empresas") or {}).get(cnpj) if cnpj else None
    if not e:
        return {}
    anos = {int(a): {"ebit": _num(v.get("ebit")), "lucro": _num(v.get("lucro")),
                     "desp_fin": _num(v.get("desp_fin"))}   # despesa financeira (conta 3.06.02), vem negativa na DRE
            for a, v in e["anos"].items()}
    return {"nome": e["nome"], "cnpj": cnpj, "anos": dict(sorted(anos.items()))}


def ebit_normalizado(h: dict, n: int = 10, campo: str = "ebit") -> dict:
    """Média dos últimos ``n`` anos com dado. Devolve média, anos usados e quantos foram negativos."""
    vals = [(a, d[campo]) for a, d in (h.get("anos") or {}).items() if d.get(campo) is not None]
    vals = vals[-n:]
    if not vals:
        return {"media": None, "n": 0, "anos": [], "negativos": 0}
    return {"media": sum(v for _, v in vals) / len(vals), "n": len(vals),
            "anos": [a for a, _ in vals], "negativos": sum(1 for _, v in vals if v < 0)}


def cobertura_juros(h: dict) -> list[dict]:
    """Por ano: EBIT, despesa financeira (positiva) e a cobertura = EBIT / despesa financeira.

    ``cobre`` é True quando o EBIT é maior que a despesa financeira (sobra para o acionista antes
    do imposto). Sem despesa financeira (empresa sem dívida) a cobertura fica None e ``cobre`` True
    se o EBIT for positivo. A despesa financeira da DRE inclui variação cambial e outros itens,
    então é uma medida conservadora."""
    out = []
    for ano, d in (h.get("anos") or {}).items():
        ebit, desp = d.get("ebit"), d.get("desp_fin")
        if ebit is None or desp is None:
            continue
        desp = abs(desp)
        cob = (ebit / desp) if desp > 0 else None
        out.append({"ano": ano, "ebit": ebit, "desp_fin": desp, "cobertura": cob,
                    "cobre": (ebit > desp) if desp > 0 else ebit > 0})
    return out
