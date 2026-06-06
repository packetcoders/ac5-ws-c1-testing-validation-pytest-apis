"""Allure reporting: assert error counters and annotate the report.

The same source-of-truth counter check as 004_sot, now decorated with Allure
feature and title metadata. Run from the workshop root and write the raw
results:

    uv run pytest examples/003_pytest/005_reporting --alluredir=allure-results
"""

import allure
import pytest


@allure.feature("Interface health")
@allure.title("{interface_name} is error-free")
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
@pytest.mark.parametrize("interface_error", ["fcs_errors", "in_discards"])
def test_no_interface_error(
    interfaces, interface_name, interface_error, expected_state
):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data[interface_error] == expected_state[interface_error]
