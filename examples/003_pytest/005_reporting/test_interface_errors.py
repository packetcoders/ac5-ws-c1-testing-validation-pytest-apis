"""A second test reusing the same fixture, this time checking error counters.

Two tests, one fixture: that is the point of putting `interfaces` in
conftest.py. Run from the workshop root:

    uv run pytest examples/003_pytest/002_fixtures/ -v
"""
import allure
import pytest


@allure.feature("Interface health")
@allure.title("{interface_name} is error-free")
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
@pytest.mark.parametrize("interface_error", ["fcs_errors", "in_discards"])
def test_no_interface_error(interfaces, interface_name, interface_error, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data[interface_error] == expected_state[interface_error]


