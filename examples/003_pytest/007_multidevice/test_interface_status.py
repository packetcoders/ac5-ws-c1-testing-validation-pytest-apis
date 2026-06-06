"""Multi-device reporting: assert status across every leaf in the pod.

Identical to 006_eos_reporting/test_interface_status.py. Nothing here changed:
the fan-out comes entirely from the `interfaces` fixture, which is parametrized
over the pod in conftest.py. pytest crosses that with interface_name below, so
each case is named [<interface>-<leaf>], e.g. test_interface_up[Ethernet1-leaf1].

Run from the workshop root with a populated .env:

    uv run pytest examples/003_pytest/007_multidevice/ -v
"""

import allure
import pytest


@allure.feature("Interface health")
@allure.title("{interface_name} is up")
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Management0"])
def test_interface_up(interfaces, interface_name, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]

    assert interface_data["status"] == expected_state["status"]
