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
# Setores do Yahoo (inglês) -> português, para o screener de ações americanas.
_SETORES_PT = {
    "Technology": "Tecnologia",
    "Industrials": "Indústria",
    "Financial Services": "Financeiro",
    "Consumer Cyclical": "Consumo cíclico",
    "Healthcare": "Saúde",
    "Consumer Defensive": "Consumo defensivo",
    "Communication Services": "Comunicação",
    "Energy": "Energia",
    "Real Estate": "Imobiliário",
    "Basic Materials": "Materiais básicos",
    "Utilities": "Utilidades (energia/água)",
}

# Tema claro ("cinza neutro" estilo Oceans14): marinho + cinza + branco dominam,
# dourado só em detalhe, verde/vermelho só para alta/baixa.
COR_BG = "#F4F7F8"       # fundo da página (quase branco, como o site)
COR_ACCENT = "#0FA3B8"   # ciano legível (linhas de gráfico, links/hover)
COR_CIANO = "#3FD0E0"    # ciano vivo da marca (SÓ preenchimento/destaque, nunca texto)
COR_LIGHT = "#334155"    # texto/labels de eixo em gráficos claros (escuro p/ contraste)
COR_CARD = "#FFFFFF"     # card branco
COR_BORDA = "#E2E8F2"    # borda clara
COR_INK = "#0B1F2A"      # texto principal (marinho-teal escuro, como o site)
COR_INK2 = "#0B1F2A"     # texto secundário
COR_MUT = "#4F6470"      # muted (ainda bem legível)
COR_NAVY = "#0B1F2A"     # marca marinho-teal
COR_GOLD = "#C69A2E"     # dourado para TEXTO (contraste ok)
COR_GOLD_HI = "#FFD666"  # dourado claro (SÓ preenchimento/destaque em fundo escuro)

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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');
        html, body, [class*="st-"], [class*="css-"], .stMarkdown, .stButton button,
        input, textarea, select, button, [data-testid] {
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif !important;
        }
        /* Restaura a fonte de ÍCONES (senão a ligadura vira texto 'arrow' sobre o título) */
        [data-testid="stIconMaterial"], span[data-testid="stIconMaterial"],
        .material-icons, .material-icons-outlined, .material-icons-round,
        .material-symbols-outlined, .material-symbols-rounded,
        [class*="material-symbols"], [class*="material-icons"], .stExpander summary svg + span {
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                         'Material Icons', 'Material Icons Outlined' !important;
        }
        .stApp {background: #F4F7F8;}
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {
            padding-top: 1.2rem; padding-bottom: 4rem; max-width: 1160px;
            margin-left: auto; margin-right: auto;
        }
        /* Navegação foi pro topo: a barra lateral some por completo */
        section[data-testid="stSidebar"] {display: none !important;}
        [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {display: none !important;}

        /* Base tipográfica: quase tudo abaixo está em rem, então a raiz escala
           o app inteiro. 18px dá leitura confortável com mais respiro/organização. */
        html {font-size: 18px;}
        body, .stMarkdown, .stMarkdown p, .stMarkdown li {color: #132244;}
        .stMarkdown p, .stMarkdown li, label, .stRadio label, .stCheckbox label {font-size: 1.02rem;}
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
        [data-testid="stCaptionContainer"] span, [data-testid="stCaptionContainer"] li {
            font-size: 0.94rem; line-height: 1.6; color: #132244 !important; font-weight: 500;
        }
        /* Rótulos de campos (number/text/select/radio/checkbox) bem escuros p/ leitura */
        label p, [data-testid="stWidgetLabel"] p, .stNumberInput label, .stTextInput label,
        .stSelectbox label, .stRadio label, .stCheckbox label, .stTextArea label {
            color: #132244; font-weight: 600;
        }
        [data-testid="stMetricValue"] {font-size: 2rem; font-weight: 800; color: #132244;}
        [data-testid="stMetricLabel"] p {font-size: 0.9rem; letter-spacing: 0.02em; color: #132244;}
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
        .stTabs [aria-selected="true"] {color: #0B1F2A !important;}
        .stTabs [data-baseweb="tab-highlight"] {background: #3FD0E0 !important;}
        .stExpander summary p {font-size: 0.98rem; font-weight: 600;}

        h1 {font-size: 2.6rem; margin-bottom: 0.2rem;}
        h1, h2, h3, h4 {
            color: #0B1F2A; font-weight: 700; letter-spacing: -0.02em;
            font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif !important;
        }

        /* Caixa única do resultado: cenários (colunas) x métodos (linhas) */
        .ciano-matriz {
            width: 100%; border-collapse: separate; border-spacing: 0;
            background: #FFFFFF; border: 1px solid #E2E8F2;
            border-radius: 16px; overflow: hidden; margin: 8px 0 6px 0;
            box-shadow: 0 1px 2px rgba(19,34,74,.06), 0 2px 8px rgba(19,34,74,.05);
        }
        .ciano-matriz th, .ciano-matriz td {padding: 16px 18px; text-align: center;}
        .ciano-matriz thead th {
            background: #F4F6FB; color: #132244; font-size: 0.86rem; font-weight: 800;
            letter-spacing: 0.10em; text-transform: uppercase;
            border-bottom: 1px solid #E2E8F2;
        }
        .ciano-matriz tbody th {
            background: #F4F6FB; color: #132244; text-align: left;
            font-weight: 800; font-size: 1.02rem; border-right: 1px solid #E2E8F2;
        }
        .ciano-matriz tbody th small {
            display: block; color: #132244; font-weight: 600;
            font-size: 0.80rem; margin-top: 3px; text-transform: none; letter-spacing: 0;
        }
        .ciano-matriz tbody tr + tr th, .ciano-matriz tbody tr + tr td {
            border-top: 1px solid #E2E8F2;
        }
        .ciano-matriz td .v {color: #132244; font-size: 1.75rem; font-weight: 800; line-height: 1.15;}
        .ciano-matriz td .u {font-size: 0.98rem; font-weight: 700; margin-top: 4px;}
        .ciano-matriz td .na {color: #AAB4CB; font-size: 1.2rem; font-weight: 700;}
        .ciano-preco {
            color: #132244; font-size: 1.05rem; font-weight: 600; margin: 2px 0 2px 0;
        }
        .ciano-preco b {color: #132244; font-size: 1.25rem;}

        /* Tese no formato "card" (análise própria) */
        .tese-cab {display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 6px;}
        .tese-tag {
            background: #E3F1F3; color: #00586A; border: 1px solid #BFE6EC;
            font-size: 0.86rem; font-weight: 700; padding: 3px 12px; border-radius: 20px;
        }
        .tese-sub {
            color: #13224A; font-size: 0.86rem; font-weight: 800; letter-spacing: 0.10em;
            text-transform: uppercase; margin: 18px 0 6px 0;
        }
        .tese-data {
            color: #132244; font-size: 0.86rem; font-weight: 600;
            border: 1px solid #E2E8F2; border-radius: 8px; padding: 3px 10px;
        }
        .tese-resumo {
            color: #132244; font-size: 0.96rem; line-height: 1.6; margin: 8px 0 2px 0;
        }
        .noti {
            background: #FFFFFF; border: 1px solid #E2E8F2; border-radius: 12px;
            padding: 12px 16px; margin-bottom: 9px;
            box-shadow: 0 1px 2px rgba(19,34,74,.06);
        }
        .noti.hit {border-left: 4px solid #16A34A;}
        .noti a {color: #132244; font-weight: 600; font-size: 1rem; text-decoration: none; line-height: 1.4;}
        .noti a:hover {text-decoration: underline; color: #0FA3B8;}
        .noti-meta {display: block; color: #132244; font-size: 0.82rem; margin-top: 5px;}
        .noti-gat {
            display: inline-block; background: #DCFCE7; color: #15803D; font-size: 0.74rem;
            font-weight: 700; padding: 1px 8px; border-radius: 20px; margin: 0 5px 5px 0;
        }
        .tese-tag.gat-chip {background:#F1F4FA; color:#132244; border-color:#E2E8F2; font-weight:600;}

        .ciano-brand {display: inline-block; margin-bottom: 4px; background: #0B1F2A;
            padding: 14px 22px 10px; border-radius: 14px;}
        .ciano-brand img {height: 88px; width: auto; display: block;}
        .ciano-invest {
            color: #FFD666; font-size: 0.92rem; font-weight: 600;
            letter-spacing: 0.30em; text-align: right; margin-top: -10px; padding-right: 3px;
        }
        .ciano-sub {color: #132244; font-size: 1.02rem; margin: 0 0 4px 0;}

        .ciano-label {
            color: #13224A; font-size: 0.80rem; font-weight: 800;
            letter-spacing: 0.14em; text-transform: uppercase; margin: 26px 0 10px 0;
            padding-bottom: 6px; border-bottom: 2px solid #E2E8F2;
        }

        .ciano-verdict {
            display: inline-flex; align-items: center; gap: 12px;
            padding: 14px 26px; border-radius: 16px; font-weight: 800;
            font-size: 1.35rem; color: #fff; margin: 2px 0 6px 0;
        }
        .ciano-verdict small {font-weight: 500; font-size: 0.82rem; color: #F1F5FF; opacity: .95;}

        .ciano-cards {display: flex; gap: 20px; margin: 6px 0 8px 0; flex-wrap: wrap;}
        .ciano-card {
            flex: 1; min-width: 190px; background: #FFFFFF;
            border: 1px solid #E2E8F2; border-radius: 16px; padding: 22px 24px;
            box-shadow: 0 1px 2px rgba(19,34,74,.06), 0 2px 8px rgba(19,34,74,.05);
            transition: border-color .15s, box-shadow .15s, transform .15s;
        }
        .ciano-card:hover {border-color: #3FD0E0; box-shadow: 0 2px 12px rgba(63,208,224,.22); transform: translateY(-1px);}
        .ciano-card .lbl {
            color: #132244; font-size: 0.78rem; font-weight: 700;
            letter-spacing: 0.10em; text-transform: uppercase;
        }
        .ciano-card .val {color: #132244; font-size: 2.1rem; font-weight: 800; margin: 8px 0 2px 0;}
        .ciano-card .sub {font-size: 0.95rem; font-weight: 700; color: #132244;}

        /* Botão primário estilo CTA da marca */
        .stButton > button {
            background: #3FD0E0; color: #0B1F2A; border: none; border-radius: 30px;
            padding: 0.55rem 1.6rem; font-weight: 800; transition: filter .15s, box-shadow .15s;
            box-shadow: 0 1px 2px rgba(11,31,42,.10);
        }
        .stButton > button:hover {filter: brightness(1.05); color: #0B1F2A; box-shadow: 0 3px 10px rgba(63,208,224,.35);}

        section[data-testid="stSidebar"] {background: #FFFFFF; border-right: 1px solid #E2E8F2;}
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {color: #132244;}

        div[data-testid="stDataFrame"] {border: 1px solid #E2E8F2; border-radius: 14px;}

        .tese-setor {color: #132244; margin: -2px 0 8px 0; font-size: 0.95rem;}
        .tese-texto {color: #132244; line-height: 1.55; margin-bottom: 14px;}
        .tese-box {
            background: #FFFFFF; border: 1px solid #E2E8F2; border-radius: 16px;
            padding: 16px 20px; height: 100%;
            box-shadow: 0 1px 2px rgba(19,34,74,.06), 0 2px 8px rgba(19,34,74,.05);
        }
        .tese-box .tese-h {
            font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;
            font-size: 0.80rem; margin-bottom: 8px;
        }
        .tese-box ul {margin: 0; padding-left: 20px;}
        .tese-box li {color: #132244; font-size: 0.96rem; margin-bottom: 10px; line-height: 1.55;}
        .tese-fortes {border-left: 4px solid #16A34A;}
        .tese-fortes .tese-h {color: #15803D;}
        .tese-fracos {border-left: 4px solid #DC2626;}
        .tese-fracos .tese-h {color: #B91C1C;}

        /* ---- Navegação por páginas na sidebar (radio estilizado como menu) ---- */
        section[data-testid="stSidebar"] {padding-top: 6px;}
        .nav-grupo {
            color: #132244; font-size: 0.70rem; font-weight: 800; letter-spacing: 0.16em;
            text-transform: uppercase; margin: 16px 10px 6px;
        }
        .nav-grupo:first-of-type {margin-top: 4px;}
        section[data-testid="stSidebar"] div[role="radiogroup"] {gap: 3px;}
        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            width: 100%; margin: 0; padding: 9px 14px; border-radius: 10px; cursor: pointer;
            color: #132244; font-weight: 600; transition: background .12s, color .12s;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {background: #F1F4FA;}
        section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {display: none;}
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
            background: #E7F7FA; color: #0B1F2A; box-shadow: inset 3px 0 0 #3FD0E0;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {font-size: 1rem; font-weight: 600;}
        /* separador acima do bloco de premissas, que aparece só nas páginas de análise */
        section[data-testid="stSidebar"] [data-testid="stHeading"] h2 {
            font-size: 0.72rem; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase;
            color: #132244; margin-top: 10px;
        }

        /* Tabela de resultado rola na horizontal em telas estreitas, sem estourar a página */
        .ciano-matriz-wrap {width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;}
        .ciano-matriz {min-width: 520px;}

        /* ---- Barra de navegação no TOPO (estilo institucional) ---- */
        .topbar {
            display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
            padding: 10px 0 14px 0; margin-bottom: 8px;
            border-bottom: 1px solid #E2E8F2;
        }
        .topbar-brand {display: flex; align-items: center; gap: 10px;}
        .topbar-brand .mark {
            width: 34px; height: 34px; border-radius: 9px; background: #0B1F2A;
            display: inline-flex; align-items: center; justify-content: center;
        }
        .topbar-brand .mark img {height: 22px; width: auto; display: block;}
        .topbar-brand .wm {
            font-family: 'Space Grotesk','Inter',sans-serif; font-weight: 700;
            font-size: 1.25rem; color: #0B1F2A; letter-spacing: -0.01em;
        }
        /* o radio horizontal da navegação vira uma fileira de pills */
        div[role="radiogroup"][aria-label="Navegacao principal"] {
            display: flex; flex-wrap: wrap; gap: 4px; align-items: center;
        }
        div[role="radiogroup"][aria-label="Navegacao principal"] label {
            margin: 0; padding: 8px 15px; border-radius: 22px; cursor: pointer;
            color: #0B1F2A; font-weight: 600; transition: background .12s, color .12s;
        }
        div[role="radiogroup"][aria-label="Navegacao principal"] label:hover {background: #E7F7FA;}
        /* esconde a bolinha do radio — cobre as duas estruturas de versão do Streamlit:
           (local antigo) a bolinha é o 1º filho <div> do label;
           (nuvem novo) é o 1º item dentro do container de conteúdo do label. */
        div[role="radiogroup"][aria-label="Navegacao principal"] label > div:first-child,
        div[role="radiogroup"][aria-label="Navegacao principal"] label[data-testid="stRadioOption"] > div:last-child > :first-child {display: none;}
        div[role="radiogroup"][aria-label="Navegacao principal"] label p {font-size: 0.98rem; font-weight: 600; color: #0B1F2A;}
        div[role="radiogroup"][aria-label="Navegacao principal"] label:has(input:checked) {background: #0B1F2A;}
        div[role="radiogroup"][aria-label="Navegacao principal"] label:has(input:checked) p {color: #fff;}
        /* ícones de linha (Material) no menu: alinhados, na cor do texto */
        div[role="radiogroup"][aria-label="Navegacao principal"] [data-testid="stIconMaterial"] {
            font-size: 18px; color: #334155; vertical-align: -4px; margin-right: 1px;
        }
        div[role="radiogroup"][aria-label="Navegacao principal"] label:has(input:checked) [data-testid="stIconMaterial"] {color: #fff;}

        /* ---- Hero institucional (olho + título + subtítulo) ---- */
        .hero {margin: 18px 0 30px 0;}
        .hero .eyebrow {
            color: #0FA3B8; font-size: 0.80rem; font-weight: 700;
            letter-spacing: 0.22em; text-transform: uppercase; margin-bottom: 14px;
        }
        .hero h1.htitle {
            font-family: 'Space Grotesk','Inter',sans-serif; font-weight: 600;
            font-size: 3.1rem; line-height: 1.04; letter-spacing: -0.03em;
            color: #0B1F2A; margin: 0 0 14px 0; max-width: 18ch;
        }
        .hero .hsub {color: #3A4D57; font-size: 1.12rem; line-height: 1.5; max-width: 60ch; margin: 0;}

        /* Tabela de resultado rola na horizontal em telas estreitas, sem estourar a página */
        .ciano-matriz-wrap {width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;}
        .ciano-matriz {min-width: 520px;}

        /* ---- Responsivo: tablet ---- */
        @media (max-width: 900px) {
            html {font-size: 16.5px;}
            .block-container {margin-left: auto; margin-right: auto; padding-left: 1.2rem; padding-right: 1.2rem;}
            .ciano-brand img {height: 78px;}
            h1 {font-size: 2rem;}
        }
        /* ---- Responsivo: celular ---- */
        @media (max-width: 640px) {
            html {font-size: 15px;}
            .block-container {padding-top: 1.4rem; padding-left: 0.9rem; padding-right: 0.9rem;}
            .ciano-brand img {height: 60px;}
            .ciano-invest {font-size: 0.78rem; letter-spacing: 0.22em;}
            h1 {font-size: 1.7rem; margin-top: 26px !important;}
            .ciano-cards {gap: 12px;}
            .ciano-card {min-width: 100%; padding: 16px 18px;}
            .ciano-card .val {font-size: 1.7rem;}
            .ciano-matriz td .v {font-size: 1.4rem;}
            .ciano-matriz th, .ciano-matriz td {padding: 12px 12px;}
            [data-testid="stMetricValue"] {font-size: 1.6rem;}
            .ciano-verdict {font-size: 1.1rem; padding: 12px 18px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Glyph "atividade/gráfico" em ciano — a marca do topo (como o ícone do site).
_MARCA_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3FD0E0" '
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M3 12h3l2.5 6 4-13 2.5 7h4"/></svg>'
)

# Olho (eyebrow) + título + subtítulo de cada página — dá o ar institucional do site.
_HERO = {
    "🔎 Empresa": ("Análise fundamentalista", "Quanto vale a empresa?",
                   "Preço justo por DCF e múltiplos, com cenários de crescimento e a TIR que o mercado está exigindo hoje."),
    "📊 Screener": ("Varredura do mercado", "Screener",
                    "Filtra a bolsa inteira por desconto no valuation ou por crescimento de lucro — e entrega os nomes que merecem um olhar."),
    "⭐ Carteira": ("Suas posições", "Carteira",
                   "Avalia todas as empresas da sua carteira de uma vez e mostra onde está o maior potencial."),
    "🏅 Ranking": ("Comparativo", "Ranking de oportunidades",
                  "As teses próprias da Ciano ordenadas por upside, lado a lado."),
    "🔀 Cenários": ("Leitura de ciclo", "Ciclos de mercado",
                   "Onde o Ibovespa está no ciclo e quais alavancas sustentam (ou derrubam) a alta."),
    "📉 Macro": ("Panorama macro", "Indicadores econômicos",
                "Selic, IPCA, juro real e câmbio — o pano de fundo que move os preços."),
    "💵 Câmbio": ("Dólar e risco-país", "Câmbio",
                 "O real justo pelo diferencial de juros e pelo risco-Brasil, atualizado ao vivo."),
    "🌎 Estrangeiro": ("Fluxo de investidores", "Capital estrangeiro",
                      "Entrada e saída do investidor estrangeiro na B3, saldo oficial em D+2."),
    "📰 Notícias": ("Acompanhamento", "Notícias do dia",
                   "O noticiário que mexe com as suas teses, reunido num lugar só."),
    "🔔 Gatilhos": ("Monitor técnico", "Gatilhos",
                   "Quem está perto de um ponto de decisão técnico no Ibovespa, Small Caps e IFIX."),
}


# Rótulos exibidos no menu (só texto, sem ícone — estilo minimalista). As CHAVES
# continuam sendo os identificadores internos das páginas (com emoji) — só a
# exibição muda, via format_func.
_ROTULO_NAV = {
    "🔎 Empresa": "Valuation",
    "📊 Screener": "Screener",
    "⭐ Carteira": "Carteira",
    "🏅 Ranking": "Ranking",
    "🔀 Cenários": "Ciclos",
    "📉 Macro": "Macro",
    "💵 Câmbio": "Câmbio",
    "🌎 Estrangeiro": "Estrangeiro",
    "📰 Notícias": "Notícias",
    "🔔 Gatilhos": "Gatilhos",
}


def _topbar(ordem: list) -> str:
    """Barra de navegação no topo (marca à esquerda, páginas em pills). Devolve a página."""
    col_marca, col_nav = st.columns([1.2, 6])
    with col_marca:
        st.markdown(
            f'<div class="topbar-brand"><span class="mark">{_MARCA_SVG}</span>'
            f'<span class="wm">Ciano</span></div>',
            unsafe_allow_html=True,
        )
    with col_nav:
        pagina = st.radio("Navegacao principal", ordem, horizontal=True,
                          label_visibility="collapsed",
                          format_func=lambda p: _ROTULO_NAV.get(p, p))
    st.markdown('<div style="border-bottom:1px solid #E2E8F2;margin:-4px 0 6px;"></div>',
                unsafe_allow_html=True)
    return pagina


def _hero(pagina: str) -> None:
    dados = _HERO.get(pagina)
    if not dados:
        return
    olho, titulo, sub = dados
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{html.escape(olho)}</div>'
        f'<h1 class="htitle">{html.escape(titulo)}</h1>'
        f'<p class="hsub">{html.escape(sub)}</p></div>',
        unsafe_allow_html=True,
    )


def _celula(r, preco_atual: float, moeda: str) -> str:
    """Uma célula da matriz: preço justo + upside colorido (ou '—' se não se aplica)."""
    if r is None:
        return '<td><span class="na">—</span></td>'
    up = r.upside_percentual
    cor = "#16A34A" if up >= 0 else "#DC2626"
    sinal = "+" if up >= 0 else ""
    return (
        f'<td><div class="v">{moeda} {_fmt_brl(r.valuation_final_por_acao)}</div>'
        f'<div class="u" style="color:{cor};">{sinal}{up:.0f}%</div></td>'
    )


def _celula_tma(tma) -> str:
    """Célula da TIR implícita — o retorno que o mercado exige para pagar o preço de hoje."""
    if tma is None:
        return '<td><span class="na">&gt;600%</span></td>'
    # Uma TIR implícita muito alta não é o mercado sendo irracional: é sinal de que
    # o fluxo usado não pertence ao acionista (dívida). Destacamos em ÂMBAR (atenção:
    # número possivelmente irreal) — não em vermelho, que aqui significaria "baixa".
    cor = "#B45309" if tma > 0.40 else "#132244"
    return f'<td><div class="v" style="color:{cor};">{tma*100:.1f}%</div></td>'


def _render_resultado(ticker: str, preco_atual: float, resultado_ebit: dict,
                      resultado_lpa: dict = None, moeda: str = "R$",
                      tma_lucro: float = None, tma_ebit: float = None,
                      tem_lpa: bool = True) -> None:
    """Caixa única: cenários (colunas) × métodos LPA/EBIT (linhas) + TIR implícita."""
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
        '<div class="ciano-matriz-wrap">'
        '<table class="ciano-matriz">'
        '<thead><tr><th style="text-align:left;">Preço justo por ação</th>'
        f'{cabecalho}<th>TIR implícita</th></tr></thead>'
        "<tbody>"
        + linha("Método LPA", "sobre o lucro líquido", resultado_lpa, tma_lucro, tem_lpa)
        + linha("Método EBIT", "sobre o EBIT", resultado_ebit, tma_ebit, True)
        + "</tbody></table></div>"
    )

    st.markdown('<div class="ciano-label">Resultado</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ciano-preco">{ticker} — preço atual <b>{moeda} {_fmt_brl(preco_atual)}</b></div>',
        unsafe_allow_html=True,
    )
    st.markdown(tabela, unsafe_allow_html=True)
    st.caption(
        "Cada célula: preço justo por ação e o upside sobre o preço atual. "
        "**TIR implícita** = o retorno anual que o mercado precisa estar exigindo para a ação "
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
            "tma_lpa_pct": "TIR impl. LPA (%)",
            "justo_ebit": f"Justo EBIT {moeda}", "upside_ebit": "Upside EBIT (%)",
            "tma_ebit_pct": "TIR impl. EBIT (%)",
            "alavancada": "Alav.", "base": "Base", "veredito": "Veredito",
        }).set_index("Ticker")
        if exibir["Empresa"].isna().all():
            exibir = exibir.drop(columns=["Empresa"])
        st.dataframe(exibir, use_container_width=True)
        _baixar_csv_br(exibir, "lote_valuation", "dl_lote")
        st.caption(
            "Cenário intermediário. Ordenado pelo upside do **LPA** (a leitura confiável). "
            "**TIR impl.** = o retorno anual que o mercado exige para a ação valer o preço de hoje "
            "(o desconto que ele impõe). **⚠️ Alav.** = as óticas divergem: o EBIT vai para "
            "credores, então o *Justo EBIT* está superestimado e a *TIR impl. EBIT* fica irreal — "
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

        # TIR implícita: o retorno que o mercado exige para a ação valer o preço de hoje.
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
                    "superestima o preço justo (e a TIR implícita dele fica irreal)."
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


def _screener_crescimento() -> None:
    """Ranking pela média do crescimento (CAGR 5a) de EBIT, lucro e LPA."""
    import crescimento
    import indices_b3

    st.caption(
        "Ranqueia pela MÉDIA do crescimento (CAGR 5 anos) de EBIT, lucro líquido e LPA — "
        "quem mais engordou o resultado. Universo: carteiras oficiais da B3; balanços via Yahoo. "
        "Bancos entram pelo lucro/LPA (não têm EBIT)."
    )
    universos = {"Ibovespa": ["IBOV"], "Small Caps": ["SMLL"], "Ibov + Small Caps": ["IBOV", "SMLL"]}
    c1, c2 = st.columns([2, 1])
    esc = c1.radio("Universo", list(universos), index=2, horizontal=True, label_visibility="collapsed")
    topn = int(c2.number_input("Top N", value=20, min_value=10, max_value=60, step=5))

    if st.button("Rodar ranking de crescimento", type="primary"):
        tickers = []
        for idx in universos[esc]:
            tickers += indices_b3.componentes(idx).get("tickers", [])
        tickers = sorted(set(tickers))
        barra = st.progress(0.0, text=f"Lendo balanços de {len(tickers)} empresas (1ª vez é mais lento)…")
        df = crescimento.crescimento_lote(
            tickers, progresso=lambda f: barra.progress(min(f, 1.0), text=f"Balanços… {int(f * len(tickers))}/{len(tickers)}"))
        barra.empty()
        st.session_state.scr_cresc = (df, esc)

    dados = st.session_state.get("scr_cresc")
    if not dados:
        return
    df, universo = dados
    val = df[df["lucro_cagr"].notna() & df["lpa_cagr"].notna()].copy()
    if val.empty:
        st.info("Não consegui crescimento suficiente nesse universo agora.")
        return
    top = val.sort_values("media_cagr", ascending=False).head(topn)

    st.markdown(f'<div class="ciano-label">Top {len(top)} em crescimento 5a — {universo}</div>',
                unsafe_allow_html=True)
    exibir = top.copy()
    exibir["Lucro caindo?"] = exibir["lucro_cai"].map({True: "⚠️ sim", False: ""})
    exibir = exibir.rename(columns={
        "ticker": "Ticker", "media_cagr": "Média CAGR (%)", "ebit_cagr": "EBIT (%)",
        "lucro_cagr": "Lucro (%)", "lpa_cagr": "LPA (%)", "anos": "Anos",
    })[["Ticker", "Média CAGR (%)", "EBIT (%)", "Lucro (%)", "LPA (%)", "Anos", "Lucro caindo?"]]
    st.dataframe(exibir.set_index("Ticker"), use_container_width=True)
    st.caption("CAGR = crescimento anual composto do começo ao fim da série (≈5 anos). "
               "⚠️ CAGR muito alto (>100%) costuma ser efeito-base — empresa saindo de lucro perto de zero "
               "infla o número; confira as colunas EBIT/Lucro/LPA. "
               "Fonte: demonstrativos anuais do Yahoo. Crescimento passado não garante futuro.")


def _aba_screener(tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2) -> None:
    mercado = st.radio("Mercado", ["🇧🇷 B3", "🌎 EUA"], horizontal=True, key="scr_mercado")
    if mercado.startswith("🌎"):
        _aba_eua()
        return

    modo = st.radio("Ordenar por", ["Upside (valuation)", "Crescimento 5a (lucro/LPA)"],
                    horizontal=True, key="scr_modo")
    if modo.startswith("Crescimento"):
        _screener_crescimento()
        return

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

    # Setor (via Yahoo, cacheado) + filtro por setor, em português.
    import setores_b3 as sb3
    tks = list(tabela["ticker"].astype(str).str.upper())
    mapa = sb3.carregar_mapa()
    faltam = [t for t in tks if t not in mapa]
    if faltam:
        barra = st.progress(0.0, text=f"Buscando setor de {len(faltam)} ações (1ª vez; depois fica em cache)…")
        mapa = sb3.garantir_setores(tks, progresso=lambda f, t: barra.progress(f / t, text=f"Setor… {f}/{t}"))
        barra.empty()
    else:
        mapa = sb3.garantir_setores(tks)
    tabela["setor"] = tabela["ticker"].astype(str).str.upper().map(
        lambda t: _SETORES_PT.get(mapa.get(t, "—"), mapa.get(t, "—")))

    setores_disp = sorted(s for s in tabela["setor"].unique() if s and s != "—")
    sel = st.multiselect(
        "Setores", setores_disp, default=setores_disp, key="scr_setores",
        help="Filtra por setor — ex.: desmarque Tecnologia para ver só as não-tech.",
    )
    if sel and len(sel) < len(setores_disp):
        tabela = tabela[tabela["setor"].isin(sel)]
    if tabela.empty:
        st.info("Nenhuma ação nos setores selecionados.")
        return

    st.markdown(
        f'<div class="ciano-label">Ranking — {len(tabela)} ações</div>',
        unsafe_allow_html=True,
    )
    exibir = tabela.rename(
        columns={
            "ticker": "Ticker",
            "setor": "Setor",
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
            "tma_lpa_pct": "TIR impl. LPA (%)",
            "justo_ebit": "Justo EBIT R$", "upside_ebit": "Upside EBIT (%)",
            "tma_ebit_pct": "TIR impl. EBIT (%)",
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

    setores_univ = sorted({x.get("setor") for x in universo if x.get("setor")})
    sel_pt = st.multiselect(
        "Setores", [_SETORES_PT.get(s, s) for s in setores_univ],
        default=[_SETORES_PT.get(s, s) for s in setores_univ], key="eua_setores",
        help="Filtra por setor — ex.: desmarque Tecnologia para ver só as não-tech. "
        "Reaplica na hora, sem precisar rodar de novo.",
    )
    pt_para_en = {_SETORES_PT.get(s, s): s for s in setores_univ}
    setores_sel = {pt_para_en[s] for s in sel_pt}

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

    # Filtro de setores aplicado na exibição (reage na hora, sem re-rodar o Yahoo).
    if setores_sel and len(setores_sel) < len(setores_univ):
        ranking = ranking[ranking["setor"].isin(setores_sel)]
    if ranking.empty:
        st.info("Nenhuma empresa nos setores selecionados.")
        return
    ranking = ranking.copy()
    ranking["setor"] = ranking["setor"].map(lambda s: _SETORES_PT.get(s, s))

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
    # Tenta usar os anos de verdade no eixo X (datas dd/mm/aaaa). Se não parsear,
    # cai para a ordem sequencial sem rótulos (comportamento antigo).
    dfg["dt"] = pd.to_datetime(dfg["data"], dayfirst=True, errors="coerce")
    usar_tempo = dfg["dt"].notna().mean() > 0.8
    if usar_tempo:
        eixo_x = alt.X("dt:T", title=None,
                       axis=alt.Axis(format="%Y", tickCount="year", labelColor=COR_LIGHT,
                                     grid=False, labelAngle=0))
    else:
        dfg["ordem"] = range(len(dfg))
        eixo_x = alt.X("ordem:Q", title=None, axis=alt.Axis(labels=False, grid=False, ticks=False))
    linha = (
        alt.Chart(dfg)
        .mark_line(color=COR_ACCENT, strokeWidth=2)
        .encode(
            x=eixo_x,
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
    _indicador_macro(c1, "Dólar (R$)", g.get("dolar_real"), lambda v: f"R$ {v:.2f}".replace(".", ","),
                     delta_key="var_ano", ajuda="USD/BRL — quanto vale 1 dólar em reais (Yahoo). "
                     "Sobe = real mais fraco.")
    _indicador_macro(c2, "DXY (índice dólar)", g.get("dxy"), lambda v: f"{v:.2f}",
                     delta_key="var_ano", ajuda="Dólar contra uma cesta de moedas fortes.")
    _indicador_macro(c3, "Ouro (US$/oz)", g.get("ouro"),
                     lambda v: f"US$ {v:,.0f}".replace(",", "."), delta_key="var_ano")
    _indicador_macro(c4, "Treasury 10 anos", g.get("treasury10a"), lambda v: f"{v:.2f}%",
                     sufixo="%", delta_key="var_ano", ajuda="Juro longo dos EUA — o 'sem risco' em dólar.")
    e1, e2 = st.columns(2)
    _indicador_macro(e1, "Inflação EUA (CPI 12m)", g.get("cpi_eua"), lambda v: f"{v:.2f}%",
                     sufixo="%", ajuda="CPI cheio em 12 meses (fonte: BLS).")
    carry = g.get("carry_real") or {}
    cr, brr, usr = carry.get("valor"), carry.get("br_real"), carry.get("us_real")
    _indicador_macro(e2, "Carry: juro real BR − EUA", carry, lambda v: f"{v:+.1f} pp",
                     ajuda=(f"Diferencial de juro REAL (BR {brr:.1f}% − EUA {usr:.1f}%). "
                            if (brr is not None and usr is not None) else "")
                     + "O prêmio de juro real por ficar no real em vez do dólar — o principal "
                     "motor da relação câmbio/juros. Quanto maior, mais atrai capital — MAS só "
                     "se o risco fiscal/país estiver contido.")

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
    ref = (b.get("focus_ipca") or {}).get("ref")
    ano = f"para o fim de {ref}" if ref else "para o ano de referência"
    ano_cheio = f"para o ano cheio de {ref}" if ref else "para o ano cheio"
    e1, e2, e3, e4 = st.columns(4)
    _indicador_macro(e1, "Juro real ex-ante", b.get("juro_real_ex_ante"), lambda v: f"{v:.1f}%",
                     sufixo="%",
                     ajuda="((1+Selic Focus)/(1+IPCA Focus) − 1). Juro real alto pressiona a economia e o valuation.")
    _indicador_macro(e2, "Focus — IPCA", b.get("focus_ipca"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda=f"Mediana das expectativas de mercado (Focus/BC) para o IPCA acumulado {ano_cheio} "
                     "(inflação do ano inteiro, não mensal). A trajetória mostra se estão ancorando.")
    _indicador_macro(e3, "Focus — Selic", b.get("focus_selic"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda=f"Mediana das expectativas (Focus/BC) para a taxa Selic {ano} (onde o mercado "
                     "acha que o juro vai estar no fim do ano).")
    _indicador_macro(e4, "Focus — PIB", b.get("focus_pib"), lambda v: f"{v:.2f}%", sufixo="%",
                     ajuda=f"Mediana das expectativas (Focus/BC) para o crescimento do PIB {ano_cheio} "
                     "(ano inteiro vs. o anterior — não é trimestre).")

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

    # "O que derruba daqui" — painel de vigilância (movido da aba Ciclos p/ cá).
    _bloco_gatilhos(None)


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
    import indices_b3
    from gatilhos import PERIODOS_PADRAO, TOLERANCIA_PADRAO, avaliar_gatilhos

    st.caption(
        "Varre um universo inteiro da B3 e avisa quem está perto da média móvel longa "
        "(padrão: 200 semanas — a MM200 do semanal, referência de fundo de ciclo). "
        "Carteira dos índices via B3 (oficial); preços via Yahoo Finance."
    )
    rotulos = {"Ibovespa (large caps)": "IBOV", "Small Caps (SMLL)": "SMLL",
               "Fundos imobiliários (IFIX)": "IFIX"}
    escolha = st.radio("Universo", list(rotulos), horizontal=True, label_visibility="collapsed")
    idx = rotulos[escolha]
    comp = indices_b3.componentes(idx)
    if comp.get("erro"):
        st.error(comp["erro"])
        return
    if comp.get("aviso"):
        st.warning(f"⚠️ {comp['aviso']}")
    tickers = comp["tickers"]
    st.caption(f"{len(tickers)} ativos no {escolha} — fonte: {comp['fonte']}.")

    c1, c2, c3 = st.columns(3)
    periodos = int(c1.number_input("Média (candles semanais)", value=PERIODOS_PADRAO, min_value=10, step=10))
    tol = c2.number_input("Proximidade que dispara (±%)", value=TOLERANCIA_PADRAO, min_value=0.5, step=0.5)
    so_perto = c3.checkbox("Mostrar só quem está perto", value=True)

    if st.button(f"Varrer {escolha}", type="primary") and tickers:
        with st.spinner(f"Baixando histórico de {len(tickers)} ativos e calculando as médias "
                        "(pode levar 1–3 min)…"):
            res = avaliar_gatilhos(tickers, periodos=periodos, tolerancia_pct=float(tol))
        st.session_state.gatilhos = res
        st.session_state.gatilhos_meta = (escolha, float(tol))

    res = st.session_state.get("gatilhos")
    if res is None or res.empty:
        return
    universo, tol_run = st.session_state.get("gatilhos_meta", (escolha, float(tol)))

    res = res.copy()
    res["distancia_abs"] = pd.to_numeric(res["distancia_pct"], errors="coerce").abs()
    res = res.sort_values("distancia_abs", na_position="last")
    disparados = int((res["alerta"] == "🎯 na média").sum())
    st.markdown(
        f'<div class="ciano-label">{universo} — {disparados} na média (±{tol_run:.0f}%), '
        f'de {len(res)} ativos</div>',
        unsafe_allow_html=True,
    )
    mostra = res[res["alerta"] == "🎯 na média"] if so_perto else res
    if mostra.empty:
        st.info("Ninguém dentro da faixa agora. Desmarque 'Mostrar só quem está perto' para ver a lista toda "
                "ordenada por distância.")
        return
    exibir = mostra.drop(columns=["distancia_abs"]).rename(
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


_EVENTOS_FILE = Path(__file__).resolve().parent / "data" / "eventos_mercado.json"
# categoria -> (rótulo na legenda, cor)
_CAT_EVENTO = {
    "crise": ("Crise", "#DC2626"),
    "juros": ("Juros", "#EA580C"),
    "inflacao": ("Inflação", "#7C3AED"),
    "guerra": ("Guerra / choque", "#334155"),
    "erro": ("Erro econômico", "#CA8A04"),
}


def _wrap_html(texto: str, largura: int = 54) -> str:
    import textwrap
    return "<br>".join(textwrap.wrap(texto, largura))


# janelas de zoom por período (rótulo -> anos para trás a partir de hoje, ou faixa fixa)
_PERIODOS_CICLO = {
    "Tudo": None,
    "10 anos": ("anos", 10),
    "5 anos": ("anos", 5),
    "Pandemia (2020→)": ("faixa", "2020-01-01", None),
    "Crise 2008": ("faixa", "2007-01-01", "2010-12-31"),
}


def _grafico_ciclo_interativo(d: dict, periodo: str = "Tudo"):
    """Ibov interativo com eventos históricos e faixas de alta/baixa. Passe o
    mouse para ver o que aconteceu; clique num ponto para fixar o detalhe.
    Devolve (ok, evento_fixado): ok=False se o Plotly não estiver disponível
    (aí cai no gráfico Altair antigo); evento_fixado é o dict do ponto clicado."""
    try:
        import plotly.graph_objects as go
    except Exception:  # noqa: BLE001
        return False, None
    serie = d.get("serie") or []
    if not serie:
        return False, None
    df = pd.DataFrame(serie)
    df["dt"] = pd.to_datetime(df["data"])
    df = df.sort_values("dt").reset_index(drop=True)
    try:
        eventos = json.loads(_EVENTOS_FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        eventos = []

    serie_val = df.set_index("dt")["valor"]
    dmin, dmax = df["dt"].min(), df["dt"].max()
    # eventos válidos (dentro da série), agrupados por direção (verde subiu / vermelho caiu)
    ev_validos, por_dir = [], {"alta": [], "baixa": []}
    for e in eventos:
        try:
            dt = pd.to_datetime(e["data"])
        except Exception:  # noqa: BLE001
            continue
        if dt < dmin or dt > dmax:
            continue
        pos = serie_val.index.get_indexer([dt], method="nearest")[0]
        val = float(serie_val.iloc[pos])
        gidx = len(ev_validos)
        ev_validos.append(e)
        direc = "alta" if e.get("dir") == "alta" else "baixa"
        por_dir[direc].append((dt, val, e.get("titulo", ""), e.get("desc", ""), gidx))

    alto = 1.26  # quanto o marcador sobe acima da linha (offset multiplicativo no eixo log)
    fig = go.Figure()

    # --- faixas de alta (verde) e baixa (vermelho) com aviso de duração/variação ---
    _VERDE, _VERM = "rgba(34,197,94,0.07)", "rgba(239,68,68,0.07)"
    legs = d.get("legs") or []
    for k, lg in enumerate(legs):
        try:
            x0 = pd.to_datetime(lg["de"] + "-01")
            x1 = pd.to_datetime(lg["ate"] + "-01")
        except Exception:  # noqa: BLE001
            continue
        alta = lg.get("tipo") == "alta"
        fig.add_vrect(x0=x0, x1=x1, fillcolor=_VERDE if alta else _VERM,
                      opacity=1, layer="below", line_width=0)
        # rótulo só nas pernas relevantes, DENTRO da faixa (base do gráfico), sem empilhar
        if abs(lg.get("amp", 0)) < 20 or lg.get("meses", 0) < 6:
            continue
        meio = x0 + (x1 - x0) / 2
        cor_txt = "#15803D" if alta else "#B91C1C"
        txt = f"{'+' if lg.get('amp', 0) >= 0 else '−'}{abs(lg.get('amp', 0)):.0f}%<br>{lg.get('meses', 0)}m"
        fig.add_annotation(x=meio, y=0.02, yref="paper", text=txt, showarrow=False,
                           font=dict(size=10, color=cor_txt), align="center",
                           bgcolor="rgba(255,255,255,0.55)", borderpad=1)

    fig.add_trace(go.Scatter(
        x=df["dt"], y=df["valor"], mode="lines", name="Ibovespa",
        line=dict(color="#0FA3B8", width=1.7),
        hovertemplate="%{x|%b/%Y} · Ibov %{y:,.0f}<extra></extra>"))
    # hastes finas ligando cada evento ao ponto na linha (atrás dos marcadores)
    hx, hy = [], []
    for pts in por_dir.values():
        for p in pts:
            hx += [p[0], p[0], None]
            hy += [p[1], p[1] * alto, None]
    if hx:
        fig.add_trace(go.Scatter(x=hx, y=hy, mode="lines", hoverinfo="skip",
                                 line=dict(color="#C7D0DE", width=1), showlegend=False))
    # marcadores: verde = bolsa subiu, vermelho = bolsa caiu
    for direc, rotulo, cor in (("alta", "Bolsa subiu", "#16A34A"),
                               ("baixa", "Bolsa caiu", "#DC2626")):
        pts = por_dir.get(direc, [])
        if not pts:
            continue
        textos = [f"<b style='font-size:13px'>{p[2]}</b><br>"
                  f"<span style='font-size:12px'>{_wrap_html(p[3])}</span>"
                  "<br><span style='font-size:11px;color:#64748B'>clique p/ fixar</span>" for p in pts]
        fig.add_trace(go.Scatter(
            x=[p[0] for p in pts], y=[p[1] * alto for p in pts], mode="markers", name=rotulo,
            marker=dict(size=11, color=cor, line=dict(color="#FFFFFF", width=1.6)),
            customdata=[[t, p[4]] for t, p in zip(textos, pts)],
            hovertemplate="%{customdata[0]}<extra></extra>"))

    # zoom por período
    cfg = _PERIODOS_CICLO.get(periodo)
    if cfg:
        if cfg[0] == "anos":
            x_ini, x_fim = dmax - pd.DateOffset(years=cfg[1]), dmax
        else:
            x_ini = pd.to_datetime(cfg[1])
            x_fim = pd.to_datetime(cfg[2]) if cfg[2] else dmax
        fig.update_xaxes(range=[x_ini, x_fim])
        vis = df[(df["dt"] >= x_ini) & (df["dt"] <= x_fim)]["valor"]
        if len(vis):
            import math
            fig.update_yaxes(range=[math.log10(vis.min() * 0.9), math.log10(vis.max() * 1.35)])

    # eixo de preço à direita (padrão de plataforma), grade horizontal sutil
    fig.update_yaxes(type="log", side="right", showgrid=True, gridcolor="rgba(11,31,42,0.06)",
                     tickfont=dict(color="#64748B", size=11), title=None,
                     tickformat=",.0f", ticksuffix="  ", zeroline=False)
    # linha-guia vertical no hover (crosshair), ticks por ano
    fig.update_xaxes(showgrid=False, tickfont=dict(color="#64748B", size=11), title=None,
                     dtick="M24", tickformat="%Y", ticks="outside", ticklen=4,
                     tickcolor="rgba(11,31,42,0.15)", showspikes=True, spikemode="across",
                     spikethickness=1, spikedash="solid", spikecolor="rgba(11,31,42,0.22)")
    fig.update_layout(
        height=520, margin=dict(l=4, r=52, t=8, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#0B1F2A"),
        legend=dict(orientation="h", yanchor="bottom", y=1.015, x=0, title=None,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F2",
                        font=dict(color="#0B1F2A", size=13), align="left"),
        hovermode="closest", dragmode=False)

    evento_fixado = None
    try:
        ev = st.plotly_chart(fig, use_container_width=True, key="ciclo_chart",
                             on_select="rerun", selection_mode="points",
                             config={"displayModeBar": False})
        pts_sel = (ev.get("selection", {}) or {}).get("points", []) if ev else []
        for p in pts_sel:
            cd = p.get("customdata")
            if cd and len(cd) > 1 and 0 <= int(cd[1]) < len(ev_validos):
                evento_fixado = ev_validos[int(cd[1])]
                break
    except TypeError:
        # Streamlit antigo sem on_select: renderiza sem clique-fixar
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    return True, evento_fixado


def _card_evento_fixado(e: dict) -> None:
    rotulo, cor = _CAT_EVENTO.get(e.get("categoria", "crise"), ("Evento", "#334155"))
    data = e.get("data", "")
    ano = data[:4] if data else ""
    st.markdown(
        f'<div style="background:{COR_CARD};border:1px solid {COR_BORDA};'
        f'border-left:4px solid {cor};border-radius:10px;padding:14px 16px;margin:4px 0 2px;">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
        f'<span style="font-size:0.7rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;'
        f'color:{cor};">{html.escape(rotulo)}</span>'
        f'<span style="font-size:0.72rem;color:#64748B;">{html.escape(ano)}</span></div>'
        f'<div style="font-size:1rem;font-weight:700;margin-bottom:5px;">{html.escape(e.get("titulo", ""))}</div>'
        f'<div style="font-size:0.88rem;line-height:1.55;opacity:0.92;">{html.escape(e.get("desc", ""))}</div>'
        f'</div>', unsafe_allow_html=True)


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
    st.caption("A história do Ibovespa com os fatos que a moveram. **Passe o mouse** nos pontos "
               "coloridos para ver o que aconteceu (juros, guerras, inflação, erros, crises) e "
               "**clique** para fixar o detalhe. Faixas verdes = altas, vermelhas = baixas, com a "
               "duração e a variação de cada ciclo. Série do ^BVSP (Yahoo), escala log.")
    with st.spinner("Carregando o histórico do Ibovespa…"):
        d = ibov_ciclo.buscar_ciclo_ibov()
        mat = ibov_ciclo.buscar_maturidade()
    if d.get("erro"):
        st.warning(d["erro"])
        return

    try:
        periodo = st.segmented_control("Período", list(_PERIODOS_CICLO.keys()),
                                       default="Tudo", label_visibility="collapsed")
    except Exception:  # noqa: BLE001  (Streamlit antigo sem segmented_control)
        periodo = st.radio("Período", list(_PERIODOS_CICLO.keys()), horizontal=True,
                           label_visibility="collapsed")
    periodo = periodo or "Tudo"

    ok, evento = _grafico_ciclo_interativo(d, periodo)
    if not ok:
        _grafico_ciclo(d)
    elif evento:
        _card_evento_fixado(evento)
    _bloco_maturidade(d, mat)

    st.caption("Leitura educacional de estrutura de mercado, não recomendação.")


def _barra_maturidade(grad: str, marcos: list, voce_frac: float, voce_label: str, voce_cor: str) -> str:
    def _m(frac, label):
        return (f'<div style="position:absolute;left:{frac * 100:.1f}%;top:20px;transform:translateX(-50%);'
                f'text-align:center;font-size:0.70rem;line-height:1.4;color:#64748B;'
                f'font-weight:500;white-space:nowrap;">'
                f'<div style="width:1px;height:12px;background:#CBD5E1;margin:0 auto 5px;"></div>{label}</div>')
    barra = (f'<div style="position:relative;height:14px;border-radius:999px;overflow:hidden;'
             f'background:linear-gradient(90deg,{grad});box-shadow:inset 0 0 0 1px rgba(11,31,42,.05);"></div>')
    voce = (f'<div style="position:absolute;left:{min(max(voce_frac * 100, 2), 98):.1f}%;top:-40px;'
            f'transform:translateX(-50%);text-align:center;white-space:nowrap;">'
            f'<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.10em;text-transform:uppercase;'
            f'color:{voce_cor};opacity:.72;">você está aqui</div>'
            f'<div style="font-size:0.98rem;font-weight:800;color:{voce_cor};line-height:1.15;">{voce_label}</div>'
            f'<div style="color:{voce_cor};font-size:0.72rem;line-height:1;margin-top:1px;">▾</div></div>')
    return (f'<div style="position:relative;margin:54px 0 70px;">{barra}'
            + "".join(_m(f, lbl) for f, lbl in marcos) + voce + "</div>")


def _bloco_maturidade(d: dict, mat: dict) -> None:
    """Maturidade por dois eixos (esticamento MM200 + tempo desde o fundo maior) + anatomia."""
    if mat and not mat.get("erro") and mat.get("meses_desde_fundo"):
        st.markdown('<div class="ciano-label" style="margin-top:14px;">⏳ Maturidade da alta atual</div>',
                    unsafe_allow_html=True)

        # Eixo 1 — esticamento (distância da MM200 semanal)
        dist, p75 = mat["dist_atual"], mat["p75"]
        lo, hi = -35.0, max(dist + 8, 85.0)
        def fr(x):
            return max(0.0, min(1.0, (x - lo) / (hi - lo)))
        z0, z1 = fr(0) * 100, fr(p75) * 100
        grad1 = (f"#22C55E 0%,#22C55E {z0:.1f}%,#EAB308 {z0:.1f}%,#EAB308 {z1:.1f}%,"
                 f"#EF4444 {z1:.1f}%,#EF4444 100%")
        marcos1 = [(fr(0), "MM200<br>(0%)"), (fr(p75), f"esticado<br>p75 +{p75:.0f}%")]
        cor1 = "#DC2626" if dist > p75 else "#B45309" if dist > 0 else "#15803D"
        qd = mat.get("queda_desde_topo")
        qd_txt = f' · já {qd:+.0f}% do topo de 12m' if qd is not None and qd < 0 else ''
        st.markdown('<div style="font-size:0.82rem;font-weight:700;margin-bottom:2px;">Esticamento — '
                    f'distância da média de 200 semanas{qd_txt}</div>', unsafe_allow_html=True)
        st.markdown(_barra_maturidade(grad1, marcos1, fr(dist), f"{dist:+.0f}%", cor1),
                    unsafe_allow_html=True)

        # Eixo 2 — tempo desde o último fundo maior
        meses, im, ix = mat["meses_desde_fundo"], mat["inter_med"], mat["inter_max"]
        hi2 = max(meses * 1.1, (ix or meses) * 1.15)
        def fr2(x):
            return max(0.0, min(1.0, x / hi2))
        t0, t1 = fr2(im) * 100, fr2(ix) * 100
        grad2 = (f"#22C55E 0%,#22C55E {t0:.1f}%,#EAB308 {t0:.1f}%,#EAB308 {t1:.1f}%,"
                 f"#EF4444 {t1:.1f}%,#EF4444 100%")
        marcos2 = [(fr2(im), f"típico<br>{im}m"), (fr2(ix), f"recorde<br>{ix}m")]
        cor2 = "#DC2626" if meses >= ix else "#B45309" if meses > im else "#15803D"
        fd = mat["fundo_atual"]["data"]
        st.markdown('<div style="font-size:0.82rem;font-weight:700;margin-bottom:2px;">Tempo — meses '
                    f'desde o último fundo maior ({fd})</div>', unsafe_allow_html=True)
        st.markdown(_barra_maturidade(grad2, marcos2, fr2(meses), f"{meses}m", cor2),
                    unsafe_allow_html=True)

        # Síntese
        ze = "zona de topo" if dist > p75 else "neutro" if dist > 0 else "zona de fundo"
        lt = ("no recorde do ciclo" if meses >= ix
              else "perto do fim do ciclo" if meses > im
              else "ainda longe do fim")
        st.markdown(
            f"**Preço:** Ibov **{dist:+.0f}%** da MM200 — {ze}.  \n"
            f"**Tempo:** **{meses}m** desde o fundo — {lt} (típico {im}m, recorde {ix}m)."
        )
        st.caption("Fundos maiores (queda ≥15% da MM200 semanal): "
                   + ", ".join(f["data"] for f in mat["fundos"]) + ".")


def _bloco_gatilhos(mat: dict) -> None:
    """⚠️ O que derruba daqui — gatilhos de queda monitoráveis, com número ao vivo
    e limiar de alerta. Canal fiscal → juro (NTN-B) → risco (CDS) → câmbio."""
    import cambio as cmb
    import macro as mac

    cds = dol_var = ntnb = None
    try:
        a = (cmb.buscar_cambio() or {}).get("atual", {})
        cds, dol_var = a.get("cds"), a.get("dolar_var_ano")
    except Exception:  # noqa: BLE001
        pass
    try:
        b = (mac.buscar_macro() or {}).get("brasil", {})
        ntnb = (b.get("ntnb_10a") or {}).get("valor")
    except Exception:  # noqa: BLE001
        pass

    st.markdown('<div class="ciano-label" style="margin-top:16px;">⚠️ O que derruba daqui</div>',
                unsafe_allow_html=True)
    st.caption("Gatilhos monitoráveis do canal fiscal → juro → risco → câmbio. Cada um tem um número "
               "de hoje e um limiar de alerta. Não é previsão — é um painel de vigilância.")

    cards = ""
    if cds is not None:
        cor = "vermelho" if cds > 160 else "amarelo" if cds > 130 else "verde"
        cards += _card_alavanca(
            "Prêmio de risco · CDS 5a", cor, f"{cds:.0f} bps",
            "Dispara se sair de <130 para >160 bps. O CDS é o driver dominante do dólar (corr ~0,80).")
    if ntnb is not None:
        cor = "vermelho" if ntnb > 8 else "amarelo" if ntnb > 7 else "verde"
        cards += _card_alavanca(
            "Custo de oportunidade · NTN-B 10a", cor, f"{ntnb:.2f}%",
            "Dispara se a real longa passar de 8%. É o custo de oportunidade do valuation: sobe, o P/L justo cai.")
    if dol_var is not None:
        cor = "vermelho" if dol_var > 8 else "amarelo" if dol_var > 0 else "verde"
        cards += _card_alavanca(
            "Câmbio · USD/BRL no ano", cor, f"{dol_var:+.0f}%",
            "Real fraco com o CDS abrindo junto = fuga de capital. Estrangeiro saindo derruba o Ibov rápido.")
    if mat and mat.get("dist_atual") is not None:
        dist, p75 = mat["dist_atual"], mat.get("p75") or 40
        cor = "vermelho" if dist > p75 else "amarelo" if dist > 0 else "verde"
        qd = mat.get("queda_desde_topo")
        extra = f" · já {qd:+.0f}% do topo" if qd is not None and qd < 0 else ""
        cards += _card_alavanca(
            "Maturidade · esticamento MM200", cor, f"{dist:+.0f}%{extra}",
            f"Choque fiscal pega a bolsa cara e madura (topos passaram de +{p75:.0f}%). Margem de ciclo menor.")

    if cards:
        st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:12px;">{cards}</div>',
                    unsafe_allow_html=True)
    else:
        st.info("Gatilhos indisponíveis (abra as abas Câmbio/Macro uma vez para carregar CDS e NTN-B).")
    st.caption("🟢 tranquilo · 🟡 atenção · 🔴 gatilho ativo. A cadeia: fiscal sem âncora → juro (NTN-B) "
               "sobe e CDS abre → dólar dispara → BC aperta → múltiplo comprime. Fontes: "
               "worldgovernmentbonds (CDS), BCB (NTN-B), Yahoo (USD/BRL).")


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


@st.cache_data(ttl=3600, show_spinner=False)
def _lucro_ibov_agregado() -> dict:
    """Crescimento de lucro do Ibov (5a), para a alavanca Lucro virar data-driven."""
    try:
        import crescimento
        import indices_b3
        ibov = indices_b3.componentes("IBOV").get("tickers", [])
        return crescimento.crescimento_agregado(ibov) if ibov else {}
    except Exception:  # noqa: BLE001
        return {}


def _alavanca_lucro(ag: dict):
    """(cor, valor, descrição) da alavanca Lucro a partir do crescimento agregado."""
    cagr = (ag or {}).get("lucro_cagr_mediano")
    caindo = (ag or {}).get("pct_caindo")
    if cagr is None:
        return "amarelo", "s/ dado", "Crescimento de lucro indisponível agora (Yahoo)."
    if cagr >= 5 and (caindo or 0) < 45:
        cor = "verde"
    elif cagr < 0 or (caindo or 0) >= 60:
        cor = "vermelho"
    else:
        cor = "amarelo"
    val = f"{cagr:+.0f}%/a"
    cai_txt = (f" {caindo:.0f}% das empresas têm lucro menor que há 5 anos — a queda se concentra nos "
               "pesos-pesados de commodities." if caindo is not None else "")
    desc = (f"Lucro mediano do Ibov cresce {cagr:+.0f}%/a em 5 anos (LPA "
            f"{ag.get('lpa_cagr_mediano'):+.0f}%/a).{cai_txt}")
    return cor, val, desc


# Status discreto (bolinha + rótulo) por sinal — mantém os cards visualmente uniformes.
_STATUS_ALAVANCA = {
    "verde": ("Favorável", "#16A34A"),
    "amarelo": ("Neutro", "#D97706"),
    "vermelho": ("Pressão", "#DC2626"),
}


def _status_alavanca(chave: str):
    return _STATUS_ALAVANCA.get((chave or "").split("-")[0])


def _card_alavanca(nome: str, cor_chave: str, valor: str, desc: str) -> str:
    status = _status_alavanca(cor_chave)
    if status:
        rot, cor_dot = status
        chip = (f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:0.64rem;'
                f'font-weight:600;color:#64748B;letter-spacing:.02em;">'
                f'<span style="width:7px;height:7px;border-radius:50%;background:{cor_dot};"></span>'
                f'{html.escape(rot)}</span>')
    else:
        chip = ""
    return (
        f'<div style="flex:1 1 210px;min-width:190px;background:{COR_CARD};'
        f'border:1px solid {COR_BORDA};border-top:3px solid {COR_NAVY};border-radius:10px;padding:13px 15px;'
        f'box-shadow:0 1px 2px rgba(19,34,74,.05);">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:3px;">'
        f'<span style="font-size:0.68rem;letter-spacing:.05em;text-transform:uppercase;color:#64748B;font-weight:700;">{html.escape(nome)}</span>'
        f'{chip}</div>'
        f'<div style="font-size:1.2rem;font-weight:800;color:{COR_INK};margin:2px 0 5px;letter-spacing:-.01em;">{html.escape(valor)}</div>'
        f'<div style="font-size:0.72rem;color:#475569;line-height:1.45;">{html.escape(desc)}</div></div>'
    )


def _caixa_insights(frases: list) -> None:
    """Caixinha de 'insights da tela': 1-3 observações por regra sobre o que está nos dados."""
    frases = [f for f in frases if f]
    if not frases:
        return
    itens = "".join(f'<li style="margin-bottom:5px;color:#132244;">{html.escape(f)}</li>' for f in frases)
    st.markdown(
        '<div style="background:#ECF8FA;border:1px solid #CDEBF0;border-left:3px solid #3FD0E0;'
        'border-radius:12px;padding:12px 16px;margin:4px 0 16px;">'
        '<div style="font-size:0.7rem;letter-spacing:.12em;text-transform:uppercase;color:#00586A;'
        'margin-bottom:6px;font-weight:700;">💡 Insights da tela</div>'
        f'<ul style="margin:0;padding-left:18px;font-size:0.9rem;line-height:1.55;">{itens}</ul></div>',
        unsafe_allow_html=True,
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

    # --- insights da tela (nível regra, sem IA) ---
    _ins = []
    _mat = ibov_ciclo.buscar_maturidade()
    if _mat and not _mat.get("erro") and _mat.get("meses_desde_fundo"):
        _ins.append(f"Ciclo maduro por dois eixos: +{_mat['dist_atual']:.0f}% acima da MM200 (zona de topo) "
                    f"e {_mat['meses_desde_fundo']} meses desde o fundo de {_mat['fundo_atual']['data']}.")
    if viv.get("selic") is not None:
        jr = f" (real ~{viv['juro_real']:.1f}%)" if viv.get("juro_real") is not None else ""
        _ins.append(f"Juro é a alavanca-mãe: Selic {viv['selic']:.1f}%{jr} — a direção dela decide entre o "
                    "caminho 2016-19 (alta) e o 2011-15 (travado).")
    if viv.get("pl_small") and viv.get("pl_grande"):
        _ins.append(f"O 'barato' está nas small caps: grandes ~{viv['pl_grande']:.1f}x vs "
                    f"small ~{viv['pl_small']:.1f}x.")
    _caixa_insights(_ins)

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
    lucro_cor, lucro_val, lucro_desc = _alavanca_lucro(_lucro_ibov_agregado())
    cards = (
        _card_alavanca("Lucro (crescimento 5a)", lucro_cor, lucro_val, lucro_desc)
        + _card_alavanca("Múltiplo", alav.get("multiplo", ""), pl_txt + ey_txt.strip(), mult_desc)
        + _card_alavanca("Juro", alav.get("juro", ""), juro_txt, juro_desc)
        + _card_alavanca("Fluxo / alocação", alav.get("fluxo", ""), "Sub-alocado", "Local pouco em bolsa; energia potencial que espera o juro cair.")
    )
    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:12px;">{cards}</div>', unsafe_allow_html=True)

    # --- case base histórico ---
    st.markdown('<div class="ciano-label" style="margin-top:16px;">📚 Case base — ciclos desde 1994</div>',
                unsafe_allow_html=True)
    dfh = pd.DataFrame([
        {"Período": e["periodo"], "Governo": e["governo"],
         "Lucro": _emoji_alavanca(e["alavancas"].get("lucro", "")),
         "Múlt.": _emoji_alavanca(e["alavancas"].get("multiplo", "")),
         "Juro": _emoji_alavanca(e["alavancas"].get("juro", "")),
         "Fluxo": _emoji_alavanca(e["alavancas"].get("fluxo", "")),
         "O que o Ibov fez depois": e.get("ibov_resumo") or e.get("ibov_desfecho", "")}
        for e in base.get("episodios", [])
    ])
    st.dataframe(dfh, hide_index=True, use_container_width=True)
    st.caption("🟢 a favor · 🟡 neutro · 🔴 contra. Padrão histórico: **nenhum bull secular com juro subindo** — "
               "a ignição foi sempre a Selic cedendo.")

    # Seção de ciclo (fundida aqui): onde estamos no ciclo por preço/tempo.
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F2;margin:22px 0 6px;'>", unsafe_allow_html=True)
    _aba_ciclo()


# Episódios históricos para ancorar a leitura dos gráficos de câmbio.
_EVENTOS_CAMBIO = [
    ("2015-09", "Crise fiscal 2015"),
    ("2020-03", "Covid 2020"),
    ("2022-10", "Eleição 2022"),
    ("2024-12", "Susto fiscal 2024"),
    ("2026-10", "Pós-eleição 2026"),
]


def _anota_eventos(dfbase, campo: str, cor: str = "#94A3B8"):
    ev = pd.DataFrame([{"data": pd.to_datetime(d + "-01"), "label": t} for d, t in _EVENTOS_CAMBIO])
    ev = ev[ev["data"] >= dfbase["data"].min()]
    regua = alt.Chart(ev).mark_rule(color=cor, strokeDash=[3, 3], opacity=0.6).encode(x="data:T")
    txt = alt.Chart(ev).mark_text(
        angle=270, align="left", baseline="middle", dx=5, fontSize=9, color="#334155",
    ).encode(x="data:T", y=alt.value(10), text="label:N")
    return regua + txt


def _aba_cambio() -> None:
    import cambio as cmb

    st.markdown('<div class="ciano-label">Juro × Risco × Câmbio</div>', unsafe_allow_html=True)
    st.caption("O que mexe no real: risco-país e dólar andam quase colados; o carry (juro real BR−EUA) é o "
               "reforço. Fontes: BCB, Yahoo, BLS, Ipeadata (EMBI) e worldgovernmentbonds (CDS 5a). Cache 12h.")
    if st.button("Atualizar câmbio", type="primary", key="cambio_upd"):
        with st.spinner("Buscando câmbio, carry e risco…"):
            st.session_state.cambio = cmb.buscar_cambio(usar_cache=False)
    dados = st.session_state.get("cambio")
    if dados is None:
        with st.spinner("Carregando câmbio, carry e risco (pode levar ~1 min na 1ª vez)…"):
            dados = cmb.buscar_cambio()
            st.session_state.cambio = dados
    if dados.get("erro"):
        st.error(dados["erro"])
        return

    a = dados["atual"]
    if dados.get("aviso"):
        st.warning(f"⚠️ {dados['aviso']}")

    # --- insights da tela (nível regra, sem IA) ---
    _ins = []
    if a.get("cds") is not None and a.get("cds_min") is not None:
        if a["cds"] <= a["cds_min"] * 1.3:
            _ins.append(f"Risco-país (CDS) em {a['cds']:.0f} bps — perto da mínima histórica "
                        f"(faixa {a['cds_min']:.0f}–{a['cds_max']:.0f}): mercado precifica pouco risco fiscal.")
        elif a["cds"] >= a["cds_max"] * 0.8:
            _ins.append(f"Risco-país (CDS) em {a['cds']:.0f} bps — ELEVADO (perto do topo da faixa "
                        f"{a['cds_min']:.0f}–{a['cds_max']:.0f}): sinal de estresse fiscal.")
    if a.get("dolar_var_ano") is not None:
        v = a["dolar_var_ano"]
        _ins.append(f"Dólar {v:+.0f}% no ano (R$ {a['dolar']:.2f}) — real {'forte' if v < 0 else 'fraco'}.")
    if a.get("carry") is not None and a["carry"] >= 4:
        _ins.append(f"Carry alto: +{a['carry']:.1f} pp de juro real BR−EUA — atrai capital, mas só vira "
                    "real forte se o risco seguir baixo.")
    _caixa_insights(_ins)

    # --- leitura de hoje: 3 cartões ---
    risco_cor = "verde" if (a.get("cds") and a.get("cds_min") and a["cds"] <= a["cds_min"] * 1.4) else "amarelo"
    cds_txt = f"{a['cds']:.0f} bps" if a.get("cds") is not None else "—"
    cds_desc = (f"perto da mínima (faixa {a['cds_min']:.0f}–{a['cds_max']:.0f})"
                if a.get("cds_min") else "CDS 5 anos do Brasil")
    carry_txt = f"+{a['carry']:.1f} pp" if a.get("carry") is not None else "—"
    carry_desc = (f"BR {a['br_real']:.1f}% − EUA {a['us_real']:.1f}% · alto atrai capital"
                  if a.get("br_real") is not None and a.get("us_real") is not None else "juro real BR − EUA")
    dol_txt = f"R$ {a['dolar']:.2f}".replace(".", ",") if a.get("dolar") is not None else "—"
    dol_desc = (f"{a['dolar_var_ano']:+.1f}% no ano" if a.get("dolar_var_ano") is not None else "USD/BRL")
    cards = (
        _card_alavanca("Risco-país (CDS 5a)", risco_cor, cds_txt, cds_desc)
        + _card_alavanca("Carry (juro real BR−EUA)", "verde" if (a.get("carry") or 0) >= 4 else "amarelo",
                         carry_txt, carry_desc)
        + _card_alavanca("Dólar", "", dol_txt, dol_desc)
    )
    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:12px;">{cards}</div>', unsafe_allow_html=True)

    corr = a.get("corr_risco_dolar")
    _cds_v, _cds_mn = a.get("cds"), a.get("cds_min")
    _risco_baixo = bool(_cds_v and _cds_mn and _cds_v <= _cds_mn * 1.4)
    if _risco_baixo:
        _frase, _corl, _bg, _bd = (
            "risco baixo + carry alto → ambiente favorável ao real.", "#15803D", "#ECFDF3", "#BBF7D0")
        _resto = ("O mercado precifica pouco risco fiscal, e por isso o real se fortaleceu. "
                  "É a evidência da alavanca risco/fluxo da tese (aba Cenários).")
    else:
        _frase, _corl, _bg, _bd = (
            "risco subindo → o real perde o escudo do risco baixo.", "#B45309", "#FFF7ED", "#FED7AA")
        _resto = ("O CDS saiu da mínima — se continuar abrindo, puxa o dólar e aperta o juro "
                  "(a cadeia dos gatilhos na aba Cenários).")
    st.markdown(
        f'<div style="background:{_bg};border:1px solid {_bd};border-left:3px solid {_corl};'
        'border-radius:12px;padding:13px 16px;margin:14px 0 6px;font-size:0.95rem;color:#132244;">'
        f'Leitura de hoje: <b style="color:{_corl};">{_frase}</b> {_resto}</div>',
        unsafe_allow_html=True,
    )
    _cds_dt = a.get("cds_data")
    _stale = " (último fechamento disponível)" if a.get("cds_stale") else ""
    st.caption(
        f"Fontes: BCB (Selic/IPCA), Yahoo (USD/BRL, Treasury), BLS (CPI), Ipeadata (EMBI), "
        f"worldgovernmentbonds (CDS{f', {_cds_dt}' if _cds_dt else ''}{_stale}). "
        f"Painel montado em {dados.get('atualizado_em', '—')} · cache 12h."
    )

    df = pd.DataFrame(dados["serie"])
    df["data"] = pd.to_datetime(df["data"] + "-01")

    # --- Gráfico do CDS 5 anos: histórico + onde estamos ---
    st.markdown('<div class="ciano-label" style="margin-top:14px;">📊 CDS 5 anos do Brasil — onde estamos</div>',
                unsafe_allow_html=True)
    dfcds = df.dropna(subset=["cds"])
    if dfcds.empty:
        st.caption("Série do CDS indisponível no momento (fonte worldgovernmentbonds instável).")
    else:
        cds_now = float(dfcds["cds"].iloc[-1])
        cds_lo, cds_hi = float(dfcds["cds"].min()), float(dfcds["cds"].max())
        pct = float((dfcds["cds"] <= cds_now).mean() * 100)
        eixo_xc = alt.X("data:T", title=None, axis=alt.Axis(labelColor=COR_LIGHT, grid=False))
        linha = alt.Chart(dfcds).mark_line(color="#DC2626", strokeWidth=1.8).encode(
            x=eixo_xc,
            y=alt.Y("cds:Q", title="CDS 5 anos (bps)", scale=alt.Scale(zero=False),
                    axis=alt.Axis(labelColor=COR_LIGHT, gridOpacity=0.12)),
            tooltip=[alt.Tooltip("data:T", title="Mês"), alt.Tooltip("cds:Q", title="CDS (bps)", format=".0f")],
        )
        regra_now = alt.Chart(pd.DataFrame({"y": [cds_now]})).mark_rule(
            color="#DC2626", strokeDash=[4, 3], opacity=.45).encode(y="y:Q")
        ponto = alt.Chart(dfcds.iloc[[-1]]).mark_point(
            color="#DC2626", size=80, filled=True).encode(x="data:T", y="cds:Q")
        chc = alt.layer(linha, regra_now, ponto, _anota_eventos(dfcds, "cds")).properties(height=280)
        chc = chc.configure_view(strokeWidth=0).configure(background="rgba(0,0,0,0)")
        st.altair_chart(chc, use_container_width=True)
        zona = ("perto da MÍNIMA" if pct <= 25 else "perto da MÁXIMA" if pct >= 75 else "no meio da faixa")
        st.caption(
            f"Hoje ~{cds_now:.0f} bps · faixa histórica {cds_lo:.0f}–{cds_hi:.0f} bps desde 2017 · "
            f"percentil {pct:.0f}% ({zona}). Quanto maior, mais caro o mercado cobra pra 'segurar' risco Brasil. "
            "Fonte: worldgovernmentbonds (CDS 5a) — fechamento diário, pode ficar ~15-20 bps abaixo do "
            "intradiário em dias de estresse.")

    # --- Gráfico 1: risco x dólar (eixos independentes) ---
    st.markdown('<div class="ciano-label" style="margin-top:14px;">📈 Risco e dólar, lado a lado</div>',
                unsafe_allow_html=True)
    base = alt.Chart(df)
    eixo_x = alt.X("data:T", title=None, axis=alt.Axis(labelColor=COR_LIGHT, grid=False))
    l_risco = base.mark_line(color="#F87171", strokeWidth=1.8).encode(
        x=eixo_x,
        y=alt.Y("risco:Q", title="Risco-país (EMBI-equiv, bps)",
                axis=alt.Axis(titleColor="#F87171", labelColor="#F87171", grid=False)),
        tooltip=[alt.Tooltip("data:T", title="Mês"), alt.Tooltip("risco:Q", title="Risco (bps)", format=".0f")],
    )
    l_dolar = base.mark_line(color="#4C8DFF", strokeWidth=1.8).encode(
        x=eixo_x,
        y=alt.Y("dolar:Q", title="Dólar (R$)", scale=alt.Scale(zero=False),
                axis=alt.Axis(titleColor="#4C8DFF", labelColor="#4C8DFF", grid=False)),
        tooltip=[alt.Tooltip("data:T", title="Mês"), alt.Tooltip("dolar:Q", title="Dólar (R$)", format=".2f")],
    )
    ch1 = alt.layer(l_risco, l_dolar, _anota_eventos(df, "risco")).resolve_scale(y="independent")
    ch1 = ch1.properties(height=330).configure_view(strokeWidth=0).configure(background="rgba(0,0,0,0)")
    st.altair_chart(ch1, use_container_width=True)
    cap = "As duas linhas sobem e descem quase coladas"
    if corr is not None:
        cap += f" — correlação de {corr:.2f} nas variações de 12 meses"
    st.caption(cap + ". Picos de risco (2015, 2020) batem com saltos do dólar. "
               "Risco = EMBI até 2024 + CDS ao vivo (na escala do EMBI).")

    # --- Gráfico 2: carry no tempo (aprendizado) ---
    st.markdown('<div class="ciano-label" style="margin-top:10px;">🎓 Carry — juro real BR − EUA</div>',
                unsafe_allow_html=True)
    dfc = df.dropna(subset=["carry"])
    area = alt.Chart(dfc).mark_area(
        line={"color": "#EAB308", "strokeWidth": 1.8}, color="rgba(234,179,8,0.14)",
    ).encode(
        x=alt.X("data:T", title=None, axis=alt.Axis(labelColor=COR_LIGHT, grid=False)),
        y=alt.Y("carry:Q", title="Carry (pontos)", axis=alt.Axis(labelColor=COR_LIGHT, gridOpacity=0.12)),
        tooltip=[alt.Tooltip("data:T", title="Mês"), alt.Tooltip("carry:Q", title="Carry (pp)", format="+.1f")],
    )
    ch2 = alt.layer(area, _anota_eventos(dfc, "carry")).properties(height=250)
    ch2 = ch2.configure_view(strokeWidth=0).configure(background="rgba(0,0,0,0)")
    st.altair_chart(ch2, use_container_width=True)
    st.caption("O carry é a ISCA (prêmio de juro real por ficar no real) — mas sozinho não segura o câmbio: "
               "é mais lento e previsível que o risco. Subiu forte no ciclo de alta da Selic (2021-22) e segue "
               "alto hoje. Compare com o dólar acima: o carry importa, mas o risco manda.")
    st.caption("Leitura educacional da relação juro-risco-câmbio, não recomendação de investimento.")


def _fmt_mi(v: float) -> str:
    """R$ compacto: bilhões (1 casa) quando grande, senão milhões. Formato BR."""
    if abs(v) >= 1000:
        return f"R$ {v / 1000:.1f}".replace(".", ",") + " bi"
    s = f"{v:,.0f}".replace(",", ".")
    return f"R$ {s} mi"


def _aba_estrangeiro() -> None:
    import fluxo_b3

    st.markdown('<div class="ciano-label">Fluxo do estrangeiro — B3, mercado à vista</div>',
                unsafe_allow_html=True)
    st.caption("Saldo diário do investidor estrangeiro no mercado à vista de ações — número OFICIAL da B3 "
               "(sai em D+2), buscado automaticamente. Positivo = entrada, negativo = saída (R$ mi).")

    if st.button("Atualizar fluxo", type="primary", key="fluxo_upd"):
        with st.spinner("Buscando o fluxo da B3…"):
            st.session_state.fluxo = fluxo_b3.buscar_fluxo(usar_cache=False)
    dados = st.session_state.get("fluxo")
    if dados is None:
        with st.spinner("Buscando o fluxo da B3…"):
            dados = fluxo_b3.buscar_fluxo()
            st.session_state.fluxo = dados
    if dados.get("erro"):
        st.error(dados["erro"])
        _fluxo_explicacao()
        return
    if dados.get("aviso"):
        st.warning(f"⚠️ {dados['aviso']}")

    base = pd.DataFrame(dados["serie"])
    base["data"] = pd.to_datetime(base["data"])
    base["saldo"] = pd.to_numeric(base["estrangeiro"], errors="coerce")
    base = base.dropna(subset=["saldo"]).sort_values("data").reset_index(drop=True)
    base["acum"] = base["saldo"].cumsum()
    base["tipo"] = base["saldo"].apply(lambda x: "Entrada" if x >= 0 else "Saída")

    a = dados["atual"]
    c = st.columns(4)
    c[0].metric("Último dia", _fmt_mi(a["ultimo_dia"]))
    c[1].metric("No mês", _fmt_mi(a["no_mes"]))
    c[2].metric(f"No ano ({a['ano']})", _fmt_mi(a["no_ano"]))
    c[3].metric("Média 21 pregões", _fmt_mi(a["mm21"]) if a.get("mm21") is not None else "—")

    # quem comprou mais no último pregão (a contraparte do estrangeiro)
    ult = base.iloc[-1]
    locais = {"Institucional": ult.get("institucional"), "Pessoa física": ult.get("pessoa_fisica"),
              "Inst. Financeira": ult.get("inst_financeira"), "Outros": ult.get("outros")}
    comprador = max((k for k in locais if locais[k] is not None),
                    key=lambda k: locais[k], default=None)

    _ins = [f"Último pregão ({a['ultima_data']}): estrangeiro "
            f"{'comprou' if a['ultimo_dia'] >= 0 else 'vendeu'} {_fmt_mi(abs(a['ultimo_dia']))}."]
    if comprador and locais[comprador] is not None and locais[comprador] > 0:
        _ins.append(f"Do outro lado, quem mais comprou foi {comprador} ({_fmt_mi(locais[comprador])}).")
    if a["no_ano"] < 0:
        _ins.append(f"No ano o estrangeiro está VENDEDOR líquido ({_fmt_mi(a['no_ano'])}) — "
                    "pressão sobre a bolsa e o real.")
    else:
        _ins.append(f"No ano o estrangeiro está COMPRADOR líquido ({_fmt_mi(a['no_ano'])}) — "
                    "fluxo a favor da bolsa.")
    _caixa_insights(_ins)

    st.markdown('<div class="ciano-label" style="margin-top:10px;">📊 Saldo diário (entrada × saída)</div>',
                unsafe_allow_html=True)
    eixo_x = alt.X("data:T", title=None, axis=alt.Axis(labelColor=COR_LIGHT, grid=False))
    bars = alt.Chart(base).mark_bar().encode(
        x=eixo_x,
        y=alt.Y("saldo:Q", title="Saldo diário (R$ mi)", axis=alt.Axis(labelColor=COR_LIGHT, gridOpacity=0.12)),
        color=alt.Color("tipo:N", scale=alt.Scale(domain=["Entrada", "Saída"], range=["#16A34A", "#DC2626"]),
                        legend=alt.Legend(title=None, orient="top-right")),
        tooltip=[alt.Tooltip("data:T", title="Data"), alt.Tooltip("saldo:Q", title="Saldo (R$ mi)", format=",.0f")],
    ).properties(height=240).configure_view(strokeWidth=0).configure(background="rgba(0,0,0,0)")
    st.altair_chart(bars, use_container_width=True)

    st.markdown('<div class="ciano-label" style="margin-top:6px;">📈 Acumulado na janela</div>',
                unsafe_allow_html=True)
    area = alt.Chart(base).mark_area(
        line={"color": "#0FA3B8", "strokeWidth": 2}, color="rgba(63,208,224,0.14)",
    ).encode(
        x=eixo_x,
        y=alt.Y("acum:Q", title="Acumulado (R$ mi)", axis=alt.Axis(labelColor=COR_LIGHT, gridOpacity=0.12)),
        tooltip=[alt.Tooltip("data:T", title="Data"), alt.Tooltip("acum:Q", title="Acumulado (R$ mi)", format=",.0f")],
    ).properties(height=220).configure_view(strokeWidth=0).configure(background="rgba(0,0,0,0)")
    st.altair_chart(area, use_container_width=True)
    st.caption(f"Janela: {base['data'].min():%d/%m/%Y}–{base['data'].max():%d/%m/%Y} ({len(base)} pregões). "
               f"Fonte: {dados.get('fonte', 'B3 via Dados de Mercado')}. "
               f"Buscado em {dados.get('atualizado_em', '—')} · cache 6h.")

    _fluxo_explicacao()


def _fluxo_explicacao() -> None:
    with st.expander("ℹ️ Como acompanhar o estrangeiro (oficial D+2 + proxies mais rápidos)"):
        st.markdown(
            "- **À vista oficial (D+2):** a B3 divulga o saldo do estrangeiro no mercado à vista **dois "
            "pregões depois**; os portais publicam entre ~8h e 10h do D+2. É o número que fecha a conta — "
            "e é esse que o app busca sozinho aqui.\n"
            "- **Intraday (tempo real):** agressão por corretora no fluxo do mini e do cheio (Profit, Tryd). "
            "Olhe as casas estrangeiras (Morgan Stanley, Goldman, JP Morgan, UBS, BofA, Citi). É ruidoso "
            "(elas também executam ordens de locais e HFT), mas dá a direção do próprio dia.\n"
            "- **D+1 (confirmação):** posições em aberto por tipo de investidor nos derivativos (dólar futuro, "
            "índice futuro, cupom cambial), publicadas pela B3 no dia seguinte — melhor sinal de hedge/posicionamento.\n"
            "- **Mensal (lento):** fluxo cambial do Banco Central (conta financeira) — não serve para leitura tática.\n\n"
            "**Combo prático:** agressão das corretoras estrangeiras no intraday → derivativos em D+1 para "
            "confirmar → à vista oficial em D+2 para fechar.")
    st.caption("Saldo oficial da B3 buscado automaticamente (D+2). Leitura de fluxo, não recomendação.")


def _checar_senha() -> bool:
    """Tela de login com senha única (guardada em st.secrets['app_password']).

    Se nenhuma senha estiver configurada (ex.: rodando local sem secrets), libera
    o acesso — assim o desenvolvimento não trava. No Streamlit Cloud, basta
    definir o segredo 'app_password' que a tela de login passa a valer.
    """
    try:
        senha_certa = str(st.secrets.get("app_password", "") or "")
    except Exception:  # noqa: BLE001 — sem arquivo de secrets
        senha_certa = ""
    if not senha_certa or st.session_state.get("_auth_ok"):
        return True

    def _validar():
        st.session_state["_auth_ok"] = (st.session_state.get("_senha", "") == senha_certa)
        st.session_state["_senha"] = ""

    st.markdown(
        '<div style="max-width:420px;margin:12vh auto 0;text-align:center;">'
        '<div class="topbar-brand" style="justify-content:center;margin-bottom:22px;">'
        f'<span class="mark">{_MARCA_SVG}</span><span class="wm" style="font-size:1.5rem;">Ciano</span></div>'
        '<div class="eyebrow" style="color:#0FA3B8;font-size:0.78rem;font-weight:700;'
        'letter-spacing:0.22em;text-transform:uppercase;margin-bottom:10px;">Acesso restrito</div>'
        '<h1 class="htitle" style="font-family:\'Space Grotesk\',sans-serif;font-weight:600;'
        'font-size:2rem;color:#0B1F2A;margin:0 0 6px;">Valuation Ciano</h1>'
        '<p style="color:#3A4D57;margin:0 0 18px;">Digite a senha de acesso para continuar.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    col = st.columns([1, 1.4, 1])[1]
    with col:
        st.text_input("Senha", type="password", key="_senha",
                      on_change=_validar, label_visibility="collapsed",
                      placeholder="Senha de acesso")
        if st.session_state.get("_auth_ok") is False:
            st.error("Senha incorreta. Tente novamente.")
    return False


def main() -> None:
    st.set_page_config(
        page_title="Valuation Ciano", page_icon="📈", layout="wide",
        initial_sidebar_state="collapsed",
    )
    _injetar_css()
    if not _checar_senha():
        st.stop()

    # --- Navegação no TOPO (pills) ---
    paginas_analise = ["🔎 Empresa", "📊 Screener", "⭐ Carteira", "🏅 Ranking"]
    paginas_mercado = ["🔀 Cenários", "📉 Macro", "💵 Câmbio", "🌎 Estrangeiro"]
    paginas_acomp = ["📰 Notícias", "🔔 Gatilhos"]
    ordem = paginas_analise + paginas_mercado + paginas_acomp

    pagina = _topbar(ordem)
    _hero(pagina)

    # Premissas aparecem só nas páginas de análise (num expander, não mais na lateral)
    if pagina in paginas_analise:
        with st.expander("⚙️ Premissas e cenários", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            tma = _pct_para_fracao(
                c1.number_input("TMA (%)", value=PREMISSAS_PADRAO["tma"] * 100, step=0.5)
            )
            retorno_alvo = _pct_para_fracao(
                c2.number_input("Retorno alvo P/L (%)", value=PREMISSAS_PADRAO["retorno_alvo_pl"] * 100, step=0.5)
            )
            anos_fase_1 = int(
                c3.number_input("Anos fase 1", value=PREMISSAS_PADRAO["anos_fase_1"], step=1, min_value=1)
            )
            anos_fase_2 = int(
                c4.number_input("Anos fase 2", value=PREMISSAS_PADRAO["anos_fase_2"], step=1, min_value=1)
            )
            st.markdown('<div class="ciano-label" style="margin:10px 0 6px;">Cenários — crescimento do EBIT</div>',
                        unsafe_allow_html=True)
            cols = st.columns(len(CENARIOS_PADRAO))
            valores_cenarios = {}
            for col, (nome, params) in zip(cols, CENARIOS_PADRAO.items()):
                col.markdown(f"**{nome.capitalize()}**")
                g1 = _pct_para_fracao(
                    col.number_input(f"{nome} — fase 1 (%)", value=params["crescimento_fase_1"] * 100,
                                     step=0.5, key=f"{nome}_g1")
                )
                g2 = _pct_para_fracao(
                    col.number_input(f"{nome} — fase 2 (%)", value=params["crescimento_fase_2"] * 100,
                                     step=0.5, key=f"{nome}_g2")
                )
                valores_cenarios[nome] = {"g1": g1, "g2": g2}

        prem = (tma, retorno_alvo, valores_cenarios, anos_fase_1, anos_fase_2)
        if pagina == "🔎 Empresa":
            _aba_empresa(*prem)
        elif pagina == "📊 Screener":
            _aba_screener(*prem)
        elif pagina == "⭐ Carteira":
            _aba_carteira(*prem)
        elif pagina == "🏅 Ranking":
            _aba_ranking(*prem)
    else:
        paginas_mercado_fn = {
            "🔀 Cenários": _aba_cenarios,
            "📉 Macro": _aba_macro, "💵 Câmbio": _aba_cambio,
            "🌎 Estrangeiro": _aba_estrangeiro,
            "📰 Notícias": _aba_noticias, "🔔 Gatilhos": _aba_gatilhos,
        }
        paginas_mercado_fn[pagina]()


if __name__ == "__main__":
    main()
