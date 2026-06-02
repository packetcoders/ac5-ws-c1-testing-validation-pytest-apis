"""Shared fixtures for the tests in this folder.

A fixture in `conftest.py` is available to every test in its directory tree
without importing it. Both test files here name `interfaces` as a parameter
and pytest injects this return value.
"""

import pytest

@pytest.fixture
def interfaces():
    return [
        {"name": "Ethernet1", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Ethernet2", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Loopback0", "status": "up", "fcs_errors": 0, "in_discards": 0},
    ]
