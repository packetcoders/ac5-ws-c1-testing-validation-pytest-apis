"""Shared fixtures for the tests in this folder.

A fixture in `conftest.py` is available to every test in its directory tree
without importing it. Both test files here name `interfaces` as a parameter
and pytest injects this return value.
"""

import pytest


@pytest.fixture
def interfaces():
    """Flat interface records, the shape JSONata produced from the eAPI response.

    Function-scoped (the default): rebuilt fresh for every test that asks for
    it. In the real validation suite this data is read from the device; here
    it is inline so the example runs anywhere.
    """
    return [
        {"name": "Ethernet1", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Ethernet2", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Loopback0", "status": "up", "fcs_errors": 0, "in_discards": 0},
    ]
