"""Testes do cálculo de dividendo médio de 3 anos (sem acesso à internet)."""

import sys
import time
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dividendos
from dividendos import _media_proventos_3anos, buscar_dy_medio_3anos, dy_medio_3anos


class TestMediaProventos(unittest.TestCase):
    def _serie(self, pares):
        idx = pd.to_datetime([d for d, _ in pares])
        return pd.Series([v for _, v in pares], index=idx)

    def test_media_dos_3_anos_completos(self):
        # hoje = 2026 -> usa 2023, 2024, 2025 (ignora 2026, incompleto)
        serie = self._serie([
            ("2023-05-01", 1.0), ("2024-05-01", 2.0),
            ("2025-05-01", 3.0), ("2026-05-01", 9.0),
        ])
        media = _media_proventos_3anos(serie, hoje=pd.Timestamp("2026-07-01"))
        self.assertAlmostEqual(media, (1.0 + 2.0 + 3.0) / 3)

    def test_ano_sem_pagar_conta_como_zero(self):
        # Pagou só em 2025; média divide por 3 anos (2023,2024,2025).
        serie = self._serie([("2025-05-01", 3.0)])
        media = _media_proventos_3anos(serie, hoje=pd.Timestamp("2026-07-01"))
        self.assertAlmostEqual(media, 3.0 / 3)

    def test_sem_historico_devolve_none(self):
        self.assertIsNone(_media_proventos_3anos(pd.Series(dtype=float)))
        # Proventos só fora da janela (todos no ano corrente) -> None
        serie = self._serie([("2026-05-01", 5.0)])
        self.assertIsNone(_media_proventos_3anos(serie, hoje=pd.Timestamp("2026-07-01")))

    def test_dy_medio(self):
        self.assertAlmostEqual(dy_medio_3anos(2.0, 50.0), 0.04)
        self.assertIsNone(dy_medio_3anos(None, 50.0))
        self.assertIsNone(dy_medio_3anos(2.0, 0))


class TestBuscarComCache(unittest.TestCase):
    def setUp(self):
        # Redireciona o cache para um arquivo temporário e conta as "chamadas de rede".
        self._orig_file = dividendos.CACHE_FILE
        self._orig_fetch = dividendos._media_via_yfinance
        tmp = Path(self._testMethodName + "_cache.json").resolve()
        dividendos.CACHE_FILE = tmp
        self.chamadas = []

        def fake_fetch(ticker):
            self.chamadas.append(ticker)
            return {"AAAA3": 2.0, "BBBB3": None}.get(ticker.upper(), 1.0)

        dividendos._media_via_yfinance = fake_fetch

    def tearDown(self):
        dividendos.CACHE_FILE.unlink(missing_ok=True)
        dividendos.CACHE_FILE = self._orig_file
        dividendos._media_via_yfinance = self._orig_fetch

    def test_calcula_e_cacheia(self):
        precos = {"AAAA3": 50.0, "BBBB3": 20.0}
        r1 = buscar_dy_medio_3anos(precos)
        self.assertAlmostEqual(r1["AAAA3"], 2.0 / 50.0)  # DY = média/preço
        self.assertIsNone(r1["BBBB3"])                    # sem histórico
        self.assertEqual(sorted(self.chamadas), ["AAAA3", "BBBB3"])

        # 2ª chamada: vem do cache, não bate na "rede" de novo.
        self.chamadas.clear()
        r2 = buscar_dy_medio_3anos(precos)
        self.assertEqual(self.chamadas, [])
        self.assertAlmostEqual(r2["AAAA3"], 2.0 / 50.0)

    def test_yield_recalcula_com_preco_novo(self):
        buscar_dy_medio_3anos({"AAAA3": 50.0})
        self.chamadas.clear()
        # Preço caiu pela metade -> DY dobra, sem nova chamada de rede.
        r = buscar_dy_medio_3anos({"AAAA3": 25.0})
        self.assertEqual(self.chamadas, [])
        self.assertAlmostEqual(r["AAAA3"], 2.0 / 25.0)


if __name__ == "__main__":
    unittest.main()
