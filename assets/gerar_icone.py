"""Gera o ícone .ico do app a partir da logo branca da Ciano.

A logo oficial é branca e transparente — sozinha, some no fundo claro da Área de
Trabalho. Aqui ela é composta sobre o azul-marinho da marca, em um quadrado com
margem, e exportada nos tamanhos que o Windows usa (16 a 256 px).

Rodar: py assets/gerar_icone.py
"""

from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent
ORIGEM = BASE / "ciano_logo_branco.png"
DESTINO = BASE / "ciano.ico"

FUNDO = (14, 34, 102)      # #0E2266 — azul-marinho da marca
MARGEM = 0.14              # respiro em volta da logo
TAMANHOS = [(t, t) for t in (16, 24, 32, 48, 64, 128, 256)]


def gerar() -> Path:
    logo = Image.open(ORIGEM).convert("RGBA")
    lado = 512
    tela = Image.new("RGBA", (lado, lado), FUNDO + (255,))

    # Redimensiona a logo preservando proporção, com margem
    util = int(lado * (1 - 2 * MARGEM))
    escala = min(util / logo.width, util / logo.height)
    logo = logo.resize((max(1, int(logo.width * escala)),
                        max(1, int(logo.height * escala))), Image.LANCZOS)

    tela.paste(logo, ((lado - logo.width) // 2, (lado - logo.height) // 2), logo)
    tela.save(DESTINO, format="ICO", sizes=TAMANHOS)
    return DESTINO


if __name__ == "__main__":
    caminho = gerar()
    print(f"icone gerado: {caminho} ({caminho.stat().st_size / 1024:.1f} KB)")
