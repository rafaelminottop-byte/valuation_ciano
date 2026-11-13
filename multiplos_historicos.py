"""Quanto o mercado costuma pagar pelo lucro: P/L histórico por setor e P/L em função do juro real.

Os números vêm de data/multiplos_historicos.json (gerado por scripts/construir_multiplos.py).
Aqui só se lê esse arquivo e se transformam os múltiplos em preço por ação, no mesmo formato
das células da tabela de resultado (pessimista = 25% mais baixo, intermediário = mediana,
otimista = 25% mais alto).
"""
import json
from dataclasses import dataclass
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent / "data" / "multiplos_historicos.json"
CENARIOS = ("pessimista", "intermediario", "otimista")


@dataclass
class ValorPorMultiplo:
    nome: str
    multiplo: float
    valuation_final_por_acao: float
    upside_percentual: float


def carregar() -> dict:
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def multiplos_setor(setor: str, dados: dict = None) -> dict | None:
    """{'pessimista','intermediario','otimista'} -> P/L histórico do setor (ou do mercado, se o setor não existir)."""
    d = dados if dados is not None else carregar()
    s = (d.get("setores") or {}).get(setor) or d.get("mercado")
    if not s:
        return None
    return {"pessimista": s["p25"], "intermediario": s["p50"], "otimista": s["p75"]}


def multiplos_juro_real(ntnb: float, dados: dict = None) -> dict | None:
    """P/L que o mercado pagou, em média, com a NTN-B de hoje.

    Lucro/preço (%) ≈ a + b × NTN-B, com faixa de erro dos resíduos; P/L = 100 / (lucro/preço).
    Juro real mais alto -> lucro/preço exigido maior -> P/L menor.
    """
    d = dados if dados is not None else carregar()
    j = d.get("juro_real")
    if not j or ntnb is None:
        return None
    ey = j["a"] + j["b"] * ntnb
    ey_alto, ey_baixo = ey + j["res_p75"], ey + j["res_p25"]   # exigir mais retorno = P/L menor
    if min(ey_alto, ey, ey_baixo) <= 0:
        return None
    return {"pessimista": 100 / ey_alto, "intermediario": 100 / ey, "otimista": 100 / ey_baixo}


def resultado_por_multiplo(lpa: float, preco_atual: float, multiplos: dict | None) -> dict | None:
    """Preço justo = lucro por ação de hoje × múltiplo, por cenário. Mesmo formato do motor."""
    if not multiplos or not lpa or lpa <= 0 or not preco_atual or preco_atual <= 0:
        return None
    out = {}
    for cen in CENARIOS:
        m = multiplos[cen]
        justo = lpa * m
        out[cen] = ValorPorMultiplo(cen, m, justo, (justo / preco_atual - 1) * 100)
    return {"resultados": out}
