"""Pytest basics: a passing test and a failure message.

Run from the workshop root:

    uv run pytest examples/003_pytest/001_basic/ -v
"""


def test_two_plus_two():
    """A test passes when every assert is true and no exception escapes."""
    assert 2 + 2 == 4


def test_assertion_can_carry_a_message():
    """An optional second argument to assert appears on failure only."""
    interfaces_up = 4
    assert interfaces_up == 4, f"expected 4 up interfaces, got {interfaces_up}"
