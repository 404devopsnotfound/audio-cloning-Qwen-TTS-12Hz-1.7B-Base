#!/usr/bin/env python3
import os, re, subprocess, sys
from pathlib import Path
import torch
import soundfile as sf

QWEN_MODEL = os.getenv("QWEN_MODEL", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
REF_AUDIO = os.getenv("REF_AUDIO", "/app/input/reference_pt.mp3")
SUB_FILE = os.getenv("SRT_FILE", "/app/input/subtitles_en.sbv")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
CHUNK_DURATION = int(os.getenv("CHUNK_DURATION", "60"))
TARGET_SR = int(os.getenv("TARGET_SAMPLE_RATE", "24000"))

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TEMP_DIR = Path("/app/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def to_seconds(ts):
    ts = ts.replace(",", ".")
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0

def parse_subtitles(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    entries = []
    blocks = re.split(r'\r?\n\s*\r?\n', content)
    ts_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})\s*[-–>,]+\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})')

    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if len(lines) < 2:
            continue

        timestamp_line = lines[0]
        text_lines = lines[1:]
        
        match = ts_pattern.search(timestamp_line)
        if not match:
            continue

        start = to_seconds(match.group(1))
        end = to_seconds(match.group(2))
        duration = max(0.3, end - start)
        text = " ".join(text_lines).strip()
        
        if text:
            entries.append({"start": start, "end": end, "duration": duration, "text": text})

    return sorted(entries, key=lambda x: x["start"])

def get_duration(path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())
    except:
        return 0.0

def split_into_chunks(segments, chunk_duration):
    chunks = []
    current_chunk = []
    chunk_start = 0
    
    for seg in segments:
        seg_start = seg["start"]
        
        if current_chunk:
            chunk_duration_used = seg_start - chunk_start
            if chunk_duration_used >= chunk_duration:
                chunks.append(current_chunk)
                current_chunk = []
                chunk_start = seg_start
        
        current_chunk.append(seg)
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def process_chunk(chunk_segments, model, ref_wav, ref_text, chunk_idx):
    temp_dir = TEMP_DIR / f"chunk_{chunk_idx}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    generated_files = []
    
    for i, seg in enumerate(chunk_segments):
        raw_path = str(temp_dir / f"seg_{i:04d}.wav")
        
        try:
            text_len = len(seg["text"])
            estimated_duration = seg["duration"]
            tokens_estimate = max(4096, int(estimated_duration * 80))
            
            wavs, sr = model.generate_voice_clone(
                text=seg["text"],
                ref_audio=ref_wav,
                ref_text=ref_text,
                language="English",
                max_new_tokens=tokens_estimate,
                x_vector_only_mode=True,
                do_sample=False,
                non_streaming_mode=True,
            )
            
            sf.write(raw_path, wavs[0], sr)
            
            sf.write(raw_path, wavs[0], sr)
            
            # 1. Remover silêncio inicial/final excessivo gerado pela IA
            trimmed_path = raw_path.replace(".wav", "_trimmed.wav")
            subprocess.run([
                "ffmpeg", "-y", "-i", raw_path,
                "-af", "silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=1:stop_threshold=-50dB:stop_duration=0.1",
                trimmed_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.replace(trimmed_path, raw_path)

            dur = get_duration(raw_path)
            target_dur = seg["duration"]
            
            # 2. Ajuste de velocidade agressivo para sincronia total
            if dur > 0.1 and target_dur > 0.1:
                speed = dur / target_dur
                
                # Se a diferença for significativa, aplicamos o ajuste
                if abs(speed - 1.0) > 0.02: 
                    print(f"      ⚡ Sincronizando: {dur:.2f}s -> {target_dur:.2f}s ({speed:.2f}x)")
                    
                    # ffmpeg atempo suporta entre 0.5 e 2.0. Para valores fora disso, encadeamos filtros.
                    filters = []
                    temp_speed = speed
                    while temp_speed > 2.0:
                        filters.append("atempo=2.0")
                        temp_speed /= 2.0
                    while temp_speed < 0.5:
                        filters.append("atempo=0.5")
                        temp_speed /= 0.5
                    filters.append(f"atempo={temp_speed:.3f}")
                    
                    fast_path = raw_path.replace(".wav", "_sync.wav")
                    subprocess.run([
                        "ffmpeg", "-y", "-i", raw_path,
                        "-af", ",".join(filters),
                        "-ar", str(TARGET_SR), fast_path
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # 3. Garantir que o áudio final não ultrapasse o limite da legenda (corte seco se necessário)
                    final_path = raw_path.replace(".wav", "_final.wav")
                    subprocess.run([
                        "ffmpeg", "-y", "-i", fast_path,
                        "-t", str(target_dur),
                        "-ar", str(TARGET_SR), final_path
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    os.replace(final_path, raw_path)
                    if os.path.exists(fast_path): os.remove(fast_path)
                    dur = get_duration(raw_path)

            if dur < 0.1:
                print(f"      ⚠️ Apenas {dur:.2f}s - muito curto!")
            else:
                print(f"      → {dur:.2f}s (Alvo: {target_dur:.2f}s)")
            
            generated_files.append({
                "start": seg["start"],
                "duration": dur,
                "target_duration": target_dur,
                "path": raw_path
            })
            
        except Exception as e:
            print(f"      ❌ Erro: {e}")
            continue
        
        if DEVICE == "cuda":
            torch.cuda.empty_cache()
    
    if not generated_files:
        return None
    
    concat_list = str(temp_dir / "concat_list.txt")
    
    # 4. Reconstrução da timeline para evitar drift acumulado
    chunk_start_offset = generated_files[0]["start"]
    
    with open(concat_list, "w") as f:
        current_timeline = chunk_start_offset
        for seg in generated_files:
            # Se houver um buraco entre o fim do anterior e o início deste, adiciona silêncio
            gap = seg["start"] - current_timeline
            
            if gap > 0.05:
                silence_path = str(temp_dir / f"sil_{current_timeline:.3f}.wav")
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=duration={gap:.3f}:sample_rate={TARGET_SR}",
                    "-ac", "2", "-c:a", "pcm_s16le", silence_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                f.write(f"file '{os.path.abspath(silence_path)}'\n")
                current_timeline += gap
            
            f.write(f"file '{os.path.abspath(seg['path'])}'\n")
            current_timeline += seg["duration"]
    
    output_file = f"{OUTPUT_DIR}/cloned_en_chunk{chunk_idx:03d}.mp3"
    
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "128k",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,volume=0dB", output_file
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        subprocess.run(["chown", "1000:1000", output_file], check=False)
    except:
        pass
    
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return output_file

def main():
    print(f"🔍 Lendo legendas: {SUB_FILE} | Device={DEVICE}")
    all_segments = parse_subtitles(SUB_FILE)
    
    if not all_segments:
        print("❌ Nenhum segmento encontrado."); sys.exit(1)
    print(f"✅ {len(all_segments)} segmentos carregados.")

    ref_wav = str(TEMP_DIR / "ref.wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", REF_AUDIO, "-t", "30", "-ar", str(TARGET_SR), "-ac", "2",
        "-c:a", "pcm_s16le", ref_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"📼 Reference: {ref_wav}")

    sys.path.insert(0, "/app/Qwen3-TTS")
    from qwen_tts import Qwen3TTSModel
    
    print(f"🧠 Carregando {QWEN_MODEL} ({DEVICE})...")
    model = Qwen3TTSModel.from_pretrained(
        QWEN_MODEL,
        device_map=DEVICE,
        dtype=torch.bfloat16,
    )
    print("✅ Modelo carregado!")

    ref_text = os.getenv("REF_TEXT", "This is a tutorial video about installing VSCode on Ubuntu Linux.")

    chunks = split_into_chunks(all_segments, CHUNK_DURATION)
    print(f"📦 {len(chunks)} chunks de ~{CHUNK_DURATION}s cada")
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    output_files = []
    
    for chunk_idx, chunk_segments in enumerate(chunks):
        print(f"\n🎙️ Chunk {chunk_idx + 1}/{len(chunks)} ({len(chunk_segments)} segmentos)...")
        
        for i, seg in enumerate(chunk_segments):
            print(f"  [{i+1}/{len(chunk_segments)}] {seg['text'][:40]}...")
        
        output_file = process_chunk(chunk_segments, model, ref_wav, ref_text, chunk_idx)
        
        if output_file:
            output_files.append(output_file)
            print(f"  ✅ Salvo: {output_file}")
    
    print(f"\n✅ Pronto! {len(output_files)} arquivos gerados:")
    for f in output_files:
        print(f"   - {f}")

    if len(output_files) > 1:
        full_output = f"{OUTPUT_DIR}/cloned_en_full_audio.mp3"
        print(f"\n🔄 Mesclando todos os {len(output_files)} chunks em um único arquivo completo...")
        
        concat_all = "/app/temp/concat_all_chunks.txt"
        os.makedirs("/app/temp", exist_ok=True)
        
        with open(concat_all, "w") as f:
            for out_f in output_files:
                # Usar caminho absoluto para o ffmpeg concat
                f.write(f"file '{os.path.abspath(out_f)}'\n")
        
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_all,
            "-c", "copy", full_output
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        try:
            subprocess.run(["chown", "1000:1000", full_output], check=False)
        except:
            pass
            
        print(f"✅ Áudio completo gerado com sucesso: {full_output}")

    import shutil
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()