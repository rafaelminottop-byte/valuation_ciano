"""Testes do ranking de qualidade (sem acesso à internet)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ranking import (
    nota_div_liq_ebit,
    nota_dividendos,
    nota_liquidez_corrente,
    nota_margem_ebit,
    rankear_qualidade,
    score_qualidade,
    score_solidez,
)


class TestNotas(unittest.TestCase):
    def test_div_liq_ebit_faixas(self):
        self.assertEqual(nota_div_liq_ebit(-0.4), 10)  # caixa líquido
        self.assertEqual(nota_div_liq_ebit(0.5), 9)
        self.assertEqual(nota_div_liq_ebit(6.4), 0)  # PRIO — muito alavancada

    def test_liquidez_corrente_faixas(self):
        self.assertEqual(nota_liquidez_corrente(2.5), 10)
        self.assertEqual(nota_liquidez_corrente(1.2), 6)
        self.assertEqual(nota_liquidez_corrente(0.5), 2)

    def test_margem_faixas(self):
        self.assertEqual(nota_margem_ebit(0.30), 10)
        self.assertEqual(nota_margem_ebit(0.04), 4)

    def test_scores_none_com_dado_faltando(self):
        self.assertIsNone(score_solidez(None, 0.3, 1.2))
        self.assertIsNone(score_qualidade(0.2, None, 0.2))


class TestRankear(unittest.TestCase):
    def _df(self):
        # WEG (ótima), PRIO (alavancada), BANCO (P/EBIT=0 -> excluída)
        return pd.DataFrame(
            {
                "ticker": ["WEGE3", "PRIO3", "BANCO4"],
                "preco_atual": [46.0, 52.96, 20.0],
                "ebit_por_acao": [46.0 / 22.92, 52.96 / 12.28, 0.0],
                "p_ebit": [22.92, 12.28, 0.0],
                "ev_ebit": [22.53, 18.68, 0.0],
                "div_liq_patrim": [-0.19, 0.91, 0.0],
                "liquidez_corrente": [1.55, 1.92, 0.0],
                "roic": [0.2596, 0.0645, 0.0],
                "roe": [0.3543, 0.0972, 0.0771],
                "margem_ebit": [0.2118, 0.2129, 0.0],
                "liquidez": [3.3e8, 2e8, 1e8],
            }
        )

    def test_exclui_banco(self):
        rk = rankear_qualidade(self._df())
        self.assertNotIn("BANCO4", set(rk["ticker"]))

    def test_ordena_por_score(self):
        rk = rankear_qualidade(self._df())
        self.assertEqual(list(rk["ticker"]), ["WEGE3", "PRIO3"])
        self.assertGreater(
            rk[rk["ticker"] == "WEGE3"]["score"].iloc[0],
            rk[rk["ticker"] == "PRIO3"]["score"].iloc[0],
        )

    def test_prio_solidez_baixa(self):
        rk = rankear_qualidade(self._df())
        prio = rk[rk["ticker"] == "PRIO3"].iloc[0]
        self.assertAlmostEqual(prio["div_liq_ebit"], 6.40, places=1)
        self.assertLess(prio["solidez"], 4)  # muito alavancada -> solidez baixa

    def test_pesos_individuais_afetam_score(self):
        # Zera solidez, upside e dividendos -> score = pilar de qualidade
        df = self._df()
        so_qualidade = rankear_qualidade(
            df,
            pesos={
                "div_liq_ebit": 0, "div_liq_patrim": 0, "liquidez_corrente": 0,
                "roic": 1, "roe": 1, "margem_ebit": 1, "upside": 0, "dividendos": 0,
            },
        )
        prio = so_qualidade[so_qualidade["ticker"] == "PRIO3"].iloc[0]
        self.assertAlmostEqual(prio["score"], prio["qualidade"])

    def test_upside_entra_no_score(self):
        # Com peso só no upside, o score reflete o upside (PRIO barata pontua mais)
        df = self._df()
        rk = rankear_qualidade(
            df,
            pesos={
                "div_liq_ebit": 0, "div_liq_patrim": 0, "liquidez_corrente": 0,
                "roic": 0, "roe": 0, "margem_ebit": 0, "upside": 1, "dividendos": 0,
            },
        )
        self.assertIn("upside_pct", rk.columns)
        prio = rk[rk["ticker"] == "PRIO3"].iloc[0]
        wege = rk[rk["ticker"] == "WEGE3"].iloc[0]
        # PRIO (barata, upside alto) pontua mais que WEG (cara) só por upside
        self.assertGreaterEqual(prio["score"], wege["score"])

    def test_dividendos_entram_no_score(self):
        # Com peso só em dividendos, quem paga mais (DY 3a maior) pontua mais.
        df = self._df()
        pesos_so_div = {
            "div_liq_ebit": 0, "div_liq_patrim": 0, "liquidez_corrente": 0,
            "roic": 0, "roe": 0, "margem_ebit": 0, "upside": 0, "dividendos": 1,
        }
        rk = rankear_qualidade(
            df, pesos=pesos_so_div,
            dividendos={"WEGE3": 0.08, "PRIO3": 0.01},  # WEG paga 8%, PRIO 1%
        )
        self.assertIn("dy_medio_3a_pct", rk.columns)
        wege = rk[rk["ticker"] == "WEGE3"].iloc[0]
        prio = rk[rk["ticker"] == "PRIO3"].iloc[0]
        self.assertAlmostEqual(wege["dy_medio_3a_pct"], 8.0)
        self.assertGreater(wege["score"], prio["score"])

    def test_dividendos_ausentes_nao_quebram(self):
        # Sem dict de dividendos, a categoria recebe nota 0 e o ranking roda.
        rk = rankear_qualidade(self._df())
        self.assertIn("dy_medio_3a_pct", rk.columns)
        self.assertTrue(rk["dy_medio_3a_pct"].isna().all())

    def test_nota_dividendos_faixas(self):
        self.assertEqual(nota_dividendos(0.085), 10)   # 8,5%
        self.assertEqual(nota_dividendos(0.05), 6)      # 5%
        self.assertEqual(nota_dividendos(0.015), 2)     # 1,5%
        self.assertEqual(nota_dividendos(0.0), 0)
        self.assertEqual(nota_dividendos(None), 0)


if __name__ == "__main__":
    unittest.main()
