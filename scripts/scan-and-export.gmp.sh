#!/usr/bin/env bash
# Skrypt: scan-and-export.gmp.sh
# Uruchamia skanowanie, eksportuje raport PDF i wysyła go na e-mail
set -euo pipefail

# Parametry
GMP_USER="${GVM_USER:-admin}"
GMP_PASS="${GVM_PASS:-lapga6king}"
TARGET_NAME="${TARGET_NAME:-Target}"
SCRIPT_LIST="/opt/scripts/list-tasks-with-reports.gmp.py"
SCRIPT_EXPORT="/opt/scripts/export-pdf-report.gmp.py"
PDF_OUT="/tmp/raport.pdf"
CONTAINER="greenbone-cli"

# 1. Uruchom skanowanie
# (możesz pominąć jeśli skan już trwa lub chcesz tylko eksportować)
docker exec "$CONTAINER" /opt/scripts/scan-lan-alerts.sh

# 2. Pobierz report_id ostatniego raportu dla zadania o nazwie $TARGET_NAME
REPORT_ID=$(docker exec "$CONTAINER" gvm-script --gmp-username "$GMP_USER" --gmp-password "$GMP_PASS" socket "$SCRIPT_LIST" | grep " $TARGET_NAME " | tail -n1 | awk '{print $NF}')
if [ -z "$REPORT_ID" ]; then
  echo "Nie znaleziono report_id dla zadania $TARGET_NAME" >&2
  exit 2
fi

echo "[✓] Ostatni report_id: $REPORT_ID"

# 3. Eksportuj PDF
# (plik zostanie zapisany w katalogu / w kontenerze)
docker exec "$CONTAINER" gvm-script --gmp-username "$GMP_USER" --gmp-password "$GMP_PASS" socket "$SCRIPT_EXPORT" "$REPORT_ID" raport

docker exec "$CONTAINER" mv ./raport.pdf /tmp/raport.pdf 2>/dev/null || true

docker cp "$CONTAINER":/tmp/raport.pdf ./raport.pdf

echo "[✓] PDF wyeksportowany i skopiowany na hosta jako ./raport.pdf"

# 4. Wyślij PDF na maila
python3 "$(dirname "$0")/send_report_smtp.py"
