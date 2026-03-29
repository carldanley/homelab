#!/bin/bash
set -euo pipefail

python3 - <<'PY'
import os
import socket
import sys
import time

host = os.environ["XI_NETWORK_ZMQ_IP"]
port = 54003

for _ in range(150):
  try:
    with socket.create_connection((host, port), timeout=1):
      print(f"World reachable at {host}:{port}")
      sys.exit(0)
  except OSError:
    time.sleep(2)

print(f"Timed out waiting for world at {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
