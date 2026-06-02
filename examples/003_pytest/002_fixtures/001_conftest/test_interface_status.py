"""Fixtures in action: assert every interface is up.

The `interfaces` fixture lives in conftest.py; this test receives it just by
naming it as a parameter. Run from the workshop root:

    uv run pytest examples/003_pytest/002_fixtures/ -v
"""


def test_interface_up(interfaces):
    for i in interfaces:
        assert i["status"] == "up"
