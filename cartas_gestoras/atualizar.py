# -*- coding: utf-8 -*-
"""
Atualizador de cartas: sonda os padroes de URL conhecidos, detecta cartas
que ainda NAO estao no feed (dados/cartas.js), baixa os PDFs novos para
_coletados/ e extrai o texto. No fim, lista o que apareceu.

Uso:  py atualizar.py
Depois: peca ao Claude para ler os .txt novos em _coletados/ e escrever o
resumo em dados/cartas.js.
"""
import os, re, io, sys, json, urllib.request
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "_coletados")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) atualizador-cartas/1.0"}
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def urls_existentes():
    txt = open(os.path.join(BASE, "dados", "cartas.js"), encoding="utf-8").read()
    return set(re.findall(r'url:\s*"([^"]+)"', txt))


def existe(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status == 200
    except Exception:
        # alguns servidores nao aceitam HEAD; tenta GET leve
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status == 200
        except Exception:
            return False


def meses_recentes(n=2):
    y, m = date.today().year, date.today().month
    out = []
    for _ in range(n):
        out.append((y, m))
        m -= 1
        if m == 0:
            m = 12; y -= 1
    return out


def candidatos():
    """Gera (gestora, url) candidatos a partir dos padroes conhecidos."""
    c = []
    for (y, m) in meses_recentes(2):
        mm = f"{m:02d}"
        c.append(("Verde (Multimercado)",
                  f"https://www.verdeasset.com.br/public/files/rel_gestao/158094/Verde-REL-{y}_{mm}.pdf"))
        c.append(("Verde (Acoes)",
                  f"https://www.verdeasset.com.br/public/files/rel_gestao/118/Acoes-REL-{y}_{mm}.pdf"))
        # Kinea: pasta = mes seguinte
        ny, nm = (y, m + 1) if m < 12 else (y + 1, 1)
        c.append(("Kinea (Prev Multimercado)",
                  f"https://www.kinea.com.br/wp-content/uploads/{ny}/{nm:02d}/Carta-do-Gestor-Prev-Multimercado-{y}-{mm}.pdf"))
    # Dynamo: proximos numeros, testando pasta do ano corrente em varios meses
    for num in range(129, 133):
        for (y, m) in meses_recentes(2):
            c.append(("Dynamo", f"https://www.dynamo.com.br/wp-content/uploads/{y}/{m:02d}/Carta-Dynamo-{num}.pdf"))
    # Atmos: proximos numeros sequenciais
    for num in range(34, 38):
        c.append(("Atmos", f"https://www.atmoscapital.com.br/documentos/cartas/Carta-Atmos-{num}.pdf"))
    return c


def baixar_extrair(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        dados = r.read()
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(dados))
    texto = "\n".join((p.extract_text() or "") for p in reader.pages)
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", os.path.basename(url).replace(".pdf", "")).strip("_")
    os.makedirs(OUT, exist_ok=True)
    destino = os.path.join(OUT, base + ".txt")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(f"FONTE: {url}\nPAGINAS: {len(reader.pages)}\n\n{texto}")
    return destino, len(reader.pages)


def main():
    ja = urls_existentes()
    print(f"Feed atual: {len(ja)} cartas. Procurando novidades...\n")
    novas = []
    vistos = set()
    for gestora, url in candidatos():
        if url in ja or url in vistos:
            continue
        vistos.add(url)
        if existe(url):
            print(f"  NOVA  [{gestora}] {url}")
            try:
                destino, npag = baixar_extrair(url)
                novas.append({"gestora": gestora, "url": url,
                              "arquivo": os.path.relpath(destino, BASE), "paginas": npag})
            except Exception as e:
                print(f"        (erro ao baixar/extrair: {e})")
    print()
    if novas:
        with open(os.path.join(OUT, "_novas.json"), "w", encoding="utf-8") as f:
            json.dump(novas, f, ensure_ascii=False, indent=2)
        print(f"{len(novas)} carta(s) nova(s) baixada(s) para _coletados/.")
        print("Agora peca ao Claude: \"li as cartas novas em _coletados e atualize o feed\".")
    else:
        print("Nenhuma carta nova encontrada. O feed ja esta em dia. :)")


if __name__ == "__main__":
    main()
