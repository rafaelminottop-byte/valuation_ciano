"""Testes da avaliação em lote (função pura, sem rede)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lote import avaliar_lote, separar_tickers
from valuation_engine import CENARIOS_PADRAO


class TestSepararTickers(unittest.TestCase):
    def test_aceita_virgula_espaco_e_quebra_de_linha(self):
        self.assertEqual(
            separar_tickers("petr4, vale3\nwege3;itsa4  ecor3"),
            ["PETR4", "VALE3", "WEGE3", "ITSA4", "ECOR3"],
        )

    def test_remove_duplicatas_preservando_ordem(self):
        self.assertEqual(separar_tickers("AAPL msft AAPL"), ["AAPL", "MSFT"])

    def test_texto_vazio(self):
        self.assertEqual(separar_tickers(""), [])
        self.assertEqual(separar_tickers(None), [])


class TestAvaliarLote(unittest.TestCase):
    def _empresas(self):
        return [
            # Sem dívida: EBIT/ação e LPA parecidos -> óticas convergem
            {"ticker": "LIMPA", "preco_atual": 46.0, "ebit_por_acao": 2.0, "lpa": 1.5},
            # Alavancada tipo ECOR3: EBIT/ação enorme frente ao preço, LPA pequeno
            {"ticker": "ALAV", "preco_atual": 7.77, "ebit_por_acao": 5.67, "lpa": 1.05},
            # Sem LPA (prejuízo / dado ausente) -> só a coluna do EBIT
            {"ticker": "SEMLPA", "preco_atual": 20.0, "ebit_por_acao": 2.0, "lpa": None},
            # Inválida: preço zero -> sai do lote
            {"ticker": "RUIM", "preco_atual": 0.0, "ebit_por_acao": 1.0, "lpa": 1.0},
        ]

    def _df(self):
        return avaliar_lote(self._empresas(), cenarios=CENARIOS_PADRAO, tma=0.14, retorno_alvo=0.06)

    def test_descarta_invalidas(self):
        self.assertNotIn("RUIM", set(self._df()["ticker"]))
        self.assertEqual(len(self._df()), 3)

    def test_calcula_os_dois_metodos(self):
        linha = self._df().set_index("ticker").loc["LIMPA"]
        self.assertIsNotNone(linha["justo_lpa"])
        self.assertIsNotNone(linha["justo_ebit"])
        # EBIT/ação (2,0) > LPA (1,5) -> justo por EBIT maior
        self.assertGreater(linha["justo_ebit"], linha["justo_lpa"])

    def test_marca_alavancada(self):
        df = self._df().set_index("ticker")
        self.assertEqual(df.loc["ALAV"]["alavancada"], "⚠️")
        self.assertEqual(df.loc["LIMPA"]["alavancada"], "")

    def test_sem_lpa_deixa_colunas_do_lpa_vazias(self):
        # numa coluna numérica o pandas guarda o ausente como NaN, não None
        linha = self._df().set_index("ticker").loc["SEMLPA"]
        self.assertTrue(pd.isna(linha["justo_lpa"]))
        self.assertTrue(pd.isna(linha["upside_lpa"]))
        self.assertFalse(pd.isna(linha["justo_ebit"]))

    def test_ordena_por_upside_do_lpa(self):
        ordem = [x for x in self._df()["upside_lpa"] if x is not None]
        self.assertEqual(ordem, sorted(ordem, reverse=True))

    def test_tma_implicita_nas_colunas(self):
        df = self._df().set_index("ticker")
        # Empresa limpa: a TMA exigida pelo lucro e pelo EBIT ficam na mesma ordem
        limpa = df.loc["LIMPA"]
        self.assertGreater(limpa["tma_lpa_pct"], 0)
        self.assertLess(limpa["tma_ebit_pct"], 40)   # plausível

        # Alavancada: a TMA pelo EBIT dispara (ou nem converge) — é o sinal de alerta
        alav = df.loc["ALAV"]
        self.assertGreater(alav["tma_lpa_pct"], 0)
        self.assertTrue(pd.isna(alav["tma_ebit_pct"]) or alav["tma_ebit_pct"] > 50)

    def test_sem_lpa_nao_tem_tma(self):
        linha = self._df().set_index("ticker").loc["SEMLPA"]
        self.assertTrue(pd.isna(linha["tma_lpa_pct"]))

    def test_lote_vazio(self):
        self.assertTrue(avaliar_lote([], cenarios=CENARIOS_PADRAO, tma=0.14).empty)


if __name__ == "__main__":
    unittest.main()
