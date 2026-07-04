"""
Valuation Ciano - Programa principal
Roda o valuation completo (P/L + FCD do EBIT, 3 cenários) para uma lista de
tickers, buscando os dados automaticamente no Fundamentus, e exporta tudo
para uma planilha Excel com uma aba de resumo comparativo.

Uso:
    python main.py PETR4 VALE3 ITSA4 BBAS3

Requer internet real (rode fora do sandbox do Claude).
"""

import sys

import pandas as pd

from fundamentus_scraper import baixar_tabela_fundamentus, buscar_dados_ticker
from valuation_engine import calcular_valuation_completo


def rodar_para_tickers(tickers: list[str]) -> pd.DataFrame:
    print("Baixando tabela do Fundamentus (uma vez para todos os tickers)...")
    df_fundamentus = baixar_tabela_fundamentus()

    linhas = []
    for ticker in tickers:
        try:
            dados = buscar_dados_ticker(ticker, df=df_fundamentus)
        except ValueError as e:
            print(f"  [aviso] {e}")
            continue

        resultado = calcular_valuation_completo(
            ticker=dados["ticker"],
            ebit_atual=dados["ebit_atual"],
            acoes_em_circulacao=dados["acoes_em_circulacao"],
            preco_atual=dados["preco_atual"],
        )

        linha = {
            "ticker": resultado["ticker"],
            "preco_atual": resultado["preco_atual"],
            "veredito": resultado["veredito"],
        }
        for nome_cenario, r in resultado["resultados"].items():
            linha[f"{nome_cenario}_valuation"] = round(r.valuation_final_por_acao, 2)
            linha[f"{nome_cenario}_upside_pct"] = round(r.upside_percentual, 1)
        linhas.append(linha)
        print(f"  {resultado['ticker']}: {resultado['veredito']}")

    return pd.DataFrame(linhas)


def exportar_excel(df: pd.DataFrame, caminho_saida: str = "valuation_resultado.xlsx"):
    df.to_excel(caminho_saida, index=False, sheet_name="Valuation")
    print(f"\nArquivo salvo em: {caminho_saida}")


if __name__ == "__main__":
    tickers = sys.argv[1:]
    if not tickers:
        print("Uso: python main.py TICKER1 TICKER2 TICKER3 ...")
        print("Exemplo: python main.py PETR4 VALE3 ITSA4")
        sys.exit(1)

    df_resultado = rodar_para_tickers(tickers)
    exportar_excel(df_resultado)
    print("\nResumo:")
    print(df_resultado.to_string(index=False))
