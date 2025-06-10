#!/usr/bin/env bash
# Skrypt: lan-scan-alerts.sh
# Skanuje sieć LAN i uruchamia alerty
set -euo pipefail

# Parametry – pobierz z ENV lub domyślne
GMP_USER="${GVM_USER:-admin}"
GMP_PASS="${GVM_PASS:-lapga6king}"
SCRIPT_PATH="/opt/scripts/start-alert-scan.gmp.py"
SCAN_CONFIG=5
RECIPIENT="${RECIPIENT:-bso-projekt@outlook.com}"
SENDER="${SENDER:-bso-projekt@outlook.com}"
PORT_LIST_ID="33d0cd82-57c6-11e1-8ed1-406186ea4fc5"
TARGET_NAME="Target"

# Pozwól na przekazanie interfejsu/CIDR przez ENV lub argumenty
NETWORKS=( ${NETWORKS:-} )
if [ ${#NETWORKS[@]} -eq 0 ] && [ $# -gt 0 ]; then
  NETWORKS=( "$@" )
fi
if [ ${#NETWORKS[@]} -eq 0 ]; then
  # domyślnie skanuj całą podsieć lokalną
  default_route=$(ip route show default | head -n1)
  iface=$(awk '/default/ { for(i=1;i<=NF;i++) if($i=="dev") print $(i+1) }' <<<"$default_route")
  cidr=$(ip -o -f inet addr show dev "$iface" | awk '{print $4}')
  NETWORKS=( "$cidr" )
fi

# Odkryj żywe hosty w podanych sieciach
HOSTS=()
for NET in "${NETWORKS[@]}"; do
  mapfile -t FOUND < <( /opt/scripts/lan-discover-hosts.sh "$NET" )
  HOSTS+=( "${FOUND[@]}" )
done

if [ ${#HOSTS[@]} -eq 0 ]; then
  echo "Brak żywych hostów w podanych sieciach – nic do zrobienia." >&2
  exit 1
fi

HOSTS=( localhost "${HOSTS[@]}" )
HOSTS_ARGS=( ++hosts "${HOSTS[@]}" )

exec /usr/local/bin/gvm-script --gmp-username "$GMP_USER" --gmp-password "$GMP_PASS" socket "$SCRIPT_PATH" "${HOSTS_ARGS[@]}" ++port-list-id "$PORT_LIST_ID" +C "$SCAN_CONFIG" ++target-name="$TARGET_NAME" ++recipient "$RECIPIENT" ++sender "$SENDER"

