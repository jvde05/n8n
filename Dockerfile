# n8n + render araçları (ffmpeg, edge-tts) tek imajda
FROM n8nio/n8n:latest

USER root

# Render ve TTS için gerekli paketler
RUN apk add --no-cache \
      ffmpeg \
      python3 \
      py3-pip \
      fontconfig \
      ttf-dejavu \
      curl \
    && pip3 install --no-cache-dir --break-system-packages edge-tts requests

# Render scriptleri
COPY scripts /scripts
RUN chmod -R +x /scripts || true

USER node
