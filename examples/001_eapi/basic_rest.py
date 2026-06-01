"""Example: a first REST API call with `requests`.

Before touching a device, see a request and response end to end against a
public sample endpoint. The endpoint returns an already-flat list of
interface records, so parsing is a plain loop. Run from the workshop root:

    uv run examples/001_eapi/basic_rest.py
"""

import requests

URL = "https://tools.packetcoders.io/api/v1/sample/interfaces/"

# A GET reads a resource. No body, no auth: the path identifies what we want.
response = requests.get(URL, timeout=10)

# 200 means OK. raise_for_status() turns any non-2xx into an exception.
response.raise_for_status()
print(response.status_code)
# 200

# .json() parses the body into Python dicts and lists.
body = response.json()
interfaces = body["interfaces"]
print(len(interfaces))
# 5

# The sample API hands back flat records, so one loop is enough.
for intf in interfaces:
    print(f"{intf['name']:<22} {intf['status']:<22} {intf['ip_address']}")
# GigabitEthernet0/0     up                     10.0.0.1
# ...
