"""
Acompanhamento de carteira — classificação por classe e saúde financeira.

Entrada: posições (colunas ``product, total_gross_value, total_net_value``, como
exportadas pela plataforma; números no formato 6,183.09).
Saída: cada ativo com classe/subclasse, e para ações/FIIs um "termômetro" de
saúde financeira baseado nos indicadores do Fundamentus (últimos 12 meses).

A classificação não depende de internet; só o termômetro usa o Fundamentus.
Snapshots ficam em data/acompanhamento/ (dados de cliente: fora do git).
"""

import re
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent / "data" / "acompanhamento"

# ---------------------------------------------------------------- leitura
def _num(txt) -> float:
    """'6,183.09' -> 6183.09 ; '-146,838.13' -> -146838.13."""
    if isinstance(txt, (int, float)):
        return float(txt)
    return float(str(txt).strip().replace(",", "") or 0)


def ler_posicoes(texto: str) -> pd.DataFrame:
    """Lê o texto colado/arquivo (tab, ; ou vírgula entre colunas) em DataFrame."""
    linhas = [l for l in texto.strip().splitlines() if l.strip()]
    sep = "\t" if "\t" in linhas[0] else (";" if ";" in linhas[0] else ",")
    df = pd.read_csv(StringIO("\n".join(linhas)), sep=sep, dtype=str)
    df.columns = [c.strip().lower() for c in df.columns]
    df["produto"] = df["product"].str.strip()
    df["bruto"] = df["total_gross_value"].map(_num)
    df["liquido"] = df["total_net_value"].map(_num)
    return df[["produto", "bruto", "liquido"]]


# ----------------------------------------------------------- classificação
CAIXA = {"CONTA CORRENTE": "Conta corrente", "COMPROMISSADA": "Compromissada"}
RF_DIRETA = {
    "CDB": ("Crédito bancário", "CDB"), "LCA": ("Crédito bancário", "LCA"),
    "LCI": ("Crédito bancário", "LCI"),
    "CRA": ("Crédito privado", "CRA"), "CRI": ("Crédito privado", "CRI"),
    "CDCA": ("Crédito privado", "CDCA"), "DEBENTURE": ("Crédito privado", "Debênture"),
    "COE": ("Estruturadas", "COE"),
    "LFT": ("Títulos públicos", "LFT (Selic)"), "NTN-B": ("Títulos públicos", "NTN-B (IPCA)"),
    "NTN-F": ("Títulos públicos", "NTN-F (pré)"),
}
ETF_ACOES_BR = {"BOVA11", "SMAL11"}
ETF_INTERNACIONAL = {"IVVB11", "NASD11", "ACWI11", "XINA11"}
RF_LISTADOS = {"IB5M11", "LFTS11", "CDII11", "KDIF11", "JURO11"}   # ETF/FI-Infra de renda fixa
UNITS = {"TAEE11", "SAPR11", "BPAC11", "KLBN11", "SANB11", "ALUP11", "ENGI11", "CMIG11"}
FIAGRO_LISTADOS = {"CXAG11"}

RE_OPCAO = re.compile(r"^([A-Z]{4})([A-X])(\d{3,4})$")
RE_ACAO = re.compile(r"^[A-Z][A-Z0-9]{3}\d{1,2}$")

CLASSES = [  # ordem de exibição
    "Caixa & Liquidez", "Renda Fixa Direta", "Fundos de Renda Fixa",
    "Crédito Estruturado", "Multimercado", "Ações Brasil", "Internacional",
    "FIIs & Fiagro", "Alternativos", "Opções", "A receber / a liquidar",
]


def classificar(produto: str, base: float = 0.0) -> tuple[str, str]:
    """(classe, subclasse) de um produto."""
    p = produto.strip().upper()
    if p.startswith(("DIVIDENDOS -", "JUROS S/ CAPITAL -", "RENDIMENTO -")):
        return "A receber / a liquidar", "Proventos a receber"
    if p.startswith("COMPRA -"):
        return "A receber / a liquidar", "Compras a liquidar"
    if p in CAIXA:
        return "Caixa & Liquidez", CAIXA[p]
    if p in RF_DIRETA:
        return "Renda Fixa Direta", RF_DIRETA[p][0] + " · " + RF_DIRETA[p][1]
    if p.startswith("TESOURO DIRETO - "):
        tit = p.split(" - ", 1)[1]
        rotulos = {"LFT": "LFT (Selic)", "NTN-B": "NTN-B (IPCA)", "NTN-F": "NTN-F (pré)",
                   "LTN": "LTN (pré)"}
        return "Renda Fixa Direta", "Títulos públicos · " + rotulos.get(tit, tit)

    if " " not in p:  # tickers
        if RE_OPCAO.match(p):
            return "Opções", ("Call" if p[4] <= "L" else "Put")
        if p in ETF_ACOES_BR:
            return "Ações Brasil", "ETF de ações"
        if p in ETF_INTERNACIONAL:
            return "Internacional", "ETF exterior"
        if p in RF_LISTADOS:
            return "Fundos de Renda Fixa", "Listado (infra / RF)"
        if p in FIAGRO_LISTADOS:
            return "FIIs & Fiagro", "Fiagro"
        if RE_ACAO.match(p):
            if p[-2:] in ("34", "35"):
                return "Internacional", "BDR"
            if p.endswith("11") and p not in UNITS:
                return "FIIs & Fiagro", "FII"
            return "Ações Brasil", "Ação"

    # fundos (por palavras no nome)
    if "BITCOIN" in p:
        return "Alternativos", "Cripto"
    if "CAMBIAL" in p or "DOLAR" in p:
        return "Alternativos", "Cambial"
    if "FIDC" in p:
        return "Crédito Estruturado", "FIDC"
    if "FIAGRO" in p:
        return "FIIs & Fiagro", "Fiagro"
    if re.search(r"FIM\b|MULTI|GLOBAL", p):
        return "Multimercado", "Fundo multimercado"
    if re.search(r"INCENT|INFRA", p):
        return "Fundos de Renda Fixa", "Incentivados (isentos)"
    if re.search(r"FIRF|\bRF\b|CASH|SELIC|CRPR", p):
        return "Fundos de Renda Fixa", "Fundo de RF"
    return "Outros / revisar", "Não classificado"


def montar(df: pd.DataFrame, base: str = "liquido") -> pd.DataFrame:
    """Adiciona classe, subclasse, valor (na base escolhida), peso e flags."""
    df = df.copy()
    cl = [classificar(p) for p in df["produto"]]
    df["classe"] = [c[0] for c in cl]
    df["subclasse"] = [c[1] for c in cl]
    df["valor"] = df[base]
    # Divergência bruto x líquido relevante (R$ e %): normalmente imposto (RF)
    # — mas em ações costuma indicar empréstimo/garantia/ajuste a conferir.
    dif = (df["liquido"] - df["bruto"]).abs()
    df["divergente"] = (dif > 5000) & (dif / df["bruto"].abs().clip(lower=1) > 0.15)
    # Opções: ativo-objeto (4 primeiras letras) e lado (comprada/vendida)
    df["ativo_objeto"] = None
    for i, p in df["produto"].items():
        m = RE_OPCAO.match(p.strip().upper())
        if m:
            df.at[i, "ativo_objeto"] = m.group(1)
    tot = df.loc[~df["classe"].isin(["Opções", "A receber / a liquidar"]), "valor"].sum()
    df["peso_pct"] = df["valor"] / tot * 100 if tot else 0.0
    return df


def resumo_classes(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("classe").agg(valor=("valor", "sum"), n=("produto", "count"))
    g["peso_pct"] = g["valor"] / g.loc[g.index.isin(CLASSES[:9]), "valor"].sum() * 100
    return g.reindex([c for c in CLASSES + ["Outros / revisar"] if c in g.index])


# ------------------------------------------------------ saúde financeira
def _pct(v) -> float:
    try:
        return float(str(v).replace("%", "").replace(".", "").replace(",", ".")) / 100
    except ValueError:
        return float("nan")


def _faixa(x, ruim, bom, pontos=25.0):
    """Interpola 0..pontos entre 'ruim' e 'bom' (funciona nos dois sentidos)."""
    if x is None or pd.isna(x):
        return pontos / 2
    t = (x - ruim) / (bom - ruim)
    return pontos * max(0.0, min(1.0, t))


def _rotulo(nota: float) -> str:
    return "Forte" if nota >= 65 else ("Atenção" if nota >= 40 else "Frágil")


def saude_acoes(fund: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """Termômetro 0–100 por ação (Fundamentus, últimos 12 meses)."""
    linhas = []
    base = fund.set_index(fund["ticker"].str.upper())
    for t in tickers:
        if t not in base.index:
            linhas.append({"ticker": t, "nota": None, "situacao": "Sem dados",
                           "alertas": "Não está no Fundamentus"})
            continue
        r = base.loc[t]
        banco = str(r.get("base_calculo")) == "Lucro"
        roe, pl_, pvp = r["roe"], r["p_l"], r["P/VP"]
        cresc = r["cresc_receita_5a"]
        alertas = []
        if banco:
            nota = (_faixa(roe, 0.05, 0.18, 40) + _faixa(cresc, -0.05, 0.10, 20)
                    + _faixa(pl_ if pl_ > 0 else None, 20, 6, 20)
                    + _faixa(pvp, 2.5, 0.8, 20))
            if roe < 0.10:
                alertas.append(f"ROE baixo ({roe:.0%})")
        else:
            roic, marg = r["roic"], r["margem_ebit"]
            dliq, liqc = r["div_liq_patrim"] / 100, r["liquidez_corrente"]
            nota = (_faixa(roic, 0.04, 0.15) * 0.5 + _faixa(marg, 0.03, 0.25) * 0.5
                    + _faixa(dliq, 2.0, 0.3) + _faixa(liqc, 0.8, 1.6)
                    + _faixa(cresc, -0.03, 0.10))
            if roic < 0.08:
                alertas.append(f"ROIC {roic:.0%} (abaixo do custo de capital)")
            if dliq > 1.5:
                alertas.append(f"Dívida líq./PL {dliq:.1f}x")
            if liqc < 1.0:
                alertas.append(f"Liquidez corrente {liqc:.2f}")
        if pl_ <= 0:
            alertas.append("Prejuízo nos últimos 12 meses")
            nota = min(nota, 39)
        if cresc < 0:
            alertas.append("Receita encolhendo (5 anos)")
        linhas.append({
            "ticker": t, "nota": round(nota), "situacao": _rotulo(nota),
            "tipo": "Banco/seguradora" if banco else "Empresa",
            "P/L": pl_, "P/VP": pvp, "ROE": roe,
            "ROIC": None if banco else r["roic"],
            "Margem EBIT": None if banco else r["margem_ebit"],
            "Dív.líq/PL (x)": None if banco else r["div_liq_patrim"] / 100,
            "Liq. corrente": None if banco else r["liquidez_corrente"],
            "Cresc. receita 5a": cresc, "DY": _pct(r["Div.Yield"]),
            "alertas": "; ".join(alertas) or "—",
        })
    return pd.DataFrame(linhas)


def saude_fiis(fii: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """Leitura rápida de cada FII: desconto, yield e vacância."""
    base = fii.set_index("Papel")
    linhas = []
    for t in tickers:
        if t not in base.index:
            linhas.append({"ticker": t, "situacao": "Sem dados", "alertas": "Não está na lista de FIIs"})
            continue
        r = base.loc[t]
        pvp, dy, vac = r["P/VP"], r["DY"], r["Vacancia"]
        alertas = []
        if pvp > 1.10:
            alertas.append(f"Caro: P/VP {pvp:.2f}")
        if pvp < 0.70:
            alertas.append(f"Desconto grande: P/VP {pvp:.2f} (o mercado vê risco?)")
        if vac and vac > 0.15:
            alertas.append(f"Vacância {vac:.0%}")
        if dy < 0.08:
            alertas.append(f"DY baixo ({dy:.1%})")
        situ = "Atenção" if alertas else "Ok"
        linhas.append({"ticker": t, "segmento": r["Segmento"], "P/VP": pvp, "DY 12m": dy,
                       "Vacância": vac, "Liquidez diária": r["Liquidez"],
                       "situacao": situ, "alertas": "; ".join(alertas) or "—"})
    return pd.DataFrame(linhas)


# ------------------------------------------------------------- histórico
def salvar_snapshot(df: pd.DataFrame, dia: date = None) -> Path:
    PASTA.mkdir(parents=True, exist_ok=True)
    caminho = PASTA / f"posicoes_{(dia or date.today()).isoformat()}.csv"
    df[["produto", "bruto", "liquido"]].to_csv(caminho, index=False)
    return caminho


def listar_snapshots() -> list[Path]:
    return sorted(PASTA.glob("posicoes_*.csv")) if PASTA.exists() else []


def ler_snapshot(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho)


def evolucao_classes(base: str = "liquido") -> pd.DataFrame:
    """Valor por classe em cada snapshot salvo (linhas = datas)."""
    saida = {}
    for c in listar_snapshots():
        d = montar(ler_snapshot(c), base)
        saida[c.stem.replace("posicoes_", "")] = d.groupby("classe")["valor"].sum()
    return pd.DataFrame(saida).T.fillna(0.0)
