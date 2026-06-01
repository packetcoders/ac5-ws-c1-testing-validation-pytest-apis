"""Exercise 3: An intended-vs-operational validation test.

Fill in each TODO, then run from the workshop root:
    uv run pytest workspace/003_validation_suite/ -v --offline

A complete worked version is in examples/003_validation_suite/.
"""

import pytest

HOSTS = ["rtr001", "rtr002", "rtr003", "rtr004"]


# TODO 1: tag this test with @pytest.mark.intended_vs_operational, parametrize
#         over HOSTS, and assert each host's intended loopback_ip equals its
#         operational loopback_ip.
def test_loopback_matches(host, intended, operational):
    ...


# TODO 2: tag this test the same way, parametrize over HOSTS, then:
#   - build the set of (name, ip_address) pairs from intended[host]["interfaces"]
#   - build the same set from operational[host]["interfaces"]
#   - assert no intended pair is missing from the operational set
def test_full_intended_interfaces_subset(host, intended, operational):
    ...
