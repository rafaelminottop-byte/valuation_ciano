"""Testes da datação das teses (idade e alerta de tese defasada)."""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import MESES_PT, _esc_html, _esc_md, idade_tese_meses


class TestIdadeTese(unittest.TestCase):
    def _data_de(self, meses_atras: int) -> str:
        hoje = date.today()
        total = (hoje.year * 12 + hoje.month - 1) - meses_atras
        return f"{MESES_PT[total % 12]}/{total // 12}"

    def test_tese_do_mes_corrente(self):
        self.assertEqual(idade_tese_meses(self._data_de(0)), 0)

    def test_tese_de_dez_meses(self):
        self.assertEqual(idade_tese_meses(self._data_de(10)), 10)

    def test_formato_invalido_devolve_none(self):
        for ruim in ("", None, "2026", "julho", "xxx/2026", "julho/xx"):
            self.assertIsNone(idade_tese_meses(ruim))


class TestEscapes(unittest.TestCase):
    def test_cifrao_escapado_no_markdown(self):
        # Sem isso, o Streamlit lê "R$ 5,24 ... R$ 6,37" como fórmula LaTeX
        texto = "Preço atual R$ 5,24 · Market cap R$ 6,37 bi"
        self.assertNotIn("$ ", _esc_md(texto).replace(r"\$", ""))
        self.assertEqual(_esc_md(texto).count(r"\$"), 2)

    def test_cifrao_vira_entidade_no_html(self):
        self.assertIn("&#36;", _esc_html("R$ 10"))
        self.assertNotIn("$", _esc_html("R$ 10"))

    def test_html_continua_escapado(self):
        self.assertIn("&lt;", _esc_html("<script>"))


if __name__ == "__main__":
    unittest.main()
