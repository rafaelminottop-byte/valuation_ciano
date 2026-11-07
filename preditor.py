"""
Preditor de assimetria do Ibovespa — camada de LÓGICA (sem UI).

Não prevê topo/fundo (ninguém faz isso de forma confiável). Em vez disso mede,
de forma condicional e sempre com a amostra à mostra:

  1. ESTADO atual: ciclo da Selic, risco-país, carry e esticamento do Ibov.
  2. SCORE DE CONTINUIDADE (0–100): quão favorável está a assimetria para seguir
     comprado. Alto = colchão grande; baixo = o colchão sumiu.
  3. DISTRIBUIÇÃO CONDICIONAL: olhando os meses históricos em estado PARECIDO
     (vizinhos no espaço dos drivers), como foi o retorno 12m à frente do Ibov —
     mediana, piso, % positivo, razão ganho/perda — com N de meses e de episódios.
  4. FLAG DE EXAUSTÃO: alerta de RISCO (não "venda") quando a bolsa está esticada
     e o macro aperta ao mesmo tempo.

Validação dos sinais (painel mensal 1999→, retorno 12m à frente do Ibov):
  risco nível +0.48 · Selic nível +0.39 · risco Δ12m +0.29 · carry +0.22 ·
  esticamento −0.16 · Selic cortando: mediana +13% e 69% positivo.
Correlações modestas e janelas 12m sobrepostas — por isso o app mostra o N e
trata tudo como probabilidade, nunca como ordem.

Fontes (todas públicas e já usadas no projeto):
  Ibov mensal — Yahoo (^BVSP) · risco-país/carry — cambio.py (EMBI+CDS, BCB, BLS)
  Selic meta (SGS 432) e CDI (SGS 4391) — BCB via macro._json_bc (IPv4).
  NTN-B 10a — CSV do Tesouro Transparente, interpolada p/ 10 anos constantes (desde 2005).

Camadas: score de continuidade, distribuição condicional, banda de exposição,
estudo do desconto (comprar e segurar vs CDI), correlações móveis dos drivers e
validação com janelas independentes.
"""
from __future__ import annotations

import json
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_PANEL = CACHE_DIR / "preditor_painel_v2.json"  # v2: + NTN-B 10a e CDI mensal
CACHE_TTL_SEGUNDOS = 24 * 60 * 60  # 24h (padrão do projeto)

INICIO = "1999-01"   # pós-câmbio flutuante
JANELA_FWD = 12      # meses à frente que queremos descrever
K_VIZINHOS = 36      # meses análogos usados na distribuição condicional

# Pesos do score, proporcionais à força histórica (|correlação|) de cada sinal.
# Somam 1.0. O ciclo da Selic entra por BUCKET (não-linear) em vez de Δ6m linear.
PESOS = {
    "risco": 0.255,      # risco-país nível (alto = bolsa descontada)
    "selic": 0.17,       # Selic nível (alto = descontada)
    "risco_d12": 0.119,  # risco subindo nos últimos 12m (medo chegando ao pico)
    "carry": 0.102,      # carry real alto atrai capital
    "estic_inv": 0.102,  # NÃO estar esticado (exaustão invertida)
    "selic_ciclo": 0.102,# ciclo de corte favorece
    # NTN-B 10a (juro real longo): nível alto = bolsa descontada frente à renda fixa real.
    # Entrou com 15% por fundamento econômico (corr. +0,39 com o retorno 12m à frente).
    # No teste fora da amostra o ganho foi marginal e DENTRO DO RUÍDO (~9 janelas
    # independentes): não é prova de melhora — por isso o peso é modesto.
    "ntnb": 0.15,
}
# Contribuição do ciclo da Selic (0–100), das medianas 12m observadas por fase.
_CICLO_SCORE = {"cortando": 100.0, "parada": 50.0, "subindo": 18.0}


# ---------------------------------------------------------------------------
# Painel histórico
# ---------------------------------------------------------------------------
def _sgs_historico(codigo: int) -> pd.Series:
    """Série do BCB/SGS desde 1998, buscada em blocos de 9 anos (limite do SGS)."""
    import macro

    pts: dict[str, float] = {}
    fim = date.today()
    ini_total = date(1998, 1, 1)
    cur = fim
    while cur > ini_total:
        ci = max(ini_total, cur - timedelta(days=365 * 9))
        url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
               f"&dataInicial={ci.strftime('%d/%m/%Y')}&dataFinal={cur.strftime('%d/%m/%Y')}")
        bloco = macro._json_bc(url)
        for x in (bloco if isinstance(bloco, list) else []):
            v = str(x.get("valor", "")).replace(",", ".")
            try:
                pts[x["data"]] = float(v)
            except ValueError:
                pass
        cur = ci - timedelta(days=1)
    if not pts:
        return pd.Series(dtype=float)
    s = pd.Series(pts)
    s.index = pd.to_datetime(s.index, dayfirst=True)
    return s.sort_index()


def _selic_mensal() -> pd.Series:
    """Selic meta (SGS 432) no fim de cada mês."""
    s = _sgs_historico(432)
    if s.empty:
        return s
    s = s.resample("ME").last()
    return pd.Series(s.values, index=pd.PeriodIndex(s.index, freq="M"))


def _cdi_mensal() -> pd.Series:
    """CDI acumulado no mês (SGS 4391), em fração (0,011 = 1,1%)."""
    s = _sgs_historico(4391)
    if s.empty:
        return s
    s = pd.Series(s.values / 100.0, index=pd.PeriodIndex(s.index, freq="M"))
    return s[~s.index.duplicated(keep="last")]


def _ntnb_mensal() -> pd.Series:
    """NTN-B (Tesouro IPCA+ sem cupom) de 10 anos CONSTANTES, mês a mês desde 2005.

    Fonte: CSV oficial do Tesouro Transparente (o mesmo que macro.py já usa). A cada
    mês pega o último dia de negociação e INTERPOLA a taxa real para 10 anos entre os
    dois vencimentos que cercam esse prazo (a curva tinha poucos vértices, então pegar
    o 'mais próximo' dava prazos de 5 a 15 anos). Serve para captar NÍVEL e DIREÇÃO do
    juro real longo — não tem precisão de ponto-base quando os vértices vizinhos
    estão distantes.
    """
    import io

    import macro
    import requests

    macro._forcar_ipv4()
    r = requests.get(macro.URL_TESOURO_TAXAS, headers=macro.HEADERS, timeout=90)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), sep=";", encoding="latin1")
    df["Data Base"] = pd.to_datetime(df["Data Base"], format="%d/%m/%Y")
    df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], format="%d/%m/%Y")
    df["tx"] = df["Taxa Compra Manha"].astype(str).str.replace(",", ".").astype(float)
    ip = df[df["Tipo Titulo"] == "Tesouro IPCA+"].copy()
    ip["mes"] = ip["Data Base"].dt.to_period("M")
    out = {}
    for mes, g in ip.groupby("mes"):
        ult = g["Data Base"].max()
        dia = g[g["Data Base"] == ult].copy()
        dia["anos"] = (dia["Data Vencimento"] - ult).dt.days / 365.25
        dia = dia.sort_values("anos")
        a, t = dia["anos"].values, dia["tx"].values
        if len(a) >= 2 and a.min() <= 10 <= a.max():
            out[mes] = float(np.interp(10, a, t))
    if not out:
        return pd.Series(dtype=float)
    return pd.Series(list(out.values()),
                     index=pd.PeriodIndex(list(out.keys()), freq="M"), dtype=float)


def _montar_painel() -> pd.DataFrame:
    """DataFrame mensal: ibov, risco, carry, selic. Só coleta/alinhamento."""
    import cambio
    import yfinance as yf

    cb = cambio.buscar_cambio()
    dfc = pd.DataFrame(cb.get("serie") or [])
    if not dfc.empty:
        dfc["per"] = pd.PeriodIndex(dfc["data"], freq="M")
        dfc = dfc.set_index("per")[["risco", "carry"]]
    else:
        dfc = pd.DataFrame(columns=["risco", "carry"])

    h = yf.Ticker("^BVSP").history(period="max", interval="1mo")["Close"].dropna()
    ibov = pd.Series(h.values, index=pd.PeriodIndex(h.index, freq="M"), name="ibov")
    ibov = ibov[~ibov.index.duplicated(keep="last")]

    selic = _selic_mensal().rename("selic")
    cdi = _cdi_mensal().rename("cdi")
    try:
        ntnb = _ntnb_mensal().rename("ntnb")
    except Exception:  # noqa: BLE001  (sem NTN-B o modelo segue, só sem esse driver)
        ntnb = pd.Series(dtype=float, name="ntnb")

    df = pd.concat([ibov, dfc, selic, cdi, ntnb], axis=1).sort_index()
    df = df[df.index >= pd.Period(INICIO, "M")]
    return df


def _painel(usar_cache: bool = True) -> pd.DataFrame:
    """Painel com cache de 24h (JSON)."""
    if usar_cache and CACHE_PANEL.exists():
        try:
            if time.time() - CACHE_PANEL.stat().st_mtime < CACHE_TTL_SEGUNDOS:
                raw = json.loads(CACHE_PANEL.read_text(encoding="utf-8"))
                df = pd.DataFrame(raw)
                df.index = pd.PeriodIndex(df.pop("per"), freq="M")
                return df
        except Exception:  # noqa: BLE001
            pass
    df = _montar_painel()
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        out = df.reset_index(names="per").copy()
        out["per"] = out["per"].astype(str)
        CACHE_PANEL.write_text(out.to_json(orient="records"), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    return df


# ---------------------------------------------------------------------------
# Features de estado + alvo
# ---------------------------------------------------------------------------
def _com_features(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["fwd12"] = d["ibov"].shift(-JANELA_FWD) / d["ibov"] - 1.0
    d["selic_d6"] = d["selic"].diff(6)
    d["risco_d12"] = d["risco"].diff(12)
    d["mm12"] = d["ibov"].rolling(12).mean()
    d["estic"] = d["ibov"] / d["mm12"] - 1.0   # esticamento vs MM12
    # z da banda (mesma definição validada no walk-forward): desvio do ln(preço)
    # da MM24, padronizado por 36m. Mede quantos desvios o Ibov está da tendência.
    lnp = np.log(d["ibov"])
    mm24 = lnp.rolling(24).mean()
    estic_log = lnp - mm24
    mest = estic_log.rolling(36).mean()
    sest = estic_log.rolling(36).std()
    d["z"] = (estic_log - mest) / sest
    # Níveis em PONTOS do Ibov: tendência (z=0, onde recompra) e teto (z=1,5, onde alivia).
    d["ln_media"] = mm24 + mest
    d["sest"] = sest
    d["pz0"] = np.exp(d["ln_media"])
    d["pz15"] = np.exp(d["ln_media"] + 1.5 * sest)

    # NTN-B: direção do juro real longo (subindo = pressão sobre o valuation).
    if "ntnb" in d:
        d["ntnb_d12"] = d["ntnb"].diff(12)

    # Retorno a frente a partir do fechamento de t (meses t+1..t+H) — Ibov e CDI
    # com o MESMO alinhamento, para o 'excesso sobre o CDI' ser comparável.
    d["fwd24"] = d["ibov"].shift(-24) / d["ibov"] - 1.0
    if "cdi" in d:
        lg = np.log1p(d["cdi"])
        for h in (12, 24):
            d[f"cdi{h}"] = np.expm1(lg.rolling(h).sum().shift(-h))
        d["exc12"] = d["fwd12"] - d["cdi12"]
    return d


def _fase_selic(d6: float | None) -> str:
    if d6 is None or pd.isna(d6):
        return "parada"
    if d6 < -0.25:
        return "cortando"
    if d6 > 0.25:
        return "subindo"
    return "parada"


def _pct(serie: pd.Series, valor: float) -> float:
    """Percentil (0–100) de ``valor`` dentro da distribuição histórica da série."""
    s = serie.dropna()
    if s.empty or pd.isna(valor):
        return 50.0
    return float((s < valor).mean() * 100.0)


# ---------------------------------------------------------------------------
# Score de continuidade (0–100)
# ---------------------------------------------------------------------------
def _score(d: pd.DataFrame) -> dict:
    cur = d.iloc[-1]
    comp = {
        "risco": _pct(d["risco"], cur["risco"]),
        "selic": _pct(d["selic"], cur["selic"]),
        "risco_d12": _pct(d["risco_d12"], cur["risco_d12"]),
        "carry": _pct(d["carry"], cur["carry"]),
        "estic_inv": 100.0 - _pct(d["estic"], cur["estic"]),
        "selic_ciclo": _CICLO_SCORE[_fase_selic(cur["selic_d6"])],
        # NTN-B ausente/NaN -> NaN (componente é ignorado, pesos se renormalizam)
        "ntnb": (_pct(d["ntnb"], cur["ntnb"])
                 if ("ntnb" in d and pd.notna(cur.get("ntnb"))) else float("nan")),
    }
    # ignora componentes sem dado (mantém a soma dos pesos usados)
    usados = {k: v for k, v in comp.items() if v is not None and not pd.isna(v)}
    w = {k: PESOS[k] for k in usados}
    total_w = sum(w.values()) or 1.0
    score = sum(usados[k] * w[k] for k in usados) / total_w
    return {"score": round(score, 1), "componentes": {k: round(v, 0) for k, v in comp.items()}}


def _banda_score(score: float) -> tuple[str, str]:
    if score >= 68:
        return "forte", "Continuidade favorável — colchão de segurança grande."
    if score >= 45:
        return "neutro", "Terreno neutro — assimetria sem viés claro."
    return "fraco", "Colchão fino — a margem de segurança histórica sumiu."


# ---------------------------------------------------------------------------
# Banda de exposição (mean-reversion) — validada em teste fora da amostra:
# reduzir quando o Ibov sai da banda (esticado) e estacionar no CDI, recomprando
# na volta à média, bateu CDI e buy&hold em 2013–2026 (dados nunca vistos) e no
# walk-forward 2009–2026 (CAGR ~12.8% vs CDI 9.9%, tombo −31% vs −43%).
# ---------------------------------------------------------------------------
_LIMIAR_ESTICADO = 1.0   # z acima disto = zona de alívio (robusto fora da amostra)


def banda_exposicao(d: pd.DataFrame, score: float = 50.0) -> dict:
    """Zona de exposição de hoje — FORMA REFINADA (lições do stress-test):

    - Redução SEMPRE parcial (deixar só o lucro / reduzir metade), nunca 100%:
      numa bolsa que se reacomoda mais alto, sair inteiro te tira do novo patamar.
    - TRAVA DO MACRO: em zona esticada, a banda só sugere aliviar quando o score
      de continuidade NÃO está forte. Esticado + Selic cortando = bull (2016, 2026)
      — nesses casos o histórico diz para NÃO aliviar.
    - Recompra só na volta à média (z<0); nunca no teto (seria comprar caro).
    """
    z = d["z"].iloc[-1]
    if z is None or pd.isna(z):
        return {"zona": "indefinida", "z": None}

    teto = d["pz15"].iloc[-1]
    media = d["pz0"].iloc[-1]
    ibov = d["ibov"].iloc[-1]
    macro_forte = score >= 68

    if z >= _LIMIAR_ESTICADO:
        zona = "muito esticada" if z >= 1.5 else "esticada"
        if macro_forte:
            acao, ativa = "manter", False
            nota = ("Esticado, mas o macro está em continuidade forte (Selic cedendo). "
                    "Histórico (2016, 2026): não aliviar dentro de um bull.")
        else:
            acao, ativa = "aliviar parte", True
            nota = ("Esticado e macro sem apoio — considere aliviar PARTE (deixar só o lucro / "
                    "reduzir metade) e estacionar no CDI. Nunca sair 100%.")
    elif z <= 0:
        zona, acao, ativa = "comprimida", "retomar", False
        nota = "Ibov abaixo da própria tendência — zona de manter ou retomar exposição."
    else:
        zona, acao, ativa = "neutra", "manter", False
        nota = "Nem esticado nem comprimido — sem gatilho de banda."

    return {
        "z": round(float(z), 2),
        "zona": zona,
        "acao": acao,
        "ativa": ativa,
        "macro_forte": bool(macro_forte),
        "nota": nota,
        "teto_pts": int(round(float(teto))) if pd.notna(teto) else None,
        "media_pts": int(round(float(media))) if pd.notna(media) else None,
        "ibov_pts": int(round(float(ibov))) if pd.notna(ibov) else None,
    }


# ---------------------------------------------------------------------------
# Estudo do DESCONTO: comprar e segurar vs CDI quando o Ibov está bem abaixo da
# tendência (z negativo). Calculado ao vivo a partir do painel, não números fixos.
#
# O que o estudo mostrou (1999→): comprar e segurar SÓ compensou contra o CDI em
# desconto PROFUNDO (z < −1,5). Em desconto moderado (−1,0 a 0) NÃO compensou. E mesmo
# no profundo o ganho se concentra em poucos episódios (2016 e 2020) — a mediana
# esconde isso, por isso o app mostra os episódios um a um.
# ---------------------------------------------------------------------------
_FAIXAS_DESCONTO = [
    ("profundo", float("-inf"), -1.5),
    ("forte", -1.5, -1.0),
    ("moderado", -1.0, -0.5),
    ("leve", -0.5, 0.0),
]


def _episodios_z(d: pd.DataFrame, limiar: float) -> list:
    """Corridas contíguas de meses com z < limiar → [(início, fim, z_mínimo)]."""
    eps, ini, zmin = [], None, None
    for p, v in d["z"].items():
        if pd.isna(v):
            continue
        if v < limiar:
            if ini is None:
                ini, zmin = p, v
            else:
                zmin = min(zmin, v)
        elif ini is not None:
            eps.append((ini, p, float(zmin)))
            ini = None
    if ini is not None:
        eps.append((ini, d.index[-1], float(zmin)))
    return eps


def _pc(v) -> float | None:
    return None if v is None or pd.isna(v) else round(float(v) * 100, 1)


def zona_desconto(d: pd.DataFrame) -> dict:
    if "cdi12" not in d or d["cdi12"].notna().sum() < 24:
        return {"erro": "CDI histórico indisponível."}
    cur = d.iloc[-1]
    z = cur["z"]

    faixas = []
    for nome, lo, hi in _FAIXAS_DESCONTO + [("acima da média", 0.0, float("inf"))]:
        m = d[(d["z"] >= lo) & (d["z"] < hi)].dropna(subset=["fwd12", "cdi12"])
        if len(m) < 4:
            faixas.append({"faixa": nome, "n_meses": int(len(m))})
            continue
        exc = m["fwd12"] - m["cdi12"]
        faixas.append({
            "faixa": nome, "n_meses": int(len(m)), "n_episodios": _n_episodios(list(m.index)),
            "ibov_med": _pc(m["fwd12"].median()), "cdi_med": _pc(m["cdi12"].median()),
            "exc_med": _pc(exc.median()), "pct_bate": round(float((exc > 0).mean()) * 100, 0),
            "pior": _pc(m["fwd12"].min()),
        })
    faixa_atual = "acima da média"
    if pd.notna(z):
        for nome, lo, hi in _FAIXAS_DESCONTO:
            if lo <= z < hi:
                faixa_atual = nome

    # Cada episódio de desconto profundo, entrando no 1º mês em que o z cruzou −1,5.
    eps = []
    for ini, _fim, zmin in _episodios_z(d, -1.5):
        r = d.loc[ini]
        eps.append({"inicio": str(ini), "z_min": round(zmin, 1),
                    "ibov12": _pc(r["fwd12"]), "cdi12": _pc(r["cdi12"]),
                    "ibov24": _pc(r["fwd24"]), "cdi24": _pc(r["cdi24"])})
    e12 = [e for e in eps if e["ibov12"] is not None and e["cdi12"] is not None]
    e24 = [e for e in eps if e["ibov24"] is not None and e["cdi24"] is not None]

    # Em PONTOS: onde o Ibov precisa estar para o z cruzar os limiares de desconto.
    lm, s = cur.get("ln_media"), cur.get("sest")

    def nivel(k):
        return int(round(float(np.exp(lm + k * s)))) if pd.notna(lm) and pd.notna(s) else None

    n_prof, n_forte = nivel(-1.5), nivel(-1.0)
    ibov = float(cur["ibov"])
    return {
        "z": None if pd.isna(z) else round(float(z), 2),
        "faixa_atual": faixa_atual,
        "faixas": faixas,
        "episodios": eps,
        "n_ep_profundos": len(eps),
        "ep_bate12": [sum(e["ibov12"] > e["cdi12"] for e in e12), len(e12)],
        "ep_bate24": [sum(e["ibov24"] > e["cdi24"] for e in e24), len(e24)],
        "nivel_profundo_pts": n_prof,
        "nivel_forte_pts": n_forte,
        "queda_ate_profundo_pct": (round((n_prof / ibov - 1) * 100, 1) if n_prof else None),
    }


# ---------------------------------------------------------------------------
# Correlações móveis: os drivers AINDA movem o Ibov? (detector de troca de regime)
# Correlação, em janela de 36 meses, entre o retorno MENSAL do Ibov e a variação
# MENSAL de cada driver (sem sobreposição de janelas, ao contrário dos retornos 12m).
# Sinal esperado: negativo nos três (juro real, risco e Selic subindo pesam na bolsa).
# ---------------------------------------------------------------------------
def correlacoes_moveis(d: pd.DataFrame, janela: int = 36) -> list:
    r = np.log(d["ibov"]).diff()
    out = []
    # Selic fica de fora de propósito: muda em degraus, a variação mensal é quase sempre
    # zero e a correlação sairia ~0 sem significar que ela não importa (leitura enganosa).
    for nome, col in [("NTN-B 10a (juro real longo)", "ntnb"), ("Risco-país", "risco")]:
        if col not in d:
            continue
        rc = r.rolling(janela).corr(d[col].diff()).dropna()
        if len(rc) < 12:
            continue
        atual = float(rc.iloc[-1])
        status = "firme" if atual <= -0.2 else "invertida" if atual >= 0.2 else "fraca"
        out.append({
            "driver": nome, "atual": round(atual, 2), "media": round(float(rc.mean()), 2),
            "min": round(float(rc.min()), 2), "max": round(float(rc.max()), 2),
            "status": status,
            "serie": {"datas": [str(p) for p in rc.index[-72:]],
                      "valor": [round(float(v), 2) for v in rc.iloc[-72:]]},
        })
    return out


# ---------------------------------------------------------------------------
# Validação com janelas INDEPENDENTES (não sobrepostas).
# Para cada mês, o score é recalculado usando SÓ dados até aquele mês (percentis
# expansivos); depois só se amostra 1 mês a cada 12, em todas as 12 defasagens
# possíveis, para não escolher a melhor. CAVEAT que precisa ficar visível: a
# NORMALIZAÇÃO é fora da amostra, mas os PESOS foram escolhidos olhando as
# correlações da amostra inteira — logo a validação é OTIMISTA, não 100% limpa.
# ---------------------------------------------------------------------------
def validar_score(d: pd.DataFrame, inicio: str = "2016-01") -> dict:
    if "exc12" not in d:
        return {"erro": "CDI indisponível."}
    idx = [p for p in d.index if p >= pd.Period(inicio, "M")]
    if len(idx) < 60:
        return {"erro": "Histórico curto para validar."}
    E = d.loc[idx].copy()
    E["score"] = [_score(d.loc[:p])["score"] for p in idx]
    E = E.dropna(subset=["fwd12", "exc12"])
    if len(E) < 48:
        return {"erro": "Amostra curta para validar."}

    ics, terc = [], {0: [], 1: [], 2: []}
    for off in range(12):
        a = E.iloc[off::12]
        if len(a) < 6:
            continue
        ics.append(float(a["score"].rank().corr(a["fwd12"].rank())))
        q = pd.qcut(a["score"].rank(method="first"), 3, labels=False)
        for k in range(3):
            g = a[q == k]
            if len(g):
                terc[k].append((float(g["exc12"].median()), float((g["exc12"] > 0).mean())))
    nomes = ["baixo", "médio", "alto"]
    return {
        "inicio": str(E.index.min()), "fim": str(E.index.max()),
        "n_meses": int(len(E)), "n_janelas": int(len(E) // 12),
        "spearman_medio": round(float(np.mean(ics)), 2),
        "spearman_min": round(float(np.min(ics)), 2),
        "spearman_max": round(float(np.max(ics)), 2),
        "tercos": [{"nome": nomes[k],
                    "exc_med": round(float(np.mean([x[0] for x in terc[k]])) * 100, 1),
                    "pct_bate": round(float(np.mean([x[1] for x in terc[k]])) * 100, 0)}
                   for k in range(3) if terc[k]],
    }


def _seguro(fn, *args):
    """Um estudo que falha não pode derrubar a leitura inteira."""
    try:
        return fn(*args)
    except Exception as e:  # noqa: BLE001
        return {"erro": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Distribuição condicional (meses análogos)
# ---------------------------------------------------------------------------
def _n_episodios(periodos: list[pd.Period]) -> int:
    """Conta 'episódios' distintos: corridas de meses separadas por gap > 3 meses."""
    if not periodos:
        return 0
    ords = sorted(p.ordinal for p in periodos)
    eps = 1
    for a, b in zip(ords, ords[1:]):
        if b - a > 3:
            eps += 1
    return eps


def _distribuicao(d: pd.DataFrame, k: int = K_VIZINHOS) -> dict:
    cols = ["risco", "selic", "selic_d6", "carry", "estic"]
    base = d.dropna(subset=cols)
    if len(base) < k + 6:
        return {"erro": "Histórico insuficiente para análogos.", "n_meses": 0}

    mu = base[cols].mean()
    sd = base[cols].std(ddof=0).replace(0, 1.0)
    z = (base[cols] - mu) / sd
    alvo = z.iloc[-1]
    dist = np.sqrt(((z - alvo) ** 2).sum(axis=1))

    # candidatos = meses com retorno 12m conhecido (exclui o próprio presente)
    cand = dist[d.loc[dist.index, "fwd12"].notna()]
    cand = cand[cand.index != base.index[-1]]
    if cand.empty:
        return {"erro": "Sem análogos com retorno futuro conhecido.", "n_meses": 0}

    viz = cand.nsmallest(min(k, len(cand))).index
    fwd = d.loc[viz, "fwd12"].dropna()
    gpos = fwd[fwd > 0].mean()
    gneg = fwd[fwd < 0].mean()
    razao = float(gpos / abs(gneg)) if (pd.notna(gpos) and pd.notna(gneg) and gneg != 0) else None
    return {
        "n_meses": int(len(fwd)),
        "n_episodios": _n_episodios(list(fwd.index)),
        "mediana": round(float(fwd.median()) * 100, 1),
        "p25": round(float(fwd.quantile(0.25)) * 100, 1),
        "p75": round(float(fwd.quantile(0.75)) * 100, 1),
        "pior": round(float(fwd.min()) * 100, 1),
        "melhor": round(float(fwd.max()) * 100, 1),
        "pct_positivo": round(float((fwd > 0).mean()) * 100, 0),
        "ganho_perda": round(razao, 2) if razao is not None else None,
        "analogos": [str(p) for p in sorted(fwd.index)[-6:]],  # amostra recente
    }


# ---------------------------------------------------------------------------
# Entrypoint público
# ---------------------------------------------------------------------------
def prever(usar_cache: bool = True) -> dict:
    """Junta estado + score + distribuição condicional + flag de exaustão."""
    try:
        df = _painel(usar_cache=usar_cache)
    except Exception as e:  # noqa: BLE001
        return {"erro": f"Falha ao montar o painel: {e}"}
    if df.empty or "ibov" not in df or df["ibov"].notna().sum() < 60:
        return {"erro": "Painel histórico insuficiente."}

    d = _com_features(df)
    cur = d.iloc[-1]
    fase = _fase_selic(cur["selic_d6"])
    sc = _score(d)
    banda, banda_txt = _banda_score(sc["score"])

    # Flag de exaustão: esticado (topo 25% histórico) E macro apertando (score baixo).
    estic_pct = _pct(d["estic"], cur["estic"])
    exaustao = bool(estic_pct >= 75 and sc["score"] < 45)

    return {
        "erro": None,
        "data_base": str(d.index[-1]),
        "estado": {
            "ciclo_selic": fase,
            "selic": None if pd.isna(cur["selic"]) else round(float(cur["selic"]), 2),
            "risco_pais": None if pd.isna(cur["risco"]) else round(float(cur["risco"]), 0),
            "carry": None if pd.isna(cur["carry"]) else round(float(cur["carry"]), 1),
            "esticamento_pct": round(estic_pct, 0),
            "ntnb": (round(float(cur["ntnb"]), 2)
                     if ("ntnb" in d and pd.notna(cur.get("ntnb"))) else None),
        },
        "score": sc["score"],
        "banda": banda,
        "banda_texto": banda_txt,
        "componentes": sc["componentes"],
        "distribuicao": _distribuicao(d),
        "banda_exposicao": banda_exposicao(d, sc["score"]),
        "desconto": _seguro(zona_desconto, d),
        "correlacoes": _seguro(correlacoes_moveis, d),
        "validacao": _seguro(validar_score, d),
        "exaustao": exaustao,
        "serie_banda": _serie_banda(d),
        "fonte": "Yahoo (^BVSP) · cambio.py (EMBI+CDS) · BCB SGS 432/4391 · Tesouro Transparente (NTN-B)",
    }


def _serie_banda(d: pd.DataFrame, n: int = 156) -> dict:
    """Série curta (últimos ``n`` meses) p/ o gráfico Ibov × tendência × teto."""
    s = d.dropna(subset=["pz15"]).tail(n)
    return {
        "datas": [str(p) for p in s.index],
        "ibov": [int(round(v)) for v in s["ibov"]],
        "pz0": [int(round(v)) for v in s["pz0"]],
        "pz15": [int(round(v)) for v in s["pz15"]],
    }


if __name__ == "__main__":
    import pprint
    pprint.pp(prever(usar_cache=False))
