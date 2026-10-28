"""
Câmbio: a relação Juro × Risco × Câmbio do real.

Monta, de fontes públicas gratuitas, a série mensal de:
- Dólar (USD/BRL) — Yahoo
- Carry = juro real BR − juro real EUA — BCB (Selic, IPCA) + Yahoo (Treasury) + BLS (CPI)
- Risco-país — EMBI (Ipeadata, 1994→2024) emendado com o CDS 5a (worldgovernmentbonds, 2017→hoje)

A tese (validada): o real fortalece quando o carry sobe e, principalmente, quando o
risco cai. O risco é o driver mais forte (corr ~0,8 das variações de 12m com o dólar).

Tudo com cache local (as séries mudam devagar e algumas chamadas são lentas).
"""
import json
import socket
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "cambio_v2.json"
CACHE_TTL = 12 * 60 * 60  # 12h
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")}
INICIO = "2013-01-01"


def _forcar_ipv4():
    _orig = socket.getaddrinfo
    socket.getaddrinfo = lambda h, p, *a, **k: [x for x in _orig(h, p, socket.AF_INET, *a[1:], **k)]


def _mensal_yahoo(ticker: str) -> pd.Series:
    h = yf.Ticker(ticker).history(period="max", interval="1mo")["Close"].dropna()
    s = pd.Series(h.values, index=pd.to_datetime([d.date() for d in h.index]))
    return s.resample("ME").last()


def _sgs(cod: int) -> pd.Series:
    """Série diária/mensal do SGS em janelas de 6 anos (limite do BCB)."""
    pares = []
    a = int(INICIO[:4]) - 1
    while a <= date.today().year:
        b = min(a + 5, date.today().year)
        url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{cod}/dados?formato=json"
               f"&dataInicial=01/01/{a}&dataFinal=31/12/{b}")
        try:
            for x in requests.get(url, headers=HEADERS, timeout=40, verify=False).json():
                pares.append((x["data"], float(x["valor"].replace(",", "."))))
        except Exception:  # noqa: BLE001
            pass
        a = b + 1
    s = pd.Series(dict(pares))
    s.index = pd.to_datetime(s.index, format="%d/%m/%Y")
    return s.sort_index().resample("ME").last()


def _cpi_yoy() -> pd.Series:
    def bls(y0, y1):
        dados = None
        for _ in range(3):
            try:
                r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                                  json={"seriesid": ["CUUR0000SA0"], "startyear": str(y0), "endyear": str(y1)},
                                  headers={**HEADERS, "Content-Type": "application/json"}, timeout=40)
                j = r.json()
                if j.get("status") == "REQUEST_SUCCEEDED" and j["Results"].get("series"):
                    dados = j["Results"]["series"][0]["data"]
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(2)
        out = {}
        for it in (dados or []):
            if it["period"].startswith("M"):
                try:
                    m = int(it["period"][1:])
                    out[f"{it['year']}-{m:02d}-01"] = float(it["value"])
                except ValueError:
                    pass
        return out

    lvl = {}
    a = int(INICIO[:4]) - 1
    while a <= date.today().year:
        b = min(a + 9, date.today().year)
        try:
            lvl.update(bls(a, b))
        except Exception:  # noqa: BLE001
            pass
        a = b + 1
    s = pd.Series(lvl)
    s.index = pd.to_datetime(s.index)
    s = s.sort_index().resample("ME").last()
    return (s / s.shift(12) - 1) * 100


def _embi() -> pd.Series:
    url = "http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='JPM366_EMBI366')"
    ev = requests.get(url, timeout=40, verify=False).json()["value"]
    s = pd.Series({x["VALDATA"][:10]: x["VALVALOR"] for x in ev if x.get("VALVALOR") is not None})
    s.index = pd.to_datetime(s.index)
    return s.sort_index().resample("ME").last()


def _cds():
    """CDS 5 anos do Brasil (bps), série diária -> mensal + valor mais recente."""
    ep = "https://www.worldgovernmentbonds.com/wp-json/common/v1/historical"
    gv = {"JS_VARIABLE": "jsGlobalVars", "FUNCTION": "CDS", "DOMESTIC": True, "ENDPOINT": ep,
          "DATE_RIF": "2099-12-31", "DEBUG": False,
          "OBJ": {"UNIT": "", "DECIMAL": 2, "UNIT_DELTA": "%", "DECIMAL_DELTA": 2},
          "COUNTRY1": {"SYMBOL": "7", "PAESE": "Brazil", "PAESE_UPPERCASE": "BRAZIL",
                       "BANDIERA": "br", "URL_PAGE": "brazil"},
          "COUNTRY2": None, "OBJ1": {"DURATA_STRING": "5 Years", "DURATA": 60}, "OBJ2": None}
    h = {**HEADERS, "Content-Type": "application/json",
         "Referer": "https://www.worldgovernmentbonds.com/cds-historical-data/brazil/5-years/",
         "Origin": "https://www.worldgovernmentbonds.com"}
    q = None
    for _ in range(4):
        try:
            j = requests.post(ep, headers=h, json={"GLOBALVAR": gv}, timeout=30, verify=False).json()
            if j.get("success"):
                q = j["result"]["quote"]
                break
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2)
    if not q:
        return pd.Series(dtype=float), None, None
    s = pd.Series({v["DATA_VAL"]: float(v["CLOSE_VAL"]) for v in q.values()})
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    atual, data_atual = float(s.iloc[-1]), s.index[-1].strftime("%d/%m/%Y")
    faixa = (float(s.min()), float(s.max()))
    return s.resample("ME").last(), (atual, data_atual, faixa), None


def _coletar() -> dict:
    _forcar_ipv4()
    dolar = _mensal_yahoo("BRL=X")
    selic = _sgs(432)
    ipca = _sgs(13522)
    # defesa na raiz: o BCB às vezes devolve uma janela de 6 anos a menos e a série
    # fica "parada" no passado — o que trava a Selic velha e envenena o juro real.
    # Se a série não alcança ~o mês atual, a coleta é parcial: aborta (não cacheia).
    hoje = pd.Timestamp.today().normalize()
    for nome, s in (("Selic", selic), ("IPCA", ipca)):
        ult = s.index.max() if not s.empty else None
        if ult is None or (hoje - ult).days > 75:
            raise RuntimeError(f"Série {nome} veio incompleta do BCB "
                               f"(última: {ult.date() if ult is not None else 'vazia'})")
    br_real = ((1 + selic / 100) / (1 + ipca / 100) - 1) * 100
    tnx = _mensal_yahoo("^TNX")
    us_real = (tnx - _cpi_yoy()).dropna()
    carry = (br_real - us_real).dropna()

    embi = _embi()
    cds_m, cds_info, _ = _cds()
    # emenda: risco = EMBI (longo) + CDS*razao (recente), em escala EMBI
    razao = 1.43
    both = pd.concat([embi.rename("e"), cds_m.rename("c")], axis=1).dropna()
    if len(both) > 6:
        razao = float((both["e"] / both["c"]).median())
    risco = embi.copy()
    if not cds_m.empty:
        extra = cds_m[cds_m.index > embi.index.max()] * razao
        risco = pd.concat([risco, extra]).sort_index()

    df = pd.concat([dolar.rename("dolar"), carry.rename("carry"), risco.rename("risco"),
                    cds_m.rename("cds")], axis=1)
    df = df[df.index >= INICIO]

    serie = [{"data": d.strftime("%Y-%m"),
              "dolar": None if pd.isna(r.dolar) else round(float(r.dolar), 3),
              "carry": None if pd.isna(r.carry) else round(float(r.carry), 2),
              "risco": None if pd.isna(r.risco) else round(float(r.risco), 0),
              "cds": None if pd.isna(r.cds) else round(float(r.cds), 0)}
             for d, r in df.iterrows()]

    # variação do dólar no ano
    var_ano = None
    da = dolar[dolar.index.year == dolar.index[-1].year]
    if len(da) >= 2:
        var_ano = round(float(da.iloc[-1] / da.iloc[0] - 1) * 100, 1)

    atual = {
        "dolar": round(float(dolar.iloc[-1]), 2), "dolar_var_ano": var_ano,
        "carry": round(float(carry.iloc[-1]), 1) if len(carry) else None,
        "br_real": round(float(br_real.dropna().iloc[-1]), 1) if len(br_real.dropna()) else None,
        "us_real": round(float(us_real.iloc[-1]), 1) if len(us_real) else None,
        "cds": round(cds_info[0], 0) if cds_info else None,
        "cds_data": cds_info[1] if cds_info else None,
        "cds_min": round(cds_info[2][0], 0) if cds_info else None,
        "cds_max": round(cds_info[2][1], 0) if cds_info else None,
    }
    # correlação da variação 12m risco x dólar (prova da tese, calculada no próprio dado)
    corr = df[["risco", "dolar"]].dropna()
    atual["corr_risco_dolar"] = (round(float(corr["risco"].diff(12).corr(corr["dolar"].diff(12))), 2)
                                 if len(corr) > 24 else None)

    return {"atual": atual, "serie": serie, "erro": None,
            "atualizado_em": date.today().strftime("%d/%m/%Y"),
            "fontes": {"dolar": "Yahoo", "carry": "BCB + BLS",
                       "risco": "Ipeadata (EMBI) + worldgovernmentbonds (CDS)",
                       "cds": "worldgovernmentbonds"}}


def _plausivel(d: dict) -> bool:
    """Sanidade absoluta antes de virar cache (segunda rede de segurança).

    A defesa principal contra coleta parcial está no `_coletar` (aborta se a
    série do BCB não alcança o mês atual). Aqui só barramos valores fora de
    qualquer faixa razoável — regime-independente, sem lock-in de cache ruim.
    """
    if d.get("erro") or not d.get("serie"):
        return False
    a = d.get("atual") or {}
    dolar = a.get("dolar")
    if dolar is None or not (3 <= dolar <= 12):
        return False
    br = a.get("br_real")
    if br is not None and not (0 < br < 20):
        return False
    cds = a.get("cds")
    if cds is not None and not (40 <= cds <= 700):
        return False
    return True


def _carregar_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return None


def buscar_cambio(usar_cache: bool = True) -> dict:
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
        # coleta falhou inteira: degrada com elegância para o último dado bom
        if cache is not None:
            cache["aviso"] = "Fontes indisponíveis agora; mostrando o último dado válido."
            return cache
        return {"erro": f"Falha ao montar o painel de câmbio: {e}", "atual": {}, "serie": []}

    # carry-forward do CDS quando a fonte volta vazia (worldgovernmentbonds é instável)
    if cache is not None:
        ant, novo = cache.get("atual") or {}, dados.get("atual") or {}
        if novo.get("cds") is None and ant.get("cds") is not None:
            for k in ("cds", "cds_data", "cds_min", "cds_max"):
                novo[k] = ant.get(k)
            novo["cds_stale"] = True

    # blindagem: não deixa número quebrado virar cache (envenenamento de 12h)
    if not _plausivel(dados):
        if cache is not None:
            cache["aviso"] = "Coleta parcial detectada; mantido o último dado válido."
            return cache
        return dados  # sem cache anterior: devolve, mas não persiste o lixo

    try:
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    return dados


if __name__ == "__main__":
    d = buscar_cambio(usar_cache=False)
    if d.get("erro"):
        print("ERRO:", d["erro"])
    else:
        a = d["atual"]
        print("ATUAL:", a)
        print("pontos na série:", len(d["serie"]))
        print("primeiros:", d["serie"][:2])
        print("últimos:", d["serie"][-2:])
