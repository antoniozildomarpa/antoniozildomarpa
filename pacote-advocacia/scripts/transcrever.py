#!/usr/bin/env python3
"""Transcreve áudios (WhatsApp, gravação de atendimento) para texto, no próprio computador.

Usa o faster-whisper (versão leve do Whisper). O áudio não sai do computador. Na primeira vez,
o modelo é baixado da internet (uma vez só) e fica guardado.

Uso:
    python transcrever.py <audio|pasta> [--modelo small] [--com-tempo]
    python transcrever.py --baixar-modelo [--modelo small]

Saída: um .txt ao lado de cada áudio, com o mesmo nome. Áudios já transcritos são pulados.
Modelos: "small" (padrão, bom equilíbrio), "medium" (mais preciso, mais lento), "base" (rápido).
"""
import argparse
import sys
from pathlib import Path

EXTENSOES = {".opus", ".ogg", ".mp3", ".m4a", ".wav", ".aac", ".mp4", ".amr", ".webm"}


def carregar(modelo):
    from faster_whisper import WhisperModel
    return WhisperModel(modelo, device="cpu", compute_type="int8")


def transcrever(m, audio: Path, com_tempo: bool) -> Path:
    destino = audio.with_suffix(audio.suffix + ".txt")
    if destino.exists():
        print(f"já transcrito, pulado: {audio.name}")
        return destino
    segmentos, info = m.transcribe(str(audio), language="pt", vad_filter=True)
    linhas = []
    for s in segmentos:
        texto = s.text.strip()
        if com_tempo:
            ini = f"{int(s.start // 60):02d}:{int(s.start % 60):02d}"
            linhas.append(f"[{ini}] {texto}")
        else:
            linhas.append(texto)
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"OK {audio.name} -> {destino.name} ({info.duration:.0f} s de áudio)")
    return destino


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcrição local de áudio (faster-whisper).")
    ap.add_argument("entrada", nargs="?", help="arquivo de áudio ou pasta")
    ap.add_argument("--modelo", default="small")
    ap.add_argument("--com-tempo", action="store_true", help="marca o minuto de cada trecho")
    ap.add_argument("--baixar-modelo", action="store_true", help="só baixa o modelo e sai")
    args = ap.parse_args()

    m = carregar(args.modelo)
    if args.baixar_modelo:
        print(f"Modelo '{args.modelo}' pronto.")
        return 0
    if not args.entrada:
        ap.error("informe o áudio ou a pasta")
    entrada = Path(args.entrada)
    audios = sorted(x for x in entrada.rglob("*") if x.suffix.lower() in EXTENSOES) if entrada.is_dir() else [entrada]
    if not audios:
        print("Nenhum áudio encontrado.", file=sys.stderr)
        return 1
    erros = 0
    for a in audios:
        try:
            transcrever(m, a, args.com_tempo)
        except Exception as e:
            print(f"ERRO {a.name}: {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
            erros += 1
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
