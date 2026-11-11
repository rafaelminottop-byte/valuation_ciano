"""
Acompanhamento da Carteira — app Streamlit (porta 8503).

Separa todos os ativos por classe e acompanha a saúde financeira das empresas
(ações) e dos FIIs. Cada atualização das posições vira um "snapshot" datado,
para ver a evolução por classe ao longo do tempo. Lógica em acompanhamento.py.

Dentro do Valuation: página "Acompanhamento" (app.py chama render()).
Sozinho:  py -m streamlit run app_acompanhamento.py --server.port 8503
"""

from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

import acompanhamento as ac

MARINHO, DOURADO = "#0B1F2A", "#0FA3B8"   # marinho-teal e ciano da marca
COR_SITUACAO = {"Forte": "#d8efd9", "Ok": "#d8efd9", "Atenção": "#fbeccb",
                "Frágil": "#f6d3d0", "Sem dados": "#e6e6e6"}


def brl(v: float) -> str:
    return f"R$ {v:,.0f}".replace(",", ".")


@st.cache_data(ttl=6 * 3600, show_spinner="Buscando indicadores no Fundamentus…")
def _fundamentos():
    import fundamentus_scraper as f
    return f.baixar_tabela_fundamentus()


@st.cache_data(ttl=6 * 3600, show_spinner="Buscando FIIs…")
def _fiis():
    import fii
    return fii.baixar()


def _pintar(df: pd.DataFrame, col: str = "situacao"):
    return df.style.map(lambda s: f"background-color: {COR_SITUACAO.get(s, '')}", subset=[col])


def render() -> None:
    """Desenha a página inteira (usada pelo app.py e pelo modo sozinho)."""
    snaps = ac.listar_snapshots()
    if not snaps:
        st.info("Nenhuma posição salva ainda. Vá na aba **Atualizar posições** e cole os dados.")
        texto = st.text_area("Cole aqui (colunas: product, total_gross_value, total_net_value)", height=200)
        if st.button("Salvar") and texto.strip():
            ac.salvar_snapshot(ac.ler_posicoes(texto))
            st.rerun()
        return

    c_a, c_b = st.columns([1, 2])
    escolhido = c_a.selectbox(
        "Posição de", snaps[::-1], format_func=lambda p: p.stem.replace("posicoes_", ""))
    base_nome = c_b.radio("Valor considerado", ["Líquido (após impostos)", "Bruto"], horizontal=True)
    base = "liquido" if base_nome.startswith("Líq") else "bruto"
    dados = ac.montar(ac.ler_snapshot(escolhido), base)
    patrimonio = dados.loc[~dados["classe"].isin(["Opções", "A receber / a liquidar"]), "valor"].sum()

    abas = st.tabs(["Resumo por classe", "Ações — saúde das empresas", "FIIs", "Opções",
                    "Todas as posições", "Evolução", "Atualizar posições"])

    # ------------------------------------------------------------------ resumo
    with abas[0]:
        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimônio (sem opções e a liquidar)", brl(patrimonio))
        opc = dados.loc[dados["classe"] == "Opções", "valor"].sum()
        c2.metric("Opções (saldo)", brl(opc), help="Negativo = mais vendidas que compradas")
        c3.metric("Ativos", len(dados))

        res = ac.resumo_classes(dados).reset_index()
        graf = res[~res["classe"].isin(["Opções", "A receber / a liquidar"])]
        st.altair_chart(
            alt.Chart(graf).mark_bar(color=MARINHO).encode(
                x=alt.X("peso_pct:Q", title="% do patrimônio"),
                y=alt.Y("classe:N", sort="-x", title=None),
                tooltip=["classe", alt.Tooltip("valor:Q", format=",.0f"),
                         alt.Tooltip("peso_pct:Q", format=".1f")]),
            use_container_width=True)
        tab = res.rename(columns={"classe": "Classe", "valor": "Valor (R$)", "n": "Nº ativos",
                                  "peso_pct": "% patrimônio"})
        st.dataframe(tab, hide_index=True, use_container_width=True, column_config={
            "Valor (R$)": st.column_config.NumberColumn(format="%.0f"),
            "% patrimônio": st.column_config.NumberColumn(format="%.1f%%")})

        with st.expander("Detalhe por subclasse"):
            sub = (dados.groupby(["classe", "subclasse"])["valor"].sum().reset_index()
                   .sort_values(["classe", "valor"], ascending=[True, False]))
            sub["% patrimônio"] = sub["valor"] / patrimonio * 100
            st.dataframe(sub, hide_index=True, use_container_width=True, column_config={
                "valor": st.column_config.NumberColumn("Valor (R$)", format="%.0f"),
                "% patrimônio": st.column_config.NumberColumn(format="%.1f%%")})

        revisar = dados[dados["classe"] == "Outros / revisar"]
        if not revisar.empty:
            st.warning("Não consegui classificar: " + ", ".join(revisar["produto"]))
        div = dados[dados["divergente"]]
        if not div.empty:
            st.warning(
                "**Bruto e líquido muito diferentes** (em ações isso não é imposto — vale conferir "
                "empréstimo/garantia/ajuste na plataforma): "
                + "; ".join(f"{r.produto} ({brl(r.bruto)} → {brl(r.liquido)})" for r in div.itertuples()))

    # ------------------------------------------------------------------- ações
    with abas[1]:
        acoes = dados[dados["subclasse"] == "Ação"]
        saude = ac.saude_acoes(_fundamentos(), acoes["produto"].tolist())
        saude = saude.merge(acoes[["produto", "valor", "peso_pct"]], left_on="ticker",
                            right_on="produto").drop(columns="produto")
        saude = saude.sort_values("valor", ascending=False)
        frag = saude[saude["situacao"] == "Frágil"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Em ações (sem ETFs)", brl(saude["valor"].sum()))
        c2.metric("Em empresas frágeis", brl(frag["valor"].sum()),
                  f"{frag['valor'].sum() / max(saude['valor'].sum(), 1):.0%} das ações", delta_color="off")
        c3.metric("Nota média ponderada",
                  f"{(saude['nota'].fillna(0) * saude['valor']).sum() / max(saude['valor'].sum(), 1):.0f}/100")
        st.caption("Nota 0–100 com os últimos 12 meses do Fundamentus: rentabilidade (ROIC/margem), "
                   "endividamento, liquidez e crescimento; bancos usam ROE, P/VP e P/L. "
                   "Forte ≥ 65 · Atenção 40–64 · Frágil < 40 (prejuízo limita a nota a 39).")
        f1, f2, f3 = st.columns([2, 2, 2])
        sit = f1.multiselect("Situação", ["Forte", "Atenção", "Frágil", "Sem dados"],
                             default=["Forte", "Atenção", "Frágil", "Sem dados"], key="f_sit_acoes")
        tipo = f2.multiselect("Tipo", ["Empresa", "Banco/seguradora"],
                              default=["Empresa", "Banco/seguradora"], key="f_tipo_acoes")
        so_prej = f3.checkbox("Só com alerta de prejuízo ou dívida alta", key="f_alerta_acoes")
        filtro = saude["situacao"].isin(sit) & (saude["tipo"].isin(tipo) | saude["tipo"].isna())
        if so_prej:
            filtro &= saude["alertas"].str.contains("Prejuízo|Dívida", regex=True)
        saude = saude[filtro]
        st.caption(f"{len(saude)} empresas · {brl(saude['valor'].sum())} no filtro")
        mostrar = saude[["ticker", "valor", "nota", "situacao", "alertas", "P/L", "P/VP", "ROE", "ROIC",
                         "Margem EBIT", "Dív.líq/PL (x)", "Liq. corrente", "Cresc. receita 5a", "DY"]]
        st.dataframe(
            _pintar(mostrar), hide_index=True, use_container_width=True,
            column_config={
                "valor": st.column_config.NumberColumn("Valor (R$)", format="%.0f"),
                **{c: st.column_config.NumberColumn(format="%.0f%%") for c in []},
                "P/L": st.column_config.NumberColumn(format="%.1f"),
                "P/VP": st.column_config.NumberColumn(format="%.2f"),
                "ROE": st.column_config.NumberColumn(format="percent"),
                "ROIC": st.column_config.NumberColumn(format="percent"),
                "Margem EBIT": st.column_config.NumberColumn(format="percent"),
                "Cresc. receita 5a": st.column_config.NumberColumn(format="percent"),
                "DY": st.column_config.NumberColumn(format="percent"),
                "Dív.líq/PL (x)": st.column_config.NumberColumn(format="%.1f"),
                "Liq. corrente": st.column_config.NumberColumn(format="%.2f"),
            })

    # -------------------------------------------------------------------- FIIs
    with abas[2]:
        fiis_pos = dados[(dados["classe"] == "FIIs & Fiagro") & (dados["subclasse"] == "FII")]
        sf = ac.saude_fiis(_fiis(), fiis_pos["produto"].tolist()).merge(
            fiis_pos[["produto", "valor"]], left_on="ticker", right_on="produto").drop(columns="produto")
        sf = sf.sort_values("valor", ascending=False)
        c1, c2 = st.columns(2)
        c1.metric("Em FIIs (listados)", brl(sf["valor"].sum()))
        c2.metric("Em Fiagro", brl(dados.loc[dados["subclasse"] == "Fiagro", "valor"].sum()))
        st.caption("Alertas: P/VP > 1,10 (caro) ou < 0,70 (desconto grande), vacância > 15%, DY < 8%. "
                   "Desconto grande pode ser oportunidade ou risco — olhe o relatório gerencial.")
        if "segmento" in sf:
            seg = sf.groupby("segmento")["valor"].sum().sort_values(ascending=False).reset_index()
            st.altair_chart(alt.Chart(seg).mark_bar(color=DOURADO).encode(
                x=alt.X("valor:Q", title="R$"), y=alt.Y("segmento:N", sort="-x", title=None)),
                use_container_width=True)
        sit_f = st.multiselect("Situação", ["Ok", "Atenção", "Sem dados"],
                               default=["Ok", "Atenção", "Sem dados"], key="f_sit_fiis")
        sf = sf[sf["situacao"].isin(sit_f)]
        st.caption(f"{len(sf)} FIIs · {brl(sf['valor'].sum())} no filtro")
        st.dataframe(_pintar(sf), hide_index=True, use_container_width=True, column_config={
            "valor": st.column_config.NumberColumn("Valor (R$)", format="%.0f"),
            "DY 12m": st.column_config.NumberColumn(format="percent"),
            "Vacância": st.column_config.NumberColumn(format="percent"),
            "P/VP": st.column_config.NumberColumn(format="%.2f")})

    # ------------------------------------------------------------------ opções
    with abas[3]:
        op = dados[dados["classe"] == "Opções"].copy()
        op["lado"] = op["valor"].map(lambda v: "Vendida" if v < 0 else "Comprada")
        op["tipo"] = op["subclasse"]
        st.caption("Valor negativo = opção vendida (obrigação). Saldo por ativo-objeto ajuda a ver "
                   "onde a carteira está travada/exposta.")
        por_ativo = (op.groupby("ativo_objeto")["valor"].sum().sort_values().reset_index()
                     .rename(columns={"ativo_objeto": "Ativo-objeto", "valor": "Saldo (R$)"}))
        st.dataframe(por_ativo, hide_index=True, use_container_width=True,
                     column_config={"Saldo (R$)": st.column_config.NumberColumn(format="%.0f")})
        st.dataframe(op[["produto", "ativo_objeto", "tipo", "lado", "valor"]].sort_values("valor"),
                     hide_index=True, use_container_width=True,
                     column_config={"valor": st.column_config.NumberColumn("Valor (R$)", format="%.0f")})

    # ---------------------------------------------------------------- posições
    with abas[4]:
        cls = st.multiselect("Classe", ac.CLASSES + ["Outros / revisar"])
        busca = st.text_input("Buscar produto")
        v = dados
        if cls:
            v = v[v["classe"].isin(cls)]
        if busca:
            v = v[v["produto"].str.contains(busca, case=False)]
        st.dataframe(v[["produto", "classe", "subclasse", "valor", "peso_pct"]]
                     .sort_values("valor", ascending=False),
                     hide_index=True, use_container_width=True, column_config={
                         "valor": st.column_config.NumberColumn("Valor (R$)", format="%.0f"),
                         "peso_pct": st.column_config.NumberColumn("% patrimônio", format="%.2f%%")})

    # ---------------------------------------------------------------- evolução
    with abas[5]:
        ev = ac.evolucao_classes(base)
        ev = ev.drop(columns=[c for c in ("Opções", "A receber / a liquidar") if c in ev], errors="ignore")
        if len(ev) < 2:
            st.info("Só há uma posição salva. A cada atualização (aba ao lado) uma nova data entra aqui "
                    "e a evolução por classe aparece.")
        else:
            longo = ev.reset_index(names="data").melt("data", var_name="classe", value_name="valor")
            st.altair_chart(alt.Chart(longo).mark_area().encode(
                x="data:T", y="valor:Q", color="classe:N", tooltip=["data", "classe", "valor"]),
                use_container_width=True)
            st.dataframe(ev.round(0), use_container_width=True)

    # --------------------------------------------------------------- atualizar
    with abas[6]:
        st.write("Cole a exportação da plataforma (3 colunas: `product`, `total_gross_value`, "
                 "`total_net_value`). Cada data vira um snapshot; datas repetidas sobrescrevem.")
        dia = st.date_input("Data da posição", date.today())
        texto = st.text_area("Posições", height=240)
        if st.button("Salvar posição") and texto.strip():
            try:
                novo = ac.ler_posicoes(texto)
                ac.salvar_snapshot(novo, dia)
                st.success(f"{len(novo)} ativos salvos em {dia}.")
                st.rerun()
            except Exception as e:  # formato inesperado
                st.error(f"Não consegui ler: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="Acompanhamento da Carteira", page_icon="📊", layout="wide")
    render()
