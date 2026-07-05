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

from valuation_engine import calcular_valuation_completo


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
        self.assertAlmostEqual(pessimista.valuation_final_por_acao, 126.92, places=1)

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
