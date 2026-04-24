import os, torch, sys
from pathlib import Path
import soundfile as sf
import subprocess

# Configurações
QWEN_MODEL = os.getenv("QWEN_MODEL", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
REF_AUDIO = "/app/input/reference_pt.mp3"
OUTPUT_REF = "/app/output/reference_en_us.mp3"
TARGET_SR = int(os.getenv("TARGET_SAMPLE_RATE", "24000"))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Texto para a nova referência (neutro e com boa cobertura de fonemas)
# Incluímos palavras que testam diferentes sons do inglês americano
AMERICAN_TEXT = "Hello! This is a clear voice reference. I am speaking English with a natural American accent to provide the best quality for my audio cloning project."

def main():
    # Garantir que o diretório de destino existe
    Path("/app/input").mkdir(parents=True, exist_ok=True)
    
    # Preparar áudio de referência original (converter para wav temporário se necessário)
    temp_ref_wav = "/app/temp/temp_ref_convert.wav"
    Path("/app/temp").mkdir(parents=True, exist_ok=True)
    
    print(f"--- Convertendo referência original para processamento ---")
    subprocess.run([
        "ffmpeg", "-y", "-i", REF_AUDIO, "-ar", str(TARGET_SR), "-ac", "2",
        "-c:a", "pcm_s16le", temp_ref_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Importar modelo
    sys.path.insert(0, "/app/Qwen3-TTS")
    from qwen_tts import Qwen3TTSModel
    
    print(f"--- Carregando modelo {QWEN_MODEL} ({DEVICE}) ---")
    model = Qwen3TTSModel.from_pretrained(
        QWEN_MODEL,
        device_map=DEVICE,
        dtype=torch.bfloat16,
    )
    
    print(f"--- Gerando nova referência com sotaque americano ---")
    # Gerar a nova referência
    # Usamos o áudio PT para pegar a identidade da voz
    # O parâmetro language="English" e o texto em inglês ajudam o modelo a aplicar o sotaque correto
    wavs, sr = model.generate_voice_clone(
        text=AMERICAN_TEXT,
        ref_audio=temp_ref_wav,
        language="English",
        x_vector_only_mode=True, # Usar apenas o vetor de voz pois não temos a transcrição PT exata
        do_sample=False,
        non_streaming_mode=True,
    )
    
    # Salvar a nova referência
    sf.write(OUTPUT_REF, wavs[0], sr)
    print(f"✅ SUCESSO! Nova referência americana gerada em: {OUTPUT_REF}")
    
    # Limpeza
    if os.path.exists(temp_ref_wav):
        os.remove(temp_ref_wav)

if __name__ == "__main__":
    main()
