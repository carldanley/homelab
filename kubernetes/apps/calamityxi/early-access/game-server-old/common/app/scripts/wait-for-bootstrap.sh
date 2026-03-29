#!/bin/bash
set -euo pipefail

mysql_cmd() {
  mariadb \
    --protocol=TCP \
    --host="$XI_NETWORK_SQL_HOST" \
    --port="$XI_NETWORK_SQL_PORT" \
    --user="$XI_NETWORK_SQL_LOGIN" \
    --password="$XI_NETWORK_SQL_PASSWORD" \
    --database="$XI_NETWORK_SQL_DATABASE" \
    --skip-column-names \
    --batch \
    -e "$1"
}

echo "Getting public IP address..."
PUBLIC_IP="$(wget -qO- https://api.ipify.org)"
echo "Detected IP: $PUBLIC_IP"

# while true; do
#   town="$(mysql_query "SELECT CONCAT(zoneip, ':', zoneport) FROM zone_settings WHERE zoneid = 243" 2>/dev/null || true)"
#   field="$(mysql_query "SELECT CONCAT(zoneip, ':', zoneport) FROM zone_settings WHERE zoneid = 100" 2>/dev/null || true)"
#   dungeon="$(mysql_query "SELECT CONCAT(zoneip, ':', zoneport) FROM zone_settings WHERE zoneid = 9" 2>/dev/null || true)"
#   instance="$(mysql_query "SELECT CONCAT(zoneip, ':', zoneport) FROM zone_settings WHERE zoneid = 188" 2>/dev/null || true)"

#   if [ "$town" = "$PUBLIC_IP:54230" ] &&
#     [ "$field" = "$PUBLIC_IP:54230" ] &&
#     [ "$dungeon" = "$PUBLIC_IP:54230" ] &&
#     [ "$instance" = "$PUBLIC_IP:54230" ]; then
#     echo "Bootstrap zone assignments confirmed."
#     exit 0
#   fi

#   echo "Waiting for bootstrap zone assignments..."
#   sleep 5
# done
