"""Container health check: GET /healthz on the port the service listens on."""

import os
import sys
import urllib.request

port = os.environ.get("PORT", "8000")
try:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=4) as response:  # noqa: S310  # loopback only
        sys.exit(0 if response.status == 200 else 1)
except Exception:  # noqa: BLE001  # any failure is unhealthy
    sys.exit(1)
