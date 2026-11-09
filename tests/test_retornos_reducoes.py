"""Testa a tabela 'o que veio depois de cada redução' (preditor.retornos_apos_reducoes).

Usa uma série sintética com retornos constantes, para os números poderem ser conferidos à mão.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preditor  # noqa: E402


def _lab(n=40, r=0.01, cdi=0.005, z=2.0):
    datas = [str(p) for p in pd.period_range("2000-01", periods=n, freq="M")]
    ibov = [100.0 * (1 + r) ** k for k in range(n)]
    return {"datas": datas, "ibov": ibov, "r": [None] + [r] * (n - 1), "cdi": [cdi] * n,
            "z": [z] * n, "score": [None] * n, "ciclo": ["parada"] * n,
            "ln_media": [0.0] * n, "sest": [1.0] * n}


def test_reducao_unica_com_numeros_conferiveis():
    bt = preditor.backtest_banda(_lab(), alivio=1.5, recompra=0.0, modo="50")
    linhas = preditor.retornos_apos_reducoes(bt)
    assert len(linhas) == 1
    r = linhas[0]
    assert r["data"] == "2000-02" and r["parcial"] is False and r["ate"] == "2001-01"
    assert r["lucro_posicao"] == 0.0                              # comprou no início e reduziu logo
    assert r["ibov12"] == pytest.approx((1.01 ** 12 - 1) * 100, abs=0.06)
    assert r["cdi12"] == pytest.approx((1.005 ** 12 - 1) * 100, abs=0.06)
    # reduzindo 50%: a carteira rende metade Ibov, metade CDI todo mês
    assert r["carteira_ate"] == pytest.approx((1.0075 ** 12 - 1) * 100, abs=0.06)
    assert r["ibov_ate"] == r["ibov12"] and r["cdi_ate"] == r["cdi12"]   # reduziu no 1º mês: "do início" = 12m


def test_do_inicio_acumula_antes_da_reducao():
    """Reduzindo só no meio do caminho, 'do início' tem que incluir os meses antes da redução."""
    lab = _lab(n=48)
    lab["z"] = [0.0] * 10 + [2.0] * 38          # fica esticado só a partir do índice 10
    bt = preditor.backtest_banda(lab, alivio=1.5, recompra=0.0, modo="100")
    r = preditor.retornos_apos_reducoes(bt)[0]
    # 100% reduzido: a carteira rende o Ibov até a redução e o CDI depois
    # antes da redução: meses de índice 1..10 (10 meses); depois: 12 meses de CDI
    esperado = (1.01 ** 10) * (1.005 ** 12) - 1
    assert r["carteira_ate"] == pytest.approx(esperado * 100, abs=0.06)
    assert r["ibov_ate"] == pytest.approx((1.01 ** 22 - 1) * 100, abs=0.06)
    assert r["cdi_ate"] == pytest.approx((1.005 ** 22 - 1) * 100, abs=0.06)
    assert r["lucro_posicao"] == pytest.approx((1.01 ** 10 - 1) * 100, abs=0.06)   # lucro do início até a redução


def test_reducao_recente_fica_parcial():
    lab = _lab(n=40)
    lab["z"] = [0.0] * 34 + [2.0] * 6           # reduz perto do fim: faltam meses para fechar 12
    bt = preditor.backtest_banda(lab, alivio=1.5, recompra=0.0, modo="50")
    r = preditor.retornos_apos_reducoes(bt)[0]
    assert r["parcial"] is True and r["ate"] == lab["datas"][-1]
