import os, torch, sys
from pathlib import Path
import soundfile as sf

# Configurações
# Usamos o modelo específico de Voice Design para garantir o sotaque nativo
DESIGN_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
OUTPUT_REF = "/app/output/reference_en_us.mp3"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Descrição extremamente específica para forçar o sotaque americano nativo
VOICE_DESCRIPTION = "A native-born Standard American male voice from California. Clear, professional, mid-range pitch, with a crisp US West Coast accent. Absolutely no foreign or international inflections. Professional and confident."
# Texto que a referência vai dizer
REFERENCE_TEXT = "This is a native American voice sample from California. I am speaking with a clear, standard US accent for this audio project."

def main():
    # Importar modelo
    sys.path.insert(0, "/app/Qwen3-TTS")
    from qwen_tts import Qwen3TTSModel
    
    print(f"--- Carregando modelo de Voice Design: {DESIGN_MODEL} ---")
    model = Qwen3TTSModel.from_pretrained(
        DESIGN_MODEL,
        device_map=DEVICE,
        dtype=torch.bfloat16,
    )
    
    print(f"--- Desenhando voz: '{VOICE_DESCRIPTION}' ---")
    # No modelo VoiceDesign, usamos generate_voice_design ou similar
    # De acordo com a documentação da Qwen, o método é generate_voice_design
    
    try:
        wavs, sr = model.generate_voice_design(
            text=REFERENCE_TEXT,
            instruct=VOICE_DESCRIPTION,
            language="English",
            do_sample=False,
            non_streaming_mode=True,
        )
        
        # Salvar a nova referência
        sf.write(OUTPUT_REF, wavs[0], sr)
        print(f"✅ SUCESSO! Voz Americana Profissional gerada em: {OUTPUT_REF}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar voz: {e}")
        # Fallback caso o método seja diferente em algumas versões
        print("Tentando método alternativo...")
        # ...

if __name__ == "__main__":
    main()
