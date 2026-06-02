"""Example: call eAPI on your own device with raw `requests`.

The sample REST API in 001_basic_rest.py handed back a flat list. A real device
returns a nested JSON-RPC result instead, which is what motivates the JSONata
reshaping in 002_jsonata/. Run from the workshop root with a populated .env:

    uv run examples/001_eapi/002_eapi_call.py
"""

import os
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()

DEVICE_USERNAME = os.getenv("DEVICE_USERNAME")
DEVICE_PASSWORD = os.getenv("DEVICE_PASSWORD")
HOST = f"172.29.165.{os.getenv('STUDENT_ID')}"


load_dotenv(".env")

# The lab certs are self-signed, so requests will warn on every call. Silence
# the warning explicitly so example output stays readable.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = f"https://{HOST}/command-api"

PAYLOAD = {
    "jsonrpc": "2.0",
    "method": "runCmds",
    "params": {"version": 1, "cmds": ["show version"], "format": "json"},
    "id": 1,
}

response = requests.post(
    URL,
    json=PAYLOAD,
    auth=(os.getenv("DEVICE_USERNAME"), os.getenv("DEVICE_PASSWORD")),
    verify=False,
    timeout=10,
)
response.raise_for_status()

body = response.json()
# body["result"] is a list, one entry per command. show version returns a

rprint(body)
rprint(body["result"][0]["version"])
