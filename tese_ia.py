"""
Geração de tese de investimento via IA (Claude), para empresas que não estão
no relatório curado da Ciano (data/teses.json).

Usa a API da Anthropic (modelo Claude Opus 4.8) com a ferramenta de web search
para pesquisar a empresa e sintetizar setor, tese, pontos fortes e fracos.
As teses geradas ficam em data/teses_ia.json (cache local, gitignored), com a
marca de que foram geradas por IA — não confundir com o relatório da Ciano.

Requer a variável de ambiente ANTHROPIC_API_KEY (ou um perfil `ant auth login`).
"""

import json
import re
from pathlib import Path

MODELO = "claude-opus-4-8"
TESES_IA_PATH = Path(__file__).resolve().parent / "data" / "teses_ia.json"

_PROMPT = (
    "Você é um analista de investimentos. Pesquise a empresa {empresa} (ação da "
    "bolsa brasileira B3) usando web search e escreva uma tese de investimento "
    "concisa, em português do Brasil.\n\n"
    "Responda APENAS com um objeto JSON válido (sem markdown, sem texto fora do "
    "JSON) com exatamente estas chaves:\n"
    '- "setor": string curta com o setor de atuação\n'
    '- "tese": string com 2-4 frases sobre a tese central de investimento\n'
    '- "pontos_fortes": array de 4 a 6 strings curtas (vantagens, catalisadores)\n'
    '- "pontos_fracos": array de 4 a 6 strings curtas (riscos, fraquezas)\n\n'
    "Baseie-se em fatos recentes e seja específico. Não invente números."
)


def _extrair_json(texto: str) -> dict:
    """Extrai o primeiro objeto JSON de um texto (tolera cercas de markdown)."""
    texto = texto.strip()
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.DOTALL).strip()
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio == -1 or fim == -1 or fim < inicio:
        raise ValueError("Nenhum objeto JSON encontrado na resposta da IA.")
    return json.loads(texto[inicio : fim + 1])


def _normalizar(dados: dict, ticker: str) -> dict:
    """Garante a estrutura esperada e marca a origem como IA."""
    def lista(v):
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        return [str(v).strip()] if v else []

    return {
        "ticker": ticker.upper(),
        "setor": str(dados.get("setor", "")).strip(),
        "tese": str(dados.get("tese", "")).strip(),
        "pontos_fortes": lista(dados.get("pontos_fortes")),
        "pontos_fracos": lista(dados.get("pontos_fracos")),
        "origem": "IA (Claude via web search)",
    }


def carregar_teses_ia(caminho: Path = None) -> dict:
    caminho = caminho or TESES_IA_PATH
    if not caminho.exists():
        return {}
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _salvar_tese_ia(tese: dict, caminho: Path = None) -> None:
    caminho = caminho or TESES_IA_PATH
    cache = carregar_teses_ia(caminho)
    cache[tese["ticker"]] = tese
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def buscar_tese_ia_cache(ticker: str) -> dict | None:
    """Retorna a tese gerada por IA já em cache, ou None."""
    if not ticker:
        return None
    return carregar_teses_ia().get(ticker.strip().upper())


def gerar_tese_ia(ticker: str, nome: str = None, usar_cache: bool = True) -> dict:
    """Gera (ou lê do cache) a tese de um ticker via IA. Requer ANTHROPIC_API_KEY."""
    ticker = ticker.strip().upper()
    if usar_cache:
        em_cache = buscar_tese_ia_cache(ticker)
        if em_cache:
            return em_cache

    # Import tardio: só exige a lib/credencial quando realmente for gerar.
    from anthropic import Anthropic

    client = Anthropic()
    empresa = f"{ticker} ({nome})" if nome else ticker
    mensagens = [{"role": "user", "content": _PROMPT.format(empresa=empresa)}]
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]

    resposta = None
    for _ in range(6):  # trata pause_turn do loop server-side de web search
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=4000,
            thinking={"type": "adaptive"},
            tools=tools,
            messages=mensagens,
        )
        if resposta.stop_reason != "pause_turn":
            break
        mensagens = [mensagens[0], {"role": "assistant", "content": resposta.content}]

    if resposta is not None and resposta.stop_reason == "refusal":
        raise RuntimeError("A IA recusou gerar a tese para este ticker.")

    texto = "".join(b.text for b in resposta.content if b.type == "text")
    tese = _normalizar(_extrair_json(texto), ticker)
    _salvar_tese_ia(tese)
    return tese
