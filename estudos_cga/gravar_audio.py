"""
Grava SOMENTE o audio do sistema (o som que sai dos alto-falantes/fones)
em 16kHz mono - ideal para transcricao, arquivo bem pequeno (~2MB/min).

Uso:
    py gravar_audio.py "nome_da_aula"

Para PARAR: crie um arquivo chamado PARAR na mesma pasta, ou aperte Ctrl+C.
(O assistente cuida do start/stop automaticamente.)
"""
import sys
import os
import wave
import numpy as np
import soundcard as sc

SR = 16000          # 16kHz - formato do Whisper
CHUNK = 4000        # ~0.25s por leitura
PASTA = os.path.dirname(os.path.abspath(__file__))
STOP_FILE = os.path.join(PASTA, "PARAR")


def main():
    nome = sys.argv[1] if len(sys.argv) > 1 else "aula"
    pasta_aulas = os.path.join(PASTA, "aulas_audio")
    os.makedirs(pasta_aulas, exist_ok=True)
    saida = os.path.join(pasta_aulas, nome + ".wav")

    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)

    spk = sc.default_speaker()
    mic = sc.get_microphone(spk.name, include_loopback=True)
    print(f"Gravando audio de: {spk.name}")
    print(f"Salvando em: {saida}")
    print("Para parar: crie o arquivo PARAR ou Ctrl+C")

    wf = wave.open(saida, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)   # int16
    wf.setframerate(SR)

    import time
    total = 0
    parar = False
    try:
        while not parar:
            try:
                # Reabre o dispositivo (default speaker pode mudar de perfil no Bluetooth)
                spk = sc.default_speaker()
                mic = sc.get_microphone(spk.name, include_loopback=True)
                with mic.recorder(samplerate=SR, channels=1) as rec:
                    while True:
                        data = rec.record(numframes=CHUNK)
                        mono = data[:, 0] if data.ndim > 1 else data
                        pcm = np.clip(mono, -1, 1)
                        wf.writeframes((pcm * 32767).astype(np.int16).tobytes())
                        total += len(pcm)
                        if os.path.exists(STOP_FILE):
                            os.remove(STOP_FILE)
                            parar = True
                            break
            except KeyboardInterrupt:
                parar = True
            except RuntimeError as e:
                # dispositivo caiu (troca de perfil BT etc.) -> reabre e continua
                if os.path.exists(STOP_FILE):
                    os.remove(STOP_FILE)
                    parar = True
                else:
                    print(f"[reconectando audio... {e}]", flush=True)
                    time.sleep(1)
    finally:
        wf.close()

    segs = total / SR
    print(f"\nGravacao encerrada: {int(segs//60)}min{int(segs%60):02d}s")
    print(f"Arquivo: {saida}")


if __name__ == "__main__":
    main()
