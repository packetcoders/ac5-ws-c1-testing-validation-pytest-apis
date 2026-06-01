"""Example 3: A self-contained intended-vs-operational validation test.

A complete worked example for Workbook 3. Uses the same `intended` and
`operational` session fixtures from `conftest.py` as the real suite, so it
also runs under `--offline`.

Run from the workshop root:

    uv run pytest examples/003_validation_suite/ -v --offline
"""

import pytest

HOSTS = ["rtr001", "rtr002", "rtr003", "rtr004"]


@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_loopback_matches(host, intended, operational):
    """The simplest possible diff: one field on the intended side equals
    the same field on the operational side."""
    assert intended[host]["loopback_ip"] == operational[host]["loopback_ip"]


@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_full_intended_interfaces_subset(host, intended, operational):
    """Every intended (name, ip_address) pair appears in operational."""
    intended_pairs = {
        (intf["name"], intf["ip_address"]) for intf in intended[host]["interfaces"]
    }
    operational_pairs = {
        (intf["name"], intf["ip_address"]) for intf in operational[host]["interfaces"]
    }
    missing = intended_pairs - operational_pairs
    assert not missing, f"{host}: missing intended interfaces {missing}"
