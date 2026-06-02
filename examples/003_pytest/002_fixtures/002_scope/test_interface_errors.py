"""Several tests requesting the same fixture, to make scope visible.

Each test here names `interfaces`. With the default function scope the fixture
runs once per test; with session scope it runs once total. Run with -s from the
workshop root to count how often the setup print fires:

    uv run pytest examples/003_pytest/002_fixtures/002_scope/ -v -s
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
