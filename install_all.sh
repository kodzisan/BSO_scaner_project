#!/usr/bin/env bash
# Skrypt: install_all.sh
# Główna instalacja projektu BSO Greenbone Scanner
set -euo pipefail

# Struktura projektu:
# - install_all.sh (główny skrypt instalacyjny)
# - README.md (instrukcja)
# - docker-compose.yml (definicja kontenerów)
# - scripts/ (skrypty automatyzujące)
# - .env, msmtprc (konfiguracja)
# - crontab.example (wzór crona)

REPO="gitlab-stud.elka.pw.edu.pl/kgromko/bso_projekt"
REPO_DIR="bso_projekt"
RELEASE_BRANCH="main"

# 1. Instalacja Dockera i Docker Compose jeśli nie są obecne
if ! command -v docker &>/dev/null; then
  echo "Instaluję Docker..."
  curl -fsSL https://get.docker.com | sh
fi
if ! command -v docker compose &>/dev/null; then
  echo "Instaluję Docker Compose..."
  sudo apt-get update && sudo apt-get install -y docker-compose-plugin
fi

# 2. Pobranie repozytorium jeśli nie istnieje
if [ ! -d "$REPO_DIR" ]; then
  echo "Klonuję repozytorium..."
  git clone --branch "$RELEASE_BRANCH" "https://$REPO.git" "$REPO_DIR"
fi
cd "$REPO_DIR"

# 3. Przygotowanie plików konfiguracyjnych (jeśli nie istnieją)
[ -f .env ] || cp .env.example .env 2>/dev/null || touch .env
[ -f msmtprc ] || cp msmtprc.example msmtprc 2>/dev/null || touch msmtprc

# 4. Uruchomienie kontenerów
sudo docker compose -f docker-compose.yml pull
sudo docker compose up -d
sudo docker compose ps

# 5. (Opcjonalnie) Uruchomienie automatycznego skanu w kontenerze
sleep 10
echo "\nUruchamiam automatyczny skan w kontenerze...\n"
sudo docker compose exec greenbone-cli /opt/scripts/lan-scan-alerts.sh || true

# 6. Automatyczna wysyłka PDF po skanie
sleep 5
echo "\nWysyłam raport PDF na e-mail...\n"
sudo docker compose exec greenbone-cli python3 /opt/scripts/send_report_smtp.py || true

echo "\nProjekt został zainstalowany i uruchomiony!\n"
echo "Zaloguj się do Greenbone przez przeglądarkę lub poczekaj na automatyczny raport na e-mail."
