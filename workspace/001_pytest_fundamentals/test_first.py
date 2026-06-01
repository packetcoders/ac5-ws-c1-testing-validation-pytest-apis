"""Exercise 1: A first pytest file.

Fill in each TODO, then run:
    uv run pytest workspace/001_pytest_fundamentals/test_first.py -v

A complete worked version is in examples/001_pytest_fundamentals/.
"""

import pytest


# TODO 1: write a test function `test_two_plus_two` that asserts 2 + 2 == 4.


# TODO 2: write a fixture `devices` that returns a list of four device dicts,
#         each with `name` (rtr001..rtr004) and `platform` ("eos").
@pytest.fixture
def devices():
    ...


# TODO 3: write a test `test_inventory_has_four_devices(devices)` that asserts
#         the fixture returns four devices.


# TODO 4: write a parametrized test `test_host_name_starts_with_rtr(host)`
#         that runs once per host name in ["rtr001", "rtr002", "rtr003", "rtr004"]
#         and asserts the name starts with "rtr".
