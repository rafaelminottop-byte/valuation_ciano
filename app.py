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
import json
import re
from datetime import date
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import ibov_ciclo
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
        .block-container {padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1200px;}

        /* Base tipográfica: quase tudo abaixo está em rem, então subir a raiz
           aumenta o app inteiro de forma proporcional (leitura mais confortável). */
        html {font-size: 21px;}
        .stMarkdown p, .stMarkdown li, label, .stRadio label, .stCheckbox label {font-size: 1.02rem;}
        [data-testid="stCaptionContainer"] p {font-size: 0.92rem; line-height: 1.55; color: #A9BBE0;}
        [data-testid="stMetricValue"] {font-size: 2rem; font-weight: 800;}
        [data-testid="stMetricLabel"] p {font-size: 0.9rem; letter-spacing: 0.02em;}
        div[data-testid="stDataFrame"] {font-size: 1rem;}
        /* Campos e botões com mais respiro */
        .stTextInput input, .stNumberInput input, .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] {font-size: 1rem;}
        .stButton button {font-size: 1rem; font-weight: 700; padding: 0.55rem 1.4rem; border-radius: 10px;}
        /* Abas maiores e mais legíveis */
        .stTabs [data-baseweb="tab-list"] {gap: 6px;}
        .stTabs [data-baseweb="tab"] {
            font-size: 1rem; font-weight: 700; padding: 10px 18px; border-radius: 10px 10px 0 0;
        }
        .stExpander summary p {font-size: 0.98rem; font-weight: 600;}

        h1 {font-size: 2.4rem; margin-bottom: 0.2rem;}
        h1, h2, h3, h4 {color: #FFFFFF; font-weight: 800; letter-spacing: -0.015em;}

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

        /* Tese no formato "card" (análise própria) */
        .tese-cab {display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 6px;}
        .tese-tag {
            background: #1E3A8A; color: #93C5FD; border: 1px solid #3B82F6;
            font-size: 0.86rem; font-weight: 700; padding: 3px 12px; border-radius: 8px;
        }
        .tese-sub {
            color: #93C5FD; font-size: 0.86rem; font-weight: 800; letter-spacing: 0.10em;
            text-transform: uppercase; margin: 18px 0 6px 0;
        }
        .tese-data {
            color: #A9BBE0; font-size: 0.86rem; font-weight: 600;
            border: 1px solid #2A3F8A; border-radius: 8px; padding: 3px 10px;
        }
        .tese-resumo {
            color: #CBD5E1; font-size: 0.96rem; line-height: 1.6; margin: 8px 0 2px 0;
        }
        .noti {
            background: #16276E; border: 1px solid #2A3F8A; border-radius: 12px;
            padding: 12px 16px; margin-bottom: 9px;
        }
        .noti.hit {border-left: 4px solid #22C55E;}
        .noti a {color: #FFFFFF; font-weight: 600; font-size: 1rem; text-decoration: none; line-height: 1.4;}
        .noti a:hover {text-decoration: underline; color: #93C5FD;}
        .noti-meta {display: block; color: #9DB2E8; font-size: 0.82rem; margin-top: 5px;}
        .noti-gat {
            display: inline-block; background: #14532D; color: #4ADE80; font-size: 0.74rem;
            font-weight: 700; padding: 1px 8px; border-radius: 20px; margin: 0 5px 5px 0;
        }
        .tese-tag.gat-chip {background:#132876; color:#93C5FD; border-color:#2A3F8A; font-weight:600;}

        .ciano-brand {display: inline-block; margin-bottom: 4px;}
        .ciano-brand img {height: 104px; width: auto; display: block;}
        .ciano-invest {
            color: #4B8DEF; font-size: 0.92rem; font-weight: 500;
            letter-spacing: 0.30em; text-align: right; margin-top: -10px; padding-right: 3px;
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
        .tese-box ul {margin: 0; padding-left: 20px;}
        .tese-box li {color: #E2E8F0; font-size: 0.96rem; margin-bottom: 10px; line-height: 1.55;}
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
        <h1 style="margin:6px 0 0 0;">Valuation</h1>
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


def _celula_tma(tma) -> str:
    """Célula da TMA implícita — o retorno que o mercado exige para pagar o preço de hoje."""
    if tma is None:
        return '<td><span class="na">&gt;600%</span></td>'
    # Uma TMA implícita muito alta não é o mercado sendo irracional: é sinal de que
    # o fluxo usado não pertence ao acionista (dívida). Destacamos em vermelho.
    cor = "#EF4444" if tma > 0.40 else "#FFFFFF"
    return f'<td><div class="v" style="color:{cor};">{tma*100:.1f}%</div></td>'


def _render_resultado(ticker: str, preco_atual: float, resultado_ebit: dict,
                      resultado_lpa: dict = None, moeda: str = "R$",
                      tma_lucro: float = None, tma_ebit: float = None,
                      tem_lpa: bool = True) -> None:
    """Caixa única: cenários (colunas) × métodos LPA/EBIT (linhas) + TMA implícita."""
    cenarios = list(resultado_ebit["resultados"].keys())

    def linha(rotulo: str, sub: str, resultado: dict, tma_impl, mostrar_tma: bool) -> str:
        celulas = "".join(
            _celula((resultado or {}).get("resultados", {}).get(c), preco_atual, moeda)
            for c in cenarios
        )
        tma_td = _celula_tma(tma_impl) if mostrar_tma else '<td><span class="na">—</span></td>'
        return f"<tr><th>{rotulo}<small>{sub}</small></th>{celulas}{tma_td}</tr>"

    cabecalho = "".join(f"<th>{c.capitalize()}</th>" for c in cenarios)
    tabela = (
        '<table class="ciano-matriz">'
        '<thead><tr><th style="text-align:left;">Preço justo por ação</th>'
        f'{cabecalho}<th>TMA implícita</th></tr></thead>'
        "<tbody>"
        + linha("Método LPA", "sobre o lucro líquido", resultado_lpa, tma_lucro, tem_lpa)
        + linha("Método EBIT", "sobre o EBIT", resultado_ebit, tma_ebit, True)
        + "</tbody></table>"
    )

    st.markdown('<div class="ciano-label">Resultado</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ciano-preco">{ticker} — preço atual <b>{moeda} {_fmt_brl(preco_atual)}</b></div>',
        unsafe_allow_html=True,
    )
    st.markdown(tabela, unsafe_allow_html=True)
    st.caption(
        "Cada célula: preço justo por ação e o upside sobre o preço atual. "
        "**TMA implícita** = o retorno anual que o mercado precisa estar exigindo para a ação "
        "valer o preço de hoje (cenário intermediário) — é o desconto que ele impõe. "
        "Quando a do EBIT dispara, é sinal de que o EBIT não é do acionista."
    )


MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
            "agosto", "setembro", "outubro", "novembro", "dezembro"]
MESES_TESE_ALERTA = 6  # a partir daqui a tese merece revisão


def idade_tese_meses(data_tese: str) -> int | None:
    """Meses decorridos desde a data da tese ('julho/2026'). None se não parsear."""
    if not data_tese or "/" not in str(data_tese):
        return None
    mes_txt, _, ano_txt = str(data_tese).partition("/")
    try:
        mes = MESES_PT.index(mes_txt.strip().lower()) + 1
        ano = int(ano_txt)
    except (ValueError, IndexError):
        return None
    hoje = date.today()
    return (hoje.year - ano) * 12 + (hoje.month - mes)


def _baixar_csv_br(df, nome_base: str, key: str) -> None:
    """Botão de download em CSV que o Excel brasileiro abre em colunas certas.

    O Excel em pt-BR espera ';' como separador e ',' como decimal; o CSV padrão
    (',' + '.') faz ele jogar tudo numa coluna só (o "mesclado"). Aqui geramos no
    formato BR, com BOM UTF-8 para os acentos e o ⚠️ saírem corretos.
    """
    csv = df.reset_index().to_csv(sep=";", decimal=",", index=False)
    dados = ("﻿" + csv).encode("utf-8")
    st.download_button(
        "⬇️ Baixar CSV (Excel BR)", data=dados, file_name=f"{nome_base}.csv",
        mime="text/csv", key=key,
        help="Formato pronto para o Excel brasileiro (separador ; e decimal ,).",
    )


def _esc_md(texto: str) -> str:
    """Escapa o cifrão para o Streamlit não tratar 'R$ x ... R$ y' como LaTeX.

    O Streamlit renderiza `$...$` como fórmula matemática — e como as teses são
    cheias de "R$", trechos inteiros viravam monoespaçado verde. Aqui o cifrão
    vira literal.
    """
    return str(texto).replace("$", r"\$")


def _esc_html(texto: str) -> str:
    """Escapa HTML e o cifrão (entidade), para uso dentro de blocos HTML."""
    return html.escape(str(texto)).replace("$", "&#36;")


def _caixa_lista(titulo: str, itens: list, classe: str) -> str:
    """Caixa com lista (gatilhos / detratores)."""
    if not itens:
        return ""
    li = "".join(f"<li>{_esc_html(p)}</li>" for p in itens)
    return (f'<div class="tese-box {classe}"><div class="tese-h">{titulo}</div>'
            f"<ul>{li}</ul></div>")


def _render_tese_card(tese: dict, titulo: str, fonte: str) -> None:
    """Renderiza a tese no formato 'card' (análise própria, com cenários de 10 anos)."""
    st.markdown(f'<div class="ciano-label">{titulo}</div>', unsafe_allow_html=True)

    cabecalho = []
    if tese.get("classificacao"):
        cabecalho.append(f'<span class="tese-tag">{_esc_html(tese["classificacao"])}</span>')
    if tese.get("setor"):
        cabecalho.append(f'<span class="tese-setor">{_esc_html(tese["setor"])}</span>')
    if tese.get("data_tese"):
        cabecalho.append(f'<span class="tese-data">Tese de {_esc_html(tese["data_tese"])}</span>')
    if cabecalho:
        st.markdown(f'<div class="tese-cab">{" ".join(cabecalho)}</div>', unsafe_allow_html=True)
    idade = idade_tese_meses(tese.get("data_tese"))
    if idade is not None and idade >= MESES_TESE_ALERTA:
        st.warning(
            f"⏳ **Tese com {idade} meses** (de {tese['data_tese']}) — os números "
            "podem estar defasados. Vale revisar antes de decidir."
        )

    if tese.get("resumo_numeros"):
        st.markdown(
            f'<div class="tese-resumo">{_esc_html(tese["resumo_numeros"])}</div>',
            unsafe_allow_html=True,
        )

    for campo, rotulo in (("o_que_faz", "O que a empresa faz"), ("onde_atua", "Onde atua")):
        if tese.get(campo):
            st.markdown(
                f'<div class="tese-sub">{rotulo}</div>'
                f'<div class="tese-texto">{_esc_html(tese[campo])}</div>',
                unsafe_allow_html=True,
            )

    # Gatilhos x detratores lado a lado (substituem pontos fortes/fracos)
    col_g, col_d = st.columns(2)
    with col_g:
        st.markdown(_caixa_lista("Gatilhos", tese.get("gatilhos", []), "tese-fortes"),
                    unsafe_allow_html=True)
    with col_d:
        st.markdown(_caixa_lista("Contra a tese", tese.get("nao_gatilhos", []), "tese-fracos"),
                    unsafe_allow_html=True)

    if tese.get("numeros"):
        with st.expander("📊 Números recentes"):
            for n in tese["numeros"]:
                st.markdown(f"- {_esc_md(n)}")
    for campo, rotulo in (("endividamento", "💰 Endividamento"), ("dividendos", "💵 Dividendos")):
        if tese.get(campo):
            with st.expander(rotulo):
                st.markdown(_esc_md(tese[campo]))
    for extra in tese.get("extras", []):
        if extra.get("texto"):
            with st.expander(f"📌 {extra['titulo'].title()}"):
                st.markdown(_esc_md(extra["texto"]))

    if tese.get("projecoes"):
        st.markdown('<div class="tese-sub">Projeções — cenários de 10 anos</div>',
                    unsafe_allow_html=True)
        proj = pd.DataFrame(tese["projecoes"]).rename(columns={
            "indicador": "Indicador", "pessimista": "Pessimista",
            "intermediario": "Intermediário", "otimista": "Otimista",
        })
        st.dataframe(proj.set_index("Indicador"), use_container_width=True)
        st.caption(
            "Premissas próprias de cenário (análise da Ciano), não projeções oficiais — "
            "e independentes do valuation calculado acima."
        )
    st.caption(fonte)


def _render_corpo_tese(tese: dict, titulo: str, fonte: str) -> None:
    """Renderiza a tese. Usa o formato 'card' quando a empresa tem análise própria."""
    if tese.get("fonte") == "card":
        _render_tese_card(tese, titulo, fonte)
        return

    st.markdown(f'<div class="ciano-label">{titulo}</div>', unsafe_allow_html=True)
    if tese.get("setor"):
        st.markdown(
            f'<div class="tese-setor">Setor: {_esc_html(tese["setor"])}</div>',
            unsafe_allow_html=True,
        )
    if tese.get("tese"):
        st.markdown(
            f'<div class="tese-texto">{_esc_html(tese["tese"])}</div>',
            unsafe_allow_html=True,
        )
    col_f, col_r = st.columns(2)
    with col_f:
        st.markdown(_caixa_lista("Pontos fortes", tese.get("pontos_fortes", []), "tese-fortes"),
                    unsafe_allow_html=True)
    with col_r:
        st.markdown(_caixa_lista("Pontos fracos", tese.get("pontos_fracos", []), "tese-fracos"),
                    unsafe_allow_html=True)
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
            "tma_lpa_pct": "TMA impl. LPA (%)",
            "justo_ebit": f"Justo EBIT {moeda}", "upside_ebit": "Upside EBIT (%)",
            "tma_ebit_pct": "TMA impl. EBIT (%)",
            "alavancada": "Alav.", "base": "Base", "veredito": "Veredito",
        }).set_index("Ticker")
        if exibir["Empresa"].isna().all():
            exibir = exibir.drop(columns=["Empresa"])
        st.dataframe(exibir, use_container_width=True)
        _baixar_csv_br(exibir, "lote_valuation", "dl_lote")
        st.caption(
            "Cenário intermediário. Ordenado pelo upside do **LPA** (a leitura confiável). "
            "**TMA impl.** = o retorno anual que o mercado exige para a ação valer o preço de hoje "
            "(o desconto que ele impõe). **⚠️ Alav.** = as óticas divergem: o EBIT vai para "
            "credores, então o *Justo EBIT* está superestimado e a *TMA impl. EBIT* fica irreal — "
            "use as colunas do LPA."
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

        # TMA implícita: o retorno que o mercado exige para a ação valer o preço de hoje.
        from lentes import leitura_reversa

        lr = leitura_reversa(emp["preco_atual"], emp["ebit_por_acao"], lpa,
                             cenarios_uso["intermediario"], tma_uso, retorno_alvo)
        _render_resultado(emp["ticker"], emp["preco_atual"], resultado_ebit,
                          resultado_lpa, moeda=moeda,
                          tma_lucro=lr["tma_lucro"], tma_ebit=lr["tma_ebit"],
                          tem_lpa=resultado_lpa is not None)

        # Guarda-corpo: quando as duas óticas divergem muito, o EBIT está distorcido
        # por dívida (vai para credores, não para o acionista) — vale um aviso curto.
        if resultado_lpa is not None:
            if lr["alavancada"]:
                st.warning(
                    "⚠️ **Empresa alavancada** — boa parte do EBIT vai para credores, "
                    "não para o acionista. Confie na linha do **Método LPA**; a do EBIT "
                    "superestima o preço justo (e a TMA implícita dele fica irreal)."
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

        _render_estimado_realizado_empresa(emp["ticker"], eua)

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
    _baixar_csv_br(exibir, "screener_b3", "dl_screener")

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


CARTEIRA_PADRAO = "Minha carteira"


def _salvar_carteira(nome: str, tickers: list) -> None:
    """Grava a carteira nomeada. A padrão também espelha em carteira.json, para a
    opção 'Minha carteira' da aba Gatilhos continuar enxergando a mesma coisa."""
    import carteira as cart
    import listas as lst

    lst.salvar_lista(nome, tickers)
    if nome == CARTEIRA_PADRAO:
        cart.salvar_carteira(tickers)


def _migrar_carteira_antiga() -> None:
    """Move a carteira única legada (carteira.json) para uma carteira nomeada."""
    import carteira as cart
    import listas as lst

    antigos = cart.carregar_carteira()
    if antigos and CARTEIRA_PADRAO not in lst.carregar_listas():
        lst.salvar_lista(CARTEIRA_PADRAO, antigos)


def _aba_carteira(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    import listas as lst
    from fundamentus_scraper import baixar_tabela_fundamentus, buscar_dados_ticker
    from lote import avaliar_lote

    _migrar_carteira_antiga()

    st.caption(
        "Monte **várias carteiras** e avalie cada uma de uma vez. Elas ficam salvas em "
        "`data/listas.json` e também aparecem na aba **Gatilhos** (em 'Lista salva')."
    )

    carteiras = lst.carregar_listas()
    nomes = sorted(carteiras)
    NOVA = "➕ Nova carteira..."

    escolha = st.selectbox("Carteira", nomes + [NOVA], key="cart_sel")
    if escolha == NOVA:
        c1, c2 = st.columns([4, 1])
        nome_novo = c1.text_input("Nome da nova carteira", key="cart_nome",
                                  placeholder="ex.: Dividendos, Small caps, Long prazo").strip()
        if c2.button("Criar", type="primary") and nome_novo:
            if nome_novo in carteiras:
                st.warning(f"Já existe uma carteira chamada '{nome_novo}'.")
            else:
                _salvar_carteira(nome_novo, [])
                st.success(f"Carteira '{nome_novo}' criada.")
                st.rerun()
        return

    tickers = carteiras.get(escolha, [])

    col_a, col_b = st.columns([4, 1])
    novo = col_a.text_input("Adicionar ticker", value="", key="cart_novo",
                            placeholder="ex.: PRIO3").strip().upper()
    if col_b.button("Adicionar", type="primary") and novo:
        # Valida no Fundamentus antes de salvar (evita typos — "WEOE3" em vez de WEGE3).
        df_val = baixar_tabela_fundamentus()
        if (df_val["ticker"].str.upper() == novo).any():
            _salvar_carteira(escolha, tickers + [novo])
            st.success(f"{novo} adicionado a '{escolha}'.")
            st.rerun()
        else:
            st.warning(f"{novo} não foi encontrado no Fundamentus — verifique o ticker.")

    if not tickers:
        st.info(f"A carteira '{escolha}' está vazia. Adicione tickers acima.")
    else:
        st.caption(f"**{escolha}** — {len(tickers)} empresa(s): " + ", ".join(tickers))
        rem = st.multiselect("Remover da carteira", tickers, key="cart_rem")
        if rem and st.button("Remover selecionados"):
            _salvar_carteira(escolha, [t for t in tickers if t not in rem])
            st.rerun()

        if st.button("Avaliar carteira", type="primary"):
            with st.spinner(f"Avaliando '{escolha}'..."):
                df = baixar_tabela_fundamentus()
                empresas, falhas = [], []
                for t in tickers:
                    try:
                        d = buscar_dados_ticker(t, df=df)
                        linha = df[df["ticker"].str.upper() == t]
                        p_l = pd.to_numeric(linha["p_l"], errors="coerce").iloc[0] if not linha.empty else None
                        empresas.append({
                            "ticker": t,
                            "preco_atual": d["preco_atual"],
                            "ebit_por_acao": d["ebit_atual"] / d["acoes_em_circulacao"],
                            "lpa": (d["preco_atual"] / p_l) if (p_l and p_l > 0) else None,
                            "base_calculo": d.get("base_calculo", "EBIT"),
                        })
                    except ValueError as e:
                        falhas.append((t, str(e)[:70]))
                st.session_state.carteira_result = {
                    "nome": escolha,
                    "df": avaliar_lote(
                        empresas, cenarios=montar_cenarios(valores_cenarios), tma=tma,
                        retorno_alvo=retorno_alvo, anos_fase_1=anos_fase_1, anos_fase_2=anos_fase_2,
                    ),
                    "falhas": falhas,
                }

    with st.expander("🗑️ Excluir esta carteira"):
        st.caption(f"Remove '{escolha}' e seus tickers. Não afeta as outras carteiras.")
        if st.button(f"Excluir '{escolha}'"):
            lst.remover_lista(escolha)
            st.session_state.pop("carteira_result", None)
            st.success(f"Carteira '{escolha}' excluída.")
            st.rerun()

    res = st.session_state.get("carteira_result")
    if res and not res["df"].empty:
        st.markdown(
            f'<div class="ciano-label">{res["nome"]} — avaliada</div>', unsafe_allow_html=True
        )
        exibir = res["df"].rename(columns={
            "ticker": "Ticker", "preco": "Preço R$",
            "justo_lpa": "Justo LPA R$", "upside_lpa": "Upside LPA (%)",
            "tma_lpa_pct": "TMA impl. LPA (%)",
            "justo_ebit": "Justo EBIT R$", "upside_ebit": "Upside EBIT (%)",
            "tma_ebit_pct": "TMA impl. EBIT (%)",
            "alavancada": "Alav.", "base": "Base", "veredito": "Veredito",
        }).drop(columns=["nome"], errors="ignore").set_index("Ticker")
        st.dataframe(exibir, use_container_width=True)
        _baixar_csv_br(exibir, f"carteira_{res['nome']}", "dl_carteira")
        st.caption(
            "Cenário intermediário, ordenado pelo upside do **LPA**. **⚠️ Alav.** = o EBIT vai "
            "para credores; use as colunas do LPA."
        )
        if res["falhas"]:
            with st.expander(f"⚠️ {len(res['falhas'])} não avaliada(s)"):
                for t, erro in res["falhas"]:
                    st.caption(f"**{t}** — {erro}")


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
    _baixar_csv_br(exibir, "ranking_b3", "dl_ranking")


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
    _baixar_csv_br(exibir, "eua_valuation", "dl_eua")
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
    d1, d2, d3, d4 = st.columns(4)
    _indicador_macro(d1, "Selic meta", b.get("selic"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Taxa básica de juros (meta, a.a.).")
    _indicador_macro(d2, "IPCA (12 meses)", b.get("ipca12m"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Inflação acumulada em 12 meses.")
    _indicador_macro(d3, "CDI (12 meses)", b.get("cdi12m"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="CDI acumulado nos últimos 252 pregões, composto a partir da taxa diária anualizada (SGS 4389).")
    _indicador_macro(d4, "Dívida Bruta / PIB", b.get("divida_pib"), lambda v: f"{v:.1f}%", sufixo="%",
                     ajuda="Dívida bruta do governo geral sobre o PIB.")
    e1, e2, e3, e4 = st.columns(4)
    _indicador_macro(e1, "Juro real ex-ante", b.get("juro_real_ex_ante"), lambda v: f"{v:.1f}%",
                     sufixo="%",
                     ajuda="((1+Selic Focus)/(1+IPCA Focus) − 1). Juro real alto pressiona a economia e o valuation.")
    _indicador_macro(e2, "Focus — IPCA", b.get("focus_ipca"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Mediana das expectativas de inflação (Focus/BC). A trajetória mostra se estão ancorando.")
    _indicador_macro(e3, "Focus — Selic", b.get("focus_selic"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Mediana das expectativas para a Selic (Focus/BC).")
    _indicador_macro(e4, "Focus — PIB", b.get("focus_pib"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda="Mediana das expectativas de crescimento do PIB (Focus/BC).")

    ref = (b.get("focus_ipca") or {}).get("ref")
    if ref:
        st.caption(
            f"Focus com ano de referência {ref}. Fontes: Yahoo Finance, "
            "BLS (EUA) e Banco Central do Brasil (SGS/Olinda)."
        )

    st.markdown('<div class="ciano-label">📊 Valuation do mercado (earnings yield × NTN-B)</div>',
                unsafe_allow_html=True)
    st.caption(
        "P/L agregado do mercado (Fundamentus, ponderado por liquidez — outliers de lucro "
        "quase zero são descartados; validado contra o P/L Ibovespa do Oceans14). "
        "Earnings yield = 1/P/L. Spread contra a NTN-B de 10 anos (Tesouro Transparente) "
        "é o prêmio de risco de equity: quanto mais comprimido, menos a bolsa compensa o "
        "risco extra frente à renda fixa real — mas cruze sempre com a trajetória de lucro "
        "(bloco abaixo): spread baixo + lucro expandindo é sinal diferente de spread baixo "
        "+ lucro contraindo."
    )
    pl_m = b.get("pl_mercado", {})
    ntnb = b.get("ntnb_10a", {})
    spread = b.get("spread_ey_ntnb", {})
    f1, f2, f3, f4 = st.columns(4)
    _indicador_macro(f1, "P/L mercado (pond. liquidez)", pl_m, lambda v: f"{v:.2f}x",
                     ajuda=f"{pl_m.get('n_papeis', '—')} papéis líquidos com P/L positivo e "
                           "não-outlier (P/L < 30x) usados na ponderação.")
    _indicador_macro(f2, "Earnings yield", {"valor": pl_m.get("earnings_yield")}, lambda v: f"{v:.2f}%",
                     sufixo="%", ajuda="1 / P/L do mercado.")
    _indicador_macro(f3, "NTN-B 10 anos", ntnb, lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda=f"Vencimento usado: {ntnb.get('vencimento', '—')}. "
                           f"Data-base: {ntnb.get('data', '—')}.")
    _indicador_macro(f4, "Spread (p.p.)", spread, lambda v: f"{v:+.2f}",
                     ajuda="Earnings yield − NTN-B 10a. Positivo = bolsa paga prêmio sobre a "
                           "renda fixa real; negativo = bolsa cara frente à NTN-B.")
    if pl_m.get("erro"):
        st.warning(f"P/L do mercado indisponível: {pl_m['erro']}")
    if ntnb.get("erro"):
        st.warning(f"NTN-B indisponível: {ntnb['erro']}")

    _bloco_expectativa_lucro()


def _bloco_expectativa_lucro() -> None:
    """Índice de revisão do lucro esperado das maiores empresas da B3."""
    import lucro_esperado as le
    from fundamentus_scraper import baixar_tabela_fundamentus

    st.markdown('<div class="ciano-label">📈 Expectativa de lucro (B3)</div>', unsafe_allow_html=True)
    st.caption(
        "Olha para **frente**: os analistas estão **subindo ou cortando** a estimativa de lucro do "
        "**próximo ano** das ações mais líquidas da B3 (Yahoo Finance). O nível importa pouco — o "
        "que informa é a **direção**: índice acima de 100 = elevaram nos últimos 90 dias; abaixo = cortaram."
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
    # A: acumula um ponto por dia para a série longa crescer ao vivo
    historico = le.registrar_historico(valor)

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

    aba_90d, aba_acum = st.tabs(["📈 Trajetória 90 dias", "🗓️ Histórico acumulado"])
    with aba_90d:
        _grafico_trajetoria(indice.get("serie") or [], "Índice (base 100)")
    with aba_acum:
        if len(historico) >= 2:
            _grafico_trajetoria(
                [{"data": p["data"], "valor": p["valor"]} for p in historico],
                "Índice (base 100)")
            st.caption(
                f"{len(historico)} dias registrados. Esta série **cresce ao vivo**: cada vez que "
                "você atualiza, um ponto do dia é guardado — em semanas vira uma trajetória longa "
                "das revisões (o de 90 dias vem do Yahoo e é sempre curto)."
            )
        else:
            st.info(
                "🌱 O histórico acumulado começa hoje. Cada atualização deste indicador guarda "
                "um ponto do dia; volte nos próximos dias/semanas para ver a trajetória longa se "
                "formar. (A janela de 90 dias, ao lado, já funciona desde agora.)"
            )

    _bloco_surpresa_lucro(int(n_cesta))


def _bloco_surpresa_lucro(n_cesta: int) -> None:
    """Índice de surpresa de resultados (estimado × reportado) — histórico longo."""
    import surpresa_lucro as sl
    from fundamentus_scraper import baixar_tabela_fundamentus

    st.markdown('<div class="ciano-label">🎯 Surpresa de resultados (B3)</div>', unsafe_allow_html=True)
    st.caption(
        "Olha para **trás**: no balanço que já saiu, as empresas **bateram ou frustraram** o consenso? "
        "Mediana da surpresa (%) da cesta por trimestre, com ~2 anos de histórico (Yahoo Finance)."
    )
    st.caption(
        "ℹ️ **Futuro × passado:** este bloco (surpresa) é o **passado**; a revisão acima é o **futuro**. "
        "Podem divergir — bater uma estimativa que os analistas já cortaram é fácil. Surpresa positiva "
        "**com** revisão caindo é sinal de cautela, não de força."
    )
    if st.button("Calcular / atualizar surpresa de resultados", key="surpresa_run"):
        df = baixar_tabela_fundamentus()
        liq = pd.to_numeric(df["liquidez"], errors="coerce")
        cesta = df.assign(_l=liq).nlargest(n_cesta, "_l")["ticker"].str.upper().tolist()
        barra = st.progress(0.0, text="Buscando resultados no Yahoo Finance...")
        st.session_state.indice_surpresa = sl.buscar_indice_surpresa(
            [f"{t}.SA" for t in cesta], usar_cache=False,  # "atualizar" força recálculo
            progresso=lambda i, n: barra.progress(i / n, text=f"Resultados... {i}/{n}"),
        )
        barra.empty()

    ind = st.session_state.get("indice_surpresa")
    if not ind:
        st.info("Clique em **Calcular** para montar o índice de surpresa (histórico de ~2 anos).")
        return
    if ind.get("valor") is None:
        st.info("Sem dados de surpresa disponíveis para a cesta.")
        return

    v = ind["valor"]
    bateram = ind.get("pct_bateram")
    s1, s2 = st.columns(2)
    s1.metric("Surpresa mediana (últ. tri)", f"{v:+.1f}%",
              help="Mediana de (EPS reportado − estimado) / estimado no trimestre mais recente.")
    s2.metric("Empresas que bateram", f"{bateram:.0f}% da cesta" if bateram is not None else "—",
              help="Quantas superaram o consenso no último trimestre.")
    if v > 1:
        st.success(f"✅ A B3 **superou** o consenso no último balanço (mediana +{v:.1f}%).")
    elif v < -1:
        st.warning(f"⚠️ A B3 **frustrou** o consenso no último balanço (mediana {v:.1f}%).")
    else:
        st.info("➖ Resultados **em linha** com o consenso no último balanço.")

    aba_gap, aba_surp = st.tabs(["📉 Estimado × Realizado", "📊 Surpresa (%)"])
    with aba_gap:
        est_real = ind.get("serie_est_real") or []
        if len(est_real) >= 2:
            _grafico_estimado_realizado(est_real)
            st.caption(
                "LPA **médio** da cesta por trimestre. Onde a linha **Realizado** fica acima "
                "da **Estimado**, a B3 bateu o consenso; abaixo, frustrou. A distância entre "
                "elas é a surpresa. (O nível oscila com quais empresas reportaram — o que "
                "importa é o **gap** entre as duas.)"
            )
        else:
            st.caption("Sem dados suficientes para as duas linhas.")
    with aba_surp:
        _grafico_trajetoria(ind.get("serie") or [], "Surpresa (%)", sufixo="%")


def _render_estimado_realizado_empresa(ticker: str, eua: bool) -> None:
    """Gráfico estimado × realizado da empresa individual (consenso de analistas)."""
    yahoo = ticker if eua else f"{ticker}.SA"
    chave = f"earn_{yahoo}"
    if chave not in st.session_state:
        import surpresa_lucro as sl
        try:
            with st.spinner("Buscando estimativas de analistas no Yahoo Finance..."):
                st.session_state[chave] = sl.serie_empresa(yahoo)
        except Exception:  # noqa: BLE001
            st.session_state[chave] = []

    serie = st.session_state[chave]
    st.markdown(
        '<div class="ciano-label">Estimado × Realizado (consenso de analistas)</div>',
        unsafe_allow_html=True,
    )
    if len(serie) < 2:
        st.caption("Sem histórico de estimativas de analistas para este ticker no Yahoo Finance.")
        return
    _grafico_estimado_realizado(serie)
    st.caption(
        "Lucro por ação **estimado** pelos analistas × **reportado**, por trimestre "
        "(Yahoo Finance). Onde o realizado fica acima do estimado, a empresa bateu o consenso; "
        "abaixo, frustrou."
    )


def _grafico_estimado_realizado(serie: list) -> None:
    """Duas linhas no mesmo gráfico: LPA estimado x realizado por trimestre."""
    longo = []
    for p in serie:
        longo.append({"data": p["data"], "linha": "Estimado", "valor": p["estimado"]})
        longo.append({"data": p["data"], "linha": "Realizado", "valor": p["reportado"]})
    dfg = pd.DataFrame(longo)
    ordem = [p["data"] for p in serie]
    chart = (
        alt.Chart(dfg)
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("data:N", sort=ordem, title=None,
                    axis=alt.Axis(labelColor=COR_LIGHT, labelAngle=-45)),
            y=alt.Y("valor:Q", title="LPA médio (R$)", scale=alt.Scale(zero=False),
                    axis=alt.Axis(grid=True, gridOpacity=0.15, labelColor=COR_LIGHT)),
            color=alt.Color("linha:N", title=None,
                            scale=alt.Scale(domain=["Estimado", "Realizado"],
                                            range=["#F59E0B", COR_ACCENT]),
                            legend=alt.Legend(orient="top", labelColor="#FFFFFF")),
            tooltip=[alt.Tooltip("data:N", title="Trimestre"),
                     alt.Tooltip("linha:N", title=""),
                     alt.Tooltip("valor:Q", title="LPA médio", format=".2f")],
        )
        .properties(height=260)
        .configure_view(strokeWidth=0)
        .configure(background="rgba(0,0,0,0)")
    )
    st.altair_chart(chart, use_container_width=True)


def _card_noticia(n: dict) -> str:
    """HTML de uma notícia: título linkado, fonte, data e chips de gatilho."""
    chips = "".join(f'<span class="noti-gat">⚡ {_esc_html(g)}</span>' for g in n.get("gatilhos", []))
    meta = " · ".join(x for x in (_esc_html(n.get("fonte", "")), n.get("data", "")) if x)
    hit = " hit" if n.get("gatilhos") else ""
    link = html.escape(n.get("link", ""), quote=True)
    return (f'<div class="noti{hit}">{chips}<br>' if chips else f'<div class="noti{hit}">') + (
        f'<a href="{link}" target="_blank" rel="noopener">{_esc_html(n["titulo"])}</a>'
        f'<span class="noti-meta">{meta}</span></div>'
    )


def _aba_noticias() -> None:
    import noticias as nt
    from teses import carregar_teses

    teses = carregar_teses()
    st.caption(
        "Notícias das empresas com tese (Google News), com as manchetes ligadas aos "
        "**gatilhos** da tese destacadas com ⚡. Fonte pública; cache de 2h."
    )

    # Empresas com gatilho (formato card) primeiro; depois as demais.
    def _rotulo(tk):
        nome = teses[tk].get("nome") or tk
        marca = " 🎯" if teses[tk].get("gatilhos") else ""
        return f"{tk} — {nome}{marca}"

    ordenadas = sorted(teses, key=lambda k: (0 if teses[k].get("gatilhos") else 1, k))

    modo = st.radio("Modo", ["Por empresa", "Radar de gatilhos (todas as teses em card)"],
                    horizontal=True, key="noti_modo")
    dias = st.slider("Últimos N dias", 3, 30, 14, key="noti_dias")

    if modo == "Por empresa":
        tk = st.selectbox("Empresa", ordenadas, format_func=_rotulo, key="noti_emp")
        tese = teses[tk]
        gatilhos = tese.get("gatilhos") or []
        if gatilhos:
            chips = "".join(
                f'<span class="tese-tag gat-chip">{_esc_html(re.split(chr(8212)+"|—|–|-", g, maxsplit=1)[0].strip())}</span>'
                for g in gatilhos
            )
            st.markdown(f'<div class="tese-cab">{chips}</div>', unsafe_allow_html=True)
            st.caption("Gatilhos da tese — notícias que citam esses temas vêm marcadas com ⚡.")

        if st.button("Buscar notícias", type="primary", key="noti_run"):
            nome = tese.get("nome") or tk
            with st.spinner(f"Buscando notícias de {nome}..."):
                # Busca pelo TICKER (ex.: MOVI3): evita o ruído de nomes ambíguos
                # ("Movida", "Vale", "São Martinho") e traz só o que é da empresa.
                itens = nt.buscar_noticias(tk, dias=dias)
                st.session_state.noti = {
                    "itens": nt.marcar_e_ordenar(itens, nt.palavras_chave_gatilhos(tese)),
                    "nome": f"{tk} · {nome}",
                }

        dados = st.session_state.get("noti")
        if dados:
            itens = dados["itens"]
            n_hit = sum(1 for n in itens if n["gatilhos"])
            so_gat = st.checkbox("Só as ligadas aos gatilhos ⚡", value=False, key="noti_sog")
            mostrar = [n for n in itens if n["gatilhos"]] if so_gat else itens
            st.markdown(
                f'<div class="ciano-label">{dados["nome"]} — {len(mostrar)} manchetes'
                + (f" · {n_hit} ⚡ gatilho" if n_hit else "") + "</div>",
                unsafe_allow_html=True,
            )
            if not mostrar:
                st.info("Nenhuma notícia (tente aumentar os dias ou desmarcar o filtro).")
            for n in mostrar:
                st.markdown(_card_noticia(n), unsafe_allow_html=True)
        return

    # --- Radar: varre as teses e mostra só o que bateu gatilho ---
    escopo = st.radio(
        "Varrer", [f"Todas as teses ({len(teses)})", "Só as em card (gatilhos estruturados)"],
        horizontal=True, key="noti_escopo",
    )
    if escopo.startswith("Todas"):
        alvos = [tk for tk in ordenadas if teses[tk].get("gatilhos") or teses[tk].get("pontos_fortes")]
    else:
        alvos = [tk for tk in ordenadas if teses[tk].get("gatilhos")]
    st.caption(
        f"Varre {len(alvos)} empresas e lista só as notícias que citam um catalisador. "
        "As em formato antigo usam os pontos fortes como palavras-chave. "
        "A 1ª varredura é mais lenta (uma busca por empresa); depois fica em cache (2h)."
    )
    if st.button("Rodar radar de gatilhos", type="primary", key="noti_radar"):
        achados = []
        barra = st.progress(0.0, text="Varrendo notícias...")
        for i, tk in enumerate(alvos, 1):
            tese = teses[tk]
            nome = tese.get("nome") or tk
            try:
                itens = nt.buscar_noticias(tk, dias=dias)  # pelo ticker (sem ruído de nome)
                marcadas = nt.marcar_e_ordenar(itens, nt.palavras_chave_gatilhos(tese))
                for n in marcadas:
                    if n["gatilhos"]:
                        achados.append({**n, "empresa": f"{tk} · {nome}"})
            except Exception:  # noqa: BLE001
                pass
            barra.progress(i / len(alvos), text=f"Varrendo... {i}/{len(alvos)}")
        barra.empty()
        achados.sort(key=lambda n: -n.get("ts", 0))
        st.session_state.noti_radar_res = achados

    achados = st.session_state.get("noti_radar_res")
    if achados is not None:
        st.markdown(
            f'<div class="ciano-label">Radar — {len(achados)} manchetes de gatilho '
            f'(últimos {dias} dias)</div>', unsafe_allow_html=True,
        )
        if not achados:
            st.info("Nenhum gatilho no noticiário nesse período.")
        for n in achados:
            st.markdown(f'<div class="tese-sub" style="margin:10px 0 2px">{_esc_html(n["empresa"])}</div>',
                        unsafe_allow_html=True)
            st.markdown(_card_noticia(n), unsafe_allow_html=True)


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


def _fmt_pts(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


def _card_ciclo(titulo: str, texto: str, cor: str) -> str:
    return (
        f'<div style="flex:1 1 320px;min-width:280px;background:{COR_CARD};'
        f'border:1px solid {COR_BORDA};border-top:3px solid {cor};border-radius:10px;padding:14px;">'
        f'<div style="font-size:0.85rem;font-weight:700;margin-bottom:6px;">{html.escape(titulo)}</div>'
        f'<div style="font-size:0.8rem;opacity:0.9;line-height:1.5;">{html.escape(texto)}</div></div>'
    )


def _grafico_ciclo(d: dict) -> None:
    serie = d["serie"]
    dfg = pd.DataFrame(serie)
    dfg["ordem"] = range(len(dfg))
    ordem_por_data = {s["data"]: i for i, s in enumerate(serie)}
    piv = [
        {"ordem": ordem_por_data[p["data"]], "valor": p["valor"],
         "tipo": "Topo" if p["tipo"] == "H" else "Fundo", "data": p["data"]}
        for p in d["pivos"] if p["data"] in ordem_por_data
    ]
    eixo_x = alt.X("ordem:Q", title=None, axis=alt.Axis(labels=False, grid=False, ticks=False))
    eixo_y = alt.Y("valor:Q", title=None, scale=alt.Scale(type="log", zero=False),
                   axis=alt.Axis(grid=True, gridOpacity=0.12, labelColor=COR_LIGHT))
    linha = alt.Chart(dfg).mark_line(color=COR_ACCENT, strokeWidth=1.6).encode(
        x=eixo_x, y=eixo_y,
        tooltip=[alt.Tooltip("data:N", title="Data"), alt.Tooltip("valor:Q", title="Ibov", format=",.0f")],
    )
    camadas = linha
    if piv:
        dfp = pd.DataFrame(piv)
        pontos = alt.Chart(dfp).mark_point(size=60, filled=True).encode(
            x="ordem:Q", y=eixo_y,
            color=alt.Color("tipo:N",
                            scale=alt.Scale(domain=["Topo", "Fundo"], range=["#EF4444", "#22C55E"]),
                            legend=alt.Legend(title=None, orient="top")),
            tooltip=[alt.Tooltip("data:N", title="Data"), alt.Tooltip("tipo:N", title="Pivô"),
                     alt.Tooltip("valor:Q", title="Ibov", format=",.0f")],
        )
        camadas = linha + pontos
    chart = camadas.properties(height=320).configure_view(strokeWidth=0).configure(background="rgba(0,0,0,0)")
    st.altair_chart(chart, use_container_width=True)


def _aba_ciclo() -> None:
    st.markdown('<div class="ciano-label">Ciclo do Ibovespa</div>', unsafe_allow_html=True)
    st.caption("Onde o mercado está no ciclo — série longa do ^BVSP (Yahoo, mensal). "
               "Contexto macro pra ajudar no timing das teses.")
    with st.spinner("Carregando o histórico do Ibovespa…"):
        d = ibov_ciclo.buscar_ciclo_ibov()
    if d.get("erro"):
        st.warning(d["erro"])
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Ibovespa", _fmt_pts(d["atual"]))
    c2.metric("Máxima histórica", _fmt_pts(d["ath"]))
    est = d["esticamento"]
    c3.metric("Esticamento vs média 24m", f"{est['desvio_pct']:+.0f}%", help=est["nota"])

    st.markdown(
        '<div style="display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 4px;">'
        + _card_ciclo("🔵 Ciclo grande (anos)", d["grande"], COR_ACCENT)
        + _card_ciclo("🟢 Ciclo pequeno (meses)", d["pequeno"], "#22C55E")
        + "</div>",
        unsafe_allow_html=True,
    )

    p = d.get("projecao")
    if p:
        cor_v = ("#EF4444" if "tardia" in p["veredito"]
                 else "#F59E0B" if p["veredito"] == "Avançada" else "#22C55E")
        st.markdown(
            f'<div style="background:{COR_CARD};border:1px solid {COR_BORDA};'
            f'border-left:5px solid {cor_v};border-radius:10px;padding:14px;margin:8px 0;">'
            f'<div style="font-size:0.78rem;opacity:0.7;text-transform:uppercase;letter-spacing:1px;">'
            f'Maturidade da alta atual</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:{cor_v};">{html.escape(p["veredito"])}</div>'
            f'<div style="margin-top:8px;font-size:0.82rem;line-height:1.5;">'
            f'<b>Upside:</b> {html.escape(p["upside_txt"])}</div>'
            f'<div style="margin-top:4px;font-size:0.82rem;line-height:1.5;">'
            f'<b>Tempo:</b> {html.escape(p["tempo_txt"])}</div></div>',
            unsafe_allow_html=True,
        )
        st.caption("Upside e tempo = estimativa estatística das altas modernas (pós-2008), "
                   "não previsão. Índice na máxima e esticado = risco de topo maior.")

    _grafico_ciclo(d)

    maiores = [l for l in d["legs"] if abs(l["amp"]) >= 15]
    if maiores:
        st.markdown('<div class="ciano-label">Ciclos maiores (≥15%)</div>', unsafe_allow_html=True)
        linhas = [
            {" ": "⬆️" if l["tipo"] == "alta" else "⬇️",
             "Trecho": f"{l['de']} → {l['ate']}",
             "Duração": f"{l['meses']} m",
             "Preço": f"{_fmt_pts(l['p0'])} → {_fmt_pts(l['p1'])}",
             "Amplitude": f"{l['amp']:+.0f}%"}
            for l in maiores
        ]
        # última(s) linha(s): projeção para fins de 2027 e 2028 pelo ritmo histórico
        proj = d.get("projecao") or {}
        for a in proj.get("anos", []):
            linhas.append({
                " ": "🔮",
                "Trecho": f"Proj. dez/{a['ano']} (base → forte)",
                "Duração": f"+{a['meses_frente']} m",
                "Preço": f"{_fmt_pts(a['base'])} → {_fmt_pts(a['forte'])}",
                "Amplitude": f"{a['up_base']:+.0f}% → {a['up_forte']:+.0f}%",
            })
        st.dataframe(pd.DataFrame(linhas), hide_index=True, use_container_width=True)
        if proj.get("anos"):
            st.caption(
                f"🔮 Projeção estatística (não previsão): compõe o Ibov atual pelo crescimento "
                f"anualizado das altas modernas — base ~{proj['g_anual_base']:.0f}%/ano "
                f"(mediana), forte ~{proj['g_anual_forte']:.0f}%/ano (máx). "
                "Ignora recessões/choques; quanto mais longe, mais frágil."
            )
    st.caption("Leitura educacional de estrutura de mercado, não recomendação. "
               "Pivôs = extremos numa janela de ~9 meses.")


DATA_CICLOS = Path(__file__).resolve().parent / "data" / "ciclos_historicos.json"
_COR_ALAVANCA = {"verde": "#22C55E", "amarelo": "#EAB308", "vermelho": "#EF4444"}
_EMOJI_ALAVANCA = {"verde": "🟢", "amarelo": "🟡", "vermelho": "🔴"}


def _cor_alavanca(chave: str) -> str:
    return _COR_ALAVANCA.get((chave or "").split("-")[0], "#64748B")


def _emoji_alavanca(chave: str) -> str:
    return _EMOJI_ALAVANCA.get((chave or "").split("-")[0], "⚪")


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _cenarios_dados_vivos() -> dict:
    """Puxa os números de HOJE das 4 alavancas: P/L, dispersão small×large, juro."""
    out = {"pl": None, "ey": None, "pl_grande": None, "pl_small": None,
           "selic": None, "juro_real": None}
    try:
        import fundamentus_scraper as fs
        df = fs.baixar_tabela_fundamentus()
        r = fs.pl_agregado_ponderado(df)
        out["pl"], out["ey"] = r.get("valor"), r.get("earnings_yield")
        pl = pd.to_numeric(df["p_l"], errors="coerce")
        liq = pd.to_numeric(df["liquidez"], errors="coerce")
        val = (pl > 0) & (pl < 30) & (liq > 0)
        d = pd.DataFrame({"pl": pl[val], "liq": liq[val],
                          "ticker": df["ticker"][val]}).sort_values("liq", ascending=False)
        grandes = d.head(40)
        smalls = d[(d["liq"] > 50000) & (~d["ticker"].isin(grandes["ticker"]))]
        out["pl_grande"] = float(grandes["pl"].median())
        if len(smalls):
            out["pl_small"] = float(smalls["pl"].median())
    except Exception:  # noqa: BLE001
        pass
    try:
        import macro as mac
        b = mac.buscar_macro().get("brasil", {})

        def _val(x):
            return x.get("valor") if isinstance(x, dict) else x
        out["selic"], out["juro_real"] = _val(b.get("selic")), _val(b.get("juro_real_ex_ante"))
    except Exception:  # noqa: BLE001
        pass
    return out


def _card_alavanca(nome: str, cor_chave: str, valor: str, desc: str) -> str:
    cor = _cor_alavanca(cor_chave)
    return (
        f'<div style="flex:1 1 210px;min-width:190px;background:{COR_CARD};'
        f'border:1px solid {COR_BORDA};border-left:4px solid {cor};border-radius:10px;padding:12px 14px;">'
        f'<div style="font-size:0.7rem;letter-spacing:.05em;text-transform:uppercase;opacity:.65;">{html.escape(nome)}</div>'
        f'<div style="font-size:1.15rem;font-weight:800;color:{cor};margin:2px 0 4px;">{html.escape(valor)}</div>'
        f'<div style="font-size:0.72rem;opacity:0.85;line-height:1.4;">{html.escape(desc)}</div></div>'
    )


def _aba_cenarios() -> None:
    st.markdown('<div class="ciano-label">Cenários — onde estamos no ciclo</div>', unsafe_allow_html=True)
    st.caption("As 4 alavancas que movem a bolsa (lucro, múltiplo, juro, fluxo), o estado de hoje "
               "e o case base histórico desde 1994. Decidir por analogia, não por previsão.")
    try:
        base = json.loads(DATA_CICLOS.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        st.error("Não consegui ler data/ciclos_historicos.json.")
        return

    viv = _cenarios_dados_vivos()
    hoje = next((e for e in base.get("episodios", []) if e["id"] == "2022-hoje"), {})
    alav = hoje.get("alavancas", {})

    # --- as 4 alavancas hoje ---
    st.markdown('<div class="ciano-label" style="margin-top:6px;">🎛️ As 4 alavancas hoje</div>',
                unsafe_allow_html=True)
    pl_txt = f"P/L {viv['pl']:.1f}x" if viv.get("pl") else "P/L —"
    ey_txt = f" · EY {viv['ey']:.1f}%" if viv.get("ey") else ""
    if viv.get("pl_small") and viv.get("pl_grande"):
        mult_desc = (f"Grandes ~{viv['pl_grande']:.1f}x (no justo) vs small ~{viv['pl_small']:.1f}x "
                     "(baratas). O 'barato' está nas small caps.")
    else:
        mult_desc = "P/L do mercado ponderado por liquidez (Fundamentus)."
    juro_txt = f"Selic {viv['selic']:.1f}%" if viv.get("selic") else "Selic —"
    juro_desc = (f"Juro real ~{viv['juro_real']:.1f}%. " if viv.get("juro_real") else "") + \
        "A alavanca-mãe: sem ela ceder, as outras não ignitam."
    cards = (
        _card_alavanca("Lucro / EBIT", alav.get("lucro", ""), "Forte", "Combustível real da alta; verificável nos balanços.")
        + _card_alavanca("Múltiplo", alav.get("multiplo", ""), pl_txt + ey_txt.strip(), mult_desc)
        + _card_alavanca("Juro", alav.get("juro", ""), juro_txt, juro_desc)
        + _card_alavanca("Fluxo / alocação", alav.get("fluxo", ""), "Sub-alocado", "Local pouco em bolsa; energia potencial que espera o juro cair.")
    )
    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:12px;">{cards}</div>', unsafe_allow_html=True)

    # --- os dois cenários condicionais ---
    st.markdown('<div class="ciano-label" style="margin-top:16px;">🔀 Os dois caminhos (o juro decide)</div>',
                unsafe_allow_html=True)
    dois = (
        _card_ciclo(
            "🟢 Se a Selic ceder → análogo 2016-19",
            "Múltiplo expande + local roda pra bolsa + small caps lideram. Você tem uma alavanca A MAIS que 2016 "
            "(o lucro já forte), então seria um 2016-19 turbinado. Foi quando o Ibov fez +186%.",
            "#22C55E")
        + _card_ciclo(
            "🔴 Se travar em ~14% → análogo 2011-15",
            "CDI paga demais, o local não sai da renda fixa, o múltiplo não expande. Nem lucro forte nem bolsa "
            "'vazia' seguram — foi a 'década perdida' 2011-2016. Barato pode ficar barato por anos.",
            "#EF4444")
    )
    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:12px;">{dois}</div>', unsafe_allow_html=True)
    st.caption("Fiel da balança = regime fiscal do próximo governo (eleição out/2026). Não é 'risco lateral' — "
               "é a variável dominante da tese.")

    # --- case base histórico ---
    st.markdown('<div class="ciano-label" style="margin-top:16px;">📚 Case base — ciclos desde 1994</div>',
                unsafe_allow_html=True)
    dfh = pd.DataFrame([
        {"Período": e["periodo"], "Governo": e["governo"],
         "Lucro": _emoji_alavanca(e["alavancas"].get("lucro", "")),
         "Múlt.": _emoji_alavanca(e["alavancas"].get("multiplo", "")),
         "Juro": _emoji_alavanca(e["alavancas"].get("juro", "")),
         "Fluxo": _emoji_alavanca(e["alavancas"].get("fluxo", "")),
         "O que o Ibov fez depois": e.get("ibov_desfecho", "")}
        for e in base.get("episodios", [])
    ])
    st.dataframe(dfh, hide_index=True, use_container_width=True)
    st.caption("🟢 a favor · 🟡 neutro · 🔴 contra. Padrão histórico: **nenhum bull secular com juro subindo** — "
               "a ignição foi sempre a Selic cedendo.")

    with st.expander("💡 Lições de cada episódio (o que decidiu)"):
        for e in base.get("episodios", []):
            st.markdown(f"**{e['periodo']} — {e['governo']}**  \n{e.get('licao', '')}")

    # --- vetores vivos ---
    vet = base.get("vetores_em_observacao_2026", {})
    if vet:
        st.markdown('<div class="ciano-label" style="margin-top:10px;">🛰️ Vetores em observação (2026)</div>',
                    unsafe_allow_html=True)
        for chave, titulo in [("dispersao_small_vs_large", "Small caps ainda baratas"),
                              ("ia_disrupcao", "IA — choque exógeno de dois gumes"),
                              ("eleicao_fiscal_2026", "Eleição / fiscal 2026")]:
            v = vet.get(chave)
            if not v:
                continue
            with st.expander(f"🔹 {titulo}"):
                for k, val in v.items():
                    if k == "nota":
                        continue
                    st.markdown(f"- **{k.replace('_', ' ').capitalize()}:** {val}")

    st.caption("Leitura estruturada de tese, não recomendação de investimento. Dados de hoje: Fundamentus "
               "(P/L) e Banco Central (juro); histórico preenchido aos poucos.")


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

    # --- Abas: empresa, screener, carteira, ranking, EUA, macro, notícias e gatilhos ---
    (aba_empresa, aba_screener, aba_carteira, aba_ranking, aba_eua,
     aba_macro, aba_ciclo, aba_cenarios, aba_noticias, aba_gatilhos) = st.tabs(
        ["🔎 Empresa", "📊 Screener B3", "⭐ Carteira", "🏅 Ranking", "🇺🇸 EUA",
         "📉 Macro", "🔄 Ciclo", "🔀 Cenários", "📰 Notícias", "🔔 Gatilhos"]
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
    with aba_ciclo:
        _aba_ciclo()
    with aba_cenarios:
        _aba_cenarios()
    with aba_noticias:
        _aba_noticias()
    with aba_gatilhos:
        _aba_gatilhos()


if __name__ == "__main__":
    main()
