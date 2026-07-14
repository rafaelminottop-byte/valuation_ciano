"""Testes do índice de revisão do lucro esperado (função pura, sem rede)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lucro_esperado import _valido, indice_revisao


class TestValido(unittest.TestCase):
    def test_descarta_zero_nan_e_texto(self):
        self.assertTrue(_valido(1.5))
        self.assertFalse(_valido(0.0))          # Yahoo usa 0.0 para "sem estimativa"
        self.assertFalse(_valido(float("nan")))
        self.assertFalse(_valido(None))
        self.assertFalse(_valido("x"))


class TestIndiceRevisao(unittest.TestCase):
    def _emp(self, ticker, noventa, atual):
        return {
            "ticker": ticker,
            "valores": {"90daysAgo": noventa, "current": atual},
            "revisao_90d_pct": (atual / noventa - 1) * 100,
            "n_analistas": 5,
        }

    def test_revisao_para_cima_gera_indice_acima_de_100(self):
        # Ambas subiram 10% -> índice 110
        exp = [self._emp("A", 10.0, 11.0), self._emp("B", 2.0, 2.2)]
        r = indice_revisao(exp)
        self.assertAlmostEqual(r["valor"], 110.0)
        self.assertEqual(r["pct_revisao_positiva"], 100.0)
        self.assertEqual(r["n_empresas"], 2)

    def test_revisao_para_baixo_gera_indice_abaixo_de_100(self):
        exp = [self._emp("A", 10.0, 9.0), self._emp("B", 10.0, 9.0)]
        r = indice_revisao(exp)
        self.assertAlmostEqual(r["valor"], 90.0)
        self.assertEqual(r["pct_revisao_positiva"], 0.0)

    def test_usa_mediana_e_nao_e_dominado_por_lucro_grande(self):
        # Empresa de lucro enorme caindo 50%; duas pequenas subindo 10%.
        # A MEDIANA segue as duas que subiram -> índice 110 (não é arrastado).
        exp = [self._emp("GIGANTE", 1000.0, 500.0),
               self._emp("B", 1.0, 1.1), self._emp("C", 2.0, 2.2)]
        r = indice_revisao(exp)
        self.assertAlmostEqual(r["valor"], 110.0)
        self.assertAlmostEqual(r["pct_revisao_positiva"], 200 / 3)

    def test_serie_tem_os_pontos_da_trajetoria(self):
        exp = [{"ticker": "A",
                "valores": {"90daysAgo": 10.0, "30daysAgo": 10.5, "current": 11.0},
                "revisao_90d_pct": 10.0, "n_analistas": 3}]
        r = indice_revisao(exp)
        rotulos = [p["data"] for p in r["serie"]]
        self.assertEqual(rotulos, ["90d atrás", "30d", "hoje"])
        self.assertAlmostEqual(r["serie"][0]["valor"], 100.0)   # base
        self.assertAlmostEqual(r["serie"][-1]["valor"], 110.0)

    def test_cesta_vazia(self):
        r = indice_revisao([])
        self.assertIsNone(r["valor"])
        self.assertEqual(r["n_empresas"], 0)


if __name__ == "__main__":
    unittest.main()
