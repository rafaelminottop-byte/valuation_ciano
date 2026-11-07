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
  Selic meta — BCB SGS 432 (via macro._json_bc, IPv4).
"""
from __future__ import annotations

import json
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_PANEL = CACHE_DIR / "preditor_painel_v1.json"
CACHE_TTL_SEGUNDOS = 24 * 60 * 60  # 24h (padrão do projeto)

INICIO = "1999-01"   # pós-câmbio flutuante
JANELA_FWD = 12      # meses à frente que queremos descrever
K_VIZINHOS = 36      # meses análogos usados na distribuição condicional

# Pesos do score, proporcionais à força histórica (|correlação|) de cada sinal.
# Somam 1.0. O ciclo da Selic entra por BUCKET (não-linear) em vez de Δ6m linear.
PESOS = {
    "risco": 0.30,       # risco-país nível (alto = bolsa descontada)
    "selic": 0.20,       # Selic nível (alto = descontada)
    "risco_d12": 0.14,   # risco subindo nos últimos 12m (medo chegando ao pico)
    "carry": 0.12,       # carry real alto atrai capital
    "estic_inv": 0.12,   # NÃO estar esticado (exaustão invertida)
    "selic_ciclo": 0.12, # ciclo de corte favorece
}
# Contribuição do ciclo da Selic (0–100), das medianas 12m observadas por fase.
_CICLO_SCORE = {"cortando": 100.0, "parada": 50.0, "subindo": 18.0}


# ---------------------------------------------------------------------------
# Painel histórico
# ---------------------------------------------------------------------------
def _selic_mensal() -> pd.Series:
    """Selic meta (SGS 432) mês a mês, buscada em blocos de 9 anos (limite do SGS)."""
    import macro

    pts: dict[str, float] = {}
    fim = date.today()
    ini_total = date(1998, 1, 1)
    cur = fim
    while cur > ini_total:
        ci = max(ini_total, cur - timedelta(days=365 * 9))
        url = ("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json"
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
    s = s.sort_index().resample("ME").last()
    return pd.Series(s.values, index=pd.PeriodIndex(s.index, freq="M"))


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

    df = pd.concat([ibov, dfc, selic], axis=1).sort_index()
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
    d["pz0"] = np.exp(mm24 + mest)
    d["pz15"] = np.exp(mm24 + mest + 1.5 * sest)
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
        },
        "score": sc["score"],
        "banda": banda,
        "banda_texto": banda_txt,
        "componentes": sc["componentes"],
        "distribuicao": _distribuicao(d),
        "banda_exposicao": banda_exposicao(d, sc["score"]),
        "exaustao": exaustao,
        "serie_banda": _serie_banda(d),
        "fonte": "Yahoo (^BVSP) · cambio.py (EMBI+CDS) · BCB SGS 432",
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
