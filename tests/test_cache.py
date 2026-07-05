"""
Testes do cache local do scraper (sem acesso à internet).

Cobrem a checagem de validade por TTL e o round-trip de gravar/ler o
DataFrame em disco, além de garantir que baixar_tabela_fundamentus usa o
cache sem tocar na rede quando ele está válido.
"""

import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fundamentus_scraper as scraper
from fundamentus_scraper import _cache_valido, _processar_tabela


class TestCacheValido(unittest.TestCase):
    def test_inexistente_e_invalido(self):
        with TemporaryDirectory() as d:
            self.assertFalse(_cache_valido(Path(d) / "nao_existe.pkl", 3600))

    def test_recente_e_valido(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "c.pkl"
            p.write_text("x")
            self.assertTrue(_cache_valido(p, ttl_segundos=3600))

    def test_velho_e_invalido(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "c.pkl"
            p.write_text("x")
            velho = time.time() - 10_000
            import os

            os.utime(p, (velho, velho))
            self.assertFalse(_cache_valido(p, ttl_segundos=3600))


class TestBaixarComCache(unittest.TestCase):
    def _df_exemplo(self):
        return _processar_tabela(
            pd.DataFrame({"Papel": ["MGLU3"], "Cotação": [4.45], "P/EBIT": [2.30]})
        )

    def test_le_do_cache_sem_tocar_a_rede(self):
        with TemporaryDirectory() as d:
            cache_file = Path(d) / "fundamentus.pkl"
            self._df_exemplo().to_pickle(cache_file)
            with mock.patch.object(scraper, "CACHE_FILE", cache_file), mock.patch.object(
                scraper.requests, "get"
            ) as get_mock:
                df = scraper.baixar_tabela_fundamentus(usar_cache=True, ttl_segundos=3600)
                get_mock.assert_not_called()
                self.assertAlmostEqual(df.iloc[0]["preco_atual"], 4.45)

    def test_cache_expirado_forca_rede(self):
        with TemporaryDirectory() as d:
            cache_file = Path(d) / "fundamentus.pkl"
            with mock.patch.object(scraper, "CACHE_FILE", cache_file), mock.patch.object(
                scraper, "CACHE_DIR", Path(d)
            ), mock.patch.object(scraper.requests, "get") as get_mock:
                resp = mock.Mock()
                resp.text = (
                    "<table><tr><th>Papel</th><th>Cotação</th><th>P/EBIT</th></tr>"
                    "<tr><td>MGLU3</td><td>4,45</td><td>2,30</td></tr></table>"
                )
                resp.raise_for_status = lambda: None
                get_mock.return_value = resp

                df = scraper.baixar_tabela_fundamentus(usar_cache=True, ttl_segundos=0)
                get_mock.assert_called_once()
                self.assertTrue(cache_file.exists())
                self.assertAlmostEqual(df.iloc[0]["preco_atual"], 4.45)


if __name__ == "__main__":
    unittest.main()
