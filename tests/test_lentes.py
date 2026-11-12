"""Testes das lentes reversas (crescimento e TMA implícitos)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lentes import (
    crescimento_implicito,
    leitura_reversa,
    tma_implicita_ebit,
    tma_implicita_lucro,
)


class TestFormulasFechadas(unittest.TestCase):
    def test_crescimento_implicito_inverte_gordon(self):
        # Se o preço = LPA(1+g)/(TMA-g), recuperar g de volta.
        lpa, tma, g = 2.0, 0.14, 0.05
        preco = lpa * (1 + g) / (tma - g)
        self.assertAlmostEqual(crescimento_implicito(preco, lpa, tma), g, places=6)

    def test_tma_implicita_lucro_inverte_gordon(self):
        lpa, g, tma = 2.0, 0.05, 0.14
        preco = lpa * (1 + g) / (tma - g)
        self.assertAlmostEqual(tma_implicita_lucro(preco, lpa, g), tma, places=6)

    def test_sem_lucro_positivo_devolve_none(self):
        self.assertIsNone(crescimento_implicito(10, 0, 0.14))
        self.assertIsNone(crescimento_implicito(10, None, 0.14))
        self.assertIsNone(tma_implicita_lucro(10, -1, 0.05))

    def test_earnings_yield_alto_implica_crescimento_baixo(self):
        # Preço baixo (P/L baixo) -> mercado embute pouco crescimento.
        g_barata = crescimento_implicito(preco=7.8, lpa=1.05, tma=0.14)   # ECOR3-like
        g_cara = crescimento_implicito(preco=46.5, lpa=1.50, tma=0.14)    # WEGE3-like
        self.assertLess(g_barata, g_cara)


class TestTmaImplicitaEbit(unittest.TestCase):
    def test_recupera_tma_do_motor(self):
        # Escolhe uma empresa/TMA, calcula o justo por essa TMA e verifica que a
        # bissecção recupera a mesma TMA quando o "preço" = esse justo.
        from valuation_engine import calcular_valuation_completo
        cen = {"crescimento_fase_1": 0.10, "crescimento_fase_2": 0.023}
        ebit_acao, tma_real = 3.0, 0.20
        r = calcular_valuation_completo(ticker="X", ebit_atual=ebit_acao, acoes_em_circulacao=1.0,
                                        preco_atual=1.0, tma=tma_real, cenarios={"c": cen})
        justo = r["resultados"]["c"].valuation_final_por_acao
        tma_rec = tma_implicita_ebit(ebit_acao, justo, cen)
        self.assertAlmostEqual(tma_rec, tma_real, places=2)

    def test_ebit_enorme_frente_ao_preco_nao_converge(self):
        # EBIT/ação quase igual ao preço (P/EBIT ~1, alavancada) -> sem TMA plausível.
        cen = {"crescimento_fase_1": 0.05, "crescimento_fase_2": 0.0}
        r = tma_implicita_ebit(ebit_por_acao=5.67, preco=7.77, cenario=cen, tma_max=1.0)
        self.assertTrue(r is None or r > 0.5)   # sem o "ano zero" converge, mas em TMA absurda (~81%)


class TestLeituraReversa(unittest.TestCase):
    def _cen(self):
        return {"crescimento_fase_1": 0.10, "crescimento_fase_2": 0.023}

    def test_empresa_sem_divida_converge(self):
        # WEGE3-like: P/EBIT alto, LPA razoável -> razão baixa, não alavancada.
        r = leitura_reversa(preco=46.5, ebit_por_acao=2.03, lpa=1.50, cenario=self._cen(), tma=0.14)
        self.assertIsNotNone(r["tma_ebit"])
        self.assertLess(r["razao"], 3.0)
        self.assertFalse(r["alavancada"])

    def test_empresa_alavancada_diverge(self):
        # ECOR3-like: P/EBIT ~1.4 -> TMA-EBIT dispara (ou não converge) -> alavancada.
        r = leitura_reversa(preco=7.77, ebit_por_acao=5.67, lpa=1.05, cenario=self._cen(), tma=0.14)
        self.assertTrue(r["alavancada"])


if __name__ == "__main__":
    unittest.main()
