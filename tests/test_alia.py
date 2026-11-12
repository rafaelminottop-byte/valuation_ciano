"""Testes da importação Alia (sem rede: só detecção, classificação e agrupamento)."""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import alia


REGISTROS = [
    {"client": {"name": "Ana"}, "asset_name": "CDB XP 110% CDI", "asset_class": "Renda Fixa",
     "gross_value": "10.000,50", "invested_value": 9000},
    {"client": {"name": "Ana"}, "asset_name": "CDB XP 110% CDI", "asset_class": "Renda Fixa",
     "gross_value": 1000, "invested_value": 1000},
    {"client": {"name": "Ana"}, "asset_name": "PETR4", "asset_class": "Ações",
     "gross_value": 5000, "invested_value": 6000},
    {"client": {"name": "Bruno"}, "asset_name": "Tesouro IPCA+ 2035", "asset_class": "Título Público",
     "gross_value": 20000, "invested_value": None},
    {"client": {"name": "Bruno"}, "asset_name": "Zerado", "asset_class": "Renda Fixa",
     "gross_value": 0, "invested_value": 0},
]


class TestAlia(unittest.TestCase):
    def test_detecta_mapa_com_campos_aninhados(self):
        regs = alia.extrair_registros(REGISTROS)
        m = alia.detectar_mapa(regs)
        self.assertEqual(m["cliente"], "client.name")
        self.assertEqual(m["ativo"], "asset_name")
        self.assertEqual(m["classe"], "asset_class")
        self.assertEqual(m["valor_atual"], "gross_value")
        self.assertEqual(m["valor_aplicado"], "invested_value")

    def test_envelope(self):
        self.assertEqual(len(alia.extrair_registros({"positions": REGISTROS})), 5)
        with self.assertRaises(alia.AliaErro):
            alia.extrair_registros({"ok": True})

    def test_agrupa_soma_e_classifica(self):
        regs = alia.extrair_registros(REGISTROS)
        g = alia.agrupar_por_cliente(regs, alia.detectar_mapa(regs))
        self.assertEqual(list(g), ["Ana", "Bruno"])
        cdb = g["Ana"][0]
        self.assertAlmostEqual(cdb["valor_atual"], 11000.5)
        self.assertAlmostEqual(cdb["valor_aplicado"], 10000)
        self.assertEqual(cdb["classe"], "Renda Fixa Pós (CDI/Selic)")
        self.assertEqual(g["Ana"][1]["classe"], "Ações")
        # classe genérica ("Título Público") -> cai para o nome do ativo
        self.assertEqual(g["Bruno"][0]["classe"], "Renda Fixa IPCA+")
        self.assertEqual(g["Bruno"][0]["valor_aplicado"], 20000)  # sem custo -> usa o atual
        self.assertEqual(len(g["Bruno"]), 1)  # posição zerada ignorada

    def test_layout_btg_com_conta_e_indexador(self):
        regs = [
            {"account_number": "123", "market": "RENDA FIXA", "sub_market": "BANCARIO",
             "indexer": "100% CDI", "asset": "CDB A", "gross_value": 100.0},
            {"account_number": "123", "market": "RENDA FIXA", "sub_market": "PRIVADO",
             "indexer": "100% IPCA", "asset": "DEB B", "gross_value": 50.0},
            {"account_number": "123", "market": "VALOR EM TRANSITO", "sub_market": "RV",
             "indexer": None, "asset": "LIQ", "gross_value": 10.0},
            {"account_number": "999", "market": "RENDA FIXA", "sub_market": "TESOURO DIRETO",
             "indexer": "PRE", "asset": "LTN", "gross_value": 70.0},
        ]
        m = alia.detectar_mapa(regs)
        self.assertEqual((m["cliente"], m["classe"]), ("account_number", "market"))
        g = alia.agrupar_por_cliente(regs, m, {"123": "Fulano"})
        self.assertEqual(set(g), {"Fulano", "999"})
        classes = {p["ativo"]: p["classe"] for p in g["Fulano"]}
        self.assertEqual(classes, {"CDB A": "Renda Fixa Pós (CDI/Selic)",
                                   "DEB B": "Renda Fixa IPCA+", "LIQ": "Caixa"})
        self.assertEqual(g["999"][0]["classe"], "Renda Fixa Pré")

    def test_contas_persistem(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            alia.salvar_contas({"1": " Ana ", "2": ""}, p)
            self.assertEqual(alia.carregar_contas(p), {"1": "Ana"})

    def test_ler_lista_do_portal_btg(self):
        texto = """A
Ana Souza
004021812
Investimentos	Individual	
Ana Souza

Acessar
L
Lucas Elias
002779661
Banking	Individual	
Lucas Elias

Acessar
002779661
Investimentos	Individual	
Lucas Elias
005446236
Investimentos	Individual	
Lucas Elias

Acessar
"""
        self.assertEqual(alia.ler_lista_contas(texto), {
            "004021812": "Ana Souza", "002779661": "Lucas Elias", "005446236": "Lucas Elias"})

    def test_nome_casa_mesmo_sem_zeros_a_esquerda(self):
        regs = [{"account_number": "5407133", "asset": "X", "market": "RENDA FIXA",
                 "gross_value": 10.0}]
        g = alia.agrupar_por_cliente(regs, alia.detectar_mapa(regs), {"005407133": "Daniel"})
        self.assertEqual(list(g), ["Daniel"])

    def test_linha_sem_asset_nao_e_descartada(self):
        regs = [
            {"account_number": "1", "asset": "PETR4", "product": "ACAO", "market": "RENDA VARIAVEL",
             "sub_market": "ACAO", "gross_value": 100.0},
            {"account_number": "1", "asset": None, "product": "FUNDO XPTO FIC FIM", "market": "FUNDOS",
             "sub_market": "FN", "gross_value": 300.0},
            {"account_number": "1", "asset": "", "product": None, "market": "CONTA CORRENTE",
             "sub_market": "CC", "gross_value": 5.0},
        ]
        g = alia.agrupar_por_cliente(regs, alia.detectar_mapa(regs))["1"]
        self.assertAlmostEqual(sum(p["valor_atual"] for p in g), 405.0)
        nomes = {p["ativo"]: p["classe"] for p in g}
        self.assertEqual(nomes["FUNDO XPTO FIC FIM"], "Fundos de Investimento")
        self.assertEqual(nomes["Conta Corrente Cc"], "Caixa")

    def test_classificar(self):
        casos = {"FII MXRF11": "FIIs", "LCI Banco X": "Renda Fixa Pós (CDI/Selic)",
                 "Tesouro Prefixado 2029": "Renda Fixa Pré", "VGBL Icatu": "Previdência",
                 "BDR AAPL34": "Internacional", "Fundo Multimercado Y": "Multimercado",
                 "Dividendos ITSA4 ação": "Ações", "Bitcoin ETF": "Cripto"}
        for texto, esperado in casos.items():
            self.assertEqual(alia.classificar(texto), esperado, texto)

    def test_valor_formatos(self):
        self.assertEqual(alia._valor("1.234,56"), 1234.56)
        self.assertEqual(alia._valor("1,234.56"), 1234.56)
        self.assertEqual(alia._valor("R$ 10,5"), 10.5)
        self.assertEqual(alia._valor(None), 0)

    def test_erro_http_legivel(self):
        resp = mock.Mock(status_code=503)
        with mock.patch.object(alia.requests, "get", return_value=resp), \
             mock.patch.object(alia, "CACHE_DIR", Path("__inexistente__")):
            with self.assertRaisesRegex(alia.AliaErro, "ocupado"):
                alia.buscar_posicoes("2026-10-01")

    def test_ultimo_dia_util(self):
        from datetime import date
        self.assertEqual(alia.ultimo_dia_util(date(2026, 10, 5)), date(2026, 10, 2))  # seg -> sex


if __name__ == "__main__":
    unittest.main()
