"""Interface checks: the running interfaces match the intended interfaces.

Walks each host's `intended.interfaces` and asserts the same name, IP, and
admin state exist on the device. This is the per-link half of the validation:
the BGP-peering half lives in `test_bgp.py`.
"""

import pytest

HOSTS = ["rtr001", "rtr002", "rtr003", "rtr004"]


@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_loopback_ip_matches(host, intended, operational):
    """Loopback0 IP on the device matches the inventory's loopback_ip."""
    assert intended[host]["loopback_ip"] == operational[host]["loopback_ip"], (
        f"{host} Loopback0: "
        f"intended={intended[host]['loopback_ip']} "
        f"operational={operational[host]['loopback_ip']}"
    )


@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_intended_interfaces_present(host, intended, operational):
    """Every intended interface exists on the device."""
    intended_names = {intf["name"] for intf in intended[host]["interfaces"]}
    operational_names = {intf["name"] for intf in operational[host]["interfaces"]}
    missing = intended_names - operational_names
    assert not missing, f"{host} is missing intended interfaces: {sorted(missing)}"


@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_intended_interfaces_have_correct_ip(host, intended, operational):
    """Each intended interface has the IP the inventory says it should."""
    op_by_name = {intf["name"]: intf for intf in operational[host]["interfaces"]}
    mismatches = []
    for intended_intf in intended[host]["interfaces"]:
        op_intf = op_by_name.get(intended_intf["name"])
        if op_intf is None:
            mismatches.append(f"{intended_intf['name']} not present")
            continue
        if op_intf["ip_address"] != intended_intf["ip_address"]:
            mismatches.append(
                f"{intended_intf['name']}: intended={intended_intf['ip_address']} "
                f"operational={op_intf['ip_address']}"
            )
    assert not mismatches, f"{host} interface IP mismatches: {mismatches}"


@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_intended_interfaces_are_up(host, intended, operational):
    """Each intended-and-enabled interface is up on the device."""
    op_by_name = {intf["name"]: intf for intf in operational[host]["interfaces"]}
    down = []
    for intended_intf in intended[host]["interfaces"]:
        if not intended_intf.get("enabled", True):
            continue
        op_intf = op_by_name.get(intended_intf["name"])
        if op_intf is None or not op_intf.get("enabled"):
            down.append(intended_intf["name"])
    assert not down, f"{host} intended-up interfaces are down: {down}"
