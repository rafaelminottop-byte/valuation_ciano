# -*- coding: utf-8 -*-
"""
Coletor de cartas de gestoras.

Uso:
  py coletor.py <url_do_pdf> [<url2> ...]   -> baixa o(s) PDF(s), extrai o texto
                                               e salva em _coletados/<nome>.txt
  py coletor.py --gestora "Dynamo"          -> vasculha a pagina da gestora
                                               (em dados/gestoras.js) atras de links .pdf

Depois de rodar, peca ao Claude para ler os .txt em _coletados/ e escrever o
resumo em dados/cartas.js. O texto extraido tambem fica no console.
"""
import sys, os, re, io, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "_coletados")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) coletor-cartas/1.0"}

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def baixar(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def extrair_texto_pdf(dados_bytes):
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(dados_bytes))
    partes = [(p.extract_text() or "") for p in reader.pages]
    return "\n".join(partes), len(reader.pages)


def nome_arquivo(url):
    base = os.path.basename(urllib.parse.urlparse(url).path) or "carta"
    base = re.sub(r"\.pdf$", "", base, flags=re.I)
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", base).strip("_") or "carta"
    return base


def processar_pdf(url):
    print(f"\n== Baixando: {url}")
    try:
        dados = baixar(url)
    except Exception as e:
        print(f"   ERRO ao baixar: {e}")
        return
    if b"%PDF" not in dados[:1024]:
        print("   AVISO: nao parece um PDF (talvez precise de outro link).")
    try:
        texto, npag = extrair_texto_pdf(dados)
    except Exception as e:
        print(f"   ERRO ao extrair texto: {e}")
        return
    os.makedirs(OUT, exist_ok=True)
    destino = os.path.join(OUT, nome_arquivo(url) + ".txt")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(f"FONTE: {url}\nPAGINAS: {npag}\nCARACTERES: {len(texto)}\n\n{texto}")
    print(f"   OK: {npag} paginas, {len(texto)} chars -> {os.path.relpath(destino, BASE)}")


def links_pdf_da_pagina(url_pagina):
    try:
        req = urllib.request.Request(url_pagina, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"   ERRO ao abrir pagina: {e}")
        return []
    hrefs = re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html, flags=re.I)
    out = []
    for h in hrefs:
        out.append(urllib.parse.urljoin(url_pagina, h))
    # remove duplicatas mantendo ordem
    vistos, res = set(), []
    for u in out:
        if u not in vistos:
            vistos.add(u); res.append(u)
    return res


def pagina_da_gestora(nome):
    caminho = os.path.join(BASE, "dados", "gestoras.js")
    txt = open(caminho, encoding="utf-8").read()
    for m in re.finditer(r'nome:\s*"([^"]+)".*?pagina:\s*"([^"]+)"', txt):
        if m.group(1).lower() == nome.lower():
            return m.group(2)
    return None


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if args[0] == "--gestora":
        nome = args[1] if len(args) > 1 else ""
        pag = pagina_da_gestora(nome)
        if not pag:
            print(f"Gestora '{nome}' nao encontrada em dados/gestoras.js")
            return
        print(f"Procurando PDFs em: {pag}")
        links = links_pdf_da_pagina(pag)
        if not links:
            print("Nenhum link .pdf direto encontrado (site pode carregar via JS).")
            print("Abra a pagina no navegador, copie o link do PDF e rode:")
            print("  py coletor.py <url_do_pdf>")
            return
        print(f"Encontrados {len(links)} link(s) .pdf:")
        for l in links:
            print("  -", l)
        print("\nPara coletar, rode: py coletor.py " + " ".join(links[:3]))
        return
    for url in args:
        processar_pdf(url)
    print("\nPronto. Peca ao Claude para ler os arquivos em _coletados/ e resumir.")


if __name__ == "__main__":
    main()
