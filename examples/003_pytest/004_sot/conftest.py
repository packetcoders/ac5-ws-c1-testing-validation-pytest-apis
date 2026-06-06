"""Shared fixtures for the tests in this folder.

A fixture in `conftest.py` is available to every test in its directory tree
without importing it. Both test files here name `interfaces` as a parameter
and pytest injects this return value.
"""

from pathlib import Path

import pytest
import yaml

EXPECTED_STATE_FILE = Path(__file__).parent / "expected_state.yaml"

print(f"Expected state file path: {EXPECTED_STATE_FILE}")


def load_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def interfaces():
    return [
        {"name": "Ethernet1", "status": "up", "fcs_errors": 0, "in_discards": 1},
        {"name": "Ethernet2", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Loopback0", "status": "up", "fcs_errors": 0, "in_discards": 0},
    ]


@pytest.fixture(scope="session")
def expected_state():
    return load_yaml(EXPECTED_STATE_FILE)
