"""
Importação das posições de clientes pela API Alia (rede Tailscale).

``GET {ALIA_URL}?reference_date=AAAA-MM-DD`` devolve um array JSON com as
posições de todos os clientes na data. A chamada é síncrona e pesada: pode
disparar uma exportação real na Alia e levar até 30 min — por isso:

- timeout de leitura de 35 min (recomendação da própria API);
- o resultado fica em cache local por data (``.cache/alia/``, fora do git),
  para não refazer a exportação a cada clique. São dados financeiros
  sensíveis: nada aqui é logado ou impresso.

O layout do JSON não é fixo para nós, então os campos (cliente, ativo, classe,
valores) são detectados por nomes candidatos e o mapeamento pode ser corrigido
na tela; o mapeamento escolhido fica salvo em ``data/alia_mapa.json``.
"""

import json
import re
import os
import unicodedata
from datetime import date, timedelta
from pathlib import Path

import requests

ALIA_URL = os.environ.get("ALIA_URL", "https://vps-db.tail5d0c1d.ts.net:8443/v1/positions")
TIMEOUT = (15, 2100)  # (conexão, leitura) em segundos — leitura > 30 min
CACHE_DIR = Path(__file__).resolve().parent / ".cache" / "alia"
MAPA_PATH = Path(__file__).resolve().parent / "data" / "alia_mapa.json"
# A API identifica o cliente só pelo nº da conta; o nome é cadastrado no app.
CONTAS_PATH = Path(__file__).resolve().parent / "data" / "alia_contas.json"

# Campos do layout BTG/Alia que refinam a classe ("RENDA FIXA" + "BANCARIO" +
# "100% CDI"): somados ao texto da classe quando existirem no registro.
CAMPOS_CLASSE_EXTRA = ("sub_market", "indexer")

MENSAGENS_HTTP = {
    400: "Data ausente, inválida ou futura.",
    502: "A Alia falhou ao gerar o resultado. Tente novamente mais tarde.",
    503: "Servidor ocupado (limite de 2 exportações simultâneas). Tente em alguns segundos.",
    504: "A exportação passou de 30 min; ela continua no servidor — chame de novo a mesma data "
         "para aproveitar o job em andamento.",
}

# Campo lógico -> nomes candidatos no JSON (comparados sem acento/caixa/_).
CANDIDATOS = {
    "cliente": ["client_name", "customer_name", "investor_name", "account_name", "holder_name",
                "nome_cliente", "cliente", "client", "customer", "investidor", "titular",
                "account", "conta", "client_id", "customer_id", "account_id", "account_number"],
    "ativo": ["asset_name", "security_name", "product_name", "instrument_name", "ativo",
              "produto", "ticker", "symbol", "asset", "security", "product", "description",
              "descricao", "name", "nome"],
    "classe": ["asset_class", "classe", "classe_ativo", "product_type", "asset_type",
               "security_type", "instrument_type", "category", "categoria", "tipo",
               "type", "market", "mercado"],
    "valor_atual": ["gross_value", "market_value", "current_value", "position_value",
                    "valor_bruto", "valor_atual", "saldo_bruto", "saldo", "balance",
                    "net_value", "valor_liquido", "amount", "value", "valor", "total"],
    "valor_aplicado": ["applied_value", "invested_value", "invested_amount", "cost_basis",
                       "book_value", "valor_aplicado", "valor_investido", "custo", "cost"],
}

# Texto da classe/produto -> classe do planejamento (primeira regra que casar).
REGRAS_CLASSE = [
    (("valor em transito", "conta corrente"), "Caixa"),  # liquidações/proventos a receber
    # Fundos: classe própria, como no portal do BTG. O nome do fundo engana a
    # classificação ("Caixa", "Pré", "Imobiliário" no nome) — por isso vem antes.
    (("fundos", "fundo de investimento"), "Fundos de Investimento"),
    (("previd", "pgbl", "vgbl"), "Previdência"),
    (("cripto", "crypto", "bitcoin", "btc"), "Cripto"),
    (("fii", "imobiliario", "real estate"), "FIIs"),
    (("bdr", "internacional", "exterior", "offshore", "global", "stock us"), "Internacional"),
    (("multimercado", "hedge", "multi"), "Multimercado"),
    (("ipca", "ntn-b", "ntnb", "inflacao", "imab"), "Renda Fixa IPCA+"),
    (("prefix", "pre-fix", "pre fix", "ltn", "ntn-f", "ntnf", " pre"), "Renda Fixa Pré"),
    (("acao", "acoes", "equity", "stock", "bolsa", "renda variavel", "etf"), "Ações"),
    (("conta", "caixa", "cash", "saldo em conta", "disponivel"), "Caixa"),
    (("cdb", "lci", "lca", "lft", "selic", "cdi", " pos", "debenture", " cri", " cra",
      "renda fixa", "tesouro", "fixed income", "compromissada", " di "), "Renda Fixa Pós (CDI/Selic)"),
]


class AliaErro(RuntimeError):
    pass


def _norm(txt) -> str:
    s = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode().lower()
    return s.replace("_", "").replace("-", "").replace(" ", "")


def _plano(txt) -> str:
    s = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode().lower()
    return f" {s} "  # bordas: permite casar palavras inteiras (" di ", " pre")


def ultimo_dia_util(ref: date = None) -> date:
    """Dia útil anterior a ``ref`` (a API recusa data futura; hoje pode não estar fechado)."""
    d = (ref or date.today()) - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


# --------------------------------------------------------------------------- #
# Rede + cache
# --------------------------------------------------------------------------- #
def _cache_path(data_ref: str) -> Path:
    return CACHE_DIR / f"positions_{data_ref}.json"


def tem_cache(data_ref: str) -> bool:
    return _cache_path(data_ref).exists()


def buscar_posicoes(data_ref: str, usar_cache: bool = True) -> list[dict]:
    """Posições de todos os clientes em ``data_ref`` (AAAA-MM-DD)."""
    date.fromisoformat(data_ref)  # valida o formato antes de disparar o job
    cache = _cache_path(data_ref)
    if usar_cache and cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    try:
        r = requests.get(ALIA_URL, params={"reference_date": data_ref}, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        raise AliaErro("Sem conexão com o servidor da Alia. Verifique se o Tailscale está "
                       "ligado e se este computador tem acesso ao tailnet.") from None
    except requests.exceptions.Timeout:
        raise AliaErro(MENSAGENS_HTTP[504]) from None
    if r.status_code != 200:
        detalhe = _detalhe_erro(r)
        raise AliaErro(f"HTTP {r.status_code}: {MENSAGENS_HTTP.get(r.status_code, 'erro inesperado.')}"
                       + (f" Detalhe do servidor: {detalhe}" if detalhe else ""))
    try:
        dados = r.json()
    except ValueError:
        raise AliaErro("Resposta da Alia não é JSON.") from None
    registros = extrair_registros(dados)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")
    return registros


def _detalhe_erro(r) -> str:
    """Mensagem curta que o servidor devolve no erro (nunca dados de posição)."""
    try:
        corpo = r.json()
        if isinstance(corpo, dict):
            return str(corpo.get("detail") or corpo.get("error") or corpo.get("message") or "")[:200]
    except (ValueError, AttributeError):
        pass
    return str(getattr(r, "text", "") or "")[:200]


def extrair_registros(dados) -> list[dict]:
    """Aceita o array direto ou um envelope ({"positions": [...]}, {"data": [...]})."""
    if isinstance(dados, list):
        return [achatar(d) for d in dados if isinstance(d, dict)]
    if isinstance(dados, dict):
        for v in dados.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return [achatar(d) for d in v]
    raise AliaErro("Formato de resposta inesperado (esperava uma lista de posições).")


def achatar(d: dict, prefixo: str = "") -> dict:
    """{"client": {"name": "X"}} -> {"client.name": "X"} (só dicts; listas ficam como estão)."""
    out = {}
    for k, v in d.items():
        chave = f"{prefixo}{k}"
        if isinstance(v, dict):
            out.update(achatar(v, chave + "."))
        else:
            out[chave] = v
    return out


# --------------------------------------------------------------------------- #
# Mapeamento de campos
# --------------------------------------------------------------------------- #
def campos(registros: list[dict]) -> list[str]:
    vistos = {}
    for r in registros[:500]:
        for k in r:
            vistos.setdefault(k, None)
    return list(vistos)


def _numerico(registros: list[dict], campo: str) -> bool:
    for r in registros[:50]:
        v = r.get(campo)
        if v is None or v == "":
            continue
        return _para_num(v) is not None
    return False


def detectar_mapa(registros: list[dict]) -> dict[str, str | None]:
    """Melhor palpite de qual campo do JSON é cada campo lógico."""
    disponiveis = campos(registros)
    por_norm = {}
    for c in disponiveis:
        por_norm.setdefault(_norm(c), c)
        por_norm.setdefault(_norm(c.split(".")[-1]), c)   # "client.name" também casa "name"
        por_norm.setdefault(_norm(c.replace(".", "_")), c)  # e "client_name"
    mapa, usados = {}, set()
    for logico, nomes in CANDIDATOS.items():
        escolhido = None
        for n in nomes:
            c = por_norm.get(_norm(n))
            if c and c not in usados:
                if logico.startswith("valor") and not _numerico(registros, c):
                    continue
                escolhido = c
                break
        mapa[logico] = escolhido
        if escolhido:
            usados.add(escolhido)
    return mapa


def carregar_mapa(caminho: Path = None) -> dict:
    caminho = caminho or MAPA_PATH
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def salvar_mapa(mapa: dict, caminho: Path = None) -> None:
    caminho = caminho or MAPA_PATH
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(mapa, ensure_ascii=False, indent=2), encoding="utf-8")


def classificar(texto) -> str:
    """Texto livre de classe/produto -> uma das classes do planejamento."""
    t = _plano(texto)
    for chaves, classe in REGRAS_CLASSE:
        if any(k in t for k in chaves):
            return classe
    return "Renda Fixa Pós (CDI/Selic)" if not t.strip() else "Multimercado"


def _valor(v) -> float:
    n = _para_num(v)
    return 0.0 if n is None else n


def _para_num(v) -> float | None:
    """Número de int/float ou texto BR/US ("1.234,56", "1,234.56", "R$ 10,5"); None se não for."""
    if v is None or v == "" or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("R$", "").replace(" ", "")
    if "," in s and "." in s:  # 1.234,56 (BR) ou 1,234.56 (US)
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def carregar_contas(caminho: Path = None) -> dict[str, str]:
    """nº da conta -> nome do cliente."""
    try:
        dados = json.loads((caminho or CONTAS_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {str(k): str(v) for k, v in dados.items() if str(v).strip()}


def salvar_contas(contas: dict, caminho: Path = None) -> None:
    caminho = caminho or CONTAS_PATH
    caminho.parent.mkdir(parents=True, exist_ok=True)
    limpas = {str(k): str(v).strip() for k, v in contas.items() if v and str(v).strip()}
    caminho.write_text(json.dumps(limpas, ensure_ascii=False, indent=2), encoding="utf-8")


def ler_lista_contas(texto: str) -> dict[str, str]:
    """Lista de clientes copiada do portal do BTG -> {conta: nome}.

    O portal repete o bloco "Nome / conta / tipo (Investimentos|Banking ...) /
    Nome / Acessar", às vezes com várias contas sob o mesmo nome. Para cada
    linha que é só um número de conta, o nome é a primeira linha seguinte que
    não é o tipo da conta, a inicial do índice alfabético nem "Acessar".
    """
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    contas = {}
    for i, l in enumerate(linhas):
        if not re.fullmatch(r"\d{5,}", l):
            continue
        for prox in linhas[i + 1:i + 4]:
            baixo = prox.lower()
            if (re.fullmatch(r"\d{5,}", prox) or len(prox) <= 1 or baixo == "acessar"
                    or re.match(r"(investimentos|banking|conta|individual|conjunta)\b", baixo)):
                continue
            contas[l] = prox
            break
    return contas


def _sem_zeros(conta) -> str:
    return str(conta).strip().lstrip("0")


def _texto_classe(r: dict, ccl: str | None) -> str:
    partes = [r.get(ccl)] if ccl else []
    partes += [r.get(c) for c in CAMPOS_CLASSE_EXTRA if c != ccl]
    return " ".join(str(p) for p in partes if p not in (None, ""))


# Quando o campo do ativo vem vazio (na Alia: fundos, valores em trânsito e conta
# corrente), o nome está em outro campo. Sem isso a linha era descartada e a
# carteira perdia valor (ex.: metade do patrimônio de quem tem fundos).
ALTERNATIVAS_ATIVO = ("product", "product_name", "produto", "security_name", "issuer",
                      "description", "descricao")


def _nome_ativo(r: dict, campo: str) -> str:
    for c in (campo, *ALTERNATIVAS_ATIVO):
        v = str(r.get(c) or "").strip()
        if v:
            return v
    rotulo = " ".join(str(r.get(c) or "") for c in ("market", "sub_market")).strip()
    return rotulo.title() or "Sem descrição"


def agrupar_por_cliente(registros: list[dict], mapa: dict,
                        nomes: dict[str, str] = None) -> dict[str, list[dict]]:
    """Posições no formato do planejamento, agrupadas por cliente.

    ``nomes`` traduz o identificador do cliente (ex.: nº da conta) para o nome;
    contas sem nome ficam pelo próprio número. Posições do mesmo ativo (ex.:
    várias aplicações no mesmo CDB) são somadas.
    """
    cc, ca, ccl = mapa.get("cliente"), mapa.get("ativo"), mapa.get("classe")
    cva, cvp = mapa.get("valor_atual"), mapa.get("valor_aplicado")
    if not (cc and ca and cva):
        raise AliaErro("Mapeie ao menos os campos de cliente, ativo e valor atual.")
    # casa "005407133" com "5407133": a API e o portal podem divergir nos zeros à esquerda
    nomes = {_sem_zeros(k): v for k, v in (nomes or {}).items()}
    clientes: dict[str, dict[str, dict]] = {}
    for r in registros:
        ident = str(r.get(cc) or "").strip()
        cliente = nomes.get(_sem_zeros(ident), ident)
        ativo = _nome_ativo(r, ca)
        atual = _valor(r.get(cva))
        if not cliente or not ativo or atual == 0:
            continue
        aplicado = _valor(r.get(cvp)) if cvp else 0.0
        texto = _texto_classe(r, ccl)
        classe = classificar(texto or ativo)
        if texto and classe == "Multimercado" and classificar(ativo) != "Multimercado":
            classe = classificar(ativo)  # classe genérica (ex.: FUNDOS): tenta pelo nome do ativo
        pos = clientes.setdefault(cliente, {}).setdefault(
            ativo, {"ativo": ativo, "classe": classe, "valor_aplicado": 0.0, "valor_atual": 0.0})
        pos["valor_atual"] += atual
        pos["valor_aplicado"] += aplicado or atual
    return {c: sorted(p.values(), key=lambda x: -x["valor_atual"])
            for c, p in sorted(clientes.items(), key=lambda kv: kv[0].lower())}
