"""Parametrization: one test per interface instead of one loop.

`@pytest.mark.parametrize` runs this test once for each interface name, so a
failure pins down the exact interface rather than failing the whole loop. Run
from the workshop root:

    uv run pytest examples/003_pytest/003_parametrization/ -v
"""

import pytest


@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
def test_interface_up(interfaces, interface_name):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]
    assert interface_data["status"] == "up"
