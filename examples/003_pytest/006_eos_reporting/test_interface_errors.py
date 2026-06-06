"""Live EOS reporting: assert error counters against state from the device.

Same counter check as 005_reporting, but `interfaces` now comes from a real
device over eAPI (see conftest.py) rather than a hard-coded list. Run from the
workshop root with a populated .env:

    uv run pytest examples/003_pytest/006_eos_reporting --alluredir=allure-results
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
def test_no_interface_error(
    interfaces, interface_name, interface_error, expected_state
):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data[interface_error] == expected_state[interface_error]
