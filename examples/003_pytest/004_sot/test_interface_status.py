"""Fixtures in action: assert every interface is up.

The `interfaces` fixture lives in conftest.py; this test receives it just by
naming it as a parameter. Run from the workshop root:

    uv run pytest examples/003_pytest/002_fixtures/ -v
"""

import pytest


@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
def test_interface_up(interfaces, interface_name, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data["status"] == expected_state["status"]

