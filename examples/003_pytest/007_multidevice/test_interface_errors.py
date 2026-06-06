"""Multi-device reporting: assert error counters across every leaf in the pod.

Identical to 006_eos_reporting/test_interface_errors.py. The per-device fan-out
comes from the parametrized `interfaces` fixture in conftest.py; stacked with
interface_name and interface_error below, each case is named
[<counter>-<interface>-<leaf>], so a single bad pair on one leaf is pinned
exactly while every other leaf still reports green.

Run from the workshop root with a populated .env:

    uv run pytest examples/003_pytest/007_multidevice/ -v
"""

import allure
import pytest


@allure.feature("Interface health")
@allure.title("{interface_name} is error-free")
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Management0"])
@pytest.mark.parametrize(
    "interface_error",
    [
        "runt_frames",
        "rx_pause",
        "fcs_errors",
        "alignment_errors",
        "giant_frames",
        "symbol_errors",
        "in_discards",
    ],
)
def test_no_interface_error(interfaces, interface_name, interface_error, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data[interface_error] == expected_state[interface_error]
