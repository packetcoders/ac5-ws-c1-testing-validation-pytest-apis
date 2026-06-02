"""Example: a first REST API call with `requests`.

Before touching a device, see a request and response end to end against a
public sample endpoint. The endpoint returns an already-flat list of
interface records, so parsing is a plain loop. Run from the workshop root:

    uv run examples/001_eapi/basic_rest.py
"""

import requests
from rich import print as rprint

URL = "https://tools.packetcoders.io/api/v1/sample/interfaces/"

# A GET reads a resource. No body, no auth: the path identifies what we want.
response = requests.get(URL, timeout=10)

# 200 means OK. raise_for_status() turns any non-2xx into an exception.
response.raise_for_status()
rprint(response.status_code)
# 200

# .json() parses the body into Python dicts and lists.
body = response.json()
interfaces = body["interfaces"]
rprint(body)
