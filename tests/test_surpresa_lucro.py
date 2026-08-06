"""Testes das funções puras da surpresa de resultados e do histórico acumulado."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lucro_esperado import carregar_historico, registrar_historico
from surpresa_lucro import indice_surpresa, serie_estimado_realizado


def _s(trimestre, surpresa, estimado=1.0, reportado=1.0):
    return {"trimestre": trimestre, "surpresa_pct": surpresa,
            "estimado": estimado, "reportado": reportado}


class TestIndiceSurpresa(unittest.TestCase):
    def test_mediana_por_trimestre(self):
        por_ticker = {
            "A": [_s("2025-T2", 10.0), _s("2025-T3", -4.0)],
            "B": [_s("2025-T2", 20.0), _s("2025-T3", -2.0)],
            "C": [_s("2025-T2", 0.0), _s("2025-T3", -3.0)],
        }
        r = indice_surpresa(por_ticker, min_empresas=3)
        serie = {p["data"]: p["valor"] for p in r["serie"]}
        self.assertAlmostEqual(serie["2025-T2"], 10.0)   # mediana de 0,10,20
        self.assertAlmostEqual(serie["2025-T3"], -3.0)   # mediana de -4,-3,-2
        self.assertEqual(r["valor"], -3.0)               # trimestre mais recente
        self.assertEqual(r["n_empresas"], 3)

    def test_ignora_trimestre_com_poucas_empresas(self):
        # min_empresas=3: um trimestre com só 2 empresas não entra na série
        por_ticker = {
            "A": [_s("2025-T1", 5.0), _s("2025-T2", 1.0)],
            "B": [_s("2025-T1", 8.0), _s("2025-T2", 2.0)],
            "C": [_s("2025-T2", 3.0)],
        }
        r = indice_surpresa(por_ticker, min_empresas=3)
        self.assertEqual([p["data"] for p in r["serie"]], ["2025-T2"])  # só T2 tem 3

    def test_pct_bateram_no_ultimo_tri(self):
        por_ticker = {
            "A": [_s("2025-T3", 5.0)], "B": [_s("2025-T3", -3.0)],
            "C": [_s("2025-T3", 8.0)], "D": [_s("2025-T3", 2.0)],
        }
        self.assertEqual(indice_surpresa(por_ticker, min_empresas=3)["pct_bateram"], 75.0)  # 3 de 4

    def test_cesta_vazia(self):
        r = indice_surpresa({"A": [], "B": []})
        self.assertIsNone(r["valor"])
        self.assertEqual(r["serie"], [])


class TestSerieEstimadoRealizado(unittest.TestCase):
    def test_media_das_duas_linhas(self):
        por_ticker = {
            "A": [_s("2025-T2", 0, estimado=1.0, reportado=1.2)],
            "B": [_s("2025-T2", 0, estimado=3.0, reportado=2.8)],
            "C": [_s("2025-T2", 0, estimado=2.0, reportado=2.0)],
        }
        linhas = serie_estimado_realizado(por_ticker, min_empresas=3)
        self.assertEqual(len(linhas), 1)
        self.assertAlmostEqual(linhas[0]["estimado"], 2.0)    # média de 1,3,2
        self.assertAlmostEqual(linhas[0]["reportado"], 2.0)   # média de 1.2,2.8,2.0

    def test_respeita_minimo_de_empresas(self):
        por_ticker = {"A": [_s("2025-T2", 0)], "B": [_s("2025-T2", 0)]}
        self.assertEqual(serie_estimado_realizado(por_ticker, min_empresas=3), [])


class TestHistoricoAcumulado(unittest.TestCase):
    def setUp(self):
        self.arq = Path(self._testMethodName + "_hist.json").resolve()

    def tearDown(self):
        self.arq.unlink(missing_ok=True)

    def test_um_ponto_por_dia_sobrescreve(self):
        registrar_historico(101.0, hoje="2026-07-01", caminho=self.arq)
        registrar_historico(102.5, hoje="2026-07-02", caminho=self.arq)
        registrar_historico(103.0, hoje="2026-07-02", caminho=self.arq)  # mesmo dia -> atualiza
        h = carregar_historico(self.arq)
        self.assertEqual(len(h), 2)
        self.assertEqual(h[-1], {"data": "2026-07-02", "valor": 103.0})

    def test_mantem_ordem_cronologica(self):
        registrar_historico(100.0, hoje="2026-07-03", caminho=self.arq)
        registrar_historico(100.0, hoje="2026-07-01", caminho=self.arq)
        datas = [p["data"] for p in carregar_historico(self.arq)]
        self.assertEqual(datas, sorted(datas))

    def test_valor_none_nao_grava(self):
        registrar_historico(None, hoje="2026-07-01", caminho=self.arq)
        self.assertEqual(carregar_historico(self.arq), [])


if __name__ == "__main__":
    unittest.main()
