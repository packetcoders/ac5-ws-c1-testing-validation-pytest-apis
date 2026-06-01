"""Sanity checks: every device is reachable and reports the expected hostname.

The first layer of the validation suite. If these tests fail, the deeper
checks are not worth running, the client can't talk to the device.
"""

import pytest


@pytest.fixture(scope="module")
def host_names(intended):
    return list(intended.keys())


def test_intended_loads_four_hosts(intended):
    """The inventory must list exactly four hosts."""
    assert len(intended) == 4
    assert set(intended) == {"rtr001", "rtr002", "rtr003", "rtr004"}


@pytest.mark.parametrize("host", ["rtr001", "rtr002", "rtr003", "rtr004"])
def test_device_reports_hostname(host, clients):
    """Each device must report its own hostname through `show version`."""
    [version] = clients[host].run(["show version"])
    assert version["hostname"] == host, (
        f"{host} reports hostname={version['hostname']!r}, expected {host!r}"
    )


@pytest.mark.parametrize("host", ["rtr001", "rtr002", "rtr003", "rtr004"])
def test_device_runs_eos(host, clients):
    """Every device must run EOS at the expected major version."""
    [version] = clients[host].run(["show version"])
    assert version["version"].startswith("4."), (
        f"{host} reports EOS {version['version']}, expected 4.x"
    )
