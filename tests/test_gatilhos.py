"""Testes da lógica pura de gatilhos (sem baixar preços da rede)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gatilhos import _distancia_media


class TestDistanciaMedia(unittest.TestCase):
    def test_historico_insuficiente(self):
        precos = pd.Series([10.0] * 50)
        self.assertIsNone(_distancia_media(precos, periodos=200))

    def test_preco_na_media(self):
        precos = pd.Series([10.0] * 200)
        d = _distancia_media(precos, periodos=200)
        self.assertEqual(d["media"], 10.0)
        self.assertEqual(d["distancia_pct"], 0.0)

    def test_preco_acima_da_media(self):
        # 199 candles a 10 + 1 candle a 20 -> média ~10.05, preço 20 -> ~+99%
        precos = pd.Series([10.0] * 199 + [20.0])
        d = _distancia_media(precos, periodos=200)
        self.assertGreater(d["distancia_pct"], 90)
        self.assertEqual(d["preco"], 20.0)

    def test_ignora_nans(self):
        precos = pd.Series([10.0] * 200 + [float("nan")])
        d = _distancia_media(precos, periodos=200)
        self.assertIsNotNone(d)
        self.assertEqual(d["preco"], 10.0)


if __name__ == "__main__":
    unittest.main()
