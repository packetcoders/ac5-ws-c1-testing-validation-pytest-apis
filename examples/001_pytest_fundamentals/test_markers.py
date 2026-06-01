"""Example 2: pytest markers and selection with `-m` and `-k`.

A complete worked example for Workbook 1, Exercise 2. Run only the slow
tests with:

    uv run pytest examples/001_pytest_fundamentals/test_markers.py -m slow -v
"""

import pytest


@pytest.mark.slow
def test_a_slow_check():
    """A test tagged @pytest.mark.slow runs only when selected."""
    assert True


def test_a_fast_check():
    """An untagged test runs by default but is skipped under `-m slow`."""
    assert True


@pytest.mark.bgp
@pytest.mark.parametrize("host", ["rtr001", "rtr002"])
def test_a_bgp_check(host):
    """Markers stack with parametrize; each generated case carries the marker."""
    assert host.startswith("rtr")
