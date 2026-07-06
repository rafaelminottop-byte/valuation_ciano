"""
Listas nomeadas de tickers, persistidas em data/listas.json.

Servem para salvar o resultado de um screener (ou qualquer conjunto) com um
nome e reusá-lo em outras abas — por exemplo, a aba Gatilhos monitorando a
lista salva. Arquivo local/pessoal (fora do versionamento).
"""

import json
from pathlib import Path

LISTAS_PATH = Path(__file__).resolve().parent / "data" / "listas.json"


def carregar_listas(caminho: Path = None) -> dict:
    """Devolve {nome_da_lista: [tickers]} (vazio se não houver arquivo)."""
    caminho = caminho or LISTAS_PATH
    if not caminho.exists():
        return {}
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        str(nome): [str(t).strip().upper() for t in tickers if str(t).strip()]
        for nome, tickers in dados.items()
        if isinstance(tickers, list)
    }


def salvar_lista(nome: str, tickers, caminho: Path = None) -> dict:
    """Cria/atualiza uma lista nomeada (tickers normalizados, sem duplicatas)."""
    nome = str(nome).strip()
    if not nome:
        raise ValueError("A lista precisa de um nome.")
    limpos = []
    for t in tickers:
        t = str(t).strip().upper()
        if t and t not in limpos:
            limpos.append(t)
    listas = carregar_listas(caminho)
    listas[nome] = limpos
    caminho = caminho or LISTAS_PATH
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(listas, ensure_ascii=False, indent=2), encoding="utf-8")
    return listas


def remover_lista(nome: str, caminho: Path = None) -> dict:
    """Remove uma lista pelo nome e devolve o dicionário atualizado."""
    listas = carregar_listas(caminho)
    listas.pop(str(nome).strip(), None)
    caminho = caminho or LISTAS_PATH
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(listas, ensure_ascii=False, indent=2), encoding="utf-8")
    return listas


def nomes_listas(caminho: Path = None) -> list[str]:
    return list(carregar_listas(caminho).keys())
