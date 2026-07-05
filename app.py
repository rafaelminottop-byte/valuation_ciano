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
import html
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from teses import buscar_tese
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

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "ciano_logo_branco.png"

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
    mime = "image/svg+xml" if LOGO_PATH.suffix == ".svg" else "image/png"
    b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


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

        .ciano-brand {display: inline-block; margin-bottom: 10px;}
        .ciano-brand img {height: 56px; width: auto; display: block;}
        .ciano-invest {
            color: #4B8DEF; font-size: 0.86rem; font-weight: 500;
            letter-spacing: 0.16em; text-align: right; margin-top: -8px; padding-right: 2px;
        }
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

        .tese-setor {color: #CBD5E1; margin: -2px 0 8px 0; font-size: 0.95rem;}
        .tese-texto {color: #E2E8F0; line-height: 1.55; margin-bottom: 14px;}
        .tese-box {
            background: #1A2F72; border: 1.5px solid #2A3F8A; border-radius: 16px;
            padding: 16px 20px; height: 100%;
        }
        .tese-box .tese-h {
            font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;
            font-size: 0.80rem; margin-bottom: 8px;
        }
        .tese-box ul {margin: 0; padding-left: 18px;}
        .tese-box li {color: #E2E8F0; font-size: 0.90rem; margin-bottom: 7px; line-height: 1.42;}
        .tese-fortes {border-left: 4px solid #22C55E;}
        .tese-fortes .tese-h {color: #22C55E;}
        .tese-fracos {border-left: 4px solid #EF4444;}
        .tese-fracos .tese-h {color: #EF4444;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _cabecalho() -> None:
    uri = _logo_data_uri()
    if uri:
        marca = (
            f'<div class="ciano-brand">'
            f'<img src="{uri}" alt="Ciano"/>'
            f'<div class="ciano-invest">Investimentos</div>'
            f"</div>"
        )
    else:
        marca = '<div class="ciano-brand"><span style="color:#fff;font-weight:800;font-size:1.6rem">CIANO</span></div>'
    st.markdown(
        f"""
        {marca}
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


def _render_tese(ticker: str) -> None:
    """Mostra a tese Ciano (setor, tese, pontos fortes/fracos) se houver para o ticker."""
    tese = buscar_tese(ticker)
    if not tese:
        return

    st.markdown('<div class="ciano-label">Tese Ciano</div>', unsafe_allow_html=True)
    if tese.get("setor"):
        st.markdown(
            f'<div class="tese-setor">Setor: {html.escape(tese["setor"])}</div>',
            unsafe_allow_html=True,
        )
    if tese.get("tese"):
        st.markdown(
            f'<div class="tese-texto">{html.escape(tese["tese"])}</div>',
            unsafe_allow_html=True,
        )

    col_f, col_r = st.columns(2)
    with col_f:
        itens = "".join(f"<li>{html.escape(p)}</li>" for p in tese.get("pontos_fortes", []))
        st.markdown(
            f'<div class="tese-box tese-fortes"><div class="tese-h">Pontos fortes</div>'
            f"<ul>{itens}</ul></div>",
            unsafe_allow_html=True,
        )
    with col_r:
        itens = "".join(f"<li>{html.escape(p)}</li>" for p in tese.get("pontos_fracos", []))
        st.markdown(
            f'<div class="tese-box tese-fracos"><div class="tese-h">Pontos fracos</div>'
            f"<ul>{itens}</ul></div>",
            unsafe_allow_html=True,
        )
    st.caption("Fonte: Relatório de Teses da Ciano Investimentos.")


def _aba_empresa(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    modo = st.radio(
        "Origem dos dados", ["Buscar no Fundamentus", "Digitar manualmente"],
        horizontal=True, label_visibility="collapsed",
    )

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
                    st.session_state.empresa = {
                        "ticker": ticker,
                        "preco_atual": dados["preco_atual"],
                        "ebit_por_acao": dados["ebit_atual"] / dados["acoes_em_circulacao"],
                    }
                except Exception as e:  # noqa: BLE001 - mostra o erro na UI
                    st.error(f"Não foi possível buscar {ticker}: {e}")
    else:
        ticker = st.text_input("Nome/Ticker (rótulo)", value="EMPRESA").strip().upper()
        preco_atual = st.number_input("Preço atual (R$)", value=52.96, step=0.01, min_value=0.01)
        metodo_ebit = st.radio(
            "Como informar o EBIT?",
            ["Via P/EBIT", "Via EBIT total e nº de ações"],
            horizontal=True,
        )

        if metodo_ebit == "Via P/EBIT":
            p_ebit = st.number_input("P/EBIT", value=6.84, step=0.1)
            valido = p_ebit > 0
            ebit_por_acao = (preco_atual / p_ebit) if valido else None
            aviso = "P/EBIT deve ser positivo (EBIT negativo/zero não se aplica ao modelo)."
        else:
            col1, col2 = st.columns(2)
            ebit_total = col1.number_input("EBIT atual (12 meses)", value=100.0, step=1.0)
            acoes = col2.number_input("Nº de ações em circulação", value=1.0, step=0.01, min_value=0.0)
            st.caption(
                "Use a mesma unidade para EBIT e nº de ações (ex.: ambos em milhões). "
                "O valuation é por ação, então a unidade se cancela."
            )
            valido = ebit_total > 0 and acoes > 0
            ebit_por_acao = (ebit_total / acoes) if valido else None
            aviso = "EBIT e nº de ações devem ser positivos."

        if st.button("Calcular", type="primary"):
            if ebit_por_acao is None:
                st.error(aviso)
            else:
                st.session_state.empresa = {
                    "ticker": ticker,
                    "preco_atual": preco_atual,
                    "ebit_por_acao": ebit_por_acao,
                }

    # Resultado persistido em session_state; recalcula ao vivo com as premissas.
    emp = st.session_state.get("empresa")
    if emp:
        resultado = calcular_valuation_completo(
            ticker=emp["ticker"],
            ebit_atual=emp["ebit_por_acao"],
            acoes_em_circulacao=1.0,
            preco_atual=emp["preco_atual"],
            tma=tma,
            retorno_alvo=retorno_alvo,
            cenarios=montar_cenarios(valores_cenarios),
            anos_fase_1=anos_fase_1,
            anos_fase_2=anos_fase_2,
        )
        _render_resultado(emp["ticker"], emp["preco_atual"], resultado)
        _render_tese(emp["ticker"])


def _aba_screener(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    from fundamentus_scraper import baixar_tabela_fundamentus
    from screener import rodar_screener

    st.caption(
        "Roda o valuation em todas as ações da B3 (com EBIT positivo) e ranqueia "
        "por upside no cenário intermediário, usando as premissas da barra lateral."
    )
    c1, c2, c3 = st.columns(3)
    liq_min = c1.number_input(
        "Liquidez mín. (R$/dia)", value=1_000_000, step=500_000, min_value=0,
        help="Filtra ações pouco negociadas — sem isso o topo vira lixo ilíquido.",
    )
    cresc_min = c2.number_input(
        "Cresc. receita 5a mín. (%)", value=0.0, step=1.0,
        help="O modelo pressupõe EBIT crescente. Filtra empresas cujo crescimento "
        "de receita em 5 anos (proxy) ficou abaixo disso. Empresas sem o dado saem.",
    )
    exigir_crescimento = c2.checkbox("Exigir crescimento", value=True)
    c1.write("")
    so_desconto = c3.checkbox("Só em desconto", value=True)
    atualizar = c3.checkbox("Atualizar dados", value=False, key="scr_atualizar")

    if st.button("Rodar screener", type="primary"):
        with st.spinner("Avaliando todas as ações da B3..."):
            df = baixar_tabela_fundamentus(usar_cache=not atualizar)
            ranking = rodar_screener(
                df,
                tma=tma,
                retorno_alvo=retorno_alvo,
                cenarios=montar_cenarios(valores_cenarios),
                anos_fase_1=anos_fase_1,
                anos_fase_2=anos_fase_2,
                liquidez_minima=float(liq_min),
                crescimento_minimo=(cresc_min / 100.0) if exigir_crescimento else None,
            )
            st.session_state.screener = ranking

    ranking = st.session_state.get("screener")
    if ranking is None or ranking.empty:
        if ranking is not None:
            st.info("Nenhuma ação passou nos filtros.")
        return

    tabela = ranking.copy()
    if so_desconto:
        tabela = tabela[tabela["veredito"] == "desconto"]

    st.markdown(
        f'<div class="ciano-label">Ranking — {len(tabela)} ações</div>',
        unsafe_allow_html=True,
    )
    exibir = tabela.rename(
        columns={
            "ticker": "Ticker",
            "preco_atual": "Preço (R$)",
            "veredito": "Veredito",
            "upside_pct": "Upside (%)",
            "valuation": "Valuation (R$)",
            "cresc_receita_5a_pct": "Cresc. Rec. 5a (%)",
            "liquidez": "Liquidez (R$)",
        }
    ).set_index("Ticker")
    st.dataframe(exibir, use_container_width=True, height=560)


def _aba_carteira(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    import carteira as cart
    from fundamentus_scraper import baixar_tabela_fundamentus, buscar_dados_ticker

    st.caption("Salve empresas favoritas e avalie todas de uma vez. A carteira fica em data/carteira.json.")

    col_a, col_b = st.columns([4, 1])
    novo = col_a.text_input("Adicionar ticker", value="", key="cart_novo", placeholder="ex.: PRIO3").strip().upper()
    if col_b.button("Adicionar", type="primary") and novo:
        cart.adicionar(novo)

    tickers = cart.carregar_carteira()
    if not tickers:
        st.info("Sua carteira está vazia. Adicione tickers acima.")
        return

    rem = st.multiselect("Remover da carteira", tickers)
    if rem and st.button("Remover selecionados"):
        for t in rem:
            cart.remover(t)
        tickers = cart.carregar_carteira()

    if st.button("Avaliar carteira", type="primary"):
        with st.spinner("Avaliando carteira..."):
            df = baixar_tabela_fundamentus()
            linhas = []
            for t in tickers:
                try:
                    d = buscar_dados_ticker(t, df=df)
                    res = calcular_valuation_completo(
                        ticker=t,
                        ebit_atual=d["ebit_atual"] / d["acoes_em_circulacao"],
                        acoes_em_circulacao=1.0,
                        preco_atual=d["preco_atual"],
                        tma=tma,
                        retorno_alvo=retorno_alvo,
                        cenarios=montar_cenarios(valores_cenarios),
                        anos_fase_1=anos_fase_1,
                        anos_fase_2=anos_fase_2,
                    )
                    nomes = list(res["resultados"].keys())
                    ref = "intermediario" if "intermediario" in res["resultados"] else nomes[len(nomes) // 2]
                    r = res["resultados"][ref]
                    linhas.append(
                        {
                            "Ticker": t,
                            "Preço (R$)": round(d["preco_atual"], 2),
                            "Veredito": res["veredito"],
                            "Upside (%)": round(r.upside_percentual, 1),
                            "Valuation (R$)": round(r.valuation_final_por_acao, 2),
                        }
                    )
                except ValueError as e:
                    linhas.append({"Ticker": t, "Preço (R$)": None, "Veredito": "n/d", "Upside (%)": None, "Valuation (R$)": None, "Obs": str(e)})
            st.session_state.carteira_result = pd.DataFrame(linhas)

    resultado = st.session_state.get("carteira_result")
    if resultado is not None and not resultado.empty:
        st.markdown('<div class="ciano-label">Carteira avaliada</div>', unsafe_allow_html=True)
        st.dataframe(resultado.set_index("Ticker"), use_container_width=True)


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

    # --- Abas: empresa, screener e carteira ---
    aba_empresa, aba_screener, aba_carteira = st.tabs(
        ["🔎 Empresa", "📊 Screener B3", "⭐ Carteira"]
    )
    with aba_empresa:
        _aba_empresa(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
    with aba_screener:
        _aba_screener(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
    with aba_carteira:
        _aba_carteira(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)


if __name__ == "__main__":
    main()
