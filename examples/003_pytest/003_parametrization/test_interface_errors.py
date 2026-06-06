"""Stacked parametrization: one test per interface, per error counter.

Two `parametrize` markers multiply together, giving a separate test for every
interface-and-counter pair. Run from the workshop root:

    uv run pytest examples/003_pytest/003_parametrization/ -v
"""

import pytest


@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
@pytest.mark.parametrize("interface_error", ["fcs_errors", "in_discards"])
def test_no_interface_error(interfaces, interface_name, interface_error):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]
    assert interface_data[interface_error] == 0
