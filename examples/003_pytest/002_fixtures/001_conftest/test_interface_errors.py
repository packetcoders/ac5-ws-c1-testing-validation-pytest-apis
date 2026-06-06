"""A second test reusing the same fixture, this time checking error counters.

Two tests, one fixture: that is the point of putting `interfaces` in
conftest.py. Run from the workshop root:

    uv run pytest examples/003_pytest/002_fixtures/ -v
"""


def test_no_interface_error(interfaces):
    for i in interfaces:
        assert i["fcs_errors"] == 0
        assert i["in_discards"] == 0
