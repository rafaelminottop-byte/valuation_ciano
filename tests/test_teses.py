"""Testes do módulo de teses (data/teses.json)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from teses import buscar_tese, carregar_teses


class TestTeses(unittest.TestCase):
    def test_carrega_varias_empresas(self):
        teses = carregar_teses()
        self.assertGreater(len(teses), 50)

    def test_busca_case_insensitive(self):
        self.assertIsNotNone(buscar_tese("prio3"))
        self.assertIsNotNone(buscar_tese("PRIO3"))

    def test_estrutura_da_tese(self):
        t = buscar_tese("PRIO3")
        self.assertIn("setor", t)
        self.assertTrue(t["tese"])
        self.assertTrue(t["pontos_fortes"])
        self.assertTrue(t["pontos_fracos"])

    def test_ticker_sem_tese_retorna_none(self):
        self.assertIsNone(buscar_tese("ZZZZ9"))
        self.assertIsNone(buscar_tese(""))


if __name__ == "__main__":
    unittest.main()
