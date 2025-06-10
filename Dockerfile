# Dockerfile for greenbone-cli custom automation
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalacja wymaganych narzędzi i zależności
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iproute2 nmap iputils-ping cron python3-pip python3-venv \
        python3-lxml python3-setuptools python3-wheel git curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Instalacja gvm-tools (gvm-cli, gvm-script)
RUN pip3 install --no-cache-dir gvm-tools

# 3. Utworzenie katalogu na skrypty
RUN mkdir -p /opt/scripts
WORKDIR /opt/scripts

# 4. Kopiowanie wszystkich skryptów do kontenera
COPY scripts/ /opt/scripts/
COPY export_and_send.py /opt/scripts/
COPY msmtprc /opt/scripts/
COPY .env /opt/scripts/

# 5. Ustawienia uprawnień
RUN chmod +x /opt/scripts/*.sh

# 6. Domyślna komenda (możesz zmienić na własną lub zostawić bash)
CMD ["/opt/scripts/lan-scan-alerts.sh"]
