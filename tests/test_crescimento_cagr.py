"""CAGR deve usar os anos que separam os pontos, não a quantidade de pontos."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from crescimento import _cagr  # noqa: E402

ANOS = ["2020-12-31", "2021-12-31", "2022-12-31", "2023-12-31", "2024-12-31"]


def test_anos_faltando_no_meio_nao_inflam_o_crescimento():
    # 100 em 2020 e 150 em 2024, sem os anos do meio: 4 anos -> 10,7% a.a. (e não 50%)
    assert _cagr([100, None, None, None, 150], ANOS) == pytest.approx(10.7, abs=0.05)
    assert _cagr([100, float("nan"), None, None, 150]) == pytest.approx(10.7, abs=0.05)


def test_serie_completa_continua_igual():
    assert _cagr([100, 110, 121, 133.1, 146.41], ANOS) == pytest.approx(10.0, abs=0.05)


def test_ponta_vazia_usa_so_os_pontos_validos():
    # primeiro ano sem dado: base é 2021, fim 2024 -> 3 anos
    assert _cagr([None, 100, 110, 121, 133.1], ANOS) == pytest.approx(10.0, abs=0.05)


def test_base_ou_fim_nao_positivos_ou_pouco_dado():
    assert _cagr([-10, 5, 8, 9, 10], ANOS) is None
    assert _cagr([100, None, None, None, None], ANOS) is None
