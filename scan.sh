#!/usr/bin/env bash
# Skrypt: scan.sh
# Uruchamia skanowanie sieci LAN
set -euo pipefail

echo "Uruchamiam skan..."
docker exec greenbone-cli /opt/scripts/lan-scan-alerts.sh

