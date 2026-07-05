"""
Interface web local (Streamlit) para o valuation Ciano.

Rode com:
    streamlit run app.py

Permite buscar um ticker no Fundamentus (ou digitar Preço e P/EBIT à mão),
editar as premissas e os 3 cenários, e ver o valuation por ação com o
veredito automático.
"""

import pandas as pd
import streamlit as st

from valuation_engine import (
    CENARIOS_PADRAO,
    PREMISSAS_PADRAO,
    calcular_valuation_completo,
)


VEREDITO_ROTULO = {
    "desconto": ("🟢 Desconto", "O preço está abaixo de todos os cenários."),
    "sobrepreco": ("🔴 Sobrepreço", "O preço está acima de todos os cenários."),
    "dentro_da_faixa": ("🟡 Dentro da faixa", "O preço está dentro da faixa dos cenários."),
}


def montar_cenarios(valores: dict) -> dict:
    """Monta o dict de cenários a partir dos valores editados na interface.

    ``valores`` mapeia nome_cenario -> {"g1": float, "g2": float} em fração
    (ex.: 0.10 para 10%). Função pura, isolada da UI para ser testável.
    """
    return {
        nome: {"crescimento_fase_1": v["g1"], "crescimento_fase_2": v["g2"]}
        for nome, v in valores.items()
    }


def _pct_para_fracao(valor_pct: float) -> float:
    return valor_pct / 100.0


def main() -> None:
    st.set_page_config(page_title="Valuation Ciano", page_icon="📈", layout="wide")
    st.title("📈 Valuation Ciano")
    st.caption("P/L a valor presente + FCD do EBIT, em 3 cenários. Dados via Fundamentus.")

    # --- Barra lateral: premissas e cenários editáveis ---
    st.sidebar.header("Premissas")
    tma = _pct_para_fracao(
        st.sidebar.number_input("TMA (%)", value=PREMISSAS_PADRAO["tma"] * 100, step=0.5)
    )
    retorno_alvo = _pct_para_fracao(
        st.sidebar.number_input(
            "Retorno alvo P/L (%)", value=PREMISSAS_PADRAO["retorno_alvo_pl"] * 100, step=0.5
        )
    )
    anos_fase_1 = int(
        st.sidebar.number_input("Anos fase 1", value=PREMISSAS_PADRAO["anos_fase_1"], step=1, min_value=1)
    )
    anos_fase_2 = int(
        st.sidebar.number_input("Anos fase 2", value=PREMISSAS_PADRAO["anos_fase_2"], step=1, min_value=1)
    )

    st.sidebar.header("Cenários (crescimento do EBIT)")
    valores_cenarios = {}
    for nome, params in CENARIOS_PADRAO.items():
        st.sidebar.subheader(nome.capitalize())
        g1 = _pct_para_fracao(
            st.sidebar.number_input(
                f"{nome} — fase 1 (%)",
                value=params["crescimento_fase_1"] * 100,
                step=0.5,
                key=f"{nome}_g1",
            )
        )
        g2 = _pct_para_fracao(
            st.sidebar.number_input(
                f"{nome} — fase 2 (%)",
                value=params["crescimento_fase_2"] * 100,
                step=0.5,
                key=f"{nome}_g2",
            )
        )
        valores_cenarios[nome] = {"g1": g1, "g2": g2}

    # --- Entrada de dados da empresa ---
    st.subheader("Empresa")
    modo = st.radio(
        "Origem dos dados",
        ["Buscar no Fundamentus", "Digitar manualmente"],
        horizontal=True,
    )

    ticker = "EMPRESA"
    preco_atual = None
    ebit_por_acao = None

    if modo == "Buscar no Fundamentus":
        ticker = st.text_input("Ticker (B3)", value="PETR4").strip().upper()
        atualizar = st.checkbox(
            "Atualizar dados (ignorar cache)",
            value=False,
            help="Por padrão usa o cache local (até 6h). Marque para rebaixar do Fundamentus.",
        )
        if st.button("Buscar e calcular", type="primary"):
            with st.spinner(f"Buscando {ticker} no Fundamentus..."):
                try:
                    from fundamentus_scraper import (
                        baixar_tabela_fundamentus,
                        buscar_dados_ticker,
                    )

                    df_fonte = baixar_tabela_fundamentus(usar_cache=not atualizar)
                    dados = buscar_dados_ticker(ticker, df=df_fonte)
                    preco_atual = dados["preco_atual"]
                    ebit_por_acao = dados["ebit_atual"] / dados["acoes_em_circulacao"]
                except Exception as e:  # noqa: BLE001 - mostra o erro na UI
                    st.error(f"Não foi possível buscar {ticker}: {e}")
    else:
        ticker = st.text_input("Nome/Ticker (rótulo)", value="EMPRESA").strip().upper()
        col1, col2 = st.columns(2)
        preco_atual = col1.number_input("Preço atual (R$)", value=4.45, step=0.01, min_value=0.01)
        p_ebit = col2.number_input("P/EBIT", value=2.30, step=0.1)
        if st.button("Calcular", type="primary"):
            if p_ebit <= 0:
                st.error(
                    "P/EBIT deve ser positivo. Empresas com EBIT negativo ou zero "
                    "não têm valuation por este método."
                )
                preco_atual = None
            else:
                ebit_por_acao = preco_atual / p_ebit

    # --- Cálculo e resultado ---
    if preco_atual is not None and ebit_por_acao is not None:
        resultado = calcular_valuation_completo(
            ticker=ticker,
            ebit_atual=ebit_por_acao,
            acoes_em_circulacao=1.0,
            preco_atual=preco_atual,
            tma=tma,
            retorno_alvo=retorno_alvo,
            cenarios=montar_cenarios(valores_cenarios),
            anos_fase_1=anos_fase_1,
            anos_fase_2=anos_fase_2,
        )

        rotulo, explicacao = VEREDITO_ROTULO.get(resultado["veredito"], (resultado["veredito"], ""))
        st.markdown(f"### {ticker} — {rotulo}")
        st.caption(f"Preço atual: R$ {preco_atual:,.2f}  ·  {explicacao}")

        linhas = []
        for nome, r in resultado["resultados"].items():
            linhas.append(
                {
                    "Cenário": nome.capitalize(),
                    "Método P/L (R$)": round(r.valor_metodo_pl, 2),
                    "FCD EBIT (R$)": round(r.valor_fcd_ebit, 2),
                    "Valuation por ação (R$)": round(r.valuation_final_por_acao, 2),
                    "Upside (%)": round(r.upside_percentual, 1),
                }
            )
        df = pd.DataFrame(linhas).set_index("Cenário")
        st.dataframe(df, use_container_width=True)

        grafico = df[["Valuation por ação (R$)"]].copy()
        grafico.loc["Preço atual"] = round(preco_atual, 2)
        st.bar_chart(grafico)


if __name__ == "__main__":
    main()
