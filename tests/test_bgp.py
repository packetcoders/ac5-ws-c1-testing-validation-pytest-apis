"""BGP checks: every intended peer is configured and Established.

Walks each host's `intended.bgp.peers` and asserts the device has the same
peer at the same remote AS, with `peerState == "Established"`.
"""

import pytest

HOSTS = ["rtr001", "rtr002", "rtr003", "rtr004"]


@pytest.mark.bgp
@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_local_as_matches(host, intended, operational):
    """The device's local AS matches the inventory's bgp.local_as."""
    assert intended[host]["bgp"]["local_as"] == operational[host]["bgp"]["local_as"], (
        f"{host}: local_as intended={intended[host]['bgp']['local_as']} "
        f"operational={operational[host]['bgp']['local_as']}"
    )


@pytest.mark.bgp
@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_intended_peers_present(host, intended, operational):
    """Every intended BGP peer is configured on the device."""
    intended_peers = {p["peer_ip"] for p in intended[host]["bgp"]["peers"]}
    operational_peers = {p["peer_ip"] for p in operational[host]["bgp"]["peers"]}
    missing = intended_peers - operational_peers
    assert not missing, f"{host} is missing intended BGP peers: {sorted(missing)}"


@pytest.mark.bgp
@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_intended_peers_have_correct_remote_as(host, intended, operational):
    """Each intended peer's remote AS matches what the device reports."""
    op_by_ip = {p["peer_ip"]: p for p in operational[host]["bgp"]["peers"]}
    mismatches = []
    for intended_peer in intended[host]["bgp"]["peers"]:
        op_peer = op_by_ip.get(intended_peer["peer_ip"])
        if op_peer is None:
            mismatches.append(f"{intended_peer['peer_ip']} not present")
            continue
        if op_peer["remote_as"] != intended_peer["remote_as"]:
            mismatches.append(
                f"{intended_peer['peer_ip']}: intended_as={intended_peer['remote_as']} "
                f"operational_as={op_peer['remote_as']}"
            )
    assert not mismatches, f"{host} peer remote-AS mismatches: {mismatches}"


@pytest.mark.bgp
@pytest.mark.parametrize("host", HOSTS)
def test_intended_peers_are_established(host, intended, operational):
    """Each intended BGP peer is in the Established state."""
    op_by_ip = {p["peer_ip"]: p for p in operational[host]["bgp"]["peers"]}
    not_established = []
    for intended_peer in intended[host]["bgp"]["peers"]:
        op_peer = op_by_ip.get(intended_peer["peer_ip"])
        if op_peer is None or op_peer.get("state") != "Established":
            state = op_peer.get("state") if op_peer else "missing"
            not_established.append(f"{intended_peer['peer_ip']}={state}")
    assert not not_established, (
        f"{host} BGP peers not Established: {not_established}"
    )
