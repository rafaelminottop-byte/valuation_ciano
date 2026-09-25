"""
Transcreve uma aula (audio/video) para texto em portugues usando faster-whisper.
Uso:
    py transcrever_aula.py "C:\\caminho\\para\\arquivo.mp4"
    py transcrever_aula.py "C:\\caminho\\para\\arquivo.mp4" --modelo small

Modelos (velocidade x qualidade): tiny, base, small, medium, large-v3
Gera um .txt (com timestamps) ao lado do arquivo de origem.
"""
import sys
import os
from faster_whisper import WhisperModel


def fmt(seg_time):
    m, s = divmod(int(seg_time), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main():
    if len(sys.argv) < 2:
        print("Uso: py transcrever_aula.py \"arquivo.mp4\" [--modelo small]")
        sys.exit(1)

    origem = sys.argv[1]
    modelo = "small"
    if "--modelo" in sys.argv:
        modelo = sys.argv[sys.argv.index("--modelo") + 1]

    if not os.path.exists(origem):
        print(f"Arquivo nao encontrado: {origem}")
        sys.exit(1)

    print(f"Carregando modelo '{modelo}' (primeira vez baixa; depois fica em cache)...")
    model = WhisperModel(modelo, device="cpu", compute_type="int8")

    print("Transcrevendo (pode levar alguns minutos)...")
    segments, info = model.transcribe(origem, language="pt", vad_filter=True)

    base = os.path.splitext(origem)[0]
    saida = base + "_transcricao.txt"
    with open(saida, "w", encoding="utf-8") as f:
        for seg in segments:
            linha = f"[{fmt(seg.start)}] {seg.text.strip()}"
            print(linha)
            f.write(linha + "\n")

    print(f"\nPronto! Transcricao salva em:\n{saida}")


if __name__ == "__main__":
    main()
