"""Fixture scope: how often does a fixture run?

The default scope is `function`, so `interfaces` is rebuilt for every test that
names it. Swap the commented `scope="session"` decorator in and the setup runs
once for the whole session instead. Run with -s from the workshop root to watch
the "Setting up" print fire:

    uv run pytest examples/003_pytest/002_fixtures/002_scope/ -v -s
"""

import pytest

@pytest.fixture
#@pytest.fixture(scope="session")
def interfaces():
    print("Setting up interfaces fixture")
    return [
        {"name": "Ethernet1", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Ethernet2", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Loopback0", "status": "up", "fcs_errors": 0, "in_discards": 0},
    ]
