"""
Dados macro para apoio à decisão, de fontes públicas gratuitas.

- Global (Yahoo Finance): DXY (índice dólar), Ouro, Treasury 10 anos.
- EUA (BLS, órgão oficial de estatísticas): inflação (CPI) em 12 meses.
- Brasil (API do Banco Central): Selic meta, IPCA 12m, Dívida Bruta/PIB e as
  projeções do Focus (IPCA e Selic), mais o juro real ex-ante derivado.

Cada indicador vem com o valor mais recente E a série histórica, para o app
desenhar a trajetória.

Notas de rede (descobertas na marra):
- ``api.bcb.gov.br`` responde mal por IPv6 nesta rede (o handshake TLS trava):
  forçamos IPv4 em todas as chamadas (``_forcar_ipv4``). IPv4 também serve ao
  Yahoo e ao BLS, então não há prejuízo.
- O FRED (fred.stlouisfed.org) derruba a conexão daqui; por isso a inflação
  americana vem do BLS, que é a fonte primária do dado mesmo.

Cada consulta bate na rede, então há cache local com TTL (as séries macro mudam
devagar) — e o BC limita chamadas repetidas, o que reforça o cache.
"""

import json
import socket
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

import requests
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
# O nome do cache tem versão: ao mudar o FORMATO do que é guardado (ex.: incluir
# as séries históricas), incremente para invalidar caches antigos — senão o app
# serve um cache velho, sem os campos novos (foi exatamente o que aconteceu).
CACHE_VERSAO = 2
CACHE_FILE = CACHE_DIR / f"macro_v{CACHE_VERSAO}.json"
CACHE_TTL_SEGUNDOS = 3 * 60 * 60  # 3 horas
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Séries do SGS/BC: código -> nº de pontos do histórico (432 é diária; as outras, mensais)
SGS_SELIC, SGS_IPCA12M, SGS_DIVIDA_PIB = 432, 13522, 13762
BLS_CPI = "CUUR0000SA0"  # CPI-U, todos os itens (EUA)

_ipv4_ativo = False


def _forcar_ipv4() -> None:
    """Faz o urllib3 resolver só IPv4 (o BC trava o TLS por IPv6 nesta rede)."""
    global _ipv4_ativo
    if not _ipv4_ativo:
        import urllib3.util.connection as u3

        u3.allowed_gai_family = lambda: socket.AF_INET
        _ipv4_ativo = True


def _para_float(txt) -> float | None:
    try:
        return float(str(txt).replace(",", "."))
    except (TypeError, ValueError):
        return None


def juro_real_ex_ante(selic_pct: float, ipca_esperado_pct: float) -> float | None:
    """Juro real ex-ante (%) = ((1+Selic)/(1+IPCA esperado) − 1)·100 (Fisher)."""
    if selic_pct is None or ipca_esperado_pct is None:
        return None
    return ((1 + selic_pct / 100) / (1 + ipca_esperado_pct / 100) - 1) * 100


def variacao_12m(serie: list[dict]) -> float | None:
    """Variação % em 12 observações mensais (usada no CPI, que vem em nível)."""
    if not serie or len(serie) < 13:
        return None
    atual, ha_um_ano = serie[-1]["valor"], serie[-13]["valor"]
    if not ha_um_ano:
        return None
    return (atual / ha_um_ano - 1) * 100


def serie_juro_real(serie_selic: list[dict], serie_ipca: list[dict]) -> dict:
    """Trajetória do juro real ex-ante, cruzando as séries do Focus pela data.

    As duas séries do Focus (Selic e IPCA esperados) são pesquisadas nas mesmas
    datas, então casam por data. Função pura (testável sem rede).
    """
    ipca_por_data = {p["data"]: p["valor"] for p in (serie_ipca or [])}
    serie = []
    for p in serie_selic or []:
        jr = juro_real_ex_ante(p["valor"], ipca_por_data.get(p["data"]))
        if jr is not None:
            serie.append({"data": p["data"], "valor": jr})
    return _pacote(serie)


def _pacote(serie: list[dict]) -> dict:
    """Empacota uma série em {valor, data, serie} com o último ponto no topo."""
    if not serie:
        return {"valor": None, "data": None, "serie": []}
    ultimo = serie[-1]
    return {"valor": ultimo["valor"], "data": ultimo["data"], "serie": serie}


def _json_bc(url: str, tentativas: int = 3):
    """GET no BC com validação de conteúdo e backoff.

    Cuidados aprendidos na prática com essa API:
    - ela às vezes devolve JSON válido com ``Content-Type: text/html``, então
      validar pelo cabeçalho dá falso positivo — validamos o CONTEÚDO;
    - quando recusa a consulta, devolve 200/400 com um objeto ``{"erro": ...}``,
      que aqui vira uma mensagem legível em vez de um parse quebrado.
    """
    _forcar_ipv4()
    erro = ""
    for i in range(tentativas):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            try:
                dados = r.json()
            except ValueError:
                raise RuntimeError("Banco Central indisponível (resposta não-JSON).")
            if isinstance(dados, dict) and "erro" in dados:
                detalhe = str(dados["erro"].get("detail", ""))
                detalhe = detalhe.split(":")[-1].strip()[:70]
                raise RuntimeError(f"Banco Central recusou a consulta: {detalhe}")
            return dados
        except Exception as e:  # noqa: BLE001
            erro = str(e)
            if i < tentativas - 1:
                time.sleep(2 * (i + 1))  # backoff: 2s, 4s
    raise RuntimeError(erro[:110])


def _sgs(codigo: int, anos: int = 3) -> dict:
    """Série do SGS/BC nos últimos ``anos``.

    Usa o filtro por intervalo de datas: o endpoint ``ultimos/N`` tem um teto
    baixo de registros (400 acima de ~12 pontos) e não serve para histórico.
    """
    fim = date.today()
    ini = fim - timedelta(days=365 * anos)
    url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
           f"&dataInicial={ini.strftime('%d/%m/%Y')}&dataFinal={fim.strftime('%d/%m/%Y')}")
    dados = _json_bc(url)
    if not isinstance(dados, list):
        raise RuntimeError("Resposta inesperada do Banco Central.")
    serie = [{"data": d["data"], "valor": _para_float(d["valor"])} for d in dados]
    return _pacote([p for p in serie if p["valor"] is not None])


def _focus(indicador: str, pontos: int = 60) -> dict:
    """Evolução da mediana do Focus para o ano de referência mais recente.

    Duas consultas: a 1ª descobre o ano de referência corrente; a 2ª traz a série
    da mediana para aquele ano (mostra se as expectativas estão ancorando).
    O filtro precisa ser montado inteiro no ``$filter`` — concatenar a cláusula
    depois do ``$orderby`` corrompe a query e o Olinda devolve uma página de erro.
    """
    raiz = ("https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
            "ExpectativasMercadoAnuais?$format=json&$select=DataReferencia,Mediana,Data")

    def consulta(filtro: str, top: int) -> list:
        url = (f"{raiz}&$filter={quote(filtro)}"
               f"&$orderby={quote('Data desc')}&$top={top}")
        return _json_bc(url).get("value") or []

    linhas = consulta(f"Indicador eq '{indicador}'", 1)
    if not linhas:
        return _pacote([])
    ref = linhas[0]["DataReferencia"]

    dados = consulta(f"Indicador eq '{indicador}' and DataReferencia eq '{ref}'", pontos)
    serie = [{"data": x["Data"], "valor": _para_float(x["Mediana"])} for x in dados]
    serie = [p for p in serie if p["valor"] is not None][::-1]  # cronológico
    out = _pacote(serie)
    out["ref"] = ref
    return out


def _yahoo(ticker: str, periodo: str = "2y") -> dict:
    """Série de fechamentos do Yahoo + variação no ano (YTD)."""
    h = yf.Ticker(ticker).history(period=periodo)
    if h is None or h.empty:
        return _pacote([])
    fech = h["Close"].dropna()
    serie = [{"data": d.strftime("%d/%m/%Y"), "valor": float(v)} for d, v in fech.items()]
    out = _pacote(serie)
    # Variação no ano corrente
    ano = fech.index[-1].year
    do_ano = fech[fech.index.year == ano]
    if len(do_ano) >= 2:
        out["var_ano"] = (float(do_ano.iloc[-1]) / float(do_ano.iloc[0]) - 1) * 100
    return out


def _cpi_eua() -> dict:
    """Inflação americana (CPI) em 12 meses, via BLS. Série já convertida para % a.a."""
    _forcar_ipv4()
    ano = time.gmtime().tm_year
    r = requests.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json={"seriesid": [BLS_CPI], "startyear": str(ano - 4), "endyear": str(ano)},
        headers={**HEADERS, "Content-Type": "application/json"}, timeout=30,
    )
    bruto = r.json()["Results"]["series"][0]["data"]
    mensais = [x for x in bruto if x["period"].startswith("M")]
    mensais.sort(key=lambda x: (int(x["year"]), int(x["period"][1:])))
    niveis = [{"data": f"{x['period'][1:]}/{x['year']}", "valor": _para_float(x["value"])}
              for x in mensais]
    niveis = [p for p in niveis if p["valor"] is not None]
    # converte o nível do índice em variação de 12 meses
    yoy = [
        {"data": niveis[i]["data"],
         "valor": (niveis[i]["valor"] / niveis[i - 12]["valor"] - 1) * 100}
        for i in range(12, len(niveis))
    ]
    return _pacote(yoy)


def _coletar() -> dict:
    """Busca tudo na rede. Cada indicador falha isolado (vira {'erro': ...})."""
    def seguro(fn, *a):
        try:
            return fn(*a)
        except Exception as e:  # noqa: BLE001
            return {"valor": None, "serie": [], "erro": str(e)[:90]}

    global_ = {
        "dxy": seguro(_yahoo, "DX-Y.NYB"),
        "ouro": seguro(_yahoo, "GC=F"),
        "treasury10a": seguro(_yahoo, "^TNX"),
        "cpi_eua": seguro(_cpi_eua),
    }
    brasil = {
        "selic": seguro(_sgs, SGS_SELIC, 3),        # diária -> 3 anos
        "ipca12m": seguro(_sgs, SGS_IPCA12M, 5),    # mensal -> 5 anos
        "divida_pib": seguro(_sgs, SGS_DIVIDA_PIB, 5),
        "focus_ipca": seguro(_focus, "IPCA"),
        "focus_selic": seguro(_focus, "Selic"),
    }
    brasil["juro_real_ex_ante"] = serie_juro_real(
        brasil["focus_selic"].get("serie"), brasil["focus_ipca"].get("serie")
    )
    return {"global": global_, "brasil": brasil, "ts": time.time()}


def buscar_macro(usar_cache: bool = True, ttl_segundos: float = CACHE_TTL_SEGUNDOS) -> dict:
    """Painel macro (global + EUA + brasil) com séries históricas, via cache local."""
    if usar_cache and CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if time.time() - cache.get("ts", 0) < ttl_segundos:
                return cache
        except (json.JSONDecodeError, OSError):
            pass
    dados = _coletar()
    if usar_cache:
        CACHE_DIR.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return dados
