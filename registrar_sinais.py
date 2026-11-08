"""
Registra o sinal do mês no data/registro_sinais.json (um por mês, nunca sobrescreve).

É o teste fora da amostra de verdade: o histórico já foi visto e usado para calibrar,
então a única evidência limpa é a que ainda não aconteceu. Rode uma vez por mês.

    py registrar_sinais.py               # só grava o registro
    py registrar_sinais.py --publicar    # grava, faz commit SÓ do registro e envia ao GitHub

Se as regras do preditor.py mudarem sem um novo congelamento (versão + hash), o registro
é recusado de propósito: misturaria sinais de regras diferentes.
"""
import argparse
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
ARQ = "data/registro_sinais.json"


def _git(*args):
    return subprocess.run(["git", *args], cwd=AQUI, capture_output=True, text=True)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="Registra o sinal do mês do preditor do Ibovespa.")
    ap.add_argument("--publicar", action="store_true",
                    help="commit só do registro e envio ao GitHub (branch atual e main)")
    args = ap.parse_args()

    import preditor

    p = preditor.prever(usar_cache=False)
    if p.get("erro"):
        print("Não foi possível calcular o sinal agora:", p["erro"])
        return 1
    try:
        res = preditor.registrar(p)
    except RuntimeError as e:
        print(e)
        return 2

    e = res["entrada"]
    if res["status"] == "ja_existia":
        print(f"Já existe registro de {e['mes']} (gravado em {e['data_registro']}). Nada a fazer.")
        return 0

    print(f"Registrado {e['mes']} (regras v{e['regras_versao']}, hash {e['regras_hash']}):")
    print(f"  Ibov {e['ibov']} pts | z {e['z']} | score {e['score']} ({e['faixa_score']}) | "
          f"banda: {e['zona_banda']} | desconto: {e['faixa_desconto']} | Selic: {e['ciclo_selic']}")

    if args.publicar:
        _git("add", ARQ)
        c = _git("commit", "-m", f"Registro mensal de sinais ({e['mes']})", "--", ARQ)
        if c.returncode:
            print("Falha no commit:\n", c.stdout, c.stderr)
            return 3
        for destino in ("HEAD", "HEAD:main"):
            r = _git("push", "origin", destino)
            if r.returncode:
                print(f"Falha no push ({destino}):\n", r.stdout, r.stderr)
                return 4
        print("Registro publicado no GitHub.")
    else:
        print("Gravado localmente. Para publicar: py registrar_sinais.py --publicar (ou faça commit de "
              f"{ARQ}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
