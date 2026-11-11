"""
Carteira do Cliente — app Streamlit (porta 8502).

Análise da carteira de um cliente e projeção do patrimônio (BIG NUMBERS) a cada
5 anos, em dois cenários:

- **Selic hoje**: a meta Selic atual (BC) e o IPCA esperado (Focus);
- **Média 20 anos**: a Selic e o IPCA médios (geométricos) dos últimos 20 anos.

Responde as duas perguntas do planejamento: quanto o cliente precisa aportar por
mês para atingir o objetivo, e quanto poderá retirar sem comer o poder de
compra. As posições podem vir da API Alia. A lógica fica em ``planejamento.py``
e ``alia.py``; aqui é só a interface.

Navegação por páginas na barra lateral (sem abas aninhadas). Os valores do
cliente e das premissas ficam em ``st.session_state`` fora das chaves dos
widgets — o Streamlit descarta o estado de widgets que não são desenhados na
página atual, e o cliente precisa sobreviver à troca de página.

Rodar:  py -m streamlit run app_cliente.py --server.port 8502 --theme.base light
"""

import json
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

import planejamento as pl
from app import _fmt_brl, _logo_data_uri

SGS_SELIC_MES, SGS_IPCA_MES = 4390, 433  # % ao mês (Selic acumulada / IPCA)
ANOS_HISTORICO = 20
# Usados só se o BC estiver fora do ar (apurados em out/2026).
REF_SELIC_HOJE, REF_IPCA_FOCUS = 13.75, 4.5
REF_SELIC_20A, REF_IPCA_20A = 10.15, 5.59

# Paleta clássica: marinho da marca, dourado envelhecido, tons neutros.
MARINHO, DOURADO, ARDOSIA, GRAFITE = "#0E2266", "#A8834A", "#8C9EB8", "#5B6478"
PALETA_CLASSES = ["#0E2266", "#A8834A", "#4A6FA5", "#6B8F71", "#8C9EB8",
                  "#A44A3F", "#C9B79C", "#2F4858", "#7D6B91", "#D4A373"]

NOVO = "Novo cliente"
PAGINAS = ["Visão geral", "Projeção", "Objetivo", "Cadastro", "Importar da Alia", "Premissas"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, .stApp, .stMarkdown, button, input, textarea, select {font-family: 'Inter', sans-serif;}
.stApp {background: #FAF8F3;}
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {max-width: 1180px; padding-top: 2.4rem; padding-bottom: 4rem;}
h1, h2, h3 {font-family: 'Cormorant Garamond', serif !important; color: #0E2266; font-weight: 600 !important;}

/* Barra lateral marinho */
section[data-testid="stSidebar"] {background: #0E2266; min-width: 340px !important;}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label p,
section[data-testid="stSidebar"] [role="radiogroup"] p {color: #E9E4D8;}
/* Navegação como menu: sem bolinhas; página atual em dourado com filete à esquerda */
section[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 7px 0 7px 12px; border-left: 2px solid transparent; cursor: pointer; width: 100%;}
section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {display: none;}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover p {color: #FFFFFF;}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {border-left-color: #A8834A;}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {color: #D9B77E; font-weight: 600;}
section[data-testid="stSidebar"] [role="radiogroup"] p {font-size: 1rem; letter-spacing: 0.01em;}
[data-testid="stAppDeployButton"] {display: none;}
.sb-logo {text-align: center; padding: 6px 0 4px 0;}
.sb-logo img {height: 64px;}
.sb-logo .tag {color: #A8834A; font-size: 0.68rem; letter-spacing: 0.32em; margin-top: 2px;}
.sb-rule {border: none; border-top: 1px solid rgba(233,228,216,0.18); margin: 18px 0;}
.sb-sec {color: #A8834A !important; font-size: 0.70rem; letter-spacing: 0.22em;
         text-transform: uppercase; margin: 0 0 6px 0;}

/* Cabeçalho da página */
.eyebrow {color: #A8834A; font-size: 0.74rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase;}
.titulo {font-family: 'Cormorant Garamond', serif; color: #0E2266; font-size: 2.6rem;
         font-weight: 600; line-height: 1.1; margin: 4px 0 2px 0;}
.subtitulo {color: #5B6478; font-size: 0.98rem; margin: 0;}
.regua {border: none; border-top: 1px solid #A8834A; width: 56px; margin: 16px 0 26px 0;}
.secao {font-family: 'Cormorant Garamond', serif; color: #0E2266; font-size: 1.45rem;
        font-weight: 600; margin: 34px 0 12px 0; padding-bottom: 6px; border-bottom: 1px solid #E7E2D8;}

/* Cartões */
.grade {display: grid; gap: 16px; margin: 6px 0 8px 0;}
.g4 {grid-template-columns: repeat(4, minmax(0, 1fr));}
.g3 {grid-template-columns: repeat(3, minmax(0, 1fr));}
@media (max-width: 1000px) {.g4, .g3 {grid-template-columns: repeat(2, minmax(0, 1fr));}}
.kpi {background: #FFFFFF; border: 1px solid #E7E2D8; border-radius: 6px; padding: 18px 20px;}
.kpi .rot {color: #8A8170; font-size: 0.70rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase;}
.kpi .val {font-family: 'Cormorant Garamond', serif; color: #0E2266; font-weight: 600;
           font-size: clamp(1.5rem, 2.4vw, 2.2rem); line-height: 1.15; margin: 8px 0 4px 0; white-space: nowrap;}
.kpi .det {color: #5B6478; font-size: 0.86rem; line-height: 1.45;}
.kpi.destaque {border-top: 2px solid #A8834A;}
.kpi .val .un {font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 500; color: #5B6478; margin-left: 2px;}
.kpi .renda {color: #3F6B4A; font-weight: 600; font-size: 0.98rem; margin-top: 10px;
             padding-top: 10px; border-top: 1px dashed #E7E2D8;}
.pos {color: #3F6B4A;} .neg {color: #A44A3F;}

.aviso {background: #FBF4EC; border-left: 3px solid #A8834A; color: #5A4A33;
        padding: 10px 14px; margin-bottom: 8px; font-size: 0.92rem; border-radius: 0 4px 4px 0;}
.passo {color: #A8834A; font-size: 0.74rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; margin-top: 26px;}
.nota {color: #8A8170; font-size: 0.82rem; line-height: 1.5; margin-top: 18px;}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 4px; font-weight: 500; letter-spacing: 0.02em; padding: 0.5rem 1.4rem;}
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {border: 1px solid #E7E2D8; border-radius: 6px;}
</style>
"""


# --------------------------------------------------------------------------- #
# Dados do Banco Central
# --------------------------------------------------------------------------- #
def _meses_completos(serie: list[dict], n: int) -> list[dict]:
    """Últimos ``n`` meses fechados (descarta o mês corrente, ainda parcial)."""
    hoje = date.today()
    atual = f"/{hoje.month:02d}/{hoje.year}"
    fechados = [p for p in serie if not p["data"].endswith(atual)]
    return fechados[-n:]


@st.cache_data(ttl=6 * 60 * 60, show_spinner="Consultando Selic e IPCA no Banco Central…")
def _taxas_bc() -> dict:
    import macro as mac

    out = {"erros": []}
    try:
        sel = mac._sgs(mac.SGS_SELIC, 1)
        out["selic_hoje"], out["selic_data"] = sel["valor"], sel["data"]
    except Exception as e:  # noqa: BLE001
        out["erros"].append(f"Selic atual: {e}")
    try:
        out["ipca_focus"] = mac._focus("IPCA")["valor"]
    except Exception as e:  # noqa: BLE001
        out["erros"].append(f"Focus IPCA: {e}")

    meses = ANOS_HISTORICO * 12
    for chave, codigo in (("selic", SGS_SELIC_MES), ("ipca", SGS_IPCA_MES)):
        try:
            serie = _meses_completos(mac._sgs(codigo, ANOS_HISTORICO + 1)["serie"], meses)
            out[f"{chave}_mensal"] = serie
            out[f"{chave}_20a"] = pl.media_anual_composta([p["valor"] for p in serie])
            out[f"{chave}_periodo"] = (serie[0]["data"][3:], serie[-1]["data"][3:])
        except Exception as e:  # noqa: BLE001
            out["erros"].append(f"{chave.upper()} histórico: {e}")
    return out


def _anual(serie: list[dict]) -> dict[int, float]:
    """Taxa acumulada por ano-calendário (só anos com 12 meses na série)."""
    por_ano: dict[int, list[float]] = {}
    for p in serie or []:
        por_ano.setdefault(int(p["data"][-4:]), []).append(p["valor"])
    out = {}
    for ano, vals in por_ano.items():
        if len(vals) == 12:
            f = 1.0
            for v in vals:
                f *= 1 + v / 100
            out[ano] = (f - 1) * 100
    return out


# --------------------------------------------------------------------------- #
# Formatação e blocos visuais
# --------------------------------------------------------------------------- #
def _rs(v: float) -> str:
    return f"R$ {_fmt_brl(v)}"


def _rs_curto(v: float) -> str:
    """R$ 1,25 mi / R$ 850 mil — para os números grandes dos cartões."""
    if abs(v) >= 1e9:
        return f"R$ {_fmt_brl(v / 1e9)} bi"
    if abs(v) >= 1e6:
        return f"R$ {_fmt_brl(v / 1e6)} mi"
    if abs(v) >= 1e4:
        return f"R$ {_fmt_brl(v / 1e3).split(',')[0]} mil"
    return _rs(v)


def _mes(v: float) -> str:
    """Valor mensal para cartão: número em destaque e "/mês" discreto."""
    return f'{_rs(v)}<span class="un">/mês</span>'


def _pct(v: float, casas: int = 2) -> str:
    return f"{v:.{casas}f}%".replace(".", ",")


def _html(txt: str) -> None:
    """Bloco HTML. O "$" de "R$" vira entidade: em markdown, um par de "$" vira LaTeX."""
    st.markdown(txt.replace("$", "&#36;"), unsafe_allow_html=True)


def _md(txt: str) -> str:
    return txt.replace("$", r"\$")


def _cabecalho(eyebrow: str, titulo: str, sub: str = "") -> None:
    _html(f'<div class="eyebrow">{eyebrow}</div><div class="titulo">{titulo}</div>'
          + (f'<p class="subtitulo">{sub}</p>' if sub else "") + '<hr class="regua">')


def _secao(txt: str) -> None:
    _html(f'<div class="secao">{txt}</div>')


def _kpi(rot: str, val: str, det: str = "", extra: str = "", classe: str = "") -> str:
    return (f'<div class="kpi {classe}"><div class="rot">{rot}</div><div class="val">{val}</div>'
            f'<div class="det">{det}</div>{extra}</div>')


def _grade(cartoes: list[str], colunas: int = 4) -> None:
    _html(f'<div class="grade g{colunas}">' + "".join(cartoes) + "</div>")


def _grafico(ch: alt.Chart, altura: int = 340) -> None:
    st.altair_chart(
        ch.properties(height=altura).configure(background="transparent", font="Inter")
          .configure_view(stroke=None)
          .configure_axis(labelColor=GRAFITE, titleColor=GRAFITE, gridColor="#ECE7DC",
                          domainColor="#D9D2C3", tickColor="#D9D2C3", labelFontSize=12)
          .configure_legend(labelColor=GRAFITE, labelFontSize=12, orient="bottom", title=None),
        width="stretch",
    )


# --------------------------------------------------------------------------- #
# Estado: cliente e premissas
# --------------------------------------------------------------------------- #
def _cliente_vazio() -> dict:
    return {"nome": "", "perfil": "Moderado", "aporte_mensal": 0.0, "renda_desejada": 10000.0,
            "anos_meta": 20, "pct_cdi": 100.0, "posicoes": []}


def _abrir(dados: dict | None, existe: bool) -> None:
    st.session_state["cliente"] = {**_cliente_vazio(), **(dados or {})}
    st.session_state["existe"] = existe
    st.session_state["ver"] = st.session_state.get("ver", 0) + 1  # renova as chaves dos campos


def _k(nome: str) -> str:
    """Chave de widget atrelada ao cliente aberto (troca de cliente = campos novos)."""
    return f"{nome}_{st.session_state.get('ver', 0)}"


def _rotulos_clientes(nomes: list[str]) -> dict[str, str]:
    """Nome e nº da conta lado a lado no seletor ("Fulano · 005407133")."""
    import alia

    contas = {k.lstrip("0"): v for k, v in alia.carregar_contas().items()}
    out = {}
    for n in nomes:
        if n.isdigit():  # ficha antiga, criada antes de a conta ter nome
            titular = contas.get(n.lstrip("0"))
            out[n] = f"{titular}  ·  {n}" if titular else f"Conta {n}  ·  sem nome"
        else:
            conta = (pl.carregar_cliente(n) or {}).get("alia_conta")
            out[n] = f"{n}  ·  {conta}" if conta else n
    return out


def _sidebar() -> str:
    uri = _logo_data_uri()
    if uri:
        _html_sb = (f'<div class="sb-logo"><img src="{uri}" alt="Ciano"/>'
                    f'<div class="tag">INVESTIMENTOS</div></div><hr class="sb-rule">')
        st.sidebar.markdown(_html_sb, unsafe_allow_html=True)

    nomes = pl.listar_clientes()
    pendente = st.session_state.pop("_selecionar", None)
    if pendente is not None:
        st.session_state["sel_cliente"] = pendente if pendente in nomes else NOVO
    st.sidebar.markdown('<p class="sb-sec">Cliente</p>', unsafe_allow_html=True)
    rotulos = _rotulos_clientes(nomes)
    nomes = sorted(nomes, key=lambda n: (n.isdigit(), n.lower()))  # contas sem nome por último
    escolha = st.sidebar.selectbox("Cliente", [NOVO] + nomes, key="sel_cliente",
                                   label_visibility="collapsed",
                                   format_func=lambda n: rotulos.get(n, n))
    if st.session_state.get("_aberto") != escolha:
        st.session_state["_aberto"] = escolha
        if pendente is None or escolha == NOVO:  # troca feita pelo usuário: recarrega do disco
            dados = pl.carregar_cliente(escolha) if escolha != NOVO else None
            _abrir(dados, existe=dados is not None)

    st.sidebar.markdown('<hr class="sb-rule"><p class="sb-sec">Navegação</p>', unsafe_allow_html=True)
    pag_pendente = st.session_state.pop("_ir_para", None)
    if pag_pendente:
        st.session_state["pagina"] = pag_pendente
    return st.sidebar.radio("Página", PAGINAS, key="pagina", label_visibility="collapsed")


def _premissas_padrao(bc: dict) -> None:
    padrao = {
        "p_selic_hoje": float(bc.get("selic_hoje") or REF_SELIC_HOJE),
        "p_ipca_hoje": float(bc.get("ipca_focus") or REF_IPCA_FOCUS),
        "p_selic_20": round(float(bc.get("selic_20a") or REF_SELIC_20A), 2),
        "p_ipca_20": round(float(bc.get("ipca_20a") or REF_IPCA_20A), 2),
        "p_ir": 15.0, "p_reajustar": True,
    }
    for k, v in padrao.items():
        st.session_state.setdefault(k, v)


def _cenarios(c: dict) -> dict:
    s, fator = st.session_state, c.get("pct_cdi", 100) / 100
    return {
        "Selic hoje": {"taxa": s.p_selic_hoje * fator, "selic": s.p_selic_hoje,
                       "inflacao": s.p_ipca_hoje, "cor": MARINHO},
        f"Média {ANOS_HISTORICO} anos": {"taxa": s.p_selic_20 * fator, "selic": s.p_selic_20,
                                         "inflacao": s.p_ipca_20, "cor": DOURADO},
    }


def _autosalvar(c: dict) -> None:
    """Cliente já cadastrado: grava sozinho quando algo muda (sem botão "salvar")."""
    if not st.session_state.get("existe") or not c.get("nome", "").strip():
        return
    no_disco = pl.carregar_cliente(c["nome"])
    if no_disco is None or json.dumps(no_disco, sort_keys=True, default=str) != \
            json.dumps(c, sort_keys=True, default=str):
        pl.salvar_cliente(c)


def _sem_carteira() -> None:
    st.info("Este cliente ainda não tem posições. Cadastre em **Cadastro** ou traga da "
            "Alia em **Importar da Alia**.")


# --------------------------------------------------------------------------- #
# Páginas
# --------------------------------------------------------------------------- #
def _pg_visao_geral(c: dict, an: dict) -> None:
    _cabecalho("Visão geral", c.get("nome") or "Novo cliente",
               f"Perfil {c['perfil'].lower()}" + (f" · posição de {_data_br(c['alia_data'])}"
                                                   if c.get("alia_data") else ""))
    if not an["total"]:
        _sem_carteira()
        return

    tem_custo = abs(an["resultado"]) > 0.005
    cls = "pos" if an["resultado"] >= 0 else "neg"
    _grade([
        _kpi("Patrimônio", _rs_curto(an["total"]), f"{len(an['ativos'])} ativos", classe="destaque"),
        _kpi("Resultado", f'<span class="{cls}">{_rs_curto(an["resultado"])}</span>',
             f"{_pct(an['rentab_pct'])} sobre o aplicado") if tem_custo
        else _kpi("Resultado", "—", "custo de aquisição não informado"),
        _kpi("Maior posição", _pct(an["maior_ativo"]["peso_pct"], 1), an["maior_ativo"]["ativo"]),
        _kpi("Diversificação", f"{an['n_efetivo']:.1f}".replace(".", ","),
             "nº efetivo de ativos"),
    ])
    for a in an["alertas"]:
        _html(f'<div class="aviso">{a}</div>')

    esq, dir_ = st.columns(2, gap="large")
    with esq:
        _secao("Alocação por classe")
        dfc = pd.DataFrame(an["classes"])
        _grafico(alt.Chart(dfc).mark_arc(innerRadius=78, stroke="#FAF8F3", strokeWidth=2).encode(
            theta="valor:Q",
            color=alt.Color("classe:N", scale=alt.Scale(range=PALETA_CLASSES),
                            legend=alt.Legend(columns=2)),
            tooltip=["classe", alt.Tooltip("peso_pct:Q", format=".1f", title="%"),
                     alt.Tooltip("valor:Q", format=",.2f", title="R$")],
        ))
    with dir_:
        _secao(f"Atual × perfil {c['perfil'].lower()}")
        comp = pd.DataFrame(pl.comparar_perfil(an["classes"], an["total"], pl.PERFIS[c["perfil"]]))
        longo = comp.melt(id_vars="classe", value_vars=["atual_pct", "alvo_pct"],
                          var_name="serie", value_name="pct")
        longo["serie"] = longo["serie"].map({"atual_pct": "Atual", "alvo_pct": "Perfil"})
        _grafico(alt.Chart(longo).mark_bar(size=9).encode(
            y=alt.Y("classe:N", title=None, sort=list(comp["classe"]), axis=alt.Axis(labelLimit=220)),
            x=alt.X("pct:Q", title="% do patrimônio"),
            yOffset="serie:N",
            color=alt.Color("serie:N", scale=alt.Scale(domain=["Atual", "Perfil"],
                                                       range=[MARINHO, DOURADO])),
            tooltip=["classe", "serie", alt.Tooltip("pct:Q", format=".1f")],
        ))

    _secao("Rebalanceamento sugerido")
    tab = comp[comp["dif_pp"].abs() >= 0.05].rename(columns={
        "classe": "Classe", "atual_pct": "Atual (%)", "alvo_pct": "Perfil (%)",
        "dif_pp": "Diferença (p.p.)", "ajuste_rs": "Comprar (+) / vender (−)"})
    st.dataframe(tab.style.format({"Atual (%)": "{:.1f}", "Perfil (%)": "{:.1f}",
                                   "Diferença (p.p.)": "{:+.1f}", "Comprar (+) / vender (−)": _rs}),
                 hide_index=True, width="stretch")

    _secao("Posições")
    cols = ["ativo", "classe", "valor_atual", "peso_pct"]
    nomes = ["Ativo", "Classe", "Valor atual", "Peso (%)"]
    if tem_custo:
        cols += ["valor_aplicado", "resultado", "rentab_pct"]
        nomes += ["Aplicado", "Resultado", "Rentab. (%)"]
    pos = pd.DataFrame(an["ativos"])[cols]
    pos.columns = nomes
    st.dataframe(pos.style.format({"Valor atual": _rs, "Aplicado": _rs, "Resultado": _rs,
                                   "Peso (%)": "{:.1f}", "Rentab. (%)": "{:+.1f}"}),
                 hide_index=True, width="stretch", height=min(38 * len(pos) + 40, 560))


def _pg_projecao(c: dict, an: dict) -> None:
    _cabecalho("Projeção · Big Numbers", c.get("nome") or "Novo cliente",
               "Onde o patrimônio pode chegar a cada 5 anos, em reais de hoje.")
    if not an["total"] and not c["aporte_mensal"]:
        _sem_carteira()
        return

    cenarios = _cenarios(c)
    with st.container(border=True):
        a, b, d = st.columns([1.1, 1, 1.4])
        c["aporte_mensal"] = a.number_input("Aporte mensal (R$)", value=float(c["aporte_mensal"]),
                                            step=500.0, min_value=0.0, key=_k("aporte"))
        c["pct_cdi"] = b.number_input("Rentabilidade (% da Selic)", value=float(c["pct_cdi"]),
                                      step=5.0, min_value=0.0, key=_k("pct_cdi"))
        escolha = d.radio("Cenário", list(cenarios), horizontal=True, key="cenario_proj")
    cenarios = _cenarios(c)
    cen = cenarios[escolha]
    s = st.session_state

    marcos = pl.big_numbers(an["total"], c["aporte_mensal"], cen["taxa"], cen["inflacao"],
                            s.p_ir, reajustar_aporte=s.p_reajustar)
    ano0 = date.today().year
    _grade([
        _kpi(f"Em {m['ano']} anos · {ano0 + m['ano']}", _rs_curto(m["real"]),
             f"nominal líquido {_rs_curto(m['liquido'])}"
             + (f" · {m['multiplo']:.1f}× o patrimônio atual".replace(".", ",") if m.get("multiplo") else ""),
             extra=f'<div class="renda">{_rs(m["renda_mensal"])} / mês'
                   f'<div class="det">retirada sem perder poder de compra</div></div>',
             classe="destaque")
        for m in marcos
    ], colunas=3)
    _html(f'<p class="nota">Selic {_pct(cen["selic"])} · inflação {_pct(cen["inflacao"])} · '
          f'juro real {_pct(pl.juro_real(cen["taxa"], cen["inflacao"]))} a.a. · patrimônio inicial '
          f'{_rs(an["total"])} · aporte de {_rs(c["aporte_mensal"])}/mês'
          f'{" corrigido pela inflação" if s.p_reajustar else ""} · IR de {_pct(s.p_ir, 1)} no resgate.</p>')

    _secao("Evolução do patrimônio")
    linhas, aportado = [], "Total aportado"
    for nome, cz in cenarios.items():
        for l in pl.projetar(an["total"], c["aporte_mensal"], cz["taxa"], 30, s.p_ir,
                             cz["inflacao"], s.p_reajustar):
            linhas.append({"ano": ano0 + l["ano"], "valor": l["real"], "serie": nome})
            if nome == escolha:
                linhas.append({"ano": ano0 + l["ano"], "serie": aportado,
                               "valor": l["investido"] / (1 + cz["inflacao"] / 100) ** l["ano"]})
    nomes = list(cenarios) + [aportado]
    _grafico(alt.Chart(pd.DataFrame(linhas)).mark_line(strokeWidth=2.4).encode(
        x=alt.X("ano:Q", title=None, axis=alt.Axis(format="d", values=[ano0 + i for i in range(0, 31, 5)])),
        y=alt.Y("valor:Q", title="R$ de hoje", axis=alt.Axis(format="~s")),
        color=alt.Color("serie:N", scale=alt.Scale(domain=nomes, range=[MARINHO, DOURADO, ARDOSIA])),
        strokeDash=alt.condition(alt.datum.serie == aportado, alt.value([5, 4]), alt.value([1, 0])),
        tooltip=["serie", "ano", alt.Tooltip("valor:Q", format=",.0f", title="R$")],
    ), altura=360)

    _secao("Os dois cenários lado a lado")
    tab = {}
    for nome, cz in cenarios.items():
        for m in pl.big_numbers(an["total"], c["aporte_mensal"], cz["taxa"], cz["inflacao"],
                                s.p_ir, reajustar_aporte=s.p_reajustar):
            linha = tab.setdefault(m["ano"], {"Ano": f"{m['ano']} anos ({ano0 + m['ano']})"})
            linha[f"{nome} — patrimônio"] = m["real"]
            linha[f"{nome} — retirada/mês"] = m["renda_mensal"]
    t = pd.DataFrame(tab.values())
    st.dataframe(t.style.format({k: _rs for k in t.columns if k != "Ano"}),
                 hide_index=True, width="stretch")
    _html('<p class="nota">Valores em reais de hoje, líquidos de IR. Projeções são estimativas, '
          'não promessa de retorno.</p>')


TIPOS_META = {"renda": "Renda mensal na aposentadoria", "valor": "Juntar um valor"}


def _pg_objetivo(c: dict, an: dict, bc: dict) -> None:
    _cabecalho("Objetivo · plano de aportes", c.get("nome") or "Novo cliente",
               "Quanto aportar por mês para chegar lá.")
    with st.container(border=True):
        tipo = st.radio("Objetivo", list(TIPOS_META), format_func=TIPOS_META.get, horizontal=True,
                        index=list(TIPOS_META).index(c.get("tipo_meta", "renda")), key=_k("tipo_meta"),
                        label_visibility="collapsed")
        c["tipo_meta"] = tipo
        a, b, d = st.columns(3)
        if tipo == "renda":
            c["renda_desejada"] = a.number_input(
                "Renda mensal desejada (R$ de hoje)", value=float(c["renda_desejada"]), step=1000.0,
                min_value=0.0, key=_k("renda"))
        else:
            c["valor_meta"] = a.number_input(
                "Valor a juntar (R$ de hoje)", value=float(c.get("valor_meta", 1_000_000.0)),
                step=50_000.0, min_value=0.0, key=_k("valor_meta"))
        c["anos_meta"] = int(b.number_input("Em quantos anos", value=int(c["anos_meta"]), step=1,
                                            min_value=1, max_value=50, key=_k("anos")))
        c["aporte_mensal"] = d.number_input("Aporte mensal atual (R$)", value=float(c["aporte_mensal"]),
                                            step=500.0, min_value=0.0, key=_k("aporte_obj"))

    s = st.session_state
    patrimonio, anos = an["total"], c["anos_meta"]
    cenarios = _cenarios(c)

    def alvo_de(cz):
        if tipo == "valor":
            return c.get("valor_meta", 0.0)
        return pl.patrimonio_para_renda(c["renda_desejada"], cz["taxa"], cz["inflacao"], s.p_ir)

    def aporte_de(cz, prazo):
        alvo = alvo_de(cz)
        if alvo is None:
            return None
        return pl.aporte_para_meta(alvo, patrimonio, cz["taxa"], cz["inflacao"], prazo,
                                   s.p_ir, s.p_reajustar)

    nome_cons, nome_otim = f"Média {ANOS_HISTORICO} anos", "Selic hoje"
    cons, otim = cenarios[nome_cons], cenarios[nome_otim]
    ap_cons, ap_otim = aporte_de(cons, anos), aporte_de(otim, anos)
    meta_txt = (f"renda de {_rs(c['renda_desejada'])}/mês para sempre" if tipo == "renda"
                else f"juntar {_rs(c.get('valor_meta', 0))}")

    # --- Sugestão em destaque ---
    _secao("Sugestão de aporte")
    if ap_cons is None:
        st.warning("No cenário conservador o juro real, depois do IR, é zero ou negativo: não há renda "
                   "perpétua possível. Use o objetivo “Juntar um valor” ou revise as premissas.")
        return
    atual = c["aporte_mensal"]
    if ap_cons == 0:
        status = "O patrimônio atual já é suficiente — não é preciso aportar."
    elif atual >= ap_cons:
        status = f"O aporte atual ({_rs(atual)}) já cobre o objetivo, com folga de {_rs(atual - ap_cons)}/mês."
    elif atual >= (ap_otim or 0):
        status = (f"O aporte atual ({_rs(atual)}) só chega lá se a Selic seguir alta. "
                  f"Para ter segurança, faltam {_rs(ap_cons - atual)}/mês.")
    else:
        status = f"Faltam {_rs(ap_cons - atual)}/mês em relação ao aporte atual ({_rs(atual)})."
    reaj = ", corrigido pela inflação a cada ano" if s.p_reajustar else ""
    def sem_aporte(cz) -> str:
        """Texto para quando o patrimônio atual já basta: em quanto tempo chega lá sozinho."""
        proj = pl.projetar(patrimonio, 0, cz["taxa"], 50, s.p_ir, cz["inflacao"], s.p_reajustar)
        ano = pl.ano_atinge_meta(proj, alvo_de(cz))
        quando = f"em {ano} anos" if ano else "no prazo"
        return (f"O patrimônio atual ({_rs_curto(patrimonio)}) já chega a "
                f"{_rs_curto(alvo_de(cz))} {quando}, só com os juros.")

    cenario_txt = (f"Cenário conservador: Selic e inflação médias dos últimos {ANOS_HISTORICO} anos.")
    otim_txt = f"Selic {_pct(otim['selic'])}, inflação {_pct(otim['inflacao'])} — cenário otimista."
    _grade([
        _kpi("Aporte sugerido", "Sem aporte" if ap_cons == 0 else _mes(ap_cons),
             (sem_aporte(cons) if ap_cons == 0 else f"por {anos} anos{reaj}, para {meta_txt}.")
             + " " + cenario_txt, classe="destaque"),
        _kpi("Se a Selic seguir como hoje", "Sem aporte" if ap_otim == 0 else _mes(ap_otim),
             (sem_aporte(otim) + " " if ap_otim == 0 else "") + otim_txt),
        _kpi("Situação hoje", _mes(atual), status),
    ], colunas=3)

    alvos = [(n, alvo_de(cz)) for n, cz in cenarios.items()]
    if tipo == "renda":
        _html('<p class="nota">Patrimônio necessário para a renda: '
              + " · ".join(f"{n}: <b>{_rs_curto(v)}</b>" for n, v in alvos if v)
              + " (em R$ de hoje).</p>")

    # --- Prazo × aporte ---
    _secao("Quanto aportar conforme o prazo")
    prazos = sorted({5, 10, 15, 20, 25, 30, anos})
    linhas = []
    for prazo in prazos:
        a_c, a_o = aporte_de(cons, prazo), aporte_de(otim, prazo)
        linhas.append({"Prazo": f"{prazo} anos (até {date.today().year + prazo})"
                                + ("  ◀ objetivo" if prazo == anos else ""),
                       f"Aporte — {nome_cons}": a_c, f"Aporte — {nome_otim}": a_o})
    t = pd.DataFrame(linhas)
    st.dataframe(t.style.format({k: (lambda v: "—" if v is None else _rs(v)) for k in t.columns if k != "Prazo"}),
                 hide_index=True, width="stretch")
    _html('<p class="nota">Valores mensais em reais de hoje. Quanto mais cedo, menor o esforço: '
          'os juros compostos fazem a maior parte do trabalho nos prazos longos.</p>')

    # --- Renda possível ---
    if tipo == "renda":
        _secao("Retirada possível sem perder poder de compra")
        _grade([
            _kpi(f"Hoje · {n}", _rs(pl.renda_mensal_perpetua(patrimonio, cz["taxa"], cz["inflacao"], s.p_ir)),
                 f"por mês, com o patrimônio atual de {_rs_curto(patrimonio)}")
            for n, cz in cenarios.items()
        ], colunas=3)

    _historico(bc)


def _historico(bc: dict) -> None:
    _secao(f"Brasil nos últimos {ANOS_HISTORICO} anos")
    selic, ipca = bc.get("selic_20a"), bc.get("ipca_20a")
    if selic is None or ipca is None:
        st.info("Histórico do Banco Central indisponível agora; os cálculos usam os valores de "
                f"referência (Selic {_pct(REF_SELIC_20A)}, IPCA {_pct(REF_IPCA_20A)}).")
        return
    ini, fim = bc["selic_periodo"]
    _grade([
        _kpi("Selic média", _pct(selic), f"ao ano, de {ini} a {fim}"),
        _kpi("Inflação média (IPCA)", _pct(ipca), "ao ano, no mesmo período"),
        _kpi("Juro real médio", _pct(pl.juro_real(selic, ipca)), "o que sobrou acima da inflação",
             classe="destaque"),
    ], colunas=3)
    s, i = _anual(bc.get("selic_mensal")), _anual(bc.get("ipca_mensal"))
    linhas = [{"ano": a, "serie": "Selic", "pct": s[a]} for a in s] + \
             [{"ano": a, "serie": "IPCA", "pct": i[a]} for a in i]
    if linhas:
        _grafico(alt.Chart(pd.DataFrame(linhas)).mark_bar(size=11).encode(
            x=alt.X("ano:O", title=None, axis=alt.Axis(labelAngle=0)),
            xOffset="serie:N",
            y=alt.Y("pct:Q", title="% no ano"),
            color=alt.Color("serie:N", scale=alt.Scale(domain=["Selic", "IPCA"], range=[MARINHO, DOURADO])),
            tooltip=["ano", "serie", alt.Tooltip("pct:Q", format=".2f", title="%")],
        ), altura=300)
    _html('<p class="nota">Fonte: Banco Central do Brasil (SGS 4390 e 433). Médias geométricas dos '
          'últimos 240 meses fechados. Rentabilidade passada não garante rentabilidade futura.</p>')


def _pg_cadastro(c: dict) -> None:
    _cabecalho("Cadastro", c.get("nome") or "Novo cliente",
               "Dados do cliente e posições da carteira."
               + (" Alterações são salvas automaticamente." if st.session_state.get("existe") else ""))

    with st.container(border=True):
        a, b, d = st.columns([2, 1, 1])
        c["nome"] = a.text_input("Nome do cliente", value=c["nome"], key=_k("nome"),
                                 disabled=st.session_state.get("existe", False))
        c["perfil"] = b.selectbox("Perfil", list(pl.PERFIS), key=_k("perfil"),
                                  index=list(pl.PERFIS).index(c.get("perfil", "Moderado")))
        c["aporte_mensal"] = d.number_input("Aporte mensal (R$)", value=float(c["aporte_mensal"]),
                                            step=500.0, min_value=0.0, key=_k("aporte_cad"))

    _secao("Posições")
    st.caption("Valor atual = saldo de hoje. Valor aplicado = quanto custou (opcional). "
               "Use a última linha da tabela para incluir um ativo.")
    df = pd.DataFrame(c.get("posicoes") or [], columns=["ativo", "classe", "valor_aplicado", "valor_atual"])
    editado = st.data_editor(
        df, num_rows="dynamic", width="stretch", hide_index=True, key=_k("posicoes"),
        column_config={
            "ativo": st.column_config.TextColumn("Ativo", required=True, width="large"),
            "classe": st.column_config.SelectboxColumn("Classe", options=pl.CLASSES, required=True,
                                                       default=pl.CLASSES[0]),
            "valor_aplicado": st.column_config.NumberColumn("Valor aplicado (R$)", min_value=0, format="%.2f"),
            "valor_atual": st.column_config.NumberColumn("Valor atual (R$)", min_value=0, format="%.2f"),
        },
    )
    c["posicoes"] = editado.fillna({"valor_aplicado": 0.0, "valor_atual": 0.0}).to_dict("records")

    st.write("")
    if not st.session_state.get("existe"):
        if st.button("Criar cliente", type="primary"):
            nome = c["nome"].strip()
            if not nome:
                st.error("Informe o nome do cliente.")
            elif nome in pl.listar_clientes():
                st.error("Já existe um cliente com esse nome — escolha-o na barra lateral.")
            else:
                c["nome"] = nome
                pl.salvar_cliente(c)
                st.session_state["existe"] = True
                st.session_state["_aberto"] = nome
                st.session_state["_selecionar"] = nome
                st.rerun()
    else:
        with st.popover("Excluir cliente"):
            st.write(f"Excluir **{c['nome']}** e todas as suas posições?")
            if st.button("Sim, excluir", type="primary"):
                pl.excluir_cliente(c["nome"])
                _abrir(None, existe=False)
                st.session_state["_selecionar"] = NOVO
                st.rerun()


def _data_br(iso: str) -> str:
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return str(iso)


def _pg_alia() -> None:
    import alia

    _cabecalho("Importar da Alia", "Posições dos clientes",
               "Traga as carteiras direto da Alia (BTG). É preciso estar com o Tailscale ligado.")

    # Passo 1 — data e busca (se a data já foi baixada, carrega sozinho)
    _html('<div class="passo">Passo 1 · Data da posição</div>')
    a, b, _ = st.columns([1, 1, 2])
    data_ref = a.date_input("Data", value=alia.ultimo_dia_util(), max_value=date.today(),
                            format="DD/MM/YYYY", label_visibility="collapsed")
    iso = data_ref.isoformat()
    baixada = alia.tem_cache(iso)
    if baixada and st.session_state.get("alia_data") != iso:
        st.session_state["alia_regs"] = alia.buscar_posicoes(iso)
        st.session_state["alia_data"] = iso
    rotulo = "Baixar de novo" if baixada else "Buscar posições"
    if b.button(rotulo, type="secondary" if baixada else "primary", width="stretch"):
        with st.spinner("A Alia está exportando as posições — pode levar até 30 minutos…"):
            try:
                st.session_state["alia_regs"] = alia.buscar_posicoes(iso, usar_cache=False)
                st.session_state["alia_data"] = iso
            except alia.AliaErro as e:
                st.error(str(e))
                return
    regs = st.session_state.get("alia_regs") if st.session_state.get("alia_data") == iso else None
    if not regs:
        st.caption("Esta data ainda não foi baixada. A exportação pode levar até 30 minutos; "
                   "depois fica guardada neste computador.")
        return

    salvo = alia.carregar_mapa()
    campos = alia.campos(regs)
    mapa = {k: (salvo.get(k) if salvo.get(k) in campos else v)
            for k, v in alia.detectar_mapa(regs).items()}
    if not (mapa.get("cliente") and mapa.get("ativo") and mapa.get("valor_atual")):
        st.error("Não reconheci os campos da resposta da Alia. Ajuste em *Avançado*, no fim da página.")
        _alia_avancado(alia, regs, mapa)
        return

    por_conta = alia.agrupar_por_cliente(regs, mapa)
    nomes = alia.carregar_contas()
    st.caption(f"Posição de {_data_br(iso)}: {len(regs)} posições em {len(por_conta)} contas.")

    # Passo 2 — nome de cada conta (formulário: nada recarrega enquanto se digita)
    _html('<div class="passo">Passo 2 · Quem é quem</div>')
    norm = {k.lstrip("0"): v for k, v in nomes.items()}  # API e portal divergem nos zeros

    def nome_de(conta: str) -> str:
        return norm.get(str(conta).lstrip("0"), "")

    contas = sorted(por_conta, key=lambda k: -sum(p["valor_atual"] for p in por_conta[k]))
    sem_nome = [k for k in contas if not nome_de(k)]
    st.caption(f"A Alia identifica o cliente só pelo número da conta. {len(contas) - len(sem_nome)} de "
               f"{len(contas)} contas já têm nome. Fica salvo neste computador.")

    with st.expander("Colar a lista de clientes do portal BTG", expanded=len(sem_nome) == len(contas)):
        st.caption("No portal do assessor, selecione a lista de clientes (nome, conta, tipo), copie "
                   "(Ctrl+C) e cole aqui. O app reconhece cada conta e o nome do titular.")
        with st.form("form_lista", border=False):
            texto = st.text_area("Lista", height=180, label_visibility="collapsed",
                                 placeholder="Cole aqui a lista copiada do portal do BTG")
            if st.form_submit_button("Ler lista", type="primary"):
                lidas = alia.ler_lista_contas(texto)
                if lidas:
                    alia.salvar_contas({**nomes, **lidas})
                    st.toast(f"{len(lidas)} contas reconhecidas.")
                    st.rerun()
                else:
                    st.error("Não encontrei números de conta no texto colado.")

    tab = pd.DataFrame({
        "conta": contas,
        "nome": [nome_de(k) for k in contas],
        "patrimonio": [sum(p["valor_atual"] for p in por_conta[k]) for k in contas],
        "principais": [", ".join(p["ativo"] for p in por_conta[k][:3]) for k in contas],
    })
    with st.form("form_contas", border=False):
        ed = st.data_editor(
            tab, hide_index=True, width="stretch", disabled=["conta", "patrimonio", "principais"],
            height=min(36 * len(tab) + 40, 640),
            column_config={
                "conta": st.column_config.TextColumn("Conta", width="small"),
                "nome": st.column_config.TextColumn("Nome do cliente", width="medium"),
                "patrimonio": st.column_config.NumberColumn("Patrimônio (R$)", format="%.2f"),
                "principais": st.column_config.TextColumn("Maiores posições", width="large"),
            })
        if st.form_submit_button("Salvar nomes", type="primary"):
            alia.salvar_contas({**nomes, **dict(zip(ed["conta"], ed["nome"].fillna("")))})
            st.toast("Nomes salvos.")
            st.rerun()

    # Passo 3 — abrir no app (por titular: contas da mesma pessoa somadas)
    _html('<div class="passo">Passo 3 · Abrir a carteira</div>')
    grupos = {n: pos for n, pos in alia.agrupar_por_cliente(regs, mapa, nomes).items()
              if any(nome_de(k) == n for k in contas)}
    if not grupos:
        st.caption("Dê nome a pelo menos uma conta no passo 2.")
        return
    contas_de = {n: [k for k in contas if nome_de(k) == n] for n in grupos}

    def ficha_alia(nome: str) -> dict:
        ficha = pl.carregar_cliente(nome) or {**_cliente_vazio(), "nome": nome}
        ficha.update({"posicoes": grupos[nome], "alia_conta": ", ".join(contas_de[nome]),
                      "alia_data": iso})
        pl.salvar_cliente(ficha)
        return ficha

    a, b, d = st.columns([2, 1, 1])
    nome = a.selectbox("Cliente", list(grupos), label_visibility="collapsed",
                       format_func=lambda n: f"{n}  ·  {_rs(sum(p['valor_atual'] for p in grupos[n]))}")
    if b.button("Abrir cliente", type="primary", width="stretch"):
        alia.salvar_mapa(mapa)
        _abrir(ficha_alia(nome), existe=True)
        st.session_state["_aberto"] = nome
        st.session_state["_selecionar"] = nome
        st.session_state["_ir_para"] = "Visão geral"
        st.rerun()
    if d.button(f"Atualizar todos ({len(grupos)})", width="stretch",
                help="Grava a posição desta data na ficha de todos os clientes com nome."):
        alia.salvar_mapa(mapa)
        for n in grupos:
            ficha_alia(n)
        st.toast(f"{len(grupos)} clientes atualizados.")

    _alia_avancado(alia, regs, mapa)


def _alia_avancado(alia, regs: list[dict], mapa: dict) -> None:
    rotulos = {"cliente": "Cliente (conta)", "ativo": "Ativo", "classe": "Classe",
               "valor_atual": "Valor atual", "valor_aplicado": "Valor aplicado"}
    st.write("")
    with st.expander("Avançado · campos da Alia"):
        st.caption("Normalmente não precisa mexer: os campos são reconhecidos sozinhos.")
        opcoes = ["—"] + alia.campos(regs)
        novo = {}
        for col, (k, r) in zip(st.columns(len(rotulos)), rotulos.items()):
            v = col.selectbox(r, opcoes, index=opcoes.index(mapa[k]) if mapa.get(k) in opcoes else 0,
                              key=f"map_{k}")
            novo[k] = None if v == "—" else v
        if st.button("Salvar campos"):
            alia.salvar_mapa(novo)
            st.rerun()


def _pg_premissas(bc: dict) -> None:
    _cabecalho("Premissas", "Taxas usadas nos cálculos",
               "Vêm do Banco Central; ajuste se quiser simular outro cenário.")
    s = st.session_state
    with st.container(border=True):
        st.markdown("**Cenário Selic hoje**")
        a, b = st.columns(2)
        s.p_selic_hoje = a.number_input("Selic meta (% a.a.)", value=s.p_selic_hoje, step=0.25)
        s.p_ipca_hoje = b.number_input("IPCA esperado — Focus (% a.a.)", value=s.p_ipca_hoje, step=0.25)
    with st.container(border=True):
        st.markdown(f"**Cenário média {ANOS_HISTORICO} anos**")
        a, b = st.columns(2)
        s.p_selic_20 = a.number_input("Selic média (% a.a.)", value=s.p_selic_20, step=0.25)
        s.p_ipca_20 = b.number_input("IPCA médio (% a.a.)", value=s.p_ipca_20, step=0.25)
    with st.container(border=True):
        st.markdown("**Impostos e aportes**")
        a, b = st.columns(2)
        s.p_ir = a.number_input("IR sobre o ganho (%)", value=s.p_ir, step=2.5, min_value=0.0,
                                max_value=27.5, help="Renda fixa acima de 2 anos: 15%.")
        b.write("")
        s.p_reajustar = b.checkbox("Corrigir o aporte pela inflação todo ano", value=s.p_reajustar)
    if st.button("Voltar aos valores do Banco Central"):
        for k in ("p_selic_hoje", "p_ipca_hoje", "p_selic_20", "p_ipca_20", "p_ir", "p_reajustar"):
            s.pop(k, None)
        st.rerun()
    if bc["erros"]:
        st.caption("Parte dos dados do Banco Central não veio agora — usando valores de referência.")


def main() -> None:
    st.set_page_config(page_title="Carteira do Cliente · Ciano", page_icon="💼", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    bc = _taxas_bc()
    _premissas_padrao(bc)
    if "cliente" not in st.session_state:
        _abrir(None, existe=False)
    pagina = _sidebar()
    c = st.session_state["cliente"]
    an = pl.analisar_carteira(c.get("posicoes") or [])

    if pagina == "Visão geral":
        _pg_visao_geral(c, an)
    elif pagina == "Projeção":
        _pg_projecao(c, an)
    elif pagina == "Objetivo":
        _pg_objetivo(c, an, bc)
    elif pagina == "Cadastro":
        _pg_cadastro(c)
    elif pagina == "Importar da Alia":
        _pg_alia()
    else:
        _pg_premissas(bc)

    _autosalvar(st.session_state["cliente"])


if __name__ == "__main__":
    main()
