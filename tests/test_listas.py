"""Testes das listas nomeadas (arquivo temporário)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from listas import carregar_listas, nomes_listas, remover_lista, salvar_lista


class TestListas(unittest.TestCase):
    def test_vazio_quando_nao_existe(self):
        with TemporaryDirectory() as d:
            self.assertEqual(carregar_listas(Path(d) / "l.json"), {})

    def test_salvar_e_ler_normaliza(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "l.json"
            salvar_lista("Screener", [" wege3 ", "PRIO3", "prio3", "vale3"], p)
            self.assertEqual(carregar_listas(p)["Screener"], ["WEGE3", "PRIO3", "VALE3"])

    def test_nome_vazio_gera_erro(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                salvar_lista("  ", ["PETR4"], Path(d) / "l.json")

    def test_remover(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "l.json"
            salvar_lista("A", ["PETR4"], p)
            salvar_lista("B", ["VALE3"], p)
            remover_lista("A", p)
            self.assertEqual(nomes_listas(p), ["B"])


if __name__ == "__main__":
    unittest.main()
