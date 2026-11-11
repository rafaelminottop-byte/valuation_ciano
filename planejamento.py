"""
Análise de carteira de cliente e projeção de patrimônio (BIG NUMBERS).

Funções puras, sem Streamlit, para o app ``app_cliente.py`` e para os testes:

- ``analisar_carteira``: total, alocação por classe, concentração, rentabilidade
  por ativo e alertas.
- ``comparar_perfil``: distância da alocação atual para o perfil sugerido
  (conservador/moderado/arrojado) e o R$ a mover em cada classe.
- ``projetar`` / ``big_numbers``: evolução mês a mês do patrimônio com aportes,
  capitalizando à Selic (ou % dela), com IR sobre o ganho e valor em reais de
  hoje (descontada a inflação). Os BIG NUMBERS são os marcos a cada 5 anos.
- ``aporte_para_meta`` / ``renda_mensal_perpetua``: quanto aportar por mês para
  chegar à meta e quanto se pode retirar sem comer o poder de compra — tanto
  com a Selic de hoje quanto com a Selic/IPCA médios dos últimos 20 anos.

Persistência: um JSON por cliente em ``data/clientes/`` (fora do git — é dado
pessoal de cliente).
"""

import json
import re
import unicodedata
from pathlib import Path

CLIENTES_DIR = Path(__file__).resolve().parent / "data" / "clientes"

CLASSES = [
    "Renda Fixa Pós (CDI/Selic)",
    "Renda Fixa Pré",
    "Renda Fixa IPCA+",
    "Ações",
    "FIIs",
    "Fundos de Investimento",
    "Multimercado",
    "Internacional",
    "Previdência",
    "Cripto",
    "Caixa",
]

# Alocação de referência por perfil (% do patrimônio). Ponto de partida para a
# conversa com o cliente — editável no app, não é recomendação fechada.
PERFIS = {
    "Conservador": {
        "Renda Fixa Pós (CDI/Selic)": 45, "Renda Fixa Pré": 10, "Renda Fixa IPCA+": 25,
        "Fundos de Investimento": 10, "Ações": 5, "FIIs": 5,
    },
    "Moderado": {
        "Renda Fixa Pós (CDI/Selic)": 30, "Renda Fixa Pré": 10, "Renda Fixa IPCA+": 20,
        "Fundos de Investimento": 10, "Ações": 15, "FIIs": 10, "Internacional": 5,
    },
    "Arrojado": {
        "Renda Fixa Pós (CDI/Selic)": 10, "Renda Fixa Pré": 5, "Renda Fixa IPCA+": 15,
        "Fundos de Investimento": 10, "Ações": 35, "FIIs": 10, "Internacional": 15,
    },
}

LIMITE_ATIVO_PCT = 20.0   # um único ativo acima disso vira alerta
LIMITE_CLASSE_PCT = 60.0  # uma classe acima disso vira alerta (exceto RF pós)


# --------------------------------------------------------------------------- #
# Análise da carteira
# --------------------------------------------------------------------------- #
def _num(v) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return 0.0
    return x if x == x else 0.0  # NaN -> 0


def _br(v: float, casas: int = 1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def analisar_carteira(posicoes: list[dict]) -> dict:
    """Consolida as posições do cliente.

    Cada posição: {"ativo", "classe", "valor_aplicado", "valor_atual"}.
    Linhas sem ativo ou com valor atual <= 0 são ignoradas.
    """
    validas = []
    for p in posicoes:
        ativo = str(p.get("ativo") or "").strip()
        atual = _num(p.get("valor_atual"))
        # negativos entram (opções vendidas, saldo devedor): reduzem o patrimônio de verdade
        if not ativo or atual == 0:
            continue
        aplicado = _num(p.get("valor_aplicado")) or atual
        validas.append({
            "ativo": ativo,
            "classe": p.get("classe") or "Caixa",
            "valor_aplicado": aplicado,
            "valor_atual": atual,
        })

    total = sum(p["valor_atual"] for p in validas)
    aplicado = sum(p["valor_aplicado"] for p in validas)
    if total <= 0:
        return {"total": 0.0, "aplicado": 0.0, "resultado": 0.0, "rentab_pct": 0.0,
                "ativos": [], "classes": [], "hhi": 0.0, "n_efetivo": 0.0,
                "maior_ativo": None, "alertas": []}

    ativos = []
    for p in validas:
        ativos.append({
            **p,
            "peso_pct": p["valor_atual"] / total * 100,
            "resultado": p["valor_atual"] - p["valor_aplicado"],
            "rentab_pct": (p["valor_atual"] / p["valor_aplicado"] - 1) * 100,
        })
    ativos.sort(key=lambda a: a["valor_atual"], reverse=True)

    por_classe: dict[str, float] = {}
    for a in ativos:
        por_classe[a["classe"]] = por_classe.get(a["classe"], 0.0) + a["valor_atual"]
    classes = sorted(
        ({"classe": c, "valor": v, "peso_pct": v / total * 100} for c, v in por_classe.items()),
        key=lambda c: c["valor"], reverse=True,
    )

    # Herfindahl: soma dos pesos² (0–1). 1/HHI = nº "efetivo" de ativos iguais.
    hhi = sum((a["peso_pct"] / 100) ** 2 for a in ativos)
    alertas = []
    for a in ativos:
        if a["peso_pct"] > LIMITE_ATIVO_PCT:
            alertas.append(f"{a['ativo']} representa {_br(a['peso_pct'])}% da carteira "
                           f"(acima de {LIMITE_ATIVO_PCT:.0f}%).")
    for c in classes:
        if c["classe"] != "Renda Fixa Pós (CDI/Selic)" and c["peso_pct"] > LIMITE_CLASSE_PCT:
            alertas.append(f"{c['classe']} concentra {_br(c['peso_pct'])}% do patrimônio.")
    caixa = por_classe.get("Caixa", 0.0) / total * 100
    if caixa > 15:
        alertas.append(f"{_br(caixa)}% parado em caixa — avaliar alocação.")
    for a in ativos:
        if a["rentab_pct"] < -20:
            alertas.append(f"{a['ativo']} acumula {_br(a['rentab_pct'])}% — revisar a tese.")

    return {
        "total": total,
        "aplicado": aplicado,
        "resultado": total - aplicado,
        "rentab_pct": (total / aplicado - 1) * 100 if aplicado else 0.0,
        "ativos": ativos,
        "classes": classes,
        "hhi": hhi,
        "n_efetivo": 1 / hhi if hhi else 0.0,
        "maior_ativo": ativos[0],
        "alertas": alertas,
    }


def comparar_perfil(classes: list[dict], total: float, alvo: dict[str, float]) -> list[dict]:
    """Atual × alvo por classe: diferença em p.p. e R$ a comprar (+) / vender (−)."""
    atual = {c["classe"]: c["peso_pct"] for c in classes}
    linhas = []
    for classe in dict.fromkeys(list(alvo) + list(atual)):
        a, t = atual.get(classe, 0.0), float(alvo.get(classe, 0.0))
        linhas.append({
            "classe": classe, "atual_pct": a, "alvo_pct": t,
            "dif_pp": t - a, "ajuste_rs": (t - a) / 100 * total,
        })
    return sorted(linhas, key=lambda l: abs(l["dif_pp"]), reverse=True)


# --------------------------------------------------------------------------- #
# Projeção (BIG NUMBERS)
# --------------------------------------------------------------------------- #
def taxa_mensal(anual_pct: float) -> float:
    """Taxa anual efetiva (%) -> taxa mensal equivalente (fração)."""
    return (1 + anual_pct / 100) ** (1 / 12) - 1


def projetar(patrimonio: float, aporte_mensal: float, taxa_anual_pct: float, anos: int,
             ir_pct: float = 15.0, inflacao_pct: float = 0.0,
             reajustar_aporte: bool = True) -> list[dict]:
    """Evolução ano a ano (ano 0 = hoje).

    - Capitaliza mensalmente à taxa equivalente de ``taxa_anual_pct``; o aporte
      entra no fim de cada mês.
    - ``reajustar_aporte``: o aporte sobe pela inflação a cada 12 meses
      (o cliente mantém o esforço de poupança em termos reais).
    - ``liquido``: valor se resgatado naquele ano, com IR de ``ir_pct`` sobre o
      ganho (bruto − tudo que foi aportado). Renda fixa > 2 anos = 15%.
    - ``real``: o líquido em reais de hoje, deflacionado por ``inflacao_pct``.
    """
    i = taxa_mensal(taxa_anual_pct)
    saldo = float(patrimonio)
    investido = float(patrimonio)
    aporte = float(aporte_mensal)
    linhas = [_linha(0, saldo, investido, ir_pct, inflacao_pct, aporte)]
    for mes in range(1, int(anos) * 12 + 1):
        saldo = saldo * (1 + i) + aporte
        investido += aporte
        if mes % 12 == 0:
            ano = mes // 12
            if reajustar_aporte:
                aporte *= 1 + inflacao_pct / 100
            linhas.append(_linha(ano, saldo, investido, ir_pct, inflacao_pct, aporte))
    return linhas


def _linha(ano, saldo, investido, ir_pct, inflacao_pct, aporte) -> dict:
    ganho = max(saldo - investido, 0.0)
    ir = ganho * ir_pct / 100
    liquido = saldo - ir
    deflator = (1 + inflacao_pct / 100) ** ano
    return {
        "ano": ano, "bruto": saldo, "investido": investido, "juros": saldo - investido,
        "ir": ir, "liquido": liquido, "real": liquido / deflator, "aporte_mensal": aporte,
    }


def juro_real(taxa_anual_pct: float, inflacao_pct: float) -> float:
    """Juro real anual (%) pela equação de Fisher."""
    return ((1 + taxa_anual_pct / 100) / (1 + inflacao_pct / 100) - 1) * 100


def renda_mensal_perpetua(patrimonio: float, taxa_anual_pct: float, inflacao_pct: float,
                          ir_pct: float = 15.0) -> float:
    """Retirada mensal (R$ de hoje) que NÃO consome o poder de compra do patrimônio.

    O IR incide sobre o rendimento nominal do mês (inclusive a parte que só
    repõe a inflação); do líquido, reinveste-se o suficiente para o principal
    acompanhar a inflação e só o excedente é retirado:
    retirada = P · [(1 + i·(1−IR)) / (1 + π) − 1], com i e π mensais.
    """
    i = taxa_mensal(taxa_anual_pct) * (1 - ir_pct / 100)
    pi = taxa_mensal(inflacao_pct)
    return max(patrimonio * ((1 + i) / (1 + pi) - 1), 0.0)


def big_numbers(patrimonio: float, aporte_mensal: float, taxa_anual_pct: float,
                inflacao_pct: float, ir_pct: float = 15.0, passo: int = 5,
                horizonte: int = 30, reajustar_aporte: bool = True) -> list[dict]:
    """Marcos a cada ``passo`` anos até ``horizonte``, com a retirada mensal possível."""
    linhas = projetar(patrimonio, aporte_mensal, taxa_anual_pct, horizonte,
                      ir_pct, inflacao_pct, reajustar_aporte)
    marcos = []
    for l in linhas:
        if l["ano"] and l["ano"] % passo == 0:
            marcos.append({**l, "multiplo": l["real"] / patrimonio if patrimonio else None,
                           "renda_mensal": renda_mensal_perpetua(l["real"], taxa_anual_pct,
                                                                 inflacao_pct, ir_pct)})
    return marcos


def aporte_para_meta(meta_real: float, patrimonio: float, taxa_anual_pct: float,
                     inflacao_pct: float, anos: int, ir_pct: float = 15.0,
                     reajustar_aporte: bool = True) -> float | None:
    """Aporte mensal (R$ de hoje) para o líquido em reais de hoje chegar a ``meta_real``.

    Resolve por bisseção sobre ``projetar`` — assim vale exatamente o mesmo
    modelo da projeção (IR no resgate, aporte corrigido pela inflação).
    Zero se o patrimônio atual já basta; None se o horizonte é inválido.
    """
    if anos <= 0:
        return None

    def final(a):
        return projetar(patrimonio, a, taxa_anual_pct, anos, ir_pct,
                        inflacao_pct, reajustar_aporte)[-1]["real"]

    if final(0) >= meta_real:
        return 0.0
    lo, hi = 0.0, max(meta_real / (anos * 12), 1.0)
    while final(hi) < meta_real:
        hi *= 2
    for _ in range(50):
        meio = (lo + hi) / 2
        lo, hi = (meio, hi) if final(meio) < meta_real else (lo, meio)
    return hi


def patrimonio_para_renda(renda_mensal: float, taxa_anual_pct: float, inflacao_pct: float,
                          ir_pct: float = 15.0) -> float | None:
    """Patrimônio (R$ de hoje) que sustenta ``renda_mensal`` sem perder poder de compra."""
    por_real = renda_mensal_perpetua(1.0, taxa_anual_pct, inflacao_pct, ir_pct)
    return renda_mensal / por_real if por_real > 0 else None


def media_anual_composta(serie_mensal_pct: list[float]) -> float | None:
    """Média anual geométrica (%) de uma série de taxas mensais em %."""
    if not serie_mensal_pct:
        return None
    f = 1.0
    for v in serie_mensal_pct:
        f *= 1 + v / 100
    return (f ** (12 / len(serie_mensal_pct)) - 1) * 100


def ano_atinge_meta(linhas: list[dict], meta: float, campo: str = "real") -> int | None:
    """Primeiro ano em que ``campo`` alcança a meta (None se não alcança)."""
    for l in linhas:
        if l[campo] >= meta:
            return l["ano"]
    return None


# --------------------------------------------------------------------------- #
# Persistência de clientes
# --------------------------------------------------------------------------- #
def slug(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "cliente"


def listar_clientes(pasta: Path = None) -> list[str]:
    pasta = pasta or CLIENTES_DIR
    if not pasta.exists():
        return []
    nomes = []
    for f in sorted(pasta.glob("*.json")):
        try:
            nomes.append(json.loads(f.read_text(encoding="utf-8")).get("nome") or f.stem)
        except (json.JSONDecodeError, OSError):
            continue
    return sorted(nomes, key=str.lower)


def carregar_cliente(nome: str, pasta: Path = None) -> dict | None:
    caminho = (pasta or CLIENTES_DIR) / f"{slug(nome)}.json"
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def salvar_cliente(dados: dict, pasta: Path = None) -> Path:
    pasta = pasta or CLIENTES_DIR
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"{slug(dados['nome'])}.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def excluir_cliente(nome: str, pasta: Path = None) -> None:
    caminho = (pasta or CLIENTES_DIR) / f"{slug(nome)}.json"
    if caminho.exists():
        caminho.unlink()
