# 🎙️ Qwen3-TTS Audio Cloning & Sync

This project represents the state-of-the-art in **Zero-Shot** voice cloning and automatic dubbing synchronization, powered by Alibaba Cloud's **Qwen3-TTS** architecture.

The system was developed to enable **on-premises** (local) audio cloning, specifically focused on translating and dubbing YouTube videos. The main workflow uses **Portuguese** source audio, translating and generating cloned voices for **English** and **Spanish**.

---

## 🚀 Key Features

*   **Zero-Shot Cloning:** Generate identical voices using only 3 to 10 seconds of reference audio.
*   **Cross-Lingual Support:** Supports generating different accents from the original audio (e.g., a Portuguese reference generating American English speech).
*   **Perfect Synchronization (Lip-Sync Ready):** Automatic audio alignment with subtitle files (SRT/SBV) using 12Hz discrete token architecture.
*   **Smart Speed Adjustment:** The system calculates and applies dynamic speed variations to ensure the speech fits exactly within the subtitle timeframe.
*   **Chunk Processing:** Ability to process long videos by splitting the workload into blocks, optimizing VRAM usage.
*   **Professional Post-processing:** Automatic removal of excess silence and integrated loudness normalization via FFmpeg.

---

## 🧠 Model Architecture

The project utilizes the **Qwen3-TTS** family (1.7 Billion parameters):

1.  **Main Model (`Qwen3-TTS-12Hz-1.7B-Base`):** Responsible for voice cloning and generating speech based on subtitles.
2.  **Design Model (`Qwen3-TTS-12Hz-1.7B-VoiceDesign`):** Used to "design" specific professional voices from text descriptions.
3.  **Audio Technology:** 12Hz discrete tokens that allow ultra-precise control over prosody and speech timing.

---

## 🛠️ Execution Workflow

1.  **Input:** The system receives a reference audio (.mp3/.wav) and a subtitle file (.srt/.sbv).
2.  **Generation:** The model generates cloned speech for each subtitle segment.
3.  **Sync:** The `clone_sync.py` script adjusts the speed of each segment using FFmpeg's `atempo` filter to ensure perfect timing.
4.  **Finalization:** Segments are merged with precise silence padding and professional volume normalization.

---

## 💻 Hardware Specifications (Host)
Developed and optimized on the following setup:

*   **Processor (CPU):** Intel® Core™ Ultra 9 185H (16 Cores / 22 Threads, up to 5.1GHz)
*   **RAM:** 32GB
*   **Graphics Card (GPU):** NVIDIA® GeForce RTX™ 4070 Laptop GPU (8GB VRAM)
*   **Storage:** NVMe KIOXIA 1TB (System) + NVMe WD_BLACK SN850X 2TB (Data)

---

## 📦 Requirements & Dependencies

*   **Framework:** PyTorch (with CUDA 12.x support).
*   **Transformers:** Version 4.57.6 (as defined in the Dockerfile).
*   **Media Processing:** FFmpeg and soundfile.
*   **Environment:** Docker is recommended to ensure dependency isolation.