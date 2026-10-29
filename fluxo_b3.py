"""
Fluxo de investidores na B3 (mercado à vista), automático.

Raspa o fluxo diário por tipo de investidor (Estrangeiro, Institucional,
Pessoa física, Inst. Financeira, Outros) do Dados de Mercado, que republica
o dado OFICIAL da B3 (saldo à vista, D+2). Convenção: positivo = entrada,
negativo = saída, em R$ milhões.

Mesma filosofia de confiabilidade do cambio.py: cache local, blindagem antes
de gravar (não deixa coleta quebrada virar cache) e degradação elegante
(se a fonte cair, devolve o último dado bom com aviso, nunca uma tela de erro).
"""
import io
import json
import re
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "fluxo_b3.json"
CACHE_TTL = 6 * 60 * 60  # 6h (o dado é diário, D+2)
FONTE_URL = "https://www.dadosdemercado.com.br/fluxo"
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")}

_COLS = {"Estrangeiro": "estrangeiro", "Institucional": "institucional",
         "Pessoa física": "pessoa_fisica", "Inst. Financeira": "inst_financeira",
         "Outros": "outros"}


def _num(v) -> float | None:
    """'−2.846,16 mi' -> -2846.16 (milhão de dólar... digo, de real)."""
    s = str(v).replace("mi", "").replace("−", "-").strip()
    s = s.replace(".", "").replace(",", ".")
    s = re.sub(r"[^0-9.\-]", "", s)
    try:
        return float(s)
    except ValueError:
        return None


def _coletar() -> dict:
    r = requests.get(FONTE_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    tab = pd.read_html(io.StringIO(r.text))[0]
    if "Data" not in tab.columns or "Estrangeiro" not in tab.columns:
        raise RuntimeError("Tabela de fluxo mudou de formato na fonte.")
    tab["data"] = pd.to_datetime(tab["Data"], format="%d/%m/%Y", errors="coerce")
    tab = tab.dropna(subset=["data"])
    for origem, destino in _COLS.items():
        tab[destino] = tab[origem].map(_num) if origem in tab.columns else None
    tab = tab.sort_values("data")

    serie = [{"data": d.strftime("%Y-%m-%d"),
              **{destino: (None if pd.isna(row[destino]) else round(float(row[destino]), 1))
                 for destino in _COLS.values()}}
             for d, row in tab.set_index("data").iterrows()]

    est = tab["estrangeiro"].dropna()
    ano = int(tab["data"].dt.year.max())
    mes = int(tab[tab["data"].dt.year == ano]["data"].dt.month.max())
    no_mes = float(tab[(tab["data"].dt.year == ano) & (tab["data"].dt.month == mes)]["estrangeiro"].sum())
    no_ano = float(tab[tab["data"].dt.year == ano]["estrangeiro"].sum())
    atual = {
        "ultimo_dia": round(float(est.iloc[-1]), 1) if len(est) else None,
        "ultima_data": tab["data"].iloc[-1].strftime("%d/%m/%Y"),
        "no_mes": round(no_mes, 0), "no_ano": round(no_ano, 0), "ano": ano,
        "mm5": round(float(est.tail(5).mean()), 0) if len(est) >= 5 else None,
        "mm21": round(float(est.tail(21).mean()), 0) if len(est) >= 21 else None,
    }
    return {"atual": atual, "serie": serie, "erro": None,
            "atualizado_em": date.today().strftime("%d/%m/%Y"),
            "fonte": "B3 (saldo à vista, D+2) via Dados de Mercado"}


def _plausivel(d: dict) -> bool:
    if d.get("erro") or not d.get("serie"):
        return False
    serie = d["serie"]
    if len(serie) < 20:  # a fonte traz ~1 ano; bem menos que isso é coleta quebrada
        return False
    if d.get("atual", {}).get("ultimo_dia") is None:
        return False
    return True


def _carregar_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return None


def buscar_fluxo(usar_cache: bool = True) -> dict:
    cache = _carregar_cache()
    if usar_cache and cache is not None:
        try:
            if time.time() - CACHE_FILE.stat().st_mtime < CACHE_TTL:
                return cache
        except Exception:  # noqa: BLE001
            pass
    try:
        dados = _coletar()
    except Exception as e:  # noqa: BLE001
        if cache is not None:
            cache = dict(cache)
            cache["aviso"] = "Fonte do fluxo indisponível agora; mostrando o último dado válido."
            return cache
        return {"erro": f"Falha ao buscar o fluxo da B3: {e}", "atual": {}, "serie": []}

    if not _plausivel(dados):
        if cache is not None:
            cache = dict(cache)
            cache["aviso"] = "Coleta parcial do fluxo; mantido o último dado válido."
            return cache
        return dados

    try:
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    return dados


if __name__ == "__main__":
    d = buscar_fluxo(usar_cache=False)
    if d.get("erro"):
        print("ERRO:", d["erro"])
    else:
        print("ATUAL:", d["atual"])
        print("pontos:", len(d["serie"]), "| fonte:", d["fonte"])
        print("últimos 3:", d["serie"][-3:])
