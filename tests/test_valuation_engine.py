"""
Testes do valuation_engine.py
Cobre a metodologia Ciano (P/L a valor presente + FCD do EBIT) usando os
números do PETR4 já validados manualmente no chat (ver README.md).
"""

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


if __name__ == "__main__":
    unittest.main()
