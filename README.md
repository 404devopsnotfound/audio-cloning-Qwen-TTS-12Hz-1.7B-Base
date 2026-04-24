# 🎙️ Qwen3-TTS Audio Cloning & Sync

Este projeto representa o estado da arte em clonagem de voz (**Zero-Shot**) e sincronização automática de dublagem, utilizando a poderosa arquitetura **Qwen3-TTS** da Alibaba Cloud.

O sistema foi desenvolvido para possibilitar a clonagem de áudio em ambiente **on-premises** (local), com foco na tradução e dublagem de vídeos do YouTube. O fluxo principal utiliza áudios em **português** como fonte, realizando a tradução e geração de voz clonada para **inglês** e **espanhol**.

---

## 🚀 Principais Funcionalidades

*   **Clonagem Zero-Shot:** Gere vozes idênticas a partir de apenas 3 a 10 segundos de áudio de referência.
*   **Suporte Multi-idioma (Cross-Lingual):** Suporta a geração de sotaques diferentes do áudio original (ex: referência em português gerando fala em inglês americano).
*   **Sincronização Perfeita (Lip-Sync Ready):** Alinhamento automático de áudio com arquivos de legenda (SRT/SBV) utilizando arquitetura de tokens discretos de 12Hz.
*   **Ajuste Inteligente de Velocidade:** O sistema calcula e aplica variações de velocidade dinâmicas para garantir que a fala caiba exatamente no tempo da legenda.
*   **Processamento em Chunks:** Capacidade de processar vídeos longos dividindo o trabalho em blocos, otimizando o uso de VRAM.
*   **Pós-processamento Profissional:** Remoção de silêncios excessivos e normalização de volume (Loudness Normalization) integrada via FFmpeg.

---

## 🧠 Arquitetura do Modelo

O projeto utiliza a família **Qwen3-TTS** (1.7 Bilhões de parâmetros):

1.  **Modelo Principal (`Qwen3-TTS-12Hz-1.7B-Base`):** Responsável pela clonagem da voz e geração das falas baseadas nas legendas.
2.  **Modelo de Design (`Qwen3-TTS-12Hz-1.7B-VoiceDesign`):** Utilizado para "desenhar" vozes profissionais específicas a partir de descrições em texto.
3.  **Tecnologia de Áudio:** Tokens discretos em 12Hz que permitem controle ultra-preciso de prosódia e tempo de fala.

---

## 🛠️ Processo de Execução

1.  **Input:** O sistema recebe um áudio de referência (.mp3/.wav) e um arquivo de legendas (.srt/.sbv).
2.  **Geração:** O modelo gera a fala clonada para cada segmento da legenda.
3.  **Sincronia:** O script `clone_sync.py` ajusta a velocidade de cada segmento via filtro `atempo` do FFmpeg para garantir o "timing" perfeito.
4.  **Finalização:** Os segmentos são mesclados com preenchimento de silêncios e normalização de volume profissional.

---

## 💻 Especificações de Hardware (Host)
Desenvolvido e otimizado no seguinte setup:

*   **Processador (CPU):** Intel® Core™ Ultra 9 185H (16 Núcleos / 22 Threads, até 5.1GHz)
*   **Memória RAM:** 32GB
*   **Placa de Vídeo (GPU):** NVIDIA® GeForce RTX™ 4070 Laptop GPU (8GB VRAM)
*   **Armazenamento:** NVMe KIOXIA 1TB (Sistema) + NVMe WD_BLACK SN850X 2TB (Dados)

---

## 📦 Requisitos e Dependências

*   **Framework:** PyTorch (com suporte a CUDA 12.x).
*   **Transformers:** Versão 4.57.6 (conforme definido no Dockerfile).
*   **Processamento de Mídia:** FFmpeg e soundfile.
*   **Ambiente:** Recomendado uso de Docker para isolamento de dependências.