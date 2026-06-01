"""A second test reusing the same fixture, this time checking error counters.

Two tests, one fixture: that is the point of putting `interfaces` in
conftest.py. Run from the workshop root:

    uv run pytest examples/003_pytest/002_fixtures/ -v
"""


def test_no_interface_errors(interfaces):
    """Flat records make the check a one-line comprehension."""
    dirty = [
        intf["name"]
        for intf in interfaces
        if intf["fcs_errors"] or intf["in_discards"]
    ]
    assert not dirty, f"interfaces with errors: {dirty}"
