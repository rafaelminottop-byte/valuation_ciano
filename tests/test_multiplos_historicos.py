import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import multiplos_historicos as mh

DADOS = {
    "mercado": {"p25": 9.0, "p50": 12.0, "p75": 18.0},
    "setores": {"Utilities": {"p25": 7.0, "p50": 11.0, "p75": 20.0}},
    "juro_real": {"a": 4.0, "b": 0.5, "res_p25": -1.0, "res_p75": 1.0},
}


class TestMultiplos(unittest.TestCase):
    def test_setor_conhecido_e_desconhecido_cai_no_mercado(self):
        self.assertEqual(mh.multiplos_setor("Utilities", DADOS)["intermediario"], 11.0)
        self.assertEqual(mh.multiplos_setor("Inexistente", DADOS)["otimista"], 18.0)

    def test_juro_real_mais_alto_da_multiplo_menor(self):
        baixo = mh.multiplos_juro_real(3.0, DADOS)["intermediario"]
        alto = mh.multiplos_juro_real(8.0, DADOS)["intermediario"]
        self.assertGreater(baixo, alto)

    def test_juro_real_ordem_dos_cenarios(self):
        m = mh.multiplos_juro_real(6.0, DADOS)
        self.assertLess(m["pessimista"], m["intermediario"])
        self.assertLess(m["intermediario"], m["otimista"])
        self.assertAlmostEqual(m["intermediario"], 100 / 7.0)   # 4 + 0,5*6 = 7% de lucro/preço

    def test_resultado_preco_e_upside(self):
        r = mh.resultado_por_multiplo(2.0, 20.0, {"pessimista": 8, "intermediario": 10, "otimista": 12})["resultados"]
        self.assertAlmostEqual(r["intermediario"].valuation_final_por_acao, 20.0)
        self.assertAlmostEqual(r["intermediario"].upside_percentual, 0.0)
        self.assertAlmostEqual(r["otimista"].upside_percentual, 20.0)

    def test_sem_lucro_ou_sem_dados_nao_aplica(self):
        self.assertIsNone(mh.resultado_por_multiplo(-1.0, 10.0, {"pessimista": 8, "intermediario": 10, "otimista": 12}))
        self.assertIsNone(mh.resultado_por_multiplo(1.0, 10.0, None))
        self.assertIsNone(mh.multiplos_juro_real(None, DADOS))


if __name__ == "__main__":
    unittest.main()


class TestEvEbit(unittest.TestCase):
    M = {"pessimista": 4.0, "intermediario": 6.0, "otimista": 8.0}

    def test_desconta_a_divida_liquida(self):
        r = mh.resultado_ev_ebit(2.0, 1.0, 10.0, self.M)["resultados"]   # 2 * (6 - 1)
        self.assertAlmostEqual(r["intermediario"].valuation_final_por_acao, 10.0)
        self.assertAlmostEqual(r["intermediario"].upside_percentual, 0.0)

    def test_caixa_liquido_soma(self):
        r = mh.resultado_ev_ebit(2.0, -1.0, 10.0, self.M)["resultados"]   # 2 * (6 + 1)
        self.assertAlmostEqual(r["intermediario"].valuation_final_por_acao, 14.0)

    def test_divida_maior_que_o_valor_nao_aplica(self):
        self.assertIsNone(mh.resultado_ev_ebit(2.0, 5.0, 10.0, self.M))   # no pessimista 4-5 < 0

    def test_sem_dados(self):
        self.assertIsNone(mh.resultado_ev_ebit(2.0, None, 10.0, self.M))
        self.assertIsNone(mh.multiplos_ev_ebit("X", {}))
