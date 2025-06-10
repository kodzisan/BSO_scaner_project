#!/bin/bash
set -e

# Parametry
REPORT_ID="baaf3b7e-a49e-42e4-87c3-47e91e0d4b69"
USERNAME="admin"
PASSWORD="lapga6king"
OUTPUT_FILE="./report-${REPORT_ID}.pdf"
CONTAINER="greenbone-cli"
SOCKET="/run/gvmd/gvmd.sock"

# Tworzymy lokalny plik XML
cat <<EOF > gmp_request.xml
<authenticate>
  <credentials>
    <username>$USERNAME</username>
    <password>$PASSWORD</password>
  </credentials>
</authenticate>
<get_report report_id="$REPORT_ID" details="1">
  <report_format_id>c402cc3e-b531-11e1-9163-406186ea4fc5</report_format_id>
</get_report>
EOF

# Kopiujemy XML do kontenera
echo "[+] Kopiuję XML do kontenera..."
sudo docker cp gmp_request.xml "$CONTAINER:/tmp/gmp_request.xml"

# Uruchamiamy gvm-cli z przekierowanym plikiem wejściowym
echo "[+] Eksportuję raport jako PDF..."
sudo docker exec -i "$CONTAINER" sh -c "gvm-cli socket --socketpath $SOCKET < /tmp/gmp_request.xml" > report.b64

# Dekodujemy, jeśli wygląda na PDF
if grep -q '^JVBER' report.b64; then
  echo "[+] Dekoduję PDF..."
  base64 -d report.b64 > "$OUTPUT_FILE"
  echo "[✓] Raport zapisany jako $OUTPUT_FILE"
else
  echo "[✗] Coś poszło nie tak. To nie jest prawidłowy PDF:"
  head -n 20 report.b64
fi

# Sprzątanie
rm -f gmp_request.xml
