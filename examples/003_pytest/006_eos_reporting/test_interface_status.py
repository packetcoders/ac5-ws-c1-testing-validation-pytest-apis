"""Live EOS reporting: assert status against state pulled from the device.

Same test as 005_reporting, but `interfaces` now comes from a real device over
eAPI (see conftest.py) rather than a hard-coded list. Run from the workshop
root with a populated .env:

    uv run pytest examples/003_pytest/006_eos_reporting --alluredir=allure-results
"""

import allure
import pytest


@allure.feature("Interface health")
@allure.title("{interface_name} is up")
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Management0"])
def test_interface_up(interfaces, interface_name, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data["status"] == expected_state["status"]
