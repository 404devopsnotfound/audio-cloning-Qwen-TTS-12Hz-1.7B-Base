Olá! O projeto utiliza a tecnologia mais recente da família Qwen3-TTS, desenvolvida pelo time da Alibaba Cloud (Qwen). Aqui estão os detalhes técnicos:

1. Modelo Principal (Dublagem/Clonagem)
Nome: Qwen3-TTS-12Hz-1.7B-Base
Versão: 1.7 bilhões de parâmetros (Base).
Taxa de Amostragem Interna: 12Hz (Tokens de áudio).
Função: Este é o modelo que faz a clonagem da voz e a geração das falas baseadas nas suas legendas.
2. Modelo de Design (Criação da Voz Americana)
Nome: Qwen3-TTS-12Hz-1.7B-VoiceDesign
Função: Usamos este modelo específico para "desenhar" a voz profissional americana nativa a partir de descrições em texto.
3. Bibliotecas e Dependências
Framework: PyTorch (com suporte a CUDA/GPU).
Transformers: Versão 4.57.6 (conforme definido no seu Dockerfile).
Processamento de Áudio: ffmpeg para sincronização de tempo e soundfile para escrita de arquivos.
4. Características do Modelo
Zero-Shot Voice Cloning: Consegue clonar uma voz com apenas 3 a 10 segundos de áudio de referência.
Cross-Lingual: Suporta a geração de sotaques diferentes do áudio original (como fizemos ao transformar sua referência em inglês americano).
Sincronização: O modelo trabalha com uma arquitetura de tokens de áudio discretos, o que permite um controle muito preciso do tempo de fala.
Se precisar de mais detalhes técnicos ou de como atualizar para outras versões, é só me perguntar!