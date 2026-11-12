"""
Testes do valuation_engine.py
Cobre a metodologia Ciano (P/L a valor presente + FCD do EBIT) usando os
números do PETR4 já validados manualmente no chat (ver README.md).
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from valuation_engine import PREMISSAS_EUA, PREMISSAS_PADRAO, calcular_valuation_completo


class TestPremissasPorMercado(unittest.TestCase):
    def test_tma_brasileira_e_americana(self):
        # B3: TMA em reais. EUA: TMA em dólar (10% a.a.).
        self.assertAlmostEqual(PREMISSAS_PADRAO["tma"], 0.14)
        self.assertAlmostEqual(PREMISSAS_EUA["tma"], 0.10)

    def test_eua_herda_o_resto_das_premissas(self):
        for chave in ("anos_fase_1", "anos_fase_2"):
            self.assertEqual(PREMISSAS_EUA[chave], PREMISSAS_PADRAO[chave])

    def test_dividendo_de_6pct_vale_sobre_o_lucro_nao_sobre_o_ebit(self):
        # O P/L final capitaliza 66% do EBIT (depois do imposto) a 6%, não o EBIT inteiro.
        self.assertAlmostEqual(PREMISSAS_PADRAO["retorno_alvo_pl"], 0.06)
        self.assertAlmostEqual(PREMISSAS_PADRAO["conversao_ebit_lucro"], 0.66)
        args = dict(ticker="X", ebit_atual=10.0, acoes_em_circulacao=1.0, preco_atual=100.0)
        cheio = calcular_valuation_completo(**args, conversao_ebit_lucro=1.0)["resultados"]["intermediario"]
        padrao = calcular_valuation_completo(**args)["resultados"]["intermediario"]
        self.assertAlmostEqual(padrao.valor_metodo_pl, cheio.valor_metodo_pl * 0.66)
        self.assertAlmostEqual(padrao.valor_fcd_ebit, cheio.valor_fcd_ebit)   # o FCD não muda

    def test_tma_menor_gera_valuation_maior(self):
        # Descontar a uma taxa menor -> valor presente maior (mesma empresa).
        args = dict(ticker="X", ebit_atual=10.0, acoes_em_circulacao=1.0, preco_atual=100.0)
        br = calcular_valuation_completo(**args, tma=PREMISSAS_PADRAO["tma"])
        eua = calcular_valuation_completo(**args, tma=PREMISSAS_EUA["tma"])
        self.assertGreater(
            eua["resultados"]["intermediario"].valuation_final_por_acao,
            br["resultados"]["intermediario"].valuation_final_por_acao,
        )


class TestValuationEngine(unittest.TestCase):
    def setUp(self):
        self.resultado = calcular_valuation_completo(
            ticker="PETR4",
            ebit_atual=143_858,
            acoes_em_circulacao=12_888.732761,
            preco_atual=37.84,
        )

    def test_veredito_desconto(self):
        self.assertEqual(self.resultado["veredito"], "desconto")

    def test_tres_cenarios_presentes(self):
        self.assertEqual(
            set(self.resultado["resultados"].keys()),
            {"pessimista", "intermediario", "otimista"},
        )

    def test_valuation_final_por_acao_pessimista(self):
        pessimista = self.resultado["resultados"]["pessimista"]
        self.assertAlmostEqual(pessimista.valuation_final_por_acao, 104.45, places=1)  # era 126,92 antes de tirar o "ano zero" do FCD e de aplicar o 6% ao lucro (66% do EBIT)

    def test_valuation_cresce_do_pessimista_ao_otimista(self):
        valores = [
            r.valuation_final_por_acao for r in self.resultado["resultados"].values()
        ]
        self.assertEqual(valores, sorted(valores))

    def test_veredito_sobrepreco_quando_preco_acima_da_faixa(self):
        resultado = calcular_valuation_completo(
            ticker="PETR4",
            ebit_atual=143_858,
            acoes_em_circulacao=12_888.732761,
            preco_atual=1_000.0,
        )
        self.assertEqual(resultado["veredito"], "sobrepreco")

    def test_veredito_dentro_da_faixa(self):
        _, maximo = self.resultado["faixa_valuation"]
        minimo, _ = self.resultado["faixa_valuation"]
        preco_no_meio = (minimo + maximo) / 2
        resultado = calcular_valuation_completo(
            ticker="PETR4",
            ebit_atual=143_858,
            acoes_em_circulacao=12_888.732761,
            preco_atual=preco_no_meio,
        )
        self.assertEqual(resultado["veredito"], "dentro_da_faixa")


class TestCrescimentoIgualTma(unittest.TestCase):
    """Regressão: crescimento == TMA fazia r = 1 e dividia por zero."""

    def test_crescimento_fase_1_igual_tma_nao_quebra(self):
        r = calcular_valuation_completo(
            ticker="X",
            ebit_atual=1.0,
            acoes_em_circulacao=1.0,
            preco_atual=10.0,
            tma=0.14,
            cenarios={"t": {"crescimento_fase_1": 0.14, "crescimento_fase_2": 0.0}},
        )
        valor = r["resultados"]["t"].valuation_final_por_acao
        self.assertTrue(math.isfinite(valor))

    def test_crescimento_fase_2_igual_tma_nao_quebra(self):
        r = calcular_valuation_completo(
            ticker="X",
            ebit_atual=1.0,
            acoes_em_circulacao=1.0,
            preco_atual=10.0,
            tma=0.14,
            cenarios={"t": {"crescimento_fase_1": 0.10, "crescimento_fase_2": 0.14}},
        )
        valor = r["resultados"]["t"].valuation_final_por_acao
        self.assertTrue(math.isfinite(valor))


if __name__ == "__main__":
    unittest.main()
