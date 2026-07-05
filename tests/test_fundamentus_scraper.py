"""
Testes do fundamentus_scraper.py (sem acesso à internet).

Cobrem o parsing de números no formato brasileiro e o processamento da
tabela, incluindo a regressão em que valores já convertidos eram convertidos
de novo (ex.: 4,45 virava 445) e a remoção da dependência da coluna
"Valor de mercado", que o Fundamentus deixou de expor.
"""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fundamentus_scraper import _para_numero, _processar_tabela, buscar_dados_ticker


class TestParaNumero(unittest.TestCase):
    def test_decimal_simples(self):
        r = _para_numero(pd.Series(["4,45"]))
        self.assertAlmostEqual(r.iloc[0], 4.45)

    def test_milhar_e_decimal(self):
        r = _para_numero(pd.Series(["1.234,56"]))
        self.assertAlmostEqual(r.iloc[0], 1234.56)

    def test_percentual_vira_fracao(self):
        r = _para_numero(pd.Series(["12,3%"]))
        self.assertAlmostEqual(r.iloc[0], 0.123)


class TestProcessarTabela(unittest.TestCase):
    def test_deriva_ebit_por_acao_sem_valor_de_mercado(self):
        # Tabela crua no formato atual do Fundamentus: sem "Valor de mercado".
        # Números já convertidos (como pd.read_html com decimal="," faria).
        df_raw = pd.DataFrame(
            {
                "Papel": ["MGLU3"],
                "Cotação": [4.45],
                "P/EBIT": [2.30],
            }
        )
        df = _processar_tabela(df_raw)

        linha = df.iloc[0]
        self.assertAlmostEqual(linha["preco_atual"], 4.45)
        self.assertAlmostEqual(linha["ebit_por_acao"], 4.45 / 2.30)
        self.assertEqual(linha["acoes_em_circulacao"], 1.0)
        self.assertAlmostEqual(linha["ebit_atual"], 4.45 / 2.30)

    def test_nao_reconverte_numeros_ja_convertidos(self):
        # Regressão: 4,45 já convertido para 4.45 (float) não pode virar 445.
        df_raw = pd.DataFrame({"Papel": ["MGLU3"], "Cotação": [4.45], "P/EBIT": [2.30]})
        df = _processar_tabela(df_raw)
        self.assertLess(df.iloc[0]["preco_atual"], 10.0)

    def test_converte_texto_cru_em_formato_brasileiro(self):
        # Quando a coluna vem como texto ("4,45"), _para_numero deve agir.
        df_raw = pd.DataFrame({"Papel": ["MGLU3"], "Cotação": ["4,45"], "P/EBIT": ["2,30"]})
        df = _processar_tabela(df_raw)
        self.assertAlmostEqual(df.iloc[0]["preco_atual"], 4.45)
        self.assertAlmostEqual(df.iloc[0]["p_ebit"], 2.30)


class TestBuscarDadosTicker(unittest.TestCase):
    def test_busca_ticker_do_dataframe(self):
        df = _processar_tabela(
            pd.DataFrame({"Papel": ["MGLU3", "PETR4"], "Cotação": [4.45, 38.25], "P/EBIT": [2.30, 4.0]})
        )
        dados = buscar_dados_ticker("mglu3", df=df)
        self.assertEqual(dados["ticker"], "MGLU3")
        self.assertAlmostEqual(dados["preco_atual"], 4.45)
        self.assertAlmostEqual(dados["ebit_atual"], 4.45 / 2.30)

    def test_ticker_inexistente_gera_erro(self):
        df = _processar_tabela(pd.DataFrame({"Papel": ["MGLU3"], "Cotação": [4.45], "P/EBIT": [2.30]}))
        with self.assertRaises(ValueError):
            buscar_dados_ticker("XXXX9", df=df)


if __name__ == "__main__":
    unittest.main()
