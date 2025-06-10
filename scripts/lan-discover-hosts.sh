#!/usr/bin/env bash
# Skrypt: lan-discover-hosts.sh
# Odkrywa aktywne hosty w podanej podsieci lub na interfejsie
set -euo pipefail

# Pozwala na podanie interfejsu lub CIDR jako argument
if [[ $# -gt 0 ]]; then
  if [[ $1 == *"/"* ]]; then
    cidr="$1"
    iface=""
  else
    iface="$1"
    cidr=$(ip -o -f inet addr show dev "$iface" | awk '{print $4}')
  fi
else
  default_route=$(ip route show default | head -n1)
  iface=$(awk '/default/ { for(i=1;i<=NF;i++) if($i=="dev") print $(i+1) }' <<<"$default_route")
  cidr=$(ip -o -f inet addr show dev "$iface" | awk '{print $4}')
fi

if [[ -z "${cidr:-}" ]]; then
  echo "Nie udało się wykryć podsieci. Interface: '$iface', CIDR: '$cidr'" >&2
  exit 1
fi

if ! command -v nmap &>/dev/null; then
  echo "Nmap nie jest zainstalowany!" >&2
  exit 2
fi

echo "Wykryta podsieć: $cidr${iface:+ (interfejs $iface)}" >&2

nmap -n -sn "$cidr" -oG - | awk '/Up$/{ print $2 }'
