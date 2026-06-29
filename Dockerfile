# n8n + ACOS render cekirdegi (ffmpeg, edge-tts, python) tek imajda
FROM n8nio/n8n:latest

USER root

# Render ve TTS icin gerekli sistem paketleri
RUN apk add --no-cache \
      ffmpeg \
      python3 \
      py3-pip \
      fontconfig \
      ttf-dejavu \
      curl

# Python bagimliliklari
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# ACOS cekirdegi (moduler is mantigi) ve n8n koprusu
COPY acos /app/acos
COPY scripts /scripts
RUN chmod -R +x /scripts || true

# ACOS paketinin her yerden import edilebilmesi icin
ENV PYTHONPATH=/app

USER node
