
O projeto utiliza a tecnologia mais recente da família Qwen3-TTS, desenvolvida pelo time da Alibaba Cloud (Qwen). Aqui estão os detalhes técnicos:

    Modelo Principal (Dublagem/Clonagem) Nome: Qwen3-TTS-12Hz-1.7B-Base Versão: 1.7 bilhões de parâmetros (Base). Taxa de Amostragem Interna: 12Hz (Tokens de áudio). Função: Este é o modelo que faz a clonagem da voz e a geração das falas baseadas nas suas legendas.

    Modelo de Design (Criação da Voz Americana) Nome: Qwen3-TTS-12Hz-1.7B-VoiceDesign Função: Usamos este modelo específico para "desenhar" a voz profissional americana nativa a partir de descrições em texto.

    Bibliotecas e Dependências Framework: PyTorch (com suporte a CUDA/GPU). Transformers: Versão 4.57.6 (conforme definido no seu Dockerfile). Processamento de Áudio: ffmpeg para sincronização de tempo e soundfile para escrita de arquivos.

    Características do Modelo Zero-Shot Voice Cloning: Consegue clonar uma voz com apenas 3 a 10 segundos de áudio de referência. 

Cross-Lingual: Suporta a geração de sotaques diferentes do áudio original (como fizemos ao transformar sua referência em inglês americano).
Sincronização: O modelo trabalha com uma arquitetura de tokens de áudio discretos, o que permite um controle muito preciso do tempo de fala. 




Este projeto foi criado para possibilitar a clonagem de áudio em on-premises utilizando amostragem de voz, com o objetivo de traduzir os vídeos do youtube.
Terá como áudio fonte o português, e a tradução será realizada para o inglês e espanhol.


# 🎙️ Qwen3-TTS Audio Cloning & Sync

Este projeto representa o estado da arte em clonagem de voz (Zero-Shot) e sincronização automática de dublagem, utilizando a poderosa arquitetura **Qwen3-TTS** da Alibaba Cloud.

---

## 🚀 Principais Funcionalidades

*   **Clonagem Zero-Shot:** Gere vozes idênticas a partir de apenas 3 a 10 segundos de áudio de referência.
*   **Sincronização Perfeita (Lip-Sync Ready):** Alinhamento automático de áudio com arquivos de legenda (SRT/SBV).
*   **Ajuste Inteligente de Velocidade:** O sistema calcula e aplica variações de velocidade dinâmicas para garantir que a fala caiba exatamente no tempo da legenda sem perder a naturalidade.
*   **Processamento em Chunks:** Capacidade de processar vídeos longos dividindo o trabalho em blocos, otimizando o uso de VRAM e estabilidade.
*   **Pós-processamento Profissional:** Remoção automática de silêncios desnecessários e normalização de áudio (Loudness Normalization) integrada.

---

## 🧠 Arquitetura do Modelo

O projeto utiliza a tecnologia mais recente da família **Qwen3-TTS**, desenvolvida pelo time da Alibaba Cloud (Qwen):

1.  **Modelo Principal:** `Qwen3-TTS-12Hz-1.7B-Base` (1.7 Bilhões de parâmetros).
2.  **Modelo de Design:** `Qwen3-TTS-12Hz-1.7B-VoiceDesign` (Usado para criar perfis de voz específicos).
3.  **Tecnologia:** Arquitetura de tokens de áudio discretos (12Hz), permitindo controle preciso de prosódia e tempo.

---

## 🛠️ Processo de Execução

1.  **Input:** O sistema recebe um áudio de referência (.mp3/.wav) e um arquivo de legendas (.srt/.sbv).
2.  **Geração:** O modelo gera a fala clonada para cada segmento da legenda.
3.  **Sincronia:** O script `clone_sync.py` analisa a duração gerada vs. o tempo disponível e ajusta a velocidade via FFmpeg (filtro `atempo`).
4.  **Finalização:** Todos os segmentos são mesclados com preenchimento de silêncios precisos e normalização de volume profissional.

---

## 💻 Especificações de Hardware (Host)
Este projeto foi desenvolvido e otimizado no seguinte setup:

*   **Processador (CPU):** Intel® Core™ Ultra 9 185H (16 Núcleos / 22 Threads, até 5.1GHz)
*   **Memória RAM:** 32GB
*   **Placa de Vídeo (GPU):** NVIDIA® GeForce RTX™ 4070 Laptop GPU (8GB VRAM)
*   **Armazenamento:** 
    *   NVMe KIOXIA 1TB (Sistema)
    *   NVMe WD_BLACK SN850X 2TB (Dados)

---

## 📦 Requisitos e Dependências

*   **Framework:** PyTorch (com suporte a CUDA 12.x).
*   **Transformers:** v4.57.6+.
*   **Processamento de Mídia:** FFmpeg (obrigatório para sincronização).
*   **Ambiente:** Recomendado uso de Docker para garantir isolamento de dependências.