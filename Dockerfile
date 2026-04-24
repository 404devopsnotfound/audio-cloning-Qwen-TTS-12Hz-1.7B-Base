FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    ffmpeg \
    libsndfile1 \
    sox \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

RUN pip install --no-cache-dir torch torchaudio

RUN git clone --depth 1 https://github.com/QwenLM/Qwen3-TTS.git /app/Qwen3-TTS

RUN pip install --no-cache-dir soundfile numpy tqdm librosa "transformers==4.57.6" accelerate sentencepiece protobuf

RUN pip install --no-cache-dir --default-timeout=200 sox

RUN pip install --no-cache-dir --default-timeout=300 onnxruntime einops

COPY . .