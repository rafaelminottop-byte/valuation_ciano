"""Testes do congelamento de regras e do registro mensal de sinais (preditor.py).

Sem rede: usam um painel sintético e um arquivo de registro temporário.
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preditor  # noqa: E402


@pytest.fixture
def registro_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(preditor, "ARQ_REGISTRO", tmp_path / "data" / "registro_sinais.json")
    return preditor.ARQ_REGISTRO


def _sinal(ibov=100000):
    return {
        "score": 60.0, "banda": "neutro", "exaustao": False,
        "banda_exposicao": {"ibov_pts": ibov, "z": -0.5, "zona": "comprimida", "acao": "retomar"},
        "desconto": {"faixa_atual": "moderado"},
        "estado": {"ciclo_selic": "cortando", "ntnb": 7.5, "risco_pais": 200.0},
        "distribuicao": {"mediana": 10.0, "n_episodios": 9},
    }


def _painel(n=30, inicio="2024-01"):
    idx = pd.period_range(inicio, periods=n, freq="M")
    d = pd.DataFrame({"ibov": [100.0 + i for i in range(n)], "cdi12": [0.08] * n}, index=idx)
    return d


def test_regras_congeladas_batem_com_o_codigo():
    # Se este teste falhar, alguém mexeu nos parâmetros sem declarar uma nova versão.
    assert not preditor.regras_alteradas()


def test_hash_reage_a_mudanca_de_regra(monkeypatch):
    antes = preditor.hash_regras()
    monkeypatch.setitem(preditor.PESOS, "risco", preditor.PESOS["risco"] + 0.01)
    assert preditor.hash_regras() != antes
    assert preditor.regras_alteradas()


def test_registrar_grava_um_por_mes_e_nao_sobrescreve(registro_tmp):
    r1 = preditor.registrar(_sinal(100000), hoje=date(2026, 11, 7))
    assert r1["status"] == "registrado"
    r2 = preditor.registrar(_sinal(999999), hoje=date(2026, 11, 20))
    assert r2["status"] == "ja_existia"
    ent = preditor.ler_registro()["entradas"]
    assert len(ent) == 1 and ent[0]["ibov"] == 100000   # o primeiro valor é o que vale
    preditor.registrar(_sinal(101000), hoje=date(2026, 12, 3))
    assert [e["mes"] for e in preditor.ler_registro()["entradas"]] == ["2026-11", "2026-12"]


def test_registrar_recusa_quando_as_regras_mudaram(registro_tmp, monkeypatch):
    monkeypatch.setattr(preditor, "REGRAS_HASH_CONGELADO", "outro-hash")
    with pytest.raises(RuntimeError):
        preditor.registrar(_sinal(), hoje=date(2026, 11, 7))
    assert not registro_tmp.exists()   # nada foi gravado


def test_avaliacao_mede_12_meses_depois_e_so_com_mes_alvo_fechado(registro_tmp):
    preditor.registrar(_sinal(100.0), hoje=date(2024, 1, 10))   # alvo: 2025-01
    preditor.registrar(_sinal(100.0), hoje=date(2025, 3, 10))   # alvo: 2026-03 (fora do painel)
    d = _painel(n=14)            # 2024-01 .. 2025-02; último mês (2025-02) é o parcial
    d.loc[pd.Period("2025-01", "M"), "ibov"] = 110.0
    res = preditor.resumo_registro(d)
    a, b = res["entradas"]
    assert a["ibov12"] == 10.0 and a["cdi12"] == 8.0 and a["exc12"] == 2.0
    assert b["ibov12"] is None and b["avalia_em"] == "2026-03"


def test_avaliacao_nao_usa_o_ultimo_mes_do_painel(registro_tmp):
    preditor.registrar(_sinal(100.0), hoje=date(2024, 1, 10))   # alvo 2025-01
    d = _painel(n=13)            # termina em 2025-01 => esse mês é o parcial, não pode medir
    res = preditor.resumo_registro(d)
    assert res["entradas"][0]["ibov12"] is None
