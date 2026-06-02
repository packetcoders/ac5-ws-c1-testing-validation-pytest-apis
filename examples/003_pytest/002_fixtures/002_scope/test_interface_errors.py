"""A second test reusing the same fixture, this time checking error counters.

Two tests, one fixture: that is the point of putting `interfaces` in
conftest.py. Run from the workshop root:

    uv run pytest examples/003_pytest/002_fixtures/ -v
"""


def test_no_interface_error_1(interfaces):
    assert interfaces[0]["fcs_errors"] == 0

def test_no_interface_error_2(interfaces):
    assert interfaces[1]["fcs_errors"] == 0

def test_no_interface_error_3(interfaces):
    assert interfaces[2]["fcs_errors"] == 0

def test_no_interface_error_4(interfaces):
    assert interfaces[0]["fcs_errors"] == 0

def test_no_interface_error_5(interfaces):
    assert interfaces[0]["fcs_errors"] == 0
