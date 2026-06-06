"""Allure reporting: assert status and annotate the report.

The same source-of-truth status check as 004_sot, now decorated with Allure
feature and title metadata so the run produces a rich HTML report. Run from the
workshop root and write the raw results:

    uv run pytest examples/003_pytest/005_reporting --alluredir=allure-results
"""

import allure
import pytest


@allure.feature("Interface health")
@allure.title("{interface_name} is up")
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
def test_interface_up(interfaces, interface_name, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data["status"] == expected_state["status"]
