"""Fixtures in action: assert every interface is up.

The `interfaces` fixture lives in conftest.py; this test receives it just by
naming it as a parameter. Run from the workshop root:

    uv run pytest examples/003_pytest/002_fixtures/ -v
"""


def test_all_interfaces_up(interfaces):
    """Collect the offenders, then assert the list is empty for a clear message."""
    down = [intf["name"] for intf in interfaces if intf["status"] != "up"]
    assert not down, f"interfaces not up: {down}"
