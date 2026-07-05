"""
Carteira / watchlist persistente (data/carteira.json).

Guarda a lista de tickers favoritos do usuário para avaliar todos de uma vez
no app. As funções aceitam um caminho opcional para facilitar os testes.
"""

import json
from pathlib import Path

CARTEIRA_PATH = Path(__file__).resolve().parent / "data" / "carteira.json"


def carregar_carteira(caminho: Path = None) -> list[str]:
    """Lê a lista de tickers da carteira (vazia se não houver arquivo/erro)."""
    caminho = caminho or CARTEIRA_PATH
    if not caminho.exists():
        return []
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return [t for t in dados if isinstance(t, str)]


def salvar_carteira(tickers: list[str], caminho: Path = None) -> list[str]:
    """Grava a carteira normalizada (upper, sem duplicatas, ordem preservada)."""
    caminho = caminho or CARTEIRA_PATH
    limpos = []
    for t in tickers:
        t = str(t).strip().upper()
        if t and t not in limpos:
            limpos.append(t)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(limpos, ensure_ascii=False, indent=2), encoding="utf-8")
    return limpos


def adicionar(ticker: str, caminho: Path = None) -> list[str]:
    """Adiciona um ticker à carteira e devolve a lista atualizada."""
    atual = carregar_carteira(caminho)
    return salvar_carteira(atual + [ticker], caminho)


def remover(ticker: str, caminho: Path = None) -> list[str]:
    """Remove um ticker da carteira e devolve a lista atualizada."""
    alvo = str(ticker).strip().upper()
    restantes = [t for t in carregar_carteira(caminho) if t != alvo]
    return salvar_carteira(restantes, caminho)
