"""Testes da carteira/watchlist (arquivo temporário, sem tocar a real)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from carteira import adicionar, carregar_carteira, remover, salvar_carteira


class TestCarteira(unittest.TestCase):
    def test_vazia_quando_nao_existe(self):
        with TemporaryDirectory() as d:
            self.assertEqual(carregar_carteira(Path(d) / "c.json"), [])

    def test_adicionar_e_ler(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            adicionar("prio3", p)
            adicionar("MGLU3", p)
            self.assertEqual(carregar_carteira(p), ["PRIO3", "MGLU3"])

    def test_normaliza_e_remove_duplicatas(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            salvar_carteira([" petr4 ", "PETR4", "vale3"], p)
            self.assertEqual(carregar_carteira(p), ["PETR4", "VALE3"])

    def test_remover(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            salvar_carteira(["PETR4", "VALE3", "MGLU3"], p)
            remover("vale3", p)
            self.assertEqual(carregar_carteira(p), ["PETR4", "MGLU3"])


if __name__ == "__main__":
    unittest.main()
