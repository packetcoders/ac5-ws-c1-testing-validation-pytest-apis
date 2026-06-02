"""Source of truth: assert error counters match expected_state.yaml.

Each interface-and-counter pair is compared against the `expected_state`
fixture rather than a literal 0. Run from the workshop root:

    uv run pytest examples/003_pytest/004_sot/ -v
"""
import pytest


@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
@pytest.mark.parametrize("interface_error", ["fcs_errors", "in_discards"])
def test_no_interface_error(interfaces, interface_name, interface_error, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data[interface_error] == expected_state[interface_error]


