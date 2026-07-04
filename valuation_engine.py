"""
Motor de cálculo de valuation - Metodologia Ciano
Replica exatamente as fórmulas de valuation_ciano_config_1.json:
- Método P/L trazido a valor presente
- FCD do EBIT (anuidade crescente em duas fases)
"""

from dataclasses import dataclass


PREMISSAS_PADRAO = {
    "tma": 0.14,
    "ipca": 0.06,
    "anos_fase_1": 5,
    "anos_fase_2": 10,
    "retorno_alvo_pl": 0.06,
}

CENARIOS_PADRAO = {
    "pessimista": {"crescimento_fase_1": 0.05, "crescimento_fase_2": 0.00},
    "intermediario": {"crescimento_fase_1": 0.10, "crescimento_fase_2": 0.023},
    "otimista": {"crescimento_fase_1": 0.15, "crescimento_fase_2": 0.036},
}


@dataclass
class ResultadoCenario:
    nome: str
    valor_metodo_pl: float
    valor_fcd_ebit: float
    valuation_final_por_acao: float
    upside_percentual: float


def calcular_cenario(
    ebit_atual: float,
    acoes_em_circulacao: float,
    preco_atual: float,
    tma: float,
    retorno_alvo: float,
    crescimento_fase_1: float,
    crescimento_fase_2: float,
    anos_fase_1: int = 5,
    anos_fase_2: int = 10,
    nome_cenario: str = "",
) -> ResultadoCenario:
    g1, g2 = crescimento_fase_1, crescimento_fase_2

    # --- Método P/L trazido a valor presente ---
    lucro_projetado = ebit_atual * (1 + g1) ** anos_fase_1 * (1 + g2) ** anos_fase_2
    eps_futuro = lucro_projetado / acoes_em_circulacao
    preco_futuro = eps_futuro / retorno_alvo
    metodo_pl_valor_presente = preco_futuro / (1 + tma) ** (anos_fase_1 + anos_fase_2)

    # --- FCD do EBIT (anuidade crescente em duas fases) ---
    r1 = (1 + g1) / (1 + tma)
    fcd_ebit_fase1 = ebit_atual * (1 - r1 ** (anos_fase_1 + 1)) / (1 - r1)
    ebit_fim_fase1 = ebit_atual * r1 ** anos_fase_1

    r2 = (1 + g2) / (1 + tma)
    fcd_ebit_fase2 = ebit_fim_fase1 * r2 * (1 - r2 ** anos_fase_2) / (1 - r2)

    fcd_ebit_total = fcd_ebit_fase1 + fcd_ebit_fase2
    fcd_ebit_por_acao = fcd_ebit_total / acoes_em_circulacao

    # --- Combinação final ---
    valuation_final_por_acao = metodo_pl_valor_presente + fcd_ebit_por_acao
    upside_percentual = (valuation_final_por_acao / preco_atual - 1) * 100

    return ResultadoCenario(
        nome=nome_cenario,
        valor_metodo_pl=metodo_pl_valor_presente,
        valor_fcd_ebit=fcd_ebit_por_acao,
        valuation_final_por_acao=valuation_final_por_acao,
        upside_percentual=upside_percentual,
    )


def calcular_valuation_completo(
    ticker: str,
    ebit_atual: float,
    acoes_em_circulacao: float,
    preco_atual: float,
    tma: float = None,
    retorno_alvo: float = None,
    cenarios: dict = None,
    anos_fase_1: int = None,
    anos_fase_2: int = None,
) -> dict:
    """Roda os 3 cenários e devolve o veredito automático."""
    tma = tma if tma is not None else PREMISSAS_PADRAO["tma"]
    retorno_alvo = retorno_alvo if retorno_alvo is not None else PREMISSAS_PADRAO["retorno_alvo_pl"]
    anos_fase_1 = anos_fase_1 if anos_fase_1 is not None else PREMISSAS_PADRAO["anos_fase_1"]
    anos_fase_2 = anos_fase_2 if anos_fase_2 is not None else PREMISSAS_PADRAO["anos_fase_2"]
    cenarios = cenarios if cenarios is not None else CENARIOS_PADRAO

    resultados = {}
    for nome, params in cenarios.items():
        resultados[nome] = calcular_cenario(
            ebit_atual=ebit_atual,
            acoes_em_circulacao=acoes_em_circulacao,
            preco_atual=preco_atual,
            tma=tma,
            retorno_alvo=retorno_alvo,
            crescimento_fase_1=params["crescimento_fase_1"],
            crescimento_fase_2=params["crescimento_fase_2"],
            anos_fase_1=anos_fase_1,
            anos_fase_2=anos_fase_2,
            nome_cenario=nome,
        )

    valores = [r.valuation_final_por_acao for r in resultados.values()]
    minimo, maximo = min(valores), max(valores)
    if preco_atual > maximo:
        veredito = "sobrepreco"
    elif preco_atual < minimo:
        veredito = "desconto"
    else:
        veredito = "dentro_da_faixa"

    return {
        "ticker": ticker,
        "preco_atual": preco_atual,
        "ebit_atual": ebit_atual,
        "acoes_em_circulacao": acoes_em_circulacao,
        "resultados": resultados,
        "faixa_valuation": (minimo, maximo),
        "veredito": veredito,
    }


if __name__ == "__main__":
    # Teste rápido com os dados de PETR4 já levantados na conversa
    r = calcular_valuation_completo(
        ticker="PETR4",
        ebit_atual=143_858,           # R$ milhões (EBIT últimos 12M)
        acoes_em_circulacao=12_888.732761,  # milhões de ações
        preco_atual=37.84,
    )
    print(f"Ticker: {r['ticker']}  |  Preço atual: R$ {r['preco_atual']}")
    print(f"Veredito: {r['veredito']}")
    for nome, res in r["resultados"].items():
        print(
            f"  {nome:15s} -> P/L: R$ {res.valor_metodo_pl:7.2f}  "
            f"FCD: R$ {res.valor_fcd_ebit:7.2f}  "
            f"Final: R$ {res.valuation_final_por_acao:7.2f}  "
            f"Upside: {res.upside_percentual:+.1f}%"
        )
