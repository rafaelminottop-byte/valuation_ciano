"""Testes da análise de carteira e da projeção (BIG NUMBERS)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planejamento as pl


class TestAnalise(unittest.TestCase):
    def setUp(self):
        self.pos = [
            {"ativo": "Tesouro Selic", "classe": "Renda Fixa Pós (CDI/Selic)",
             "valor_aplicado": 50000, "valor_atual": 60000},
            {"ativo": "PETR4", "classe": "Ações", "valor_aplicado": 30000, "valor_atual": 30000},
            {"ativo": "MXRF11", "classe": "FIIs", "valor_aplicado": 12000, "valor_atual": 10000},
            {"ativo": "", "classe": "Caixa", "valor_aplicado": 1, "valor_atual": 1},  # ignorada
        ]

    def test_totais_e_pesos(self):
        r = pl.analisar_carteira(self.pos)
        self.assertAlmostEqual(r["total"], 100000)
        self.assertAlmostEqual(r["aplicado"], 92000)
        self.assertAlmostEqual(r["maior_ativo"]["peso_pct"], 60)
        self.assertAlmostEqual(sum(c["peso_pct"] for c in r["classes"]), 100)
        self.assertAlmostEqual(r["hhi"], 0.36 + 0.09 + 0.01)

    def test_alerta_concentracao(self):
        r = pl.analisar_carteira(self.pos)
        self.assertTrue(any("Tesouro Selic" in a for a in r["alertas"]))

    def test_posicao_negativa_reduz_patrimonio(self):
        r = pl.analisar_carteira(self.pos + [
            {"ativo": "PETRJ420 (opção vendida)", "classe": "Ações", "valor_aplicado": 0, "valor_atual": -2000}])
        self.assertAlmostEqual(r["total"], 98000)

    def test_vazia(self):
        self.assertEqual(pl.analisar_carteira([])["total"], 0)

    def test_comparar_perfil(self):
        r = pl.analisar_carteira(self.pos)
        linhas = {l["classe"]: l for l in pl.comparar_perfil(r["classes"], r["total"],
                                                             {"Ações": 40, "Renda Fixa Pós (CDI/Selic)": 60})}
        self.assertAlmostEqual(linhas["Ações"]["ajuste_rs"], 10000)
        self.assertAlmostEqual(linhas["FIIs"]["ajuste_rs"], -10000)


class TestProjecao(unittest.TestCase):
    def test_taxa_mensal_equivalente(self):
        self.assertAlmostEqual((1 + pl.taxa_mensal(15)) ** 12, 1.15)

    def test_sem_aporte_juros_compostos(self):
        l = pl.projetar(100000, 0, 10, 5, ir_pct=0)
        self.assertAlmostEqual(l[-1]["bruto"], 100000 * 1.1 ** 5, places=4)

    def test_ir_somente_sobre_ganho(self):
        l = pl.projetar(100000, 0, 10, 1, ir_pct=15)[-1]
        self.assertAlmostEqual(l["ir"], 10000 * 0.15, places=4)
        self.assertAlmostEqual(l["liquido"], 108500, places=4)

    def test_real_deflacionado(self):
        l = pl.projetar(100000, 0, 10, 2, ir_pct=0, inflacao_pct=10)[-1]
        self.assertAlmostEqual(l["real"], 100000, places=4)

    def test_big_numbers_a_cada_5_anos(self):
        m = pl.big_numbers(100000, 1000, 14, 4, horizonte=30)
        self.assertEqual([x["ano"] for x in m], [5, 10, 15, 20, 25, 30])
        self.assertTrue(all(a["real"] < b["real"] for a, b in zip(m, m[1:])))

    def test_aporte_para_meta_fecha_com_projecao(self):
        a = pl.aporte_para_meta(1_000_000, 100000, 12, 5, 10)
        l = pl.projetar(100000, a, 12, 10, inflacao_pct=5)[-1]
        self.assertAlmostEqual(l["real"], 1_000_000, delta=1)

    def test_aporte_zero_se_meta_ja_atingida(self):
        self.assertEqual(pl.aporte_para_meta(100, 1000, 10, 4, 5), 0)

    def test_renda_preserva_poder_de_compra(self):
        # Sem IR: retirada = juro real mensal exato
        r = pl.renda_mensal_perpetua(1_000_000, 10, 5, ir_pct=0)
        i, pi = pl.taxa_mensal(10), pl.taxa_mensal(5)
        self.assertAlmostEqual(r, 1_000_000 * ((1 + i) / (1 + pi) - 1))
        # Com IR a retirada é menor; juro real negativo -> nada a retirar
        self.assertLess(pl.renda_mensal_perpetua(1_000_000, 10, 5), r)
        self.assertEqual(pl.renda_mensal_perpetua(1_000_000, 4, 6), 0)

    def test_patrimonio_para_renda_inverso(self):
        p = pl.patrimonio_para_renda(10000, 12, 5)
        self.assertAlmostEqual(pl.renda_mensal_perpetua(p, 12, 5), 10000)

    def test_media_anual_composta(self):
        self.assertAlmostEqual(pl.media_anual_composta([1.0] * 24), (1.01 ** 12 - 1) * 100)
        self.assertIsNone(pl.media_anual_composta([]))


class TestPersistencia(unittest.TestCase):
    def test_salvar_listar_carregar_excluir(self):
        with TemporaryDirectory() as d:
            p = Path(d)
            pl.salvar_cliente({"nome": "João da Silva", "posicoes": []}, p)
            self.assertEqual(pl.listar_clientes(p), ["João da Silva"])
            self.assertEqual(pl.carregar_cliente("João da Silva", p)["nome"], "João da Silva")
            pl.excluir_cliente("João da Silva", p)
            self.assertEqual(pl.listar_clientes(p), [])

    def test_slug(self):
        self.assertEqual(pl.slug("João  Silva!"), "joao_silva")


if __name__ == "__main__":
    unittest.main()
