#!/bin/bash +x
set -euo pipefail

mysql_cmd() {
  mariadb \
    --protocol=TCP \
    --host="$XI_NETWORK_SQL_HOST" \
    --port="$XI_NETWORK_SQL_PORT" \
    --user="$XI_NETWORK_SQL_LOGIN" \
    --password="$XI_NETWORK_SQL_PASSWORD" \
    --database="$XI_NETWORK_SQL_DATABASE" \
    "$@"
}

until mysql_cmd -e "SELECT 1" >/dev/null 2>&1; do
  echo "Waiting for MariaDB..."
  sleep 5
done

echo "Running dbtool update..."
python /server/tools/dbtool.py update full

echo "Getting public IP address..."
PUBLIC_IP="$(wget -qO- https://api.ipify.org)"
echo "Detected IP: $PUBLIC_IP"

echo "Applying map shard assignments..."
mysql_cmd <<SQL
-- For now, set all zones to the same IP and port. In the future, we may want to assign
-- different zones to different IPs/ports for better load distribution.
UPDATE zone_settings
SET zoneip = '$PUBLIC_IP';
SQL

touch /tmp/bootstrap-ready
echo "Bootstrap complete."
exec sleep infinity
