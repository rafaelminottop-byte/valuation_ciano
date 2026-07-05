"""
Acesso às teses de investimento da Ciano (data/teses.json).

O JSON é gerado a partir do relatório "Ciano_Valuation_Report_Teses 2.0.docx"
e traz, por ticker: setor, tese, pontos fortes e pontos fracos.
"""

import json
from functools import lru_cache
from pathlib import Path

TESES_PATH = Path(__file__).resolve().parent / "data" / "teses.json"


@lru_cache(maxsize=1)
def carregar_teses() -> dict:
    """Carrega o dicionário de teses (ticker -> dados). Vazio se não houver arquivo."""
    if not TESES_PATH.exists():
        return {}
    return json.loads(TESES_PATH.read_text(encoding="utf-8"))


def buscar_tese(ticker: str) -> dict | None:
    """Retorna a tese de um ticker (case-insensitive) ou None se não houver."""
    if not ticker:
        return None
    return carregar_teses().get(ticker.strip().upper())
