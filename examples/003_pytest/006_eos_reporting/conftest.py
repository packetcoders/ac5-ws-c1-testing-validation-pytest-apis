"""Shared fixtures for the EOS reporting tests.

This folder is the live counterpart to the earlier fixture examples. Instead of
hand-writing the `interfaces` list, we pull `show interfaces` from the device
over eAPI (the client from examples/001_eapi/) and reshape the nested JSON-RPC
result into a flat list with JSONata (the query from examples/002_jsonata/).

The tests are unchanged: they still just name `interfaces` as a parameter and
pytest injects whatever this fixture returns, now sourced from a real device.

Run from the workshop root with a populated .env:

    uv run pytest examples/003_pytest/006_eos_reporting/ -v
"""

import os
from pathlib import Path

import jsonatapy
import pytest
import requests
import urllib3
import yaml
from dotenv import load_dotenv

# Lab certs are self-signed, so requests warns on every call. Silence it once
# here so test output stays readable.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

DEVICE_USERNAME = os.getenv("DEVICE_USERNAME")
DEVICE_PASSWORD = os.getenv("DEVICE_PASSWORD")
HOST = f"172.29.165.{os.getenv('STUDENT_ID')}"

EXPECTED_STATE_FILE = Path(__file__).parent / "expected_state.yaml"

# Flatten the nested `show interfaces` result into one dict per interface,
# renaming EOS camelCase fields to the snake_case keys the tests assert on.
INTERFACE_QUERY = """
interfaces.*.{
    "name": **.name,
    "status": lineProtocolStatus,
    "runt_frames": **.runtFrames,
    "rx_pause": **.rxPause,
    "fcs_errors": **.fcsErrors,
    "alignment_errors": **.alignmentErrors,
    "giant_frames": **.giantFrames,
    "symbol_errors": **.symbolErrors,
    "in_discards": **.inDiscards
}
"""


class EApiClient:
    """Issue eAPI commands against one device and return parsed JSON results."""

    def __init__(self, host, username, password, timeout=10):
        # __init__ just stores configuration; no network call happens yet.
        self.url = f"https://{host}/command-api"
        self.auth = (username, password)
        self.timeout = timeout

    def run(self, cmds):
        """POST a list of CLI commands; return the list of per-command results."""
        payload = {
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": {"version": 1, "cmds": cmds, "format": "json"},
            "id": 1,
        }
        response = requests.post(
            self.url,
            json=payload,
            auth=self.auth,
            verify=False,
            timeout=self.timeout,
        )
        response.raise_for_status()
        # result is a list, one entry per command in the same order as cmds.
        return response.json()["result"]


def load_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def interfaces():
    """Live interface state: pulled over eAPI, reshaped with JSONata."""
    client = EApiClient(HOST, DEVICE_USERNAME, DEVICE_PASSWORD)
    show_interfaces = client.run(["show interfaces"])[0]
    return jsonatapy.evaluate(INTERFACE_QUERY, show_interfaces)


@pytest.fixture(scope="session")
def expected_state():
    return load_yaml(EXPECTED_STATE_FILE)
