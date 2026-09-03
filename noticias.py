"""
Notícias das empresas com tese — via Google News RSS (PT-BR, grátis).

Para cada empresa da carteira de teses, busca as manchetes recentes e destaca as
que se relacionam aos GATILHOS da tese (ex.: se o gatilho é "recuperação do preço
do açúcar", uma notícia com "açúcar" no título é marcada). Assim o usuário vê,
de bate-pronto, quando um catalisador da tese aparece no noticiário.

O Google News RSS aceita o operador `when:Nd` (últimos N dias) e devolve título,
fonte, data e link. Cache local por empresa (TTL curto) para não repetir a busca.
"""

import json
import re
import time
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "noticias.json"
CACHE_TTL_SEGUNDOS = 2 * 60 * 60  # 2 horas
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Palavras sem valor de gatilho (verbos/adjetivos/conectivos comuns nos textos
# de tese). Comparação sempre sem acento e em minúsculas.
STOPWORDS = {
    "queda", "alta", "maior", "menor", "reduz", "reducao", "aumento", "aumenta",
    "custo", "sobre", "mesmo", "menos", "sendo", "ainda", "muito", "menor",
    "melhora", "piora", "efeito", "nova", "novo", "novos", "novas", "grande",
    "forte", "fraca", "baixo", "baixa", "elevado", "elevada", "acima", "abaixo",
    "estrutural", "continua", "consistente", "relevante", "potencial", "espaco",
    "historico", "historicamente", "praticamente", "possivel", "seguir", "manter",
    "pelo", "pela", "pelos", "para", "como", "entre", "cada", "todos", "todas",
    "empresa", "companhia", "setor", "mercado", "resultado", "resultados",
    "trimestre", "ano", "anos", "reais", "milhoes", "bilhoes", "bilhao",
}

# Termos-chave macro que valem como gatilho mesmo curtos (adicionados sempre que
# aparecem no texto do gatilho).
TERMOS_MACRO = {"selic", "juros", "cambio", "dolar", "ipca", "safra", "brent",
                "petroleo", "acucar", "etanol", "milho", "boi", "soja", "minerio",
                "dividendo", "dividendos", "payout", "tarifa", "tarifas"}


def _sem_acento(txt: str) -> str:
    nfkd = unicodedata.normalize("NFD", txt.lower())
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def palavras_chave_gatilhos(tese: dict) -> set:
    """Extrai as palavras-chave dos gatilhos da tese (ou pontos_fortes, se antiga).

    Pega a 'cabeça' de cada gatilho (antes do travessão) mais os termos macro que
    aparecem em qualquer parte, filtrando stopwords e palavras curtas.
    """
    fonte = tese.get("gatilhos") or tese.get("pontos_fortes") or []
    palavras = set()
    for g in fonte:
        cabeca = re.split(r"[—–-]", g, maxsplit=1)[0]
        for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", cabeca):
            wl = _sem_acento(w)
            if len(wl) >= 5 and wl not in STOPWORDS:
                palavras.add(wl)
        for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", g):  # termos macro em todo o texto
            wl = _sem_acento(w)
            if wl in TERMOS_MACRO:
                palavras.add(wl)
    return palavras


def _fmt_data(pubdate: str) -> tuple[str, float]:
    """('dd/mm', timestamp) a partir do pubDate RFC822 do RSS."""
    try:
        dt = parsedate_to_datetime(pubdate)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%d/%m"), dt.timestamp()
    except (TypeError, ValueError):
        return "", 0.0


def parse_rss(xml_bytes: bytes) -> list[dict]:
    """Converte o RSS do Google News em [{titulo, fonte, data, ts, link}]."""
    root = ET.fromstring(xml_bytes)
    itens = []
    for it in root.findall(".//item"):
        titulo = (it.findtext("title") or "").strip()
        fonte = (it.findtext("source") or "").strip()
        # O Google costuma anexar " - Fonte" ao título; removemos.
        if fonte and titulo.endswith(f"- {fonte}"):
            titulo = titulo[: -(len(fonte) + 2)].strip()
        data, ts = _fmt_data(it.findtext("pubDate") or "")
        itens.append({"titulo": titulo, "fonte": fonte, "data": data,
                      "ts": ts, "link": (it.findtext("link") or "").strip()})
    return itens


def marcar_e_ordenar(noticias: list[dict], palavras: set) -> list[dict]:
    """Marca cada notícia com os gatilhos que ela cita e ordena (gatilho + recente)."""
    for n in noticias:
        titulo_sa = _sem_acento(n["titulo"])
        n["gatilhos"] = sorted({p for p in palavras if p in titulo_sa})
    return sorted(noticias, key=lambda n: (0 if n["gatilhos"] else 1, -n.get("ts", 0)))


def _carregar_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def buscar_noticias(
    empresa: str, dias: int = 14, max_itens: int = 25,
    usar_cache: bool = True, ttl_segundos: float = CACHE_TTL_SEGUNDOS,
) -> list[dict]:
    """Manchetes recentes da ``empresa`` no Google News (PT-BR), com cache."""
    chave = f"{empresa}|{dias}"
    cache = _carregar_cache() if usar_cache else {}
    entrada = cache.get(chave)
    if usar_cache and entrada and (time.time() - entrada.get("ts", 0)) < ttl_segundos:
        return entrada["itens"][:max_itens]

    q = urllib.parse.quote(f"{empresa} when:{dias}d")
    url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    itens = parse_rss(requests.get(url, headers=HEADERS, timeout=20).content)[:max_itens]

    if usar_cache:
        cache[chave] = {"ts": time.time(), "itens": itens}
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return itens
