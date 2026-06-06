"""Source of truth: assert status matches expected_state.yaml.

Rather than hard-coding the pass condition, each interface is compared against
the `expected_state` fixture loaded from expected_state.yaml. Run from the
workshop root:

    uv run pytest examples/003_pytest/004_sot/ -v
"""

import pytest


@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
def test_interface_up(interfaces, interface_name, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data["status"] == expected_state["status"]
