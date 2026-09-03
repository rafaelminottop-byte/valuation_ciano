"""Testes das funções puras de notícias (extração de gatilhos, parse RSS, marcação)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from noticias import marcar_e_ordenar, palavras_chave_gatilhos, parse_rss


class TestPalavrasChave(unittest.TestCase):
    def test_extrai_da_cabeca_do_gatilho(self):
        tese = {"gatilhos": [
            "Recuperação do ciclo de preços de açúcar e etanol — o principal gatilho.",
            "Diversificação para etanol de milho — reduz dependência.",
        ]}
        p = palavras_chave_gatilhos(tese)
        # termos macro e substantivos relevantes entram (sem acento)
        self.assertIn("acucar", p)
        self.assertIn("etanol", p)
        self.assertIn("milho", p)
        self.assertIn("recuperacao", p)

    def test_stopwords_e_curtas_fora(self):
        tese = {"gatilhos": ["Queda da Selic — reduz custo da dívida"]}
        p = palavras_chave_gatilhos(tese)
        self.assertIn("selic", p)          # termo macro
        self.assertNotIn("queda", p)       # stopword
        self.assertNotIn("da", p)          # curta

    def test_usa_pontos_fortes_quando_nao_ha_gatilhos(self):
        tese = {"pontos_fortes": ["Forte geração de caixa e dividendo elevado"]}
        p = palavras_chave_gatilhos(tese)
        self.assertIn("dividendo", p)      # termo macro pega em todo o texto

    def test_sem_tese(self):
        self.assertEqual(palavras_chave_gatilhos({}), set())


class TestParseRss(unittest.TestCase):
    RSS = b"""<?xml version="1.0"?><rss><channel>
      <item>
        <title>Movida ve lucro saltar 100% no 2 tri - InvestNews</title>
        <link>http://x/1</link>
        <pubDate>Mon, 10 Aug 2026 12:00:00 GMT</pubDate>
        <source url="http://investnews">InvestNews</source>
      </item>
      <item>
        <title>Outra materia qualquer</title>
        <link>http://x/2</link>
        <pubDate>Sun, 09 Aug 2026 08:00:00 GMT</pubDate>
      </item>
    </channel></rss>"""

    def test_extrai_campos_e_remove_fonte_do_titulo(self):
        itens = parse_rss(self.RSS)
        self.assertEqual(len(itens), 2)
        self.assertEqual(itens[0]["titulo"], "Movida ve lucro saltar 100% no 2 tri")
        self.assertEqual(itens[0]["fonte"], "InvestNews")
        self.assertEqual(itens[0]["data"], "10/08")
        self.assertEqual(itens[0]["link"], "http://x/1")

    def test_ts_ordena_por_data(self):
        itens = parse_rss(self.RSS)
        self.assertGreater(itens[0]["ts"], itens[1]["ts"])


class TestMarcarEOrdenar(unittest.TestCase):
    def test_marca_gatilho_e_poe_no_topo(self):
        noticias = [
            {"titulo": "Notícia sem relação nenhuma", "ts": 200},
            {"titulo": "Preço do açúcar dispara no mercado", "ts": 100},
        ]
        r = marcar_e_ordenar(noticias, {"acucar", "etanol"})
        # a com gatilho vai pro topo, mesmo sendo mais antiga
        self.assertEqual(r[0]["titulo"], "Preço do açúcar dispara no mercado")
        self.assertEqual(r[0]["gatilhos"], ["acucar"])
        self.assertEqual(r[1]["gatilhos"], [])

    def test_desempate_por_data_dentro_do_grupo(self):
        noticias = [
            {"titulo": "Selic cai hoje", "ts": 100},
            {"titulo": "Selic sobe agora", "ts": 300},
        ]
        r = marcar_e_ordenar(noticias, {"selic"})
        self.assertEqual(r[0]["titulo"], "Selic sobe agora")  # mais recente primeiro


if __name__ == "__main__":
    unittest.main()
