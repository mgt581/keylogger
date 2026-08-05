#!/usr/bin/env bash
# Helper: register a device via the admin-only /register_device endpoint.
# Usage: ./register_helper.sh <NGROK_URL> <ADMIN_ID_TOKEN> <DEVICE_ID> <OWNER_UID>
set -euo pipefail
if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <NGROK_URL> <ADMIN_ID_TOKEN> <DEVICE_ID> <OWNER_UID>"
  exit 2
fi
NGROK_URL=$1
ADMIN_TOKEN=$2
DEVICE_ID=$3
OWNER_UID=$4
curl -v -X POST "${NGROK_URL}/register_device" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"device_id\":\"${DEVICE_ID}\",\"owner_uid\":\"${OWNER_UID}\",\"info\":{\"name\":\"Test Device\"}}"

