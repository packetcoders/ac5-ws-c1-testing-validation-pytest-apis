"""Example 2: Wrap eAPI in a small client class with an offline twin.

A complete worked example for Workbook 2, Exercise 2. Demonstrates the
`EApiClient` / `OfflineClient` pair from `final-project/client.py`.

Run from the workshop root:

    uv run examples/002_device_apis/2_client_class.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "final-project"))

from client import OfflineClient  # noqa: E402

# --- Offline client: same interface, no network ---

# OfflineClient reads captured payloads from data/api_responses/, so the
# example runs on a laptop in CI as well as on the lab.
client = OfflineClient(hostname="rtr001")

[version] = client.run(["show version"])
print(version["hostname"], version["version"])
# rtr001 4.28.0F

# Multiple commands return multiple results, one per command.
results = client.run(["show version", "show interfaces", "show ip bgp summary"])
print(len(results))
# 3
print(list(results[1]["interfaces"]))
# ['Loopback0', 'Ethernet1']
