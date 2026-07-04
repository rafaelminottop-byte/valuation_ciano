"""
Scraper do Fundamentus (www.fundamentus.com.br)
Puxa a tabela completa de ações da B3, incluindo EBIT, preço e valor de mercado.
Calcula nº de ações em circulação = Valor de Mercado / Preço.

IMPORTANTE: este script precisa de acesso à internet real (fora do sandbox do Claude).
Rode-o no seu computador: python fundamentus_scraper.py
"""

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


def baixar_tabela_fundamentus() -> pd.DataFrame:
    """Baixa e limpa a tabela completa de ações do Fundamentus."""
    resp = requests.get(URL_RESULTADO, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    resp.encoding = "iso-8859-1"

    tabelas = pd.read_html(resp.text, decimal=",", thousands=".")
    df = tabelas[0]

    # Colunas relevantes para o valuation (nomes conforme o site em jul/2026;
    # se o Fundamentus renomear colunas, ajuste aqui)
    colunas_uteis = {
        "Papel": "ticker",
        "Cotação": "preco_atual",
        "P/EBIT": "p_ebit",
        "EV/EBIT": "ev_ebit",
        "Valor de mercado": "valor_mercado",
        "Patrim. Líq": "patrimonio_liquido",
        "Div. Yield": "dividend_yield",
    }
    presentes = {k: v for k, v in colunas_uteis.items() if k in df.columns}
    df = df.rename(columns=presentes)

    for col in ["preco_atual", "p_ebit", "ev_ebit", "valor_mercado", "patrimonio_liquido"]:
        if col in df.columns and df[col].dtype == object:
            df[col] = _para_numero(df[col])

    # EBIT implícito = Preço da ação / P_EBIT  (isso dá o EBIT POR AÇÃO)
    # EBIT total = EBIT por ação * nº de ações
    # nº de ações = Valor de Mercado / Preço
    df["acoes_em_circulacao"] = df["valor_mercado"] / df["preco_atual"]
    df["ebit_por_acao"] = df["preco_atual"] / df["p_ebit"]
    df["ebit_atual"] = df["ebit_por_acao"] * df["acoes_em_circulacao"]

    return df


def buscar_dados_ticker(ticker: str, df: pd.DataFrame = None) -> dict:
    """Retorna os dados de um ticker específico prontos para o valuation_engine."""
    if df is None:
        df = baixar_tabela_fundamentus()

    linha = df[df["ticker"].str.upper() == ticker.upper()]
    if linha.empty:
        raise ValueError(f"Ticker {ticker} não encontrado no Fundamentus.")

    linha = linha.iloc[0]
    return {
        "ticker": ticker.upper(),
        "preco_atual": float(linha["preco_atual"]),
        "ebit_atual": float(linha["ebit_atual"]),
        "acoes_em_circulacao": float(linha["acoes_em_circulacao"]),
    }


if __name__ == "__main__":
    print("Baixando tabela do Fundamentus...")
    df = baixar_tabela_fundamentus()
    print(f"{len(df)} ações carregadas.\n")
    print(df[["ticker", "preco_atual", "ebit_atual", "acoes_em_circulacao"]].head(10))
