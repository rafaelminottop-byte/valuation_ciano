"""
Interface web local (Streamlit) para o valuation Ciano.

Rode com:
    streamlit run app.py

Layout alinhado ao design system da Ciano Investimentos (azul-marinho #0E2266,
destaque #3B82F6, cards de métrica, logo). Permite buscar um ticker no
Fundamentus (ou digitar Preço e P/EBIT à mão), editar as premissas e os 3
cenários, e ver o valuation por ação com o veredito automático.
"""

import base64
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from valuation_engine import (
    CENARIOS_PADRAO,
    PREMISSAS_PADRAO,
    calcular_valuation_completo,
)

# --- Paleta da marca (design system Ciano v1.1) ---
COR_BG = "#0E2266"
COR_ACCENT = "#3B82F6"
COR_LIGHT = "#CBD5E1"
COR_CARD = "#1A2F72"
COR_BORDA = "#2A3F8A"

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "ciano_logo_branco.svg"

VEREDITO_CONFIG = {
    "desconto": {"rotulo": "Desconto", "cor": "#22C55E", "emoji": "▲",
                 "texto": "O preço está abaixo de todos os cenários."},
    "sobrepreco": {"rotulo": "Sobrepreço", "cor": "#EF4444", "emoji": "▼",
                   "texto": "O preço está acima de todos os cenários."},
    "dentro_da_faixa": {"rotulo": "Dentro da faixa", "cor": "#F59E0B", "emoji": "＝",
                        "texto": "O preço está dentro da faixa dos cenários."},
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


def _fmt_brl(valor: float) -> str:
    """Formata número no padrão brasileiro: 1234.5 -> '1.234,50'."""
    return f"{valor:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")


def _logo_data_uri() -> str | None:
    if not LOGO_PATH.exists():
        return None
    b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def _injetar_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(1100px 600px at 15% -10%, #132876 0%, rgba(19,40,118,0) 55%),
                radial-gradient(900px 600px at 110% 10%, #16307f 0%, rgba(22,48,127,0) 50%),
                #0E2266;
        }
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {padding-top: 2.2rem; max-width: 1080px;}

        h1, h2, h3, h4 {color: #FFFFFF; font-weight: 800; letter-spacing: -0.01em;}

        .ciano-header {display: flex; align-items: center; gap: 18px; margin-bottom: 6px;}
        .ciano-header img {height: 46px; width: auto;}
        .ciano-sub {color: #CBD5E1; font-size: 1.02rem; margin: 0 0 4px 0;}

        .ciano-label {
            color: #3B82F6; font-size: 0.80rem; font-weight: 800;
            letter-spacing: 0.14em; text-transform: uppercase; margin: 26px 0 10px 0;
        }

        .ciano-verdict {
            display: inline-flex; align-items: center; gap: 12px;
            padding: 14px 26px; border-radius: 16px; font-weight: 800;
            font-size: 1.35rem; color: #fff; margin: 2px 0 6px 0;
        }
        .ciano-verdict small {font-weight: 500; font-size: 0.82rem; color: #E2E8F0; opacity: .9;}

        .ciano-cards {display: flex; gap: 20px; margin: 6px 0 8px 0; flex-wrap: wrap;}
        .ciano-card {
            flex: 1; min-width: 190px; background: #1A2F72;
            border: 1.5px solid #2A3F8A; border-radius: 18px; padding: 22px 24px;
        }
        .ciano-card .lbl {
            color: #CBD5E1; font-size: 0.78rem; font-weight: 700;
            letter-spacing: 0.10em; text-transform: uppercase;
        }
        .ciano-card .val {color: #FFFFFF; font-size: 2.1rem; font-weight: 800; margin: 8px 0 2px 0;}
        .ciano-card .sub {font-size: 0.95rem; font-weight: 700;}

        /* Botão primário estilo CTA da marca */
        .stButton > button {
            background: #3B82F6; color: #fff; border: none; border-radius: 30px;
            padding: 0.55rem 1.6rem; font-weight: 700; transition: filter .15s;
        }
        .stButton > button:hover {filter: brightness(1.1); color: #fff;}

        section[data-testid="stSidebar"] {background: #0B1B52; border-right: 1px solid #22336f;}
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {color: #fff;}

        div[data-testid="stDataFrame"] {border: 1px solid #2A3F8A; border-radius: 14px;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _cabecalho() -> None:
    uri = _logo_data_uri()
    logo_html = f'<img src="{uri}" alt="Ciano"/>' if uri else '<span style="color:#fff;font-weight:800;font-size:1.6rem">CIANO</span>'
    st.markdown(
        f"""
        <div class="ciano-header">{logo_html}</div>
        <h1 style="margin:2px 0 0 0;">Valuation por EBIT projetado</h1>
        <p class="ciano-sub">P/L a valor presente + FCD do EBIT, em 3 cenários · dados via Fundamentus</p>
        """,
        unsafe_allow_html=True,
    )


def _render_resultado(ticker: str, preco_atual: float, resultado: dict) -> None:
    cfg = VEREDITO_CONFIG.get(
        resultado["veredito"], {"rotulo": resultado["veredito"], "cor": COR_ACCENT, "emoji": "•", "texto": ""}
    )
    st.markdown('<div class="ciano-label">Resultado</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ciano-verdict" style="background:{cfg['cor']}22; border:1.5px solid {cfg['cor']};">
            <span style="color:{cfg['cor']}; font-size:1.5rem;">{cfg['emoji']}</span>
            <span>{ticker} · {cfg['rotulo']}</span>
            <small>R$ {_fmt_brl(preco_atual)} — {cfg['texto']}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cards por cenário
    cartoes = ""
    for nome, r in resultado["resultados"].items():
        cor_up = "#22C55E" if r.upside_percentual >= 0 else "#EF4444"
        sinal = "+" if r.upside_percentual >= 0 else ""
        cartoes += (
            f'<div class="ciano-card">'
            f'<div class="lbl">{nome}</div>'
            f'<div class="val">R$ {_fmt_brl(r.valuation_final_por_acao)}</div>'
            f'<div class="sub" style="color:{cor_up};">{sinal}{r.upside_percentual:.1f}% vs preço</div>'
            f"</div>"
        )
    st.markdown(f'<div class="ciano-cards">{cartoes}</div>', unsafe_allow_html=True)

    # Gráfico + detalhamento
    col_g, col_t = st.columns([3, 2])

    with col_g:
        st.markdown('<div class="ciano-label">Valuation × preço</div>', unsafe_allow_html=True)
        dados_g = [
            {"item": nome.capitalize(), "valor": r.valuation_final_por_acao, "tipo": "Cenário"}
            for nome, r in resultado["resultados"].items()
        ]
        dados_g.append({"item": "Preço atual", "valor": preco_atual, "tipo": "Preço"})
        dfg = pd.DataFrame(dados_g)
        chart = (
            alt.Chart(dfg)
            .mark_bar(cornerRadiusEnd=6, size=34)
            .encode(
                x=alt.X("valor:Q", title=None, axis=alt.Axis(grid=False, labelColor=COR_LIGHT)),
                y=alt.Y("item:N", sort=None, title=None, axis=alt.Axis(labelColor="#FFFFFF", labelFontSize=13)),
                color=alt.Color(
                    "tipo:N",
                    scale=alt.Scale(domain=["Cenário", "Preço"], range=[COR_ACCENT, "#F59E0B"]),
                    legend=None,
                ),
            )
            .properties(height=200)
            .configure_view(strokeWidth=0)
            .configure(background="rgba(0,0,0,0)")
        )
        st.altair_chart(chart, use_container_width=True)

    with col_t:
        st.markdown('<div class="ciano-label">Detalhamento (R$/ação)</div>', unsafe_allow_html=True)
        linhas = [
            {
                "Cenário": nome.capitalize(),
                "Método P/L": round(r.valor_metodo_pl, 2),
                "FCD EBIT": round(r.valor_fcd_ebit, 2),
                "Total": round(r.valuation_final_por_acao, 2),
            }
            for nome, r in resultado["resultados"].items()
        ]
        st.dataframe(pd.DataFrame(linhas).set_index("Cenário"), use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Valuation Ciano", page_icon="📈", layout="wide")
    _injetar_css()
    _cabecalho()

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
                f"{nome} — fase 1 (%)", value=params["crescimento_fase_1"] * 100, step=0.5, key=f"{nome}_g1"
            )
        )
        g2 = _pct_para_fracao(
            st.sidebar.number_input(
                f"{nome} — fase 2 (%)", value=params["crescimento_fase_2"] * 100, step=0.5, key=f"{nome}_g2"
            )
        )
        valores_cenarios[nome] = {"g1": g1, "g2": g2}

    # --- Entrada de dados da empresa ---
    st.markdown('<div class="ciano-label">Empresa</div>', unsafe_allow_html=True)
    modo = st.radio(
        "Origem dos dados", ["Buscar no Fundamentus", "Digitar manualmente"],
        horizontal=True, label_visibility="collapsed",
    )

    ticker = "EMPRESA"
    preco_atual = None
    ebit_por_acao = None

    if modo == "Buscar no Fundamentus":
        col_t, col_c = st.columns([2, 3])
        ticker = col_t.text_input("Ticker (B3)", value="PETR4").strip().upper()
        atualizar = col_c.checkbox(
            "Atualizar dados (ignorar cache)", value=False,
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
        _render_resultado(ticker, preco_atual, resultado)


if __name__ == "__main__":
    main()
