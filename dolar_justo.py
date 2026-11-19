"""
Dólar justo: dois jeitos de medir se o real está caro ou barato, sem prometer previsão.

1) PPC (paridade do poder de compra): o dólar compensa a diferença de inflação Brasil × EUA
   a partir de um ANO-BASE. O resultado depende quase só do ano-base escolhido; por isso o
   app mostra vários anos-base lado a lado, nunca um número único.
2) Modelo de fundamentos (regressão desde 2013, em variações de 12 meses): dólar global (DXY),
   commodities, risco-país e carry. Diz quanto do movimento do dólar vem de fora e quanto vem do risco
   Brasil. Traz um teste honesto: ajustado só até 2019 e conferido de 2020 em diante. (Testei antes a
   versão em NÍVEIS: ela falhou fora da amostra, então não é usada.)

Fontes públicas gratuitas (Yahoo, BCB, BLS). Cache local de 24h. Funções de cálculo são puras
(recebem séries prontas) para poderem ser testadas sem rede.
"""
from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

CACHE_FILE = Path(__file__).resolve().parent / ".cache" / "dolar_justo_v1.json"
CACHE_TTL = 24 * 60 * 60
ANOS_BASE_PADRAO = (2010, 2015, 2019, 2022)
CORTE_TESTE = "2019-12"          # ajuste só até aqui; o resto é teste fora da amostra
MIN_MESES_MODELO = 60
_HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")}


# ----------------------------------------------------------------- cálculo (puro)
def _mensal(s: pd.Series) -> pd.Series:
    s = s.copy()
    s.index = pd.to_datetime(s.index)
    return s.sort_index().resample("ME").last()


def ppc_por_ano_base(dolar: pd.Series, ipca_mensal_pct: pd.Series, cpi_eua: pd.Series,
                     anos_base=ANOS_BASE_PADRAO) -> dict:
    """Dólar pela PPC para cada ano-base.

    dolar: USD/BRL mensal. ipca_mensal_pct: IPCA mensal em %. cpi_eua: nível do CPI americano.
    Base = média do ano-base (dólar e níveis de preço), para não depender de um mês isolado.
    Devolve {ano: {"base": dólar médio do ano, "justo": dólar pela PPC hoje}}.
    """
    dolar, cpi_eua = _mensal(dolar), _mensal(cpi_eua)
    idx_br = (1 + _mensal(ipca_mensal_pct) / 100).cumprod()
    df = pd.concat([dolar.rename("d"), idx_br.rename("br"), cpi_eua.rename("us")], axis=1).dropna()
    out = {}
    if df.empty:
        return out
    for ano in anos_base:
        b = df[df.index.year == ano]
        if len(b) < 6:
            continue
        d0, br0, us0 = b["d"].mean(), b["br"].mean(), b["us"].mean()
        ult = df.iloc[-1]
        out[int(ano)] = {"base": float(d0),
                         "justo": float(d0 * (ult["br"] / br0) / (ult["us"] / us0)),
                         "ate": df.index[-1].strftime("%Y-%m"), "dolar_ate": float(ult["d"])}
    return out


ANOS_BASE_GRAFICO = tuple(range(2008, 2025))
ANO_BASE_INICIAL = 2019


def ppc_serie(dolar: pd.Series, ipca_mensal_pct: pd.Series, cpi_eua: pd.Series, ano_base: int):
    """Dólar justo pela PPC mês a mês: dólar médio do ano-base corrigido pela inflação BR / EUA.
    Devolve Series mensal (None se o ano-base não tem dado suficiente)."""
    dolar, cpi_eua = _mensal(dolar), _mensal(cpi_eua)
    idx_br = (1 + _mensal(ipca_mensal_pct) / 100).cumprod()
    df = pd.concat([dolar.rename("d"), idx_br.rename("br"), cpi_eua.rename("us")], axis=1).dropna()
    b = df[df.index.year == ano_base]
    if len(b) < 6:
        return None
    d0, br0, us0 = b["d"].mean(), b["br"].mean(), b["us"].mean()
    return d0 * (df["br"] / br0) / (df["us"] / us0)


FATORES = ("dxy", "commod", "risco", "carry")
ROTULO_FATOR = {"dxy": "Dólar no mundo (DXY)", "commod": "Commodities", "risco": "Risco-país",
                "carry": "Juro real BR − EUA"}


def _variacoes_12m(df: pd.DataFrame) -> pd.DataFrame:
    """Variação em 12 meses: ln para dólar/DXY/commodities/risco; diferença simples para o carry.
    Trabalhar em variações (e não em níveis) evita a regressão espúria de séries com tendência."""
    L = np.log(df[["dolar", "dxy", "commod", "risco"]])
    d = L.diff(12)
    d["carry"] = df["carry"].diff(12)
    return d.dropna()


def _ajusta(d: pd.DataFrame):
    X = np.column_stack([np.ones(len(d))] + [d[k].values for k in FATORES])
    y = d["dolar"].values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    ss_res = float(((y - X @ beta) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return beta, (1 - ss_res / ss_tot if ss_tot else float("nan"))


def modelo_fundamentos(df: pd.DataFrame) -> dict | None:
    """df mensal com colunas dolar, dxy, commod, risco, carry.

    Explica a variação do dólar em 12 meses por: dólar global, commodities, risco-país e carry.
    "Dólar explicado" = dólar de 12 meses atrás x exp(variação que os fatores justificam).
    A diferença para o dólar real é a parte que o modelo não explica.
    None se não houver dado suficiente."""
    df = df.dropna()
    d = _variacoes_12m(df)
    if len(d) < MIN_MESES_MODELO:
        return None
    beta, r2 = _ajusta(d)
    ult = d.iloc[-1]
    dolar_atual = float(df["dolar"].iloc[-1])
    dolar_12m = float(df["dolar"].iloc[-13])
    explicado_log = float(beta[0] + sum(beta[i + 1] * ult[k] for i, k in enumerate(FATORES)))
    explicado = dolar_12m * float(np.exp(explicado_log))

    # contribuição de cada fator no movimento de 12m, em pontos percentuais do dólar de 12m atrás
    contrib_pp = {k: float(beta[i + 1] * ult[k] * 100) for i, k in enumerate(FATORES)}
    contrib_pp["tendencia"] = float(beta[0] * 100)           # deriva média da amostra
    contrib_pp["nao_explicado"] = float((ult["dolar"] - explicado_log) * 100)

    fitted = [None] * 12 + [float(dolar_12m_i * np.exp(beta[0] + sum(beta[i + 1] * r[k]
                                                                      for i, k in enumerate(FATORES))))
                            for dolar_12m_i, (_, r) in zip(df["dolar"].values[:-12], d.iterrows())]
    return {
        "dolar_atual": dolar_atual, "dolar_12m": dolar_12m, "explicado": explicado,
        "variacao_real_pct": float((np.exp(ult["dolar"]) - 1) * 100),
        "variacao_explicada_pct": float((np.exp(explicado_log) - 1) * 100),
        "gap_pct": float((dolar_atual / explicado - 1) * 100),
        "r2": r2, "meses": int(len(d)),
        "de": df.index[0].strftime("%Y-%m"), "ate": df.index[-1].strftime("%Y-%m"),
        "coef": {k: float(beta[i + 1]) for i, k in enumerate(FATORES)},
        "contrib_pp": contrib_pp,
        "serie": {"data": [x.strftime("%Y-%m") for x in df.index],
                  "dolar": [float(v) for v in df["dolar"]], "explicado": fitted},
        "teste": teste_fora_amostra(df),
    }


def teste_fora_amostra(df: pd.DataFrame, corte: str = CORTE_TESTE) -> dict | None:
    """Ajusta só com as variações até `corte` e confere de 2020 em diante (relação antiga ainda vale?).
    Compara o erro com o de 'o dólar não muda em 12 meses' (a referência ingênua)."""
    d = _variacoes_12m(df.dropna())
    tr, te = d[d.index <= corte], d[d.index > corte]
    if len(tr) < 36 or len(te) < 24:
        return None
    beta, _ = _ajusta(tr)
    Xt = np.column_stack([np.ones(len(te))] + [te[k].values for k in FATORES])
    pred, real = Xt @ beta, te["dolar"].values
    ss_tot = float(((real - real.mean()) ** 2).sum())
    return {"corte": corte, "meses_teste": int(len(te)),
            "corr": float(np.corrcoef(real, pred)[0, 1]),
            "r2_fora": float(1 - ((real - pred) ** 2).sum() / ss_tot) if ss_tot else float("nan"),
            "erro_medio_pp": float(np.abs(real - pred).mean() * 100),
            "erro_dolar_parado_pp": float(np.abs(real).mean() * 100)}


def faixa_justa(ppc: dict, modelo: dict | None) -> dict:
    """Resumo: faixa de PPC (mín–máx entre anos-base) e valor do modelo; posição do dólar atual."""
    vals = [v["justo"] for v in ppc.values()]
    out = {"ppc_min": min(vals) if vals else None, "ppc_max": max(vals) if vals else None}
    if modelo:
        out["explicado"] = modelo["explicado"]
        out["dolar_atual"] = modelo["dolar_atual"]
    return out


# ----------------------------------------------------------------- coleta (rede)
def _yahoo(ticker: str) -> pd.Series:
    import yfinance as yf
    h = yf.Ticker(ticker).history(period="max", interval="1mo")["Close"].dropna()
    s = pd.Series(h.values, index=pd.to_datetime([d.date() for d in h.index]))
    return s.resample("ME").last()


def _ipca_mensal() -> pd.Series:
    import requests
    pares, a = [], 2000
    while a <= date.today().year:
        b = min(a + 5, date.today().year)
        url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
               f"&dataInicial=01/01/{a}&dataFinal=31/12/{b}")
        r = None
        for _ in range(3):                       # o BCB às vezes devolve vazio: tenta de novo
            try:
                r = requests.get(url, headers=_HEADERS, timeout=40, verify=False).json()
                break
            except Exception:  # noqa: BLE001
                time.sleep(2)
        if r is None:
            raise RuntimeError("IPCA mensal indisponível no BCB")
        pares += [(x["data"], float(x["valor"].replace(",", "."))) for x in r]
        a = b + 1
    s = pd.Series(dict(pares))
    s.index = pd.to_datetime(s.index, format="%d/%m/%Y")
    return s.sort_index().resample("ME").last()


def _cpi_eua_nivel() -> pd.Series:
    """Nível do CPI americano (BLS). A API sem chave falha de forma intermitente e às vezes devolve
    a janela pela metade: cada janela só é aceita se vier praticamente completa; senão tenta de novo."""
    import requests
    lvl, a = {}, 2002
    while a <= date.today().year:
        b = min(a + 9, date.today().year)
        esperado = (b - a + 1) * 12 - (12 - date.today().month if b == date.today().year else 0) - 3
        for _ in range(5):
            try:
                j = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                                  json={"seriesid": ["CUUR0000SA0"], "startyear": str(a), "endyear": str(b)},
                                  timeout=40).json()
                if j.get("status") == "REQUEST_SUCCEEDED" and j["Results"].get("series"):
                    parcial = {}
                    for it in j["Results"]["series"][0]["data"]:
                        if it["period"].startswith("M") and it["period"] != "M13":
                            parcial[f"{it['year']}-{int(it['period'][1:]):02d}-01"] = float(it["value"])
                    if len(parcial) >= esperado:
                        lvl.update(parcial)
                        break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(3)
        a = b + 1
    s = pd.Series(lvl)
    s.index = pd.to_datetime(s.index)
    return s.sort_index().resample("ME").last()


def _serie_json(s: pd.Series) -> dict:
    return {d.strftime("%Y-%m"): float(v) for d, v in s.dropna().items()}


def _serie_de_json(d: dict) -> pd.Series:
    s = pd.Series(d)
    s.index = pd.to_datetime(s.index) + pd.offsets.MonthEnd(0)
    return s.sort_index()


SERIES = ("dxy", "commod", "dolar", "ipca", "cpi_eua")
_FONTE = {"dxy": lambda: _serie_json(_yahoo("DX-Y.NYB")), "commod": lambda: _serie_json(_yahoo("DBC")),
          "dolar": lambda: _serie_json(_yahoo("BRL=X")), "ipca": lambda: _serie_json(_ipca_mensal()),
          "cpi_eua": lambda: _serie_json(_cpi_eua_nivel())}
RETENTAR_APOS = 6 * 60 * 60      # série que falhou só é tentada de novo depois de 6h (BLS limita requisições)


def _problema(s: dict | None, hoje: pd.Timestamp | None = None, max_dias: int = 120) -> str | None:
    """Motivo pelo qual uma série não presta, ou None se está boa.

    Coleta parcial (uma janela de anos que falhou) deixaria a série parada no passado ou com buraco no
    meio, e o PPC/modelo seriam calculados em cima de dado velho. Por isso a série é recusada."""
    hoje = hoje if hoje is not None else pd.Timestamp.today().normalize()
    s = s or {}
    if len(s) < 100:
        return "incompleta"
    ult = pd.Timestamp(max(s) + "-01")
    if (hoje - ult).days > max_dias:
        return f"parada em {max(s)}"
    faltam = len(pd.period_range("2010-01", ult.strftime("%Y-%m"), freq="M")) -         len({m for m in s if m >= "2010-01"})
    if faltam > 2:
        return f"com {faltam} meses faltando desde 2010"
    return None


def _validar_frescor(d: dict, hoje: pd.Timestamp | None = None, max_dias: int = 120) -> None:
    for nome in SERIES:
        motivo = _problema(d.get(nome), hoje, max_dias)
        if motivo:
            raise RuntimeError(f"série {nome} {motivo}")


def _ler_cache() -> dict | None:
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else None
    except Exception:  # noqa: BLE001
        return None


def carregar_insumos(usar_cache: bool = True) -> dict:
    """Cada série é tratada sozinha: a que falhar mantém a versão boa do cache (se houver) ou fica de fora.
    O resultado traz `faltando` (séries sem dado bom) e `aviso`; só levanta erro se nada serviu."""
    cache = _ler_cache() or {}
    agora = time.time()
    tentado = float(cache.get("tentado_em", 0)) if usar_cache else 0
    out, faltando, mexeu = {}, [], False
    for nome in SERIES:
        atual = cache.get(nome)
        bom = _problema(atual) is None
        # série boa e recente no cache: reaproveita; ruim: só refaz se a última tentativa já passou
        if bom and usar_cache and agora - float(cache.get("gerado_ts", 0)) < CACHE_TTL:
            out[nome] = atual
            continue
        if not bom and usar_cache and agora - tentado < RETENTAR_APOS:
            faltando.append(nome)
            continue
        try:
            nova = _FONTE[nome]()
            nova = nova if isinstance(nova, dict) else None
        except Exception:  # noqa: BLE001
            nova = None
        mexeu = True
        if nova and _problema(nova) is None:
            out[nome] = nova
        elif bom:
            out[nome] = atual                  # fonte falhou: fica com o último dado bom
        else:
            faltando.append(nome)
    if len(out) == 0:
        raise RuntimeError("nenhuma fonte disponível agora")
    out["faltando"] = faltando
    out["gerado_ts"] = agora if not faltando else cache.get("gerado_ts", 0)
    out["tentado_em"] = agora if mexeu else cache.get("tentado_em", agora)
    out["gerado_em"] = date.today().isoformat()
    if mexeu or not CACHE_FILE.exists():
        try:
            CACHE_FILE.parent.mkdir(exist_ok=True)
            CACHE_FILE.write_text(json.dumps(out), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    if faltando:
        out["aviso"] = ("Sem dado confiável agora para: " + ", ".join(faltando) +
                        ". O que depende disso não é mostrado até a fonte voltar.")
    return out


def calcular(serie_cambio: list[dict], insumos: dict) -> dict:
    """serie_cambio = cambio.buscar_cambio()['serie'] (traz dolar, carry, risco). Junta tudo e calcula.
    Cada parte só aparece se os dados dela estão bons (PPC precisa de IPCA e CPI; modelo de DXY e commod)."""
    cb = pd.DataFrame(serie_cambio)
    cb.index = pd.to_datetime(cb["data"] + "-01") + pd.offsets.MonthEnd(0)
    dolar = _serie_de_json(insumos["dolar"])
    ppc, ppc_series = {}, {}
    if insumos.get("ipca") and insumos.get("cpi_eua"):
        ipca_s, cpi_s = _serie_de_json(insumos["ipca"]), _serie_de_json(insumos["cpi_eua"])
        ppc = ppc_por_ano_base(dolar, ipca_s, cpi_s)
        for ano in ANOS_BASE_GRAFICO:
            sr = ppc_serie(dolar, ipca_s, cpi_s, ano)
            if sr is not None:
                ppc_series[ano] = {"data": [d.strftime("%Y-%m") for d in sr.index],
                                   "justo": [float(v) for v in sr]}
    modelo = None
    if insumos.get("dxy") and insumos.get("commod"):
        painel = pd.DataFrame({"dolar": dolar, "dxy": _serie_de_json(insumos["dxy"]),
                               "commod": _serie_de_json(insumos["commod"]),
                               "risco": cb["risco"], "carry": cb["carry"]})
        modelo = modelo_fundamentos(painel[painel.index >= "2013-01-01"])
    return {"ppc": ppc, "ppc_series": ppc_series, "dolar_serie": {"data": [d.strftime("%Y-%m") for d in dolar.index], "dolar": [float(v) for v in dolar]}, "modelo": modelo, "faixa": faixa_justa(ppc, modelo),
            "dolar_atual": float(dolar.iloc[-1]), "mes": dolar.index[-1].strftime("%Y-%m"),
            "aviso": insumos.get("aviso"), "faltando": insumos.get("faltando", [])}
