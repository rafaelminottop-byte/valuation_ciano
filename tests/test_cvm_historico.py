"""Testes do histórico de EBIT da CVM (sem rede: usam um cache sintético)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cvm_historico as cvm  # noqa: E402

CACHE = {
    "tickers": {"CICL3": "11", "CICL4": "11"},
    "empresas": {"11": {"nome": "CICLICA S.A.", "anos": {
        "2013": {"ebit": 10.0, "lucro": 6.0}, "2014": {"ebit": -4.0, "lucro": -6.0},
        "2015": {"ebit": -6.0, "lucro": -9.0}, "2016": {"ebit": 8.0},
        "2017": {"ebit": 20.0, "lucro": 12.0}}}},
}


def test_historico_liga_ticker_ao_cnpj_e_ordena_os_anos():
    h = cvm.historico("cicl4", CACHE)
    assert h["nome"] == "CICLICA S.A."
    assert list(h["anos"]) == [2013, 2014, 2015, 2016, 2017]
    assert h["anos"][2016] == {"ebit": 8.0, "lucro": None, "desp_fin": None}


def test_ticker_desconhecido_devolve_vazio():
    assert cvm.historico("XXXX3", CACHE) == {}


def test_media_normalizada_usa_so_os_n_ultimos_anos_e_conta_negativos():
    h = cvm.historico("CICL3", CACHE)
    r = cvm.ebit_normalizado(h, 3)                      # 2015, 2016, 2017
    assert r["anos"] == [2015, 2016, 2017]
    assert r["media"] == pytest.approx((-6 + 8 + 20) / 3)
    assert r["negativos"] == 1
    r_tudo = cvm.ebit_normalizado(h, 99)
    assert r_tudo["n"] == 5 and r_tudo["negativos"] == 2
    assert r_tudo["media"] == pytest.approx(28 / 5)


def test_media_sem_dados():
    assert cvm.ebit_normalizado({}, 5)["media"] is None


def test_cobertura_dos_juros_compara_ebit_com_despesa_financeira():
    cache = {"tickers": {"X3": "1"}, "empresas": {"1": {"nome": "X", "anos": {
        "2020": {"ebit": 100.0, "desp_fin": -40.0},     # a DRE traz a despesa negativa
        "2021": {"ebit": 30.0, "desp_fin": -60.0},
        "2022": {"ebit": 50.0, "desp_fin": 0.0},        # sem dívida
        "2023": {"ebit": 50.0}}}}}                      # sem a conta: ignora
    c = {r["ano"]: r for r in cvm.cobertura_juros(cvm.historico("X3", cache))}
    assert c[2020]["cobertura"] == pytest.approx(2.5) and c[2020]["cobre"]
    assert c[2021]["cobertura"] == pytest.approx(0.5) and not c[2021]["cobre"]
    assert c[2022]["cobertura"] is None and c[2022]["cobre"]
    assert 2023 not in c
