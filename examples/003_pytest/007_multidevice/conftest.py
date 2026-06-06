"""Shared fixtures for the multi-device tests.

This folder fans the live EOS reporting suite (006_eos_reporting) out across
every leaf in your pod. The tests are unchanged from 006: they still just name
`interfaces` as a parameter. The only difference is the fixture, which is now
*parametrized* over the pod, so pytest runs every test once per leaf and reports
each leaf's pass/fail on its own line ([leaf1], [leaf2], ...).

The pod membership comes from a local inventory (devices.yaml) and the pod
helper (helpers.py), both kept in this folder so the example is self-contained.
`expected_state.yaml` is a single shared baseline: the same intended state is
asserted against every device.

Run from the workshop root with a populated .env:

    uv run pytest examples/003_pytest/007_multidevice/ -v
"""

import os
from pathlib import Path

import jsonatapy
import pytest
import requests
import urllib3
from dotenv import load_dotenv

from helpers import load_yaml, pod_devices

# Lab certs are self-signed, so requests warns on every call. Silence it once
# here so test output stays readable.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

DEVICE_USERNAME = os.getenv("DEVICE_USERNAME")
DEVICE_PASSWORD = os.getenv("DEVICE_PASSWORD")

DEVICES_FILE = Path(__file__).parent / "devices.yaml"
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


POD = pod_devices(load_yaml(DEVICES_FILE))


@pytest.fixture(scope="session", params=POD, ids=[device["name"] for device in POD])
def interfaces(request):
    """Live interface state for one pod leaf, pulled over eAPI and reshaped.

    Parametrizing the fixture over the pod is what fans the suite out: every
    test that names `interfaces` runs once per leaf. request.param is this
    leaf's device dict, and ids labels each case with its name ([leaf1], ...).
    """
    device = request.param

    client = EApiClient(device["host"], DEVICE_USERNAME, DEVICE_PASSWORD)
    show_interfaces = client.run(["show interfaces"])[0]
    return jsonatapy.evaluate(INTERFACE_QUERY, show_interfaces)


@pytest.fixture(scope="session")
def expected_state():
    """One shared baseline, asserted against every device in the pod."""
    return load_yaml(EXPECTED_STATE_FILE)
