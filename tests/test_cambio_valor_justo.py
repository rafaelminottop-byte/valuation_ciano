"""Testes da régua de preço justo do dólar (funções puras do módulo cambio, sem rede)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cambio import (_ppc_por_base, carregar_valor_justo, media_vizinhos, paridade_poder_compra,
                    premio_sobre_justo)


class TestPPC(unittest.TestCase):
    def test_inflacao_igual_mantem_o_dolar(self):
        self.assertAlmostEqual(paridade_poder_compra(4.0, 100, 150, 100, 150), 4.0)

    def test_mais_inflacao_no_brasil_sobe_o_dolar(self):
        # BR +44,9%, EUA +30,4% sobre base 4,03 -> ~4,48 (conta usada no relatório)
        v = paridade_poder_compra(4.03, 100, 144.9, 100, 130.4)
        self.assertAlmostEqual(v, 4.03 * 1.449 / 1.304, places=6)
        self.assertGreater(v, 4.03)

    def test_entradas_invalidas(self):
        self.assertIsNone(paridade_poder_compra(0, 100, 150, 100, 150))
        self.assertIsNone(paridade_poder_compra(4.0, 100, 150, 0, 150))
        self.assertIsNone(paridade_poder_compra(None, 100, 150, 100, 150))

    def test_ppc_por_base_usa_dezembro_e_ultimo_mes_comum(self):
        idx = pd.date_range("2017-12-31", periods=97, freq="ME")
        dolar = pd.Series(4.0, index=idx)
        br = pd.Series([100 * 1.004 ** i for i in range(97)], index=idx)
        eua = pd.Series([100 * 1.002 ** i for i in range(96)] + [None], index=idx)
        r = _ppc_por_base(dolar, br, eua, (2019, 2017))
        self.assertEqual(r["ate"], idx[95].strftime("%Y-%m"))
        self.assertIn("base_2019", r)
        self.assertIn("base_2017", r)
        self.assertGreater(r["base_2017"], r["base_2019"])  # base mais antiga acumula mais diferencial

    def test_ppc_por_base_sem_dados(self):
        vazio = pd.Series(dtype=float)
        self.assertEqual(_ppc_por_base(vazio, vazio, vazio, (2019,)), {})


class TestPremio(unittest.TestCase):
    def test_premio(self):
        self.assertAlmostEqual(premio_sobre_justo(5.65, 5.0), 13.0)
        self.assertLess(premio_sobre_justo(4.5, 5.0), 0)

    def test_premio_sem_dado(self):
        self.assertIsNone(premio_sobre_justo(None, 5.0))
        self.assertIsNone(premio_sobre_justo(5.65, None))

    def test_media_vizinhos(self):
        self.assertAlmostEqual(media_vizinhos({"a": 4.5, "b": 4.5, "c": 12.25, "d": 6.25}), 6.875)
        self.assertIsNone(media_vizinhos({}))
        self.assertIsNone(media_vizinhos(None))


class TestArquivoReferencias(unittest.TestCase):
    def test_json_tem_modelos_datados_e_juros_dos_vizinhos(self):
        vj = carregar_valor_justo()
        self.assertTrue(vj["modelos"])
        for m in vj["modelos"]:
            self.assertTrue(3 <= m["valor"] <= 10)
            self.assertTrue(m["fonte"] and m["data"])
        self.assertEqual(len(vj["juros_vizinhos"]["taxas"]), 4)


if __name__ == "__main__":
    unittest.main()
