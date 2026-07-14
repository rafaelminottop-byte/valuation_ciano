"""Testes das funções puras do módulo macro (sem acesso à rede)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from macro import _pacote, _para_float, juro_real_ex_ante, serie_juro_real, variacao_12m


class TestSerieJuroReal(unittest.TestCase):
    def test_cruza_selic_e_ipca_pela_data(self):
        selic = [{"data": "2026-07-01", "valor": 14.0}, {"data": "2026-07-10", "valor": 14.0}]
        ipca = [{"data": "2026-07-01", "valor": 5.0}, {"data": "2026-07-10", "valor": 4.0}]
        r = serie_juro_real(selic, ipca)
        self.assertEqual(len(r["serie"]), 2)
        # IPCA esperado caindo -> juro real sobe
        self.assertGreater(r["serie"][1]["valor"], r["serie"][0]["valor"])
        self.assertAlmostEqual(r["valor"], ((1.14 / 1.04) - 1) * 100)

    def test_data_sem_par_e_ignorada(self):
        selic = [{"data": "A", "valor": 14.0}, {"data": "B", "valor": 14.0}]
        ipca = [{"data": "A", "valor": 5.0}]
        self.assertEqual(len(serie_juro_real(selic, ipca)["serie"]), 1)

    def test_series_vazias(self):
        self.assertEqual(serie_juro_real([], [])["serie"], [])
        self.assertIsNone(serie_juro_real(None, None)["valor"])


class TestSeries(unittest.TestCase):
    def test_pacote_pega_o_ultimo_ponto(self):
        serie = [{"data": "01/2026", "valor": 1.0}, {"data": "02/2026", "valor": 2.0}]
        p = _pacote(serie)
        self.assertEqual(p["valor"], 2.0)
        self.assertEqual(p["data"], "02/2026")
        self.assertEqual(len(p["serie"]), 2)

    def test_pacote_vazio(self):
        p = _pacote([])
        self.assertIsNone(p["valor"])
        self.assertEqual(p["serie"], [])

    def test_variacao_12m(self):
        # 13 pontos: de 100 para 110 -> +10% em 12 meses
        serie = [{"data": str(i), "valor": 100.0} for i in range(12)]
        serie.append({"data": "12", "valor": 110.0})
        self.assertAlmostEqual(variacao_12m(serie), 10.0)

    def test_variacao_12m_curta_demais(self):
        self.assertIsNone(variacao_12m([{"data": "1", "valor": 100.0}]))


class TestMacroPuro(unittest.TestCase):
    def test_para_float_aceita_virgula_e_ponto(self):
        self.assertAlmostEqual(_para_float("14,25"), 14.25)
        self.assertAlmostEqual(_para_float("81.04"), 81.04)
        self.assertIsNone(_para_float("x"))
        self.assertIsNone(_para_float(None))

    def test_juro_real_ex_ante_fisher(self):
        # Selic 14,25% e IPCA esperado 5,16% -> ~8,6% real
        jr = juro_real_ex_ante(14.25, 5.16)
        self.assertAlmostEqual(jr, ((1.1425 / 1.0516) - 1) * 100, places=6)
        self.assertGreater(jr, 8.0)
        self.assertLess(jr, 9.0)

    def test_juro_real_none_quando_falta_dado(self):
        self.assertIsNone(juro_real_ex_ante(None, 5.0))
        self.assertIsNone(juro_real_ex_ante(14.0, None))


if __name__ == "__main__":
    unittest.main()
