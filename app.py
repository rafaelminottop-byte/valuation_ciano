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
    PREMISSAS_EUA,
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
        .block-container {padding-top: 2.2rem; max-width: 1120px;}

        /* Base tipográfica: quase tudo abaixo está em rem, então subir a raiz
           aumenta o app inteiro de forma proporcional (leitura mais confortável). */
        html {font-size: 18px;}
        .stMarkdown p, .stMarkdown li, label, .stRadio label, .stCheckbox label {font-size: 1.02rem;}
        [data-testid="stCaptionContainer"] p {font-size: 0.94rem; line-height: 1.5;}
        [data-testid="stMetricValue"] {font-size: 1.9rem;}
        [data-testid="stMetricLabel"] p {font-size: 0.92rem;}
        div[data-testid="stDataFrame"] {font-size: 1rem;}

        h1, h2, h3, h4 {color: #FFFFFF; font-weight: 800; letter-spacing: -0.01em;}

        /* Caixa única do resultado: cenários (colunas) x métodos (linhas) */
        .ciano-matriz {
            width: 100%; border-collapse: separate; border-spacing: 0;
            background: #1A2F72; border: 1.5px solid #2A3F8A;
            border-radius: 18px; overflow: hidden; margin: 8px 0 6px 0;
        }
        .ciano-matriz th, .ciano-matriz td {padding: 16px 18px; text-align: center;}
        .ciano-matriz thead th {
            background: #132876; color: #CBD5E1; font-size: 0.86rem; font-weight: 800;
            letter-spacing: 0.10em; text-transform: uppercase;
            border-bottom: 1.5px solid #2A3F8A;
        }
        .ciano-matriz tbody th {
            background: #132876; color: #FFFFFF; text-align: left;
            font-weight: 800; font-size: 1.02rem; border-right: 1.5px solid #2A3F8A;
        }
        .ciano-matriz tbody th small {
            display: block; color: #9DB2E8; font-weight: 600;
            font-size: 0.80rem; margin-top: 3px; text-transform: none; letter-spacing: 0;
        }
        .ciano-matriz tbody tr + tr th, .ciano-matriz tbody tr + tr td {
            border-top: 1.5px solid #2A3F8A;
        }
        .ciano-matriz td .v {color: #FFFFFF; font-size: 1.75rem; font-weight: 800; line-height: 1.15;}
        .ciano-matriz td .u {font-size: 0.98rem; font-weight: 700; margin-top: 4px;}
        .ciano-matriz td .na {color: #7C8DB5; font-size: 1.2rem; font-weight: 700;}
        .ciano-preco {
            color: #CBD5E1; font-size: 1.05rem; font-weight: 600; margin: 2px 0 2px 0;
        }
        .ciano-preco b {color: #FFFFFF; font-size: 1.25rem;}

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


def _celula(r, preco_atual: float, moeda: str) -> str:
    """Uma célula da matriz: preço justo + upside colorido (ou '—' se não se aplica)."""
    if r is None:
        return '<td><span class="na">—</span></td>'
    up = r.upside_percentual
    cor = "#22C55E" if up >= 0 else "#EF4444"
    sinal = "+" if up >= 0 else ""
    return (
        f'<td><div class="v">{moeda} {_fmt_brl(r.valuation_final_por_acao)}</div>'
        f'<div class="u" style="color:{cor};">{sinal}{up:.0f}%</div></td>'
    )


def _render_resultado(ticker: str, preco_atual: float, resultado_ebit: dict,
                      resultado_lpa: dict = None, moeda: str = "R$") -> None:
    """Caixa única do resultado: cenários (colunas) × métodos LPA e EBIT (linhas)."""
    cenarios = list(resultado_ebit["resultados"].keys())

    def linha(rotulo: str, sub: str, resultado: dict) -> str:
        celulas = "".join(
            _celula((resultado or {}).get("resultados", {}).get(c), preco_atual, moeda)
            for c in cenarios
        )
        return f"<tr><th>{rotulo}<small>{sub}</small></th>{celulas}</tr>"

    cabecalho = "".join(f"<th>{c.capitalize()}</th>" for c in cenarios)
    tabela = (
        '<table class="ciano-matriz">'
        f'<thead><tr><th style="text-align:left;">Preço justo por ação</th>{cabecalho}</tr></thead>'
        "<tbody>"
        + linha("Método LPA", "sobre o lucro líquido", resultado_lpa)
        + linha("Método EBIT", "sobre o EBIT", resultado_ebit)
        + "</tbody></table>"
    )

    st.markdown('<div class="ciano-label">Resultado</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ciano-preco">{ticker} — preço atual <b>{moeda} {_fmt_brl(preco_atual)}</b></div>',
        unsafe_allow_html=True,
    )
    st.markdown(tabela, unsafe_allow_html=True)
    st.caption("Cada célula: preço justo por ação e o upside sobre o preço atual.")


def _render_corpo_tese(tese: dict, titulo: str, fonte: str) -> None:
    """Renderiza setor, tese e as caixas de pontos fortes/fracos."""
    st.markdown(f'<div class="ciano-label">{titulo}</div>', unsafe_allow_html=True)
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
    st.caption(fonte)


def _render_tese(ticker: str) -> None:
    """Mostra a tese: primeiro a curada da Ciano; senão a gerada por IA (cache
    ou sob demanda via web search)."""
    from tese_ia import buscar_tese_ia_cache, gerar_tese_ia

    curada = buscar_tese(ticker)
    if curada:
        _render_corpo_tese(curada, "Tese Ciano", "Fonte: Relatório de Teses da Ciano Investimentos.")
        return

    ia = buscar_tese_ia_cache(ticker)
    if ia:
        _render_corpo_tese(ia, "Tese (gerada por IA)", "⚠️ Gerada por IA via web search — não é do relatório da Ciano. Confira antes de decidir.")
        return

    st.markdown('<div class="ciano-label">Tese</div>', unsafe_allow_html=True)
    st.caption(f"{ticker} não está no relatório da Ciano.")
    if st.button("🔎 Pesquisar tese com IA", key=f"tese_ia_{ticker}"):
        with st.spinner(f"Pesquisando {ticker} na web e sintetizando a tese..."):
            try:
                gerar_tese_ia(ticker)
                st.rerun()
            except Exception as e:  # noqa: BLE001 - mostra o erro na UI
                st.error(
                    f"Não foi possível gerar a tese: {e}. "
                    "Verifique se a variável de ambiente ANTHROPIC_API_KEY está configurada."
                )


def _busca_em_lote(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    """Avalia várias empresas de uma vez, pelos dois métodos (LPA e EBIT)."""
    from lote import avaliar_lote, separar_tickers

    mercado = st.radio("Mercado", ["B3 (Fundamentus)", "EUA (Yahoo)"], horizontal=True, key="lote_mkt")
    eua = mercado.startswith("EUA")
    exemplo = "AAPL MSFT JPM KO" if eua else "PETR4 VALE3 WEGE3 ECOR3 ITSA4"
    texto = st.text_area(
        "Tickers (separe por espaço, vírgula ou linha)", value=exemplo, height=90, key="lote_txt"
    )
    tickers = separar_tickers(texto)
    st.caption(f"{len(tickers)} ticker(s) reconhecido(s).")

    if st.button("Avaliar lote", type="primary", key="lote_run") and tickers:
        empresas, falhas = [], []
        barra = st.progress(0.0, text="Buscando dados...")
        if eua:
            from mercado_eua import buscar_ticker_eua

            for i, t in enumerate(tickers, 1):
                try:
                    empresas.append(buscar_ticker_eua(t))
                except Exception as erro:  # noqa: BLE001
                    falhas.append((t, str(erro)[:70]))
                barra.progress(i / len(tickers), text=f"Buscando... {i}/{len(tickers)}")
        else:
            from fundamentus_scraper import baixar_tabela_fundamentus, buscar_dados_ticker

            df_fonte = baixar_tabela_fundamentus()
            for i, t in enumerate(tickers, 1):
                try:
                    d = buscar_dados_ticker(t, df=df_fonte)
                    linha = df_fonte[df_fonte["ticker"].str.upper() == t]
                    p_l = pd.to_numeric(linha["p_l"], errors="coerce").iloc[0] if not linha.empty else None
                    empresas.append({
                        "ticker": t,
                        "preco_atual": d["preco_atual"],
                        "ebit_por_acao": d["ebit_atual"] / d["acoes_em_circulacao"],
                        "lpa": (d["preco_atual"] / p_l) if (p_l and p_l > 0) else None,
                        "base_calculo": d.get("base_calculo", "EBIT"),
                    })
                except Exception as erro:  # noqa: BLE001
                    falhas.append((t, str(erro)[:70]))
                barra.progress(i / len(tickers), text=f"Buscando... {i}/{len(tickers)}")
        barra.empty()

        st.session_state.lote = {
            "df": avaliar_lote(
                empresas, cenarios=montar_cenarios(valores_cenarios),
                tma=PREMISSAS_EUA["tma"] if eua else tma, retorno_alvo=retorno_alvo,
                anos_fase_1=anos_fase_1, anos_fase_2=anos_fase_2,
            ),
            "falhas": falhas,
            "moeda": "US$" if eua else "R$",
        }

    lote = st.session_state.get("lote")
    if not lote:
        return
    df, moeda = lote["df"], lote["moeda"]
    if df.empty:
        st.info("Nenhuma empresa avaliável no lote.")
    else:
        n_alav = int((df["alavancada"] == "⚠️").sum())
        st.markdown(
            f'<div class="ciano-label">Lote — {len(df)} empresas'
            + (f" · {n_alav} alavancada(s)" if n_alav else "")
            + "</div>",
            unsafe_allow_html=True,
        )
        exibir = df.rename(columns={
            "ticker": "Ticker", "nome": "Empresa", "preco": f"Preço {moeda}",
            "justo_lpa": f"Justo LPA {moeda}", "upside_lpa": "Upside LPA (%)",
            "justo_ebit": f"Justo EBIT {moeda}", "upside_ebit": "Upside EBIT (%)",
            "alavancada": "Alav.", "base": "Base", "veredito": "Veredito",
        }).set_index("Ticker")
        if exibir["Empresa"].isna().all():
            exibir = exibir.drop(columns=["Empresa"])
        st.dataframe(exibir, use_container_width=True)
        st.caption(
            "Cenário intermediário. Ordenado pelo upside do **LPA** (a leitura confiável). "
            "**⚠️ Alav.** = as óticas divergem: o EBIT vai para credores, então o *Justo EBIT* "
            "está superestimado — use o *Justo LPA*."
        )
    if lote["falhas"]:
        with st.expander(f"⚠️ {len(lote['falhas'])} não avaliada(s)"):
            for t, erro in lote["falhas"]:
                st.caption(f"**{t}** — {erro}")


def _aba_empresa(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    modo = st.radio(
        "Origem dos dados",
        ["Buscar no Fundamentus", "Buscar no Yahoo (EUA)", "Lote (várias empresas)",
         "Digitar manualmente"],
        horizontal=True, label_visibility="collapsed",
    )

    if modo == "Lote (várias empresas)":
        _busca_em_lote(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
        return

    if modo == "Buscar no Yahoo (EUA)":
        ticker = st.text_input("Ticker (EUA)", value="AAPL").strip().upper()
        st.caption(
            "Ação americana via Yahoo Finance. Usa a **TMA em dólar (10% a.a.)** — o fluxo "
            "é em USD. Bancos usam o lucro líquido no lugar do EBIT."
        )
        if st.button("Buscar e calcular", type="primary", key="btn_eua_emp"):
            with st.spinner(f"Buscando {ticker} no Yahoo Finance..."):
                try:
                    from mercado_eua import buscar_ticker_eua

                    d = buscar_ticker_eua(ticker)
                    st.session_state.empresa = {
                        "ticker": d["ticker"],
                        "preco_atual": d["preco_atual"],
                        "ebit_por_acao": d["ebit_por_acao"],
                        "lpa": d.get("lpa"),
                        "base": d["base_calculo"],
                        "mercado": "EUA",
                        "nome": d.get("nome"),
                    }
                except Exception as e:  # noqa: BLE001 - mostra o erro na UI
                    st.error(f"Não foi possível buscar {ticker}: {e}")

    elif modo == "Buscar no Fundamentus":
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
                    linha = df_fonte[df_fonte["ticker"].str.upper() == ticker]
                    p_l = pd.to_numeric(linha["p_l"], errors="coerce").iloc[0] if not linha.empty else None
                    lpa = (dados["preco_atual"] / p_l) if (p_l and p_l > 0) else None
                    st.session_state.empresa = {
                        "ticker": ticker,
                        "preco_atual": dados["preco_atual"],
                        "ebit_por_acao": dados["ebit_atual"] / dados["acoes_em_circulacao"],
                        "lpa": lpa,
                        "base": dados.get("base_calculo", "EBIT"),
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
        eua = emp.get("mercado") == "EUA"
        # Empresa americana: fluxo em dólar -> TMA em dólar (10%), não a do Brasil.
        tma_uso = PREMISSAS_EUA["tma"] if eua else tma
        moeda = "US$" if eua else "R$"
        cenarios_uso = montar_cenarios(valores_cenarios)
        comuns = dict(
            acoes_em_circulacao=1.0, preco_atual=emp["preco_atual"], tma=tma_uso,
            retorno_alvo=retorno_alvo, cenarios=cenarios_uso,
            anos_fase_1=anos_fase_1, anos_fase_2=anos_fase_2,
        )
        # O mesmo motor, rodado sobre os dois fluxos: o EBIT e o lucro líquido (LPA).
        resultado_ebit = calcular_valuation_completo(
            ticker=emp["ticker"], ebit_atual=emp["ebit_por_acao"], **comuns
        )
        lpa = emp.get("lpa")
        resultado_lpa = None
        if lpa and lpa > 0:
            resultado_lpa = calcular_valuation_completo(
                ticker=emp["ticker"], ebit_atual=lpa, **comuns
            )

        _render_resultado(emp["ticker"], emp["preco_atual"], resultado_ebit,
                          resultado_lpa, moeda=moeda)

        # Guarda-corpo: quando as duas óticas divergem muito, o EBIT está distorcido
        # por dívida (vai para credores, não para o acionista) — vale um aviso curto.
        if resultado_lpa is not None:
            from lentes import leitura_reversa

            lr = leitura_reversa(emp["preco_atual"], emp["ebit_por_acao"], lpa,
                                 cenarios_uso["intermediario"], tma_uso, retorno_alvo)
            if lr["alavancada"]:
                st.warning(
                    "⚠️ **Empresa alavancada** — boa parte do EBIT vai para credores, "
                    "não para o acionista. Confie na linha do **Método LPA**; a do EBIT "
                    "superestima o preço justo."
                )
        elif emp.get("base") != "Lucro":
            st.caption("Sem lucro por ação disponível — só a linha do EBIT se aplica.")

        if emp.get("base") == "Lucro":
            st.caption(
                "Base: lucro líquido (banco — não reporta EBIT). As duas linhas usam o "
                "lucro, então coincidem."
            )
        if eua:
            nome = emp.get("nome") or emp["ticker"]
            st.caption(f"🇺🇸 {nome} — Yahoo Finance · TMA em dólar de "
                       f"{PREMISSAS_EUA['tma']*100:.0f}% a.a. (a TMA da barra lateral vale só para a B3).")
        if not eua:
            _render_tese(emp["ticker"])


def _aba_screener(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    from fundamentus_scraper import baixar_tabela_fundamentus
    from screener import rodar_screener

    st.caption(
        "Roda o valuation em todas as ações da B3 (com EBIT positivo) e ranqueia "
        "por upside no cenário intermediário. Como o upside é ~ (15 / P-EBIT − 1), "
        "o topo tende a ser o menor P/EBIT — as de P/EBIT baixo (possível EBIT "
        "distorcido) vêm marcadas com ⚠️ para você conferir a tese."
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
    pebit_min = c1.number_input(
        "P/EBIT mín. (0 = mostrar tudo)", value=0.0, step=0.5, min_value=0.0,
        help="Por padrão mostramos tudo e só sinalizamos com ⚠️ as de P/EBIT baixo "
        "(possível EBIT distorcido). Suba o piso se quiser excluí-las do ranking.",
    )
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
                pebit_minimo=float(pebit_min),
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
            "base": "Base",
            "alerta": "Alerta",
            "preco_atual": "Preço (R$)",
            "p_ebit": "P/EBIT",
            "veredito": "Veredito",
            "upside_pct": "Upside (%)",
            "valuation": "Valuation (R$)",
            "cresc_receita_5a_pct": "Cresc. Rec. 5a (%)",
            "liquidez": "Liquidez (R$)",
        }
    ).set_index("Ticker")
    st.dataframe(exibir, use_container_width=True, height=560)

    # Salvar o resultado como lista nomeada (reusável na aba Gatilhos)
    import listas as lst

    st.markdown('<div class="ciano-label">Salvar como lista</div>', unsafe_allow_html=True)
    cs1, cs2, cs3 = st.columns([3, 2, 2])
    nome = cs1.text_input("Nome da lista", value="Screener", key="scr_nome").strip()
    topn = int(cs2.number_input(
        "Salvar top N", value=min(20, len(tabela)), min_value=1, max_value=len(tabela), step=5
    ))
    cs3.write("")
    if cs3.button("💾 Salvar lista") and nome:
        lst.salvar_lista(nome, list(tabela["ticker"].head(topn)))
        st.success(f'Lista "{nome}" salva com {topn} tickers. Use na aba Gatilhos.')


def _aba_carteira(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    import carteira as cart
    from fundamentus_scraper import baixar_tabela_fundamentus, buscar_dados_ticker

    st.caption("Salve empresas favoritas e avalie todas de uma vez. A carteira fica em data/carteira.json.")

    col_a, col_b = st.columns([4, 1])
    novo = col_a.text_input("Adicionar ticker", value="", key="cart_novo", placeholder="ex.: PRIO3").strip().upper()
    if col_b.button("Adicionar", type="primary") and novo:
        # Valida que o ticker existe no Fundamentus antes de salvar (evita typos
        # como "WEOE3" — a Weg é WEGE3 — entrarem na carteira).
        df_val = baixar_tabela_fundamentus()
        if (df_val["ticker"].str.upper() == novo).any():
            cart.adicionar(novo)
            st.success(f"{novo} adicionado à carteira.")
        else:
            st.warning(f"{novo} não foi encontrado no Fundamentus — verifique o ticker (não adicionado).")

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


def _precos_candidatos_ranking(df, liquidez_minima: float) -> dict:
    """{ticker: preço} das empresas que entram no ranking (P/EBIT > 0 e líquidas).

    Espelha os filtros de rankear_qualidade para só buscar dividendos de quem de
    fato será ranqueado (evita bater no Yahoo Finance para o mercado inteiro).
    """
    p_ebit = pd.to_numeric(df.get("p_ebit"), errors="coerce")
    preco = pd.to_numeric(df.get("preco_atual"), errors="coerce")
    liquidez = pd.to_numeric(df.get("liquidez"), errors="coerce")
    ok = (p_ebit > 0) & (preco > 0)
    if liquidez_minima > 0:
        ok &= liquidez >= liquidez_minima
    cand = df[ok]
    return dict(zip(cand["ticker"].astype(str).str.upper(), preco[ok]))


def _aba_ranking(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    from fundamentus_scraper import baixar_tabela_fundamentus
    from ranking import PESOS_PADRAO, rankear_qualidade

    st.caption(
        "Ranking combinado: solidez financeira (Dív.Líq/EBIT, Dív.Líq/Patrim., "
        "Liquidez Corr.) + qualidade (ROIC, ROE, Margem EBIT) + upside do valuation "
        "+ dividendos (DY médio dos últimos 3 anos). "
        "Bancos e empresas sem EBIT positivo ficam de fora."
    )
    c1, c2 = st.columns(2)
    liq_min = c1.number_input(
        "Liquidez mín. (R$/dia)", value=1_000_000, step=500_000, min_value=0, key="rk_liq"
    )
    atualizar = c2.checkbox("Atualizar dados", value=False, key="rk_atualizar")

    with st.expander("⚖️ Pesos das categorias (relativos)", expanded=True):
        st.caption("Solidez financeira")
        a1, a2, a3 = st.columns(3)
        p_de = a1.number_input("Dív.Líq/EBIT", value=PESOS_PADRAO["div_liq_ebit"], min_value=0.0, step=5.0, key="w_de")
        p_dp = a2.number_input("Dív.Líq/Patrim.", value=PESOS_PADRAO["div_liq_patrim"], min_value=0.0, step=5.0, key="w_dp")
        p_lc = a3.number_input("Liquidez Corr.", value=PESOS_PADRAO["liquidez_corrente"], min_value=0.0, step=5.0, key="w_lc")
        st.caption("Qualidade do negócio")
        b1, b2, b3 = st.columns(3)
        p_roic = b1.number_input("ROIC", value=PESOS_PADRAO["roic"], min_value=0.0, step=5.0, key="w_roic")
        p_roe = b2.number_input("ROE", value=PESOS_PADRAO["roe"], min_value=0.0, step=5.0, key="w_roe")
        p_mrg = b3.number_input("Margem EBIT", value=PESOS_PADRAO["margem_ebit"], min_value=0.0, step=5.0, key="w_mrg")
        st.caption("Valuation e proventos")
        d1, d2, _d3 = st.columns(3)
        p_up = d1.number_input("Upside", value=PESOS_PADRAO["upside"], min_value=0.0, step=5.0, key="w_up")
        p_div = d2.number_input(
            "Dividendos (DY 3a)", value=PESOS_PADRAO["dividendos"], min_value=0.0, step=5.0, key="w_div"
        )
        pesos = {
            "div_liq_ebit": p_de, "div_liq_patrim": p_dp, "liquidez_corrente": p_lc,
            "roic": p_roic, "roe": p_roe, "margem_ebit": p_mrg, "upside": p_up,
            "dividendos": p_div,
        }
        soma = sum(pesos.values())
        if soma <= 0:
            st.warning("Ao menos um peso precisa ser maior que zero.")
        else:
            st.caption(
                f"Solidez ≈ {round(100 * (p_de + p_dp + p_lc) / soma)}% · "
                f"Qualidade ≈ {round(100 * (p_roic + p_roe + p_mrg) / soma)}% · "
                f"Upside ≈ {round(100 * p_up / soma)}% · "
                f"Dividendos ≈ {round(100 * p_div / soma)}% do score"
            )
        if p_div > 0:
            st.caption(
                "ℹ️ Com peso em Dividendos, a 1ª execução busca o histórico de "
                "proventos no Yahoo Finance (pode demorar); depois fica em cache (24h)."
            )

    if st.button("Rodar ranking", type="primary") and sum(pesos.values()) > 0:
        with st.spinner("Avaliando solidez, qualidade e upside de todas as ações..."):
            df = baixar_tabela_fundamentus(usar_cache=not atualizar)

        dividendos = None
        if pesos.get("dividendos", 0) > 0:
            precos = _precos_candidatos_ranking(df, float(liq_min))
            with st.spinner(
                f"Buscando dividendos (3 anos) de {len(precos)} empresas no Yahoo Finance..."
            ):
                from dividendos import buscar_dy_medio_3anos

                dividendos = buscar_dy_medio_3anos(precos, usar_cache=not atualizar)

        with st.spinner("Montando o ranking..."):
            st.session_state.ranking = rankear_qualidade(
                df, pesos=pesos, liquidez_minima=float(liq_min),
                tma=tma, retorno_alvo=retorno_alvo,
                cenarios=montar_cenarios(valores_cenarios),
                anos_fase_1=anos_fase_1, anos_fase_2=anos_fase_2,
                dividendos=dividendos,
            )

    ranking = st.session_state.get("ranking")
    if ranking is None:
        return
    if ranking.empty:
        st.info("Nenhuma ação passou nos filtros.")
        return

    st.markdown(
        f'<div class="ciano-label">Ranking — {len(ranking)} empresas</div>',
        unsafe_allow_html=True,
    )
    exibir = ranking.rename(
        columns={
            "ticker": "Ticker",
            "score": "Score",
            "solidez": "Solidez",
            "qualidade": "Qualidade",
            "upside_pct": "Upside (%)",
            "dy_medio_3a_pct": "Div. 3a (%)",
            "div_liq_ebit": "Dív.Líq/EBIT",
            "roic_pct": "ROIC (%)",
            "roe_pct": "ROE (%)",
            "margem_ebit_pct": "Margem EBIT (%)",
        }
    ).set_index("Ticker")
    st.dataframe(exibir, use_container_width=True, height=560)


def _aba_eua() -> None:
    import mercado_eua as meua
    from valuation_engine import PREMISSAS_EUA

    universo = meua.carregar_universo()
    st.caption(
        f"Valuation de {len(universo)} empresas americanas (metodologia Ciano), com a "
        f"**TMA em dólar** ({PREMISSAS_EUA['tma']*100:.0f}% a.a. — o fluxo é em USD). "
        "Bancos usam o lucro líquido no lugar do EBIT. Os filtros abaixo removem os "
        "*upsides-fantasma*: empresas muito alavancadas (o EBIT vai pagar juros, não o "
        "acionista) e múltiplos anômalos (P/EBIT < 3)."
    )

    c1, c2, c3 = st.columns(3)
    dl_max = c1.number_input(
        "Dív.Líq/EBIT máx.", value=meua.DIV_LIQ_EBIT_MAX_PADRAO, min_value=0.0, step=0.5, key="eua_dl",
        help="0 = sem filtro de alavancagem. Bancos passam sempre.",
    )
    pebit_min = c2.number_input(
        "P/EBIT mín.", value=meua.P_EBIT_MINIMO_PADRAO, min_value=0.0, step=0.5, key="eua_pe",
        help="Exclui múltiplos anômalos que geram upside irreal.",
    )
    tma_eua = _pct_para_fracao(
        c3.number_input("TMA em dólar (%)", value=PREMISSAS_EUA["tma"] * 100, min_value=0.0, step=0.5, key="eua_tma")
    )
    c4, c5 = st.columns(2)
    so_crescente = c4.checkbox("Só EBIT crescente", value=False, key="eua_cresc")
    atualizar = c5.checkbox("Atualizar dados (ignora cache)", value=False, key="eua_upd")

    if st.button("Rodar valuation EUA", type="primary", key="eua_run"):
        barra = st.progress(0.0, text="Buscando dados no Yahoo Finance...")

        def _prog(feitos, total):
            barra.progress(feitos / total, text=f"Buscando dados... {feitos}/{total}")

        df = meua.buscar_dados_eua(usar_cache=not atualizar, progresso=_prog)
        barra.empty()
        if df.empty:
            st.error("Não foi possível obter dados. Tente novamente (limite do Yahoo).")
            return
        st.session_state.eua = meua.rankear_eua(
            df, div_liq_ebit_max=dl_max, p_ebit_minimo=pebit_min,
            apenas_crescente=so_crescente, tma=tma_eua,
        )

    ranking = st.session_state.get("eua")
    if ranking is None:
        st.info("Clique em **Rodar valuation EUA**. A 1ª vez baixa os demonstrativos (alguns minutos); depois fica em cache (12h).")
        return
    if ranking.empty:
        st.info("Nenhuma empresa passou nos filtros.")
        return

    n_desc = int((ranking["veredito"] == "desconto").sum())
    st.markdown(
        f'<div class="ciano-label">EUA — {len(ranking)} empresas · {n_desc} com desconto</div>',
        unsafe_allow_html=True,
    )
    exibir = ranking.rename(
        columns={
            "ticker": "Ticker", "nome": "Empresa", "setor": "Setor",
            "upside_pct": "Upside (%)", "veredito": "Veredito", "preco": "Preço US$",
            "justo": "Justo US$", "div_liq_ebit": "Dív.Líq/EBIT", "p_ebit": "P/EBIT",
            "dy_medio_3a_pct": "Div. 3a (%)", "base": "Base", "citacoes": "Convicção",
        }
    ).drop(columns=["crescente"]).set_index("Ticker")
    st.dataframe(exibir, use_container_width=True, height=560)
    st.caption("Convicção = nº de posts que citaram a empresa (proxy de consenso de mercado, do screening de origem).")


def _grafico_trajetoria(serie: list, rotulo: str, sufixo: str = "") -> None:
    """Linha da trajetória histórica de um indicador macro."""
    if not serie:
        st.caption("Sem histórico disponível para este indicador.")
        return
    dfg = pd.DataFrame(serie)
    dfg["ordem"] = range(len(dfg))
    linha = (
        alt.Chart(dfg)
        .mark_line(color=COR_ACCENT, strokeWidth=2)
        .encode(
            x=alt.X("ordem:Q", title=None, axis=alt.Axis(labels=False, grid=False, ticks=False)),
            y=alt.Y("valor:Q", title=None, scale=alt.Scale(zero=False),
                    axis=alt.Axis(grid=True, gridOpacity=0.15, labelColor=COR_LIGHT)),
            tooltip=[alt.Tooltip("data:N", title="Data"),
                     alt.Tooltip("valor:Q", title=rotulo, format=".2f")],
        )
        .properties(height=180)
        .configure_view(strokeWidth=0)
        .configure(background="rgba(0,0,0,0)")
    )
    st.altair_chart(linha, use_container_width=True)
    ini, fim = dfg.iloc[0], dfg.iloc[-1]
    st.caption(
        f"{ini['data']}: {ini['valor']:.2f}{sufixo}  →  {fim['data']}: {fim['valor']:.2f}{sufixo}"
        f"  ({len(dfg)} pontos)"
    )


def _indicador_macro(col, rotulo: str, no: dict, fmt, sufixo: str = "",
                     delta_key: str = None, ajuda: str = None) -> None:
    """Métrica + expander com a trajetória histórica."""
    d = no or {}
    val = d.get("valor")
    with col:
        delta = None
        if delta_key and d.get(delta_key) is not None:
            delta = f"{d[delta_key]:+.1f}% no ano"
        st.metric(rotulo, fmt(val) if val is not None else "—", delta=delta,
                  help=ajuda or d.get("erro"))
        with st.expander("📈 trajetória"):
            _grafico_trajetoria(d.get("serie") or [], rotulo, sufixo)


def _aba_macro() -> None:
    import macro as mac

    st.caption(
        "Indicadores macro de fontes públicas gratuitas — **Global** via Yahoo Finance, "
        "**EUA (inflação)** via BLS, **Brasil** via API do Banco Central (SGS e Focus). "
        "Clique em **📈 trajetória** sob cada indicador para ver a série histórica. "
        "Cache de 3h (as séries mudam devagar)."
    )
    if st.button("Atualizar dados macro", type="primary", key="macro_upd"):
        with st.spinner("Buscando indicadores (Yahoo + BLS + Banco Central)..."):
            st.session_state.macro = mac.buscar_macro(usar_cache=False)

    dados = st.session_state.get("macro")
    if dados is None:
        with st.spinner("Carregando indicadores..."):
            dados = mac.buscar_macro()
            st.session_state.macro = dados

    st.markdown('<div class="ciano-label">🌎 Global / Fluxo</div>', unsafe_allow_html=True)
    g = dados.get("global", {})
    c1, c2, c3, c4 = st.columns(4)
    _indicador_macro(c1, "DXY (índice dólar)", g.get("dxy"), lambda v: f"{v:.2f}",
                     delta_key="var_ano", ajuda="Dólar contra uma cesta de moedas.")
    _indicador_macro(c2, "Ouro (US$/oz)", g.get("ouro"),
                     lambda v: f"US$ {v:,.0f}".replace(",", "."), delta_key="var_ano")
    _indicador_macro(c3, "Treasury 10 anos", g.get("treasury10a"), lambda v: f"{v:.2f}%",
                     sufixo="%", delta_key="var_ano", ajuda="Juro longo dos EUA — o 'sem risco' em dólar.")
    _indicador_macro(c4, "Inflação EUA (CPI 12m)", g.get("cpi_eua"), lambda v: f"{v:.2f}%",
                     sufixo="%", ajuda="CPI cheio em 12 meses (fonte: BLS).")

    st.markdown('<div class="ciano-label">🇧🇷 Brasil — Macro</div>', unsafe_allow_html=True)
    b = dados.get("brasil", {})
    d1, d2, d3 = st.columns(3)
    _indicador_macro(d1, "Selic meta", b.get("selic"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Taxa básica de juros (meta, a.a.).")
    _indicador_macro(d2, "IPCA (12 meses)", b.get("ipca12m"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Inflação acumulada em 12 meses.")
    _indicador_macro(d3, "Dívida Bruta / PIB", b.get("divida_pib"), lambda v: f"{v:.1f}%", sufixo="%",
                     ajuda="Dívida bruta do governo geral sobre o PIB.")
    e1, e2, e3 = st.columns(3)
    _indicador_macro(e1, "Juro real ex-ante", b.get("juro_real_ex_ante"), lambda v: f"{v:.1f}%",
                     sufixo="%",
                     ajuda="((1+Selic Focus)/(1+IPCA Focus) − 1). Juro real alto pressiona a economia e o valuation.")
    _indicador_macro(e2, "Focus — IPCA", b.get("focus_ipca"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Mediana das expectativas de inflação (Focus/BC). A trajetória mostra se estão ancorando.")
    _indicador_macro(e3, "Focus — Selic", b.get("focus_selic"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Mediana das expectativas para a Selic (Focus/BC).")

    ref = (b.get("focus_ipca") or {}).get("ref")
    if ref:
        st.caption(
            f"Focus com ano de referência {ref}. Fontes: Yahoo Finance, "
            "BLS (EUA) e Banco Central do Brasil (SGS/Olinda)."
        )

    _bloco_expectativa_lucro()


def _bloco_expectativa_lucro() -> None:
    """Índice de revisão do lucro esperado das maiores empresas da B3."""
    import lucro_esperado as le
    from fundamentus_scraper import baixar_tabela_fundamentus

    st.markdown('<div class="ciano-label">📈 Expectativa de lucro (B3)</div>', unsafe_allow_html=True)
    st.caption(
        "Consenso de analistas para o lucro do próximo ano nas ações mais líquidas da B3 "
        "(Yahoo Finance). O **nível** importa pouco — o que informa é a **direção da revisão**: "
        "índice acima de 100 = expectativas elevadas nos últimos 90 dias; abaixo = cortes."
    )
    c1, c2 = st.columns([1, 2])
    n_cesta = c1.number_input("Tamanho da cesta", value=30, min_value=10, max_value=60, step=5,
                              key="lucro_n", help="As N ações mais líquidas da B3 (proxy do Ibovespa).")
    recarregar = c2.button("Calcular / atualizar expectativa de lucro", key="lucro_run")

    indice = st.session_state.get("indice_lucro")
    if recarregar or indice is None:
        df = baixar_tabela_fundamentus()
        liq = pd.to_numeric(df["liquidez"], errors="coerce")
        cesta = df.assign(_l=liq).nlargest(int(n_cesta), "_l")["ticker"].str.upper().tolist()
        barra = st.progress(0.0, text="Buscando consenso de lucro no Yahoo Finance...")
        indice = le.buscar_indice_revisao(
            [f"{t}.SA" for t in cesta],
            usar_cache=not recarregar,
            progresso=lambda i, n: barra.progress(i / n, text=f"Consenso de lucro... {i}/{n}"),
        )
        barra.empty()
        st.session_state.indice_lucro = indice

    if not indice or indice.get("valor") is None:
        st.info("Não foi possível montar o índice (sem consenso disponível).")
        return

    valor = indice["valor"]
    variacao = valor - 100
    breadth = indice.get("pct_revisao_positiva")
    m1, m2 = st.columns(2)
    m1.metric("Índice de revisão (90d)", f"{valor:.1f}", delta=f"{variacao:+.1f}% em 90 dias",
              help="Mediana da estimativa de lucro da cesta, base 100 = 90 dias atrás.")
    m2.metric("Revisões positivas", f"{breadth:.0f}% da cesta" if breadth is not None else "—",
              help="Amplitude: quantas empresas tiveram o lucro esperado elevado. "
                   "Acima de 50% = revisões predominantemente positivas.")

    if variacao > 0.5:
        st.success(f"✅ **Expectativas subindo** — analistas elevaram o lucro esperado da B3 em "
                   f"{variacao:.1f}% nos últimos 90 dias ({indice['n_empresas']} empresas).")
    elif variacao < -0.5:
        st.warning(f"⚠️ **Expectativas caindo** — analistas cortaram o lucro esperado da B3 em "
                   f"{abs(variacao):.1f}% nos últimos 90 dias ({indice['n_empresas']} empresas).")
    else:
        st.info(f"➖ **Expectativas em platô** — sem revisão relevante em 90 dias "
                f"({indice['n_empresas']} empresas). O autor do relatório chama a atenção para "
                "platôs: costumam preceder viradas.")

    with st.expander("📈 trajetória das revisões"):
        _grafico_trajetoria(indice.get("serie") or [], "Índice (base 100)")


def _aba_gatilhos() -> None:
    import carteira as cart
    import listas as lst
    from gatilhos import PERIODOS_PADRAO, TOLERANCIA_PADRAO, avaliar_gatilhos

    st.caption(
        "Avisa quando o preço chega perto da média móvel (padrão: 200 semanas — "
        "MM200 no gráfico semanal). Histórico de preços via Yahoo Finance."
    )
    fonte = st.radio(
        "Empresas a monitorar", ["Minha carteira", "Lista salva", "Digitar lista"],
        horizontal=True, label_visibility="collapsed",
    )
    if fonte == "Minha carteira":
        tickers = cart.carregar_carteira()
        if not tickers:
            st.info("Sua carteira está vazia — adicione tickers na aba Carteira, ou use 'Digitar lista'.")
            return
        st.caption("Monitorando: " + ", ".join(tickers))
    elif fonte == "Lista salva":
        nomes = lst.nomes_listas()
        if not nomes:
            st.info("Nenhuma lista salva ainda — rode o Screener e clique em 'Salvar lista'.")
            return
        nome = st.selectbox("Lista", nomes)
        tickers = lst.carregar_listas().get(nome, [])
        st.caption(f"Monitorando ({len(tickers)}): " + ", ".join(tickers))
    else:
        txt = st.text_input("Tickers separados por espaço ou vírgula", value="WEGE3 PRIO3 VALE3")
        tickers = [t for t in txt.replace(",", " ").split() if t]

    c1, c2 = st.columns(2)
    periodos = int(c1.number_input("Média (candles semanais)", value=PERIODOS_PADRAO, min_value=10, step=10))
    tol = c2.number_input("Proximidade que dispara (±%)", value=TOLERANCIA_PADRAO, min_value=0.5, step=0.5)

    if st.button("Verificar gatilhos", type="primary") and tickers:
        with st.spinner("Baixando histórico e calculando as médias..."):
            st.session_state.gatilhos = avaliar_gatilhos(tickers, periodos=periodos, tolerancia_pct=float(tol))

    res = st.session_state.get("gatilhos")
    if res is None or res.empty:
        return

    disparados = int((res["alerta"] == "🎯 na média").sum())
    st.markdown(
        f'<div class="ciano-label">Gatilhos — {disparados} na média (±{tol:.0f}%)</div>',
        unsafe_allow_html=True,
    )
    exibir = res.rename(
        columns={
            "ticker": "Ticker",
            "preco": "Preço (R$)",
            "media": "Média (R$)",
            "distancia_pct": "Distância (%)",
            "alerta": "Gatilho",
        }
    ).set_index("Ticker")
    st.dataframe(exibir, use_container_width=True)


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

    # --- Abas: empresa, screener, carteira, ranking, EUA, macro e gatilhos ---
    (aba_empresa, aba_screener, aba_carteira, aba_ranking, aba_eua,
     aba_macro, aba_gatilhos) = st.tabs(
        ["🔎 Empresa", "📊 Screener B3", "⭐ Carteira", "🏅 Ranking", "🇺🇸 EUA",
         "📉 Macro", "🔔 Gatilhos"]
    )
    with aba_empresa:
        _aba_empresa(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
    with aba_screener:
        _aba_screener(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
    with aba_carteira:
        _aba_carteira(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
    with aba_ranking:
        _aba_ranking(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
    with aba_eua:
        _aba_eua()
    with aba_macro:
        _aba_macro()
    with aba_gatilhos:
        _aba_gatilhos()


if __name__ == "__main__":
    main()
