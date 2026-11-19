import unittest

import numpy as np
import pandas as pd

import dolar_justo as dj


def _idx(n, ini="2010-01-31"):
    return pd.date_range(ini, periods=n, freq="ME")


class TestPPC(unittest.TestCase):
    def test_mesma_inflacao_nao_muda_o_dolar(self):
        i = _idx(120)
        dolar = pd.Series(3.0, index=i)
        ipca = pd.Series(0.5, index=i)                       # 0,5% ao mês no Brasil
        cpi = pd.Series(100 * 1.005 ** np.arange(120), index=i)   # idem nos EUA
        r = dj.ppc_por_ano_base(dolar, ipca, cpi, anos_base=(2012,))
        self.assertAlmostEqual(r[2012]["justo"], 3.0, places=2)

    def test_mais_inflacao_no_brasil_sobe_o_dolar_justo(self):
        i = _idx(120)
        dolar = pd.Series(3.0, index=i)
        ipca = pd.Series(1.0, index=i)
        cpi = pd.Series(100 * 1.002 ** np.arange(120), index=i)
        r = dj.ppc_por_ano_base(dolar, ipca, cpi, anos_base=(2012,))
        self.assertGreater(r[2012]["justo"], 3.0)

    def test_ano_base_sem_dados_e_ignorado(self):
        i = _idx(24)
        r = dj.ppc_por_ano_base(pd.Series(3.0, index=i), pd.Series(0.5, index=i),
                                pd.Series(100.0, index=i), anos_base=(1990,))
        self.assertEqual(r, {})


class TestModelo(unittest.TestCase):
    def _painel(self, n=200, seed=0):
        rng = np.random.default_rng(seed)
        i = _idx(n, "2010-01-31")
        dxy = 90 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
        risco = 200 * np.exp(np.cumsum(rng.normal(0, 0.05, n)))
        commod = 25 * np.exp(np.cumsum(rng.normal(0, 0.03, n)))
        carry = np.cumsum(rng.normal(0, 0.2, n))
        # dólar construído com relação conhecida (nas variações, o que importa)
        ln_d = np.cumsum(0.4 * np.diff(np.log(risco), prepend=np.log(risco[0]))
                         + 0.3 * np.diff(np.log(dxy), prepend=np.log(dxy[0]))
                         + rng.normal(0, 0.005, n)) + np.log(3.0)
        return pd.DataFrame({"dolar": np.exp(ln_d), "dxy": dxy, "commod": commod,
                             "risco": risco, "carry": carry}, index=i)

    def test_recupera_relacao_conhecida(self):
        m = dj.modelo_fundamentos(self._painel())
        self.assertIsNotNone(m)
        self.assertAlmostEqual(m["coef"]["risco"], 0.4, delta=0.1)
        self.assertAlmostEqual(m["coef"]["dxy"], 0.3, delta=0.1)
        self.assertGreater(m["r2"], 0.8)

    def test_contribuicoes_somam_a_variacao_real(self):
        m = dj.modelo_fundamentos(self._painel())
        soma = sum(m["contrib_pp"].values())
        real = np.log1p(m["variacao_real_pct"] / 100) * 100
        self.assertAlmostEqual(soma, real, places=6)

    def test_serie_explicada_tem_mesmo_tamanho(self):
        m = dj.modelo_fundamentos(self._painel())
        self.assertEqual(len(m["serie"]["data"]), len(m["serie"]["explicado"]))
        self.assertIsNone(m["serie"]["explicado"][0])

    def test_pouco_dado_devolve_none(self):
        self.assertIsNone(dj.modelo_fundamentos(self._painel(n=40)))

    def test_teste_fora_da_amostra_bate_o_dolar_parado(self):
        t = dj.teste_fora_amostra(self._painel(n=240))
        self.assertIsNotNone(t)
        self.assertLess(t["erro_medio_pp"], t["erro_dolar_parado_pp"])


class TestFaixa(unittest.TestCase):
    def test_faixa(self):
        f = dj.faixa_justa({2015: {"base": 3, "justo": 4.0}, 2019: {"base": 4, "justo": 4.5}}, None)
        self.assertEqual((f["ppc_min"], f["ppc_max"]), (4.0, 4.5))


if __name__ == "__main__":
    unittest.main()


class TestFrescor(unittest.TestCase):
    def _d(self, ult):
        meses = [f"{2010 + i // 12}-{i % 12 + 1:02d}" for i in range(200)]
        meses = [m for m in meses if m <= ult]
        s = {m: 1.0 for m in meses}
        return {k: s for k in ("dxy", "commod", "dolar", "ipca", "cpi_eua")}

    def test_serie_parada_e_recusada(self):
        d = self._d("2026-09")
        d["cpi_eua"] = {m: 1.0 for m in list(d["dxy"])[:150]}       # BLS parou há anos
        with self.assertRaises(RuntimeError):
            dj._validar_frescor(d, hoje=pd.Timestamp("2026-11-19"))

    def test_series_em_dia_passam(self):
        dj._validar_frescor(self._d("2026-10"), hoje=pd.Timestamp("2026-11-19"))

    def test_buraco_no_meio_e_recusado(self):
        d = self._d("2026-10")
        d["cpi_eua"] = {m: v for m, v in d["cpi_eua"].items() if not ("2015-01" <= m <= "2015-12")}
        with self.assertRaises(RuntimeError):
            dj._validar_frescor(d, hoje=pd.Timestamp("2026-11-19"))


class TestDegradacao(unittest.TestCase):
    def test_sem_cpi_o_modelo_continua_e_o_ppc_some(self):
        n = 200
        i = pd.date_range("2010-01-31", periods=n, freq="ME")
        rng = np.random.default_rng(1)
        ser = lambda v: {d.strftime("%Y-%m"): float(x) for d, x in zip(i, v)}
        ins = {"dolar": ser(3 * np.exp(np.cumsum(rng.normal(0, .02, n)))),
               "dxy": ser(90 * np.exp(np.cumsum(rng.normal(0, .01, n)))),
               "commod": ser(25 * np.exp(np.cumsum(rng.normal(0, .02, n)))),
               "ipca": ser(np.full(n, .4)), "cpi_eua": None, "faltando": ["cpi_eua"]}
        cambio = [{"data": d.strftime("%Y-%m"), "risco": 200 * np.exp(rng.normal(0, .1)),
                   "carry": float(rng.normal(5, 1))} for d in i]
        r = dj.calcular(cambio, ins)
        self.assertEqual(r["ppc"], {})
        self.assertIsNotNone(r["modelo"])
        self.assertEqual(r["faltando"], ["cpi_eua"])


class TestPPCSerie(unittest.TestCase):
    def test_serie_bate_com_o_ponto_final(self):
        i = _idx(120)
        dolar = pd.Series(3.0, index=i)
        ipca = pd.Series(1.0, index=i)
        cpi = pd.Series(100 * 1.002 ** np.arange(120), index=i)
        s = dj.ppc_serie(dolar, ipca, cpi, 2012)
        ponto = dj.ppc_por_ano_base(dolar, ipca, cpi, anos_base=(2012,))[2012]["justo"]
        self.assertAlmostEqual(float(s.iloc[-1]), ponto, places=9)
        self.assertGreater(float(s.iloc[-1]), float(s.iloc[0]))

    def test_ano_sem_dado_devolve_none(self):
        i = _idx(24)
        self.assertIsNone(dj.ppc_serie(pd.Series(3.0, index=i), pd.Series(.5, index=i),
                                       pd.Series(100.0, index=i), 1990))
