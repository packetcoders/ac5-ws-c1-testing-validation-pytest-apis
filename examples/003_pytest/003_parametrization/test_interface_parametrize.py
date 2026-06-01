"""Parametrize and markers: one check per interface, tags for selection.

Each parametrized case appears as its own test in the output:

    uv run pytest examples/003_pytest/003_parametrization/ -v

Markers tag tests so you can select a subset. Run only the slow case:

    uv run pytest examples/003_pytest/003_parametrization/ -m slow -v
"""

import pytest

# A conftest fixture in 002_fixtures/ is not visible here (conftest only
# applies to its own directory tree), so the data is module-level instead.
INTERFACES = [
    {"name": "Ethernet1", "status": "up", "fcs_errors": 0},
    {"name": "Ethernet2", "status": "up", "fcs_errors": 0},
    {"name": "Loopback0", "status": "up", "fcs_errors": 0},
]
IDS = [intf["name"] for intf in INTERFACES]


# One test definition, one generated case per interface. `ids` gives each case
# a readable name in the output instead of interface0, interface1, ...
@pytest.mark.parametrize("intf", INTERFACES, ids=IDS)
def test_interface_is_up(intf):
    assert intf["status"] == "up"


@pytest.mark.parametrize("intf", INTERFACES, ids=IDS)
def test_interface_has_no_errors(intf):
    assert intf["fcs_errors"] == 0


# Markers tag a test for `-m` selection. Custom markers are declared in
# pyproject.toml ([tool.pytest.ini_options] markers) to avoid warnings.
@pytest.mark.slow
def test_a_slow_check():
    """Runs by default, but also selectable (or skippable) via `-m slow`."""
    assert True
