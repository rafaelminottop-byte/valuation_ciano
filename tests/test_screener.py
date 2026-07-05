"""Testes do screener (sem acesso à internet)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from screener import rodar_screener


def _df():
    # ticker, preco, ebit_por_acao, p_ebit, liquidez, cresc_receita_5a (fração)
    return pd.DataFrame(
        {
            "ticker": ["AAA3", "BBB3", "CCC3", "DDD3", "EEE3"],
            "preco_atual": [10.0, 10.0, 10.0, -1.0, 10.0],
            "ebit_por_acao": [2.0, 1.0, 5.0, 2.0, -1.0],  # EEE3 tem EBIT negativo
            "p_ebit": [5.0, 10.0, 0.5, 5.0, 5.0],  # CCC3 tem P/EBIT anômalo (< 1)
            "liquidez": [5_000_000, 100_000, 5_000_000, 5_000_000, 5_000_000],
            "cresc_receita_5a": [0.10, 0.10, -0.05, 0.10, 0.10],  # CCC3 encolhe
        }
    )


class TestScreener(unittest.TestCase):
    def test_exclui_ebit_negativo_e_preco_invalido(self):
        rk = rodar_screener(_df())
        # DDD3 (preço<0) e EEE3 (EBIT<0) ficam de fora
        self.assertNotIn("DDD3", set(rk["ticker"]))
        self.assertNotIn("EEE3", set(rk["ticker"]))

    def test_ordena_por_upside_desc(self):
        rk = rodar_screener(_df())
        ups = list(rk["upside_pct"])
        self.assertEqual(ups, sorted(ups, reverse=True))

    def test_filtro_liquidez(self):
        rk = rodar_screener(_df(), liquidez_minima=1_000_000)
        self.assertNotIn("BBB3", set(rk["ticker"]))  # ilíquida

    def test_filtro_crescimento_exclui_quem_encolhe(self):
        rk = rodar_screener(_df(), crescimento_minimo=0.0)
        self.assertNotIn("CCC3", set(rk["ticker"]))  # receita 5a negativa

    def test_sem_filtro_crescimento_inclui_quem_encolhe(self):
        rk = rodar_screener(_df(), crescimento_minimo=None)
        self.assertIn("CCC3", set(rk["ticker"]))

    def test_filtro_pebit_minimo_exclui_anomalias(self):
        # CCC3 tem P/EBIT 0.5 (< 1); com piso 1.0 deve sair
        rk = rodar_screener(_df(), crescimento_minimo=None, pebit_minimo=1.0)
        self.assertNotIn("CCC3", set(rk["ticker"]))
        self.assertIn("AAA3", set(rk["ticker"]))

    def test_alerta_pebit_baixo_por_padrao_nao_exclui(self):
        # Sem piso, CCC3 (P/EBIT 0.5) aparece, mas com alerta preenchido
        rk = rodar_screener(_df(), crescimento_minimo=None)
        self.assertIn("CCC3", set(rk["ticker"]))
        alerta_ccc = rk[rk["ticker"] == "CCC3"]["alerta"].iloc[0]
        alerta_aaa = rk[rk["ticker"] == "AAA3"]["alerta"].iloc[0]
        self.assertTrue(alerta_ccc)  # P/EBIT 0.5 < 2 -> alertado
        self.assertFalse(alerta_aaa)  # P/EBIT 5 -> sem alerta


if __name__ == "__main__":
    unittest.main()
