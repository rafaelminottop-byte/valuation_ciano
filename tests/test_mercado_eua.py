"""Testes das partes puras do mercado_eua (montagem de registro e ranking/filtros)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mercado_eua import _montar_registro, rankear_eua


class TestMontarRegistro(unittest.TestCase):
    def _bruto(self, **kw):
        base = {"preco": 100.0, "fluxo_total": 5e9, "acoes": 1e9,
                "div_liquida": 10e9, "media_div_3a": 2.0, "fluxo_crescente": True}
        base.update(kw)
        return base

    def test_deriva_metricas(self):
        u = {"ticker": "XYZ", "nome": "XYZ Co", "setor": "Tech", "base_calculo": "EBIT", "citacoes": 3}
        r = _montar_registro(u, self._bruto())
        self.assertAlmostEqual(r["ebit_por_acao"], 5.0)         # 5e9 / 1e9
        self.assertAlmostEqual(r["p_ebit"], 20.0)               # 100 / 5
        self.assertAlmostEqual(r["div_liq_ebit"], 2.0)          # 10e9 / 5e9
        self.assertAlmostEqual(r["dy_medio_3a"], 0.02)          # 2 / 100

    def test_descarta_invalidos(self):
        u = {"ticker": "X"}
        self.assertIsNone(_montar_registro(u, self._bruto(preco=0)))
        self.assertIsNone(_montar_registro(u, self._bruto(fluxo_total=None)))
        self.assertIsNone(_montar_registro(u, self._bruto(acoes=None)))
        self.assertIsNone(_montar_registro(u, {"erro": "sem dados"}))

    def test_fluxo_negativo_sem_div_liq_ebit(self):
        # EBIT negativo -> nao calcula div_liq/ebit (evita sinal invertido)
        r = _montar_registro({"ticker": "X"}, self._bruto(fluxo_total=-1e9))
        self.assertIsNone(r["div_liq_ebit"])
        self.assertIsNone(r["p_ebit"])


class TestRankearEua(unittest.TestCase):
    def _df(self):
        # SÓLIDA (barata, pouca dívida), ALAVANCADA (barata mas endividada),
        # ANOMALA (P/EBIT<3), BANCO (base Lucro, sem div_liq_ebit)
        return pd.DataFrame([
            {"ticker": "SOL", "nome": "Solida", "setor": "Ind", "citacoes": 2,
             "base_calculo": "EBIT", "preco_atual": 100.0, "ebit_por_acao": 12.0,
             "p_ebit": 8.3, "div_liq_ebit": 1.0, "dy_medio_3a": 0.03, "fluxo_crescente": True},
            {"ticker": "ALV", "nome": "Alavancada", "setor": "Tel", "citacoes": 1,
             "base_calculo": "EBIT", "preco_atual": 20.0, "ebit_por_acao": 8.0,
             "p_ebit": 2.5, "div_liq_ebit": 8.0, "dy_medio_3a": 0.05, "fluxo_crescente": True},
            {"ticker": "ANO", "nome": "Anomala", "setor": "Fin", "citacoes": 1,
             "base_calculo": "EBIT", "preco_atual": 10.0, "ebit_por_acao": 8.0,
             "p_ebit": 1.25, "div_liq_ebit": 0.5, "dy_medio_3a": 0.0, "fluxo_crescente": False},
            {"ticker": "BNK", "nome": "Banco", "setor": "Fin", "citacoes": 1,
             "base_calculo": "Lucro", "preco_atual": 100.0, "ebit_por_acao": 15.0,
             "p_ebit": 6.7, "div_liq_ebit": None, "dy_medio_3a": 0.04, "fluxo_crescente": True},
        ])

    def test_exclui_alavancada_e_anomala_banco_passa(self):
        rk = rankear_eua(self._df())
        tickers = set(rk["ticker"])
        self.assertIn("SOL", tickers)
        self.assertIn("BNK", tickers)          # banco passa (sem filtro de alavancagem)
        self.assertNotIn("ALV", tickers)       # dívida 8x > 3x
        self.assertNotIn("ANO", tickers)       # P/EBIT 1.25 < 3

    def test_sem_filtros_traz_todas(self):
        rk = rankear_eua(self._df(), div_liq_ebit_max=0, p_ebit_minimo=0)
        self.assertEqual(len(rk), 4)

    def test_ordena_por_upside(self):
        rk = rankear_eua(self._df(), div_liq_ebit_max=0, p_ebit_minimo=0)
        self.assertEqual(list(rk["upside_pct"]), sorted(rk["upside_pct"], reverse=True))

    def test_apenas_crescente(self):
        rk = rankear_eua(self._df(), p_ebit_minimo=0, div_liq_ebit_max=0, apenas_crescente=True)
        self.assertNotIn("ANO", set(rk["ticker"]))  # unica nao-crescente


if __name__ == "__main__":
    unittest.main()
