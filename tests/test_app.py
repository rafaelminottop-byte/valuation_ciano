"""
Testes da lógica pura do app Streamlit (sem subir a interface).

Só cobre `montar_cenarios`, que converte os valores editados na interface
no formato que o valuation_engine espera. A UI em si não é testada aqui.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import montar_cenarios
from valuation_engine import calcular_valuation_completo


class TestMontarCenarios(unittest.TestCase):
    def test_formato_esperado_pelo_engine(self):
        valores = {
            "pessimista": {"g1": 0.05, "g2": 0.00},
            "otimista": {"g1": 0.15, "g2": 0.036},
        }
        cenarios = montar_cenarios(valores)
        self.assertEqual(
            cenarios["pessimista"],
            {"crescimento_fase_1": 0.05, "crescimento_fase_2": 0.00},
        )
        self.assertEqual(
            cenarios["otimista"],
            {"crescimento_fase_1": 0.15, "crescimento_fase_2": 0.036},
        )

    def test_cenarios_montados_rodam_no_engine(self):
        cenarios = montar_cenarios(
            {
                "baixo": {"g1": 0.05, "g2": 0.0},
                "alto": {"g1": 0.15, "g2": 0.03},
            }
        )
        res = calcular_valuation_completo(
            ticker="X",
            ebit_atual=1.0,
            acoes_em_circulacao=1.0,
            preco_atual=10.0,
            cenarios=cenarios,
        )
        self.assertEqual(set(res["resultados"].keys()), {"baixo", "alto"})


if __name__ == "__main__":
    unittest.main()
