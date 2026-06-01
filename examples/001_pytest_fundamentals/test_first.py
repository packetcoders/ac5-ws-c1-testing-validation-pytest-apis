"""Example 1: A first pytest file with one test, one fixture, and one parametrize.

A complete worked example for Workbook 1, Exercise 1. Run it from the
examples directory:

    uv run pytest examples/001_pytest_fundamentals/test_first.py -v
"""

import pytest


# --- A plain test ---

def test_two_plus_two():
    """A test passes when every assert is true and no exception escapes."""
    assert 2 + 2 == 4


def test_assertion_can_carry_a_message():
    """An optional second argument to assert appears on failure only."""
    interfaces_up = 4
    assert interfaces_up == 4, f"expected 4 up interfaces, got {interfaces_up}"


# --- A fixture and a test that uses it ---

@pytest.fixture
def devices():
    """A function-scoped fixture: rebuilt for every test that asks for it."""
    return [
        {"name": "rtr001", "platform": "eos"},
        {"name": "rtr002", "platform": "eos"},
        {"name": "rtr003", "platform": "eos"},
        {"name": "rtr004", "platform": "eos"},
    ]


def test_inventory_has_four_devices(devices):
    """The test receives the fixture's return value by naming it as a parameter."""
    assert len(devices) == 4


# --- Parametrize: one test, many cases ---

@pytest.mark.parametrize("host", ["rtr001", "rtr002", "rtr003", "rtr004"])
def test_host_name_starts_with_rtr(host):
    """Each value in the list produces its own test in the output."""
    assert host.startswith("rtr")
