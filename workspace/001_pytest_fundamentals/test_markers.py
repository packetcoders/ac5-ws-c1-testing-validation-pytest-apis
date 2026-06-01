"""Exercise 2: pytest markers and selection.

Fill in each TODO, then run:
    uv run pytest workspace/001_pytest_fundamentals/test_markers.py -m slow -v

A complete worked version is in examples/001_pytest_fundamentals/.
"""

import pytest


# TODO 1: tag this test with @pytest.mark.slow, then assert True.
def test_a_slow_check():
    ...


# TODO 2: leave this one untagged. Assert True. It should run by default but
#         be skipped under `-m slow`.
def test_a_fast_check():
    ...


# TODO 3: tag this test with @pytest.mark.bgp and parametrize over
#         ["rtr001", "rtr002"]. Assert each host name starts with "rtr".
def test_a_bgp_check(host):
    ...
