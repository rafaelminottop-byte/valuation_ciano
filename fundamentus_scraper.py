"""
Scraper do Fundamentus (www.fundamentus.com.br)
Puxa a tabela completa de ações da B3 (preço, P/EBIT etc.) e deriva o EBIT
por ação usado no valuation. Guarda um cache local (.cache/fundamentus.pkl)
para não rebaixar tudo a cada consulta.

IMPORTANTE: a primeira busca precisa de acesso à internet real.
Rode-o no seu computador: python fundamentus_scraper.py
"""

import math
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL_RESULTADO = "https://www.fundamentus.com.br/resultado.php"

HEADERS = {
    # Fundamentus bloqueia requests sem User-Agent de navegador
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
}

# A tabela do Fundamentus muda pouco durante o dia, então guardamos uma cópia
# local para não rebaixar tudo a cada consulta (e permitir uso offline).
# O nome do cache tem uma versão: ao mudar as colunas produzidas (ex.: incluir
# liquidez/crescimento), incremente CACHE_VERSAO para invalidar caches antigos.
CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_VERSAO = 3
CACHE_FILE = CACHE_DIR / f"fundamentus_v{CACHE_VERSAO}.pkl"
CACHE_TTL_SEGUNDOS = 6 * 60 * 60  # 6 horas


def _cache_valido(caminho: Path, ttl_segundos: float) -> bool:
    """True se o arquivo de cache existe e é mais novo que o TTL."""
    if not caminho.exists():
        return False
    idade = time.time() - caminho.stat().st_mtime
    return idade < ttl_segundos


def _para_numero(serie: pd.Series) -> pd.Series:
    """Converte strings no formato brasileiro ('1.234,56' ou '12,3%') para float."""
    s = serie.astype(str).str.strip()
    is_pct = s.str.contains("%")
    s = s.str.replace(".", "", regex=False)
    s = s.str.replace(",", ".", regex=False)
    s = s.str.replace("%", "", regex=False)
    numeros = pd.to_numeric(s, errors="coerce")
    numeros = numeros.where(~is_pct, numeros / 100)
    return numeros


# Colunas relevantes para o valuation (nomes conforme o site;
# se o Fundamentus renomear colunas, ajuste aqui)
COLUNAS_UTEIS = {
    "Papel": "ticker",
    "Cotação": "preco_atual",
    "P/EBIT": "p_ebit",
    "EV/EBIT": "ev_ebit",
    "Patrim. Líq": "patrimonio_liquido",
    "Div. Yield": "dividend_yield",
    "Liq.2meses": "liquidez",  # liquidez média diária (R$) — filtra ilíquidas
    "Cresc. Rec.5a": "cresc_receita_5a",  # crescimento de receita em 5 anos (proxy de crescimento)
    # Métricas de qualidade/risco (ranking):
    "ROIC": "roic",
    "ROE": "roe",
    "Mrg Ebit": "margem_ebit",
    "Dív.Líq/ Patrim.": "div_liq_patrim",
    "Liq. Corr.": "liquidez_corrente",
}


def _processar_tabela(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia colunas, converte números e deriva as colunas do valuation.

    Recebe a tabela crua do Fundamentus (com os nomes de coluna do site) e
    devolve o DataFrame pronto para o valuation. Isolado de baixar_tabela_*
    para ser testável sem acesso à internet.
    """
    presentes = {k: v for k, v in COLUNAS_UTEIS.items() if k in df.columns}
    df = df.rename(columns=presentes)

    # _para_numero só deve rodar sobre texto cru; se pd.read_html já converteu
    # o formato brasileiro (dtype numérico), converter de novo distorceria os
    # valores (ex.: 4,45 viraria 445). Checamos "não numérico" em vez de
    # "== object" para cobrir também o dtype de string do backend pyarrow.
    numericas = [
        "preco_atual", "p_ebit", "ev_ebit", "patrimonio_liquido", "liquidez",
        "cresc_receita_5a", "roic", "roe", "margem_ebit", "div_liq_patrim",
        "liquidez_corrente",
    ]
    for col in numericas:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = _para_numero(df[col])

    # EBIT por ação = Preço / P_EBIT.
    # O nº de ações se cancela no cálculo final por ação (ver valuation_engine),
    # então normalizamos para 1. A tabela resultado.php do Fundamentus não expõe
    # mais "Valor de mercado" para derivar o total de ações.
    df["ebit_por_acao"] = df["preco_atual"] / df["p_ebit"]
    df["acoes_em_circulacao"] = 1.0
    df["ebit_atual"] = df["ebit_por_acao"]

    return df


def baixar_tabela_fundamentus(
    usar_cache: bool = True, ttl_segundos: float = CACHE_TTL_SEGUNDOS
) -> pd.DataFrame:
    """Baixa e limpa a tabela completa de ações do Fundamentus.

    Se ``usar_cache`` for True e houver um cache local mais novo que
    ``ttl_segundos``, devolve o cache em vez de acessar a rede. O resultado
    baixado é sempre gravado no cache. Passe ``usar_cache=False`` (ou
    ``ttl_segundos=0``) para forçar uma atualização.
    """
    if usar_cache and _cache_valido(CACHE_FILE, ttl_segundos):
        return pd.read_pickle(CACHE_FILE)

    resp = requests.get(URL_RESULTADO, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    resp.encoding = "iso-8859-1"

    tabelas = pd.read_html(StringIO(resp.text), decimal=",", thousands=".")
    df = _processar_tabela(tabelas[0])

    if usar_cache:
        CACHE_DIR.mkdir(exist_ok=True)
        df.to_pickle(CACHE_FILE)

    return df


def buscar_dados_ticker(ticker: str, df: pd.DataFrame = None) -> dict:
    """Retorna os dados de um ticker específico prontos para o valuation_engine."""
    if df is None:
        df = baixar_tabela_fundamentus()

    linha = df[df["ticker"].str.upper() == ticker.upper()]
    if linha.empty:
        raise ValueError(f"Ticker {ticker} não encontrado no Fundamentus.")

    linha = linha.iloc[0]
    preco_atual = float(linha["preco_atual"])
    ebit_atual = float(linha["ebit_atual"])

    # A metodologia por EBIT só faz sentido com preço e EBIT positivos e
    # finitos. Empresas com EBIT negativo (P/EBIT < 0) ou zerado (P/EBIT = 0,
    # que gera divisão por zero -> infinito) produziriam valuation sem sentido.
    if not math.isfinite(preco_atual) or preco_atual <= 0:
        raise ValueError(f"Ticker {ticker.upper()} tem preço inválido no Fundamentus.")
    if not math.isfinite(ebit_atual) or ebit_atual <= 0:
        raise ValueError(
            f"Ticker {ticker.upper()} tem EBIT não-positivo (P/EBIT <= 0); "
            "o valuation por EBIT não se aplica a esta empresa."
        )

    return {
        "ticker": ticker.upper(),
        "preco_atual": preco_atual,
        "ebit_atual": ebit_atual,
        "acoes_em_circulacao": float(linha["acoes_em_circulacao"]),
    }


if __name__ == "__main__":
    print("Baixando tabela do Fundamentus...")
    df = baixar_tabela_fundamentus()
    print(f"{len(df)} ações carregadas.\n")
    print(df[["ticker", "preco_atual", "ebit_atual", "acoes_em_circulacao"]].head(10))
