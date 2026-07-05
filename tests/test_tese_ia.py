"""Testes das funções puras de tese_ia (sem chamar a API da Anthropic)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tese_ia import _extrair_json, _normalizar, _salvar_tese_ia, buscar_tese_ia_cache, carregar_teses_ia


class TestExtrairJson(unittest.TestCase):
    def test_json_puro(self):
        d = _extrair_json('{"setor": "Bancos", "tese": "ok"}')
        self.assertEqual(d["setor"], "Bancos")

    def test_json_com_cerca_markdown(self):
        d = _extrair_json('```json\n{"setor": "Varejo"}\n```')
        self.assertEqual(d["setor"], "Varejo")

    def test_json_com_texto_em_volta(self):
        d = _extrair_json('Segue: {"a": 1} fim')
        self.assertEqual(d["a"], 1)

    def test_sem_json_gera_erro(self):
        with self.assertRaises(ValueError):
            _extrair_json("sem json aqui")


class TestNormalizar(unittest.TestCase):
    def test_estrutura_e_origem(self):
        t = _normalizar(
            {"setor": " Energia ", "tese": "t", "pontos_fortes": ["a", " b "], "pontos_fracos": "risco"},
            "eqtl3",
        )
        self.assertEqual(t["ticker"], "EQTL3")
        self.assertEqual(t["setor"], "Energia")
        self.assertEqual(t["pontos_fortes"], ["a", "b"])
        self.assertEqual(t["pontos_fracos"], ["risco"])
        self.assertIn("IA", t["origem"])


class TestCacheIa(unittest.TestCase):
    def test_salva_e_le(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "teses_ia.json"
            _salvar_tese_ia(_normalizar({"setor": "X"}, "AAAA3"), p)
            cache = carregar_teses_ia(p)
            self.assertIn("AAAA3", cache)

    def test_cache_inexistente(self):
        self.assertIsNone(buscar_tese_ia_cache("ZZZZ9"))


if __name__ == "__main__":
    unittest.main()
