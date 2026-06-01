"""Example 1: Call eAPI with raw `requests` to retrieve facts.

A complete worked example for Workbook 2, Exercise 1. Run from the workshop
root with a populated .env:

    uv run examples/002_device_apis/1_eapi_call.py
"""

import os
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / "final-project" / ".env")

# The lab certs are self-signed, so requests will warn on every call. Silence
# the warning explicitly so example output stays readable.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://172.29.163.101/command-api"
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
# dict of facts.
[version] = body["result"]
print(version["hostname"], version["version"])
# rtr001 4.28.0F
