"""Shared pytest fixtures for the C1 validation suite.

Lives at the repo root so every test in `tests/` picks the fixtures up.
A `--offline` flag swaps the live eAPI client for one that replays captured
payloads from `data/api_responses/`, so the same suite runs against the lab
or in CI.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Make `final-project/` importable as a flat module path.
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "final-project"))

from client import EApiClient, OfflineClient  # noqa: E402
from state import load_intended_state, load_operational_state  # noqa: E402


def pytest_addoption(parser):
    """Add a --offline flag so the suite can read from captured payloads."""
    parser.addoption(
        "--offline",
        action="store_true",
        default=False,
        help="Read responses from data/api_responses/ instead of the lab.",
    )


@pytest.fixture(scope="session")
def offline(request) -> bool:
    return request.config.getoption("--offline")


@pytest.fixture(scope="session")
def intended() -> dict:
    """Per-host intended state, loaded once per pytest run."""
    return load_intended_state()


@pytest.fixture(scope="session")
def hosts(intended) -> list[str]:
    """The list of host names in inventory order."""
    return list(intended.keys())


@pytest.fixture(scope="session")
def credentials() -> tuple[str, str]:
    """DEVICE_USERNAME / DEVICE_PASSWORD from .env."""
    load_dotenv(ROOT / "final-project" / ".env")
    return os.getenv("DEVICE_USERNAME", ""), os.getenv("DEVICE_PASSWORD", "")


@pytest.fixture(scope="session")
def clients(intended, credentials, offline) -> dict:
    """One eAPI (or offline) client per host, keyed by host name."""
    username, password = credentials
    out = {}
    for name, data in intended.items():
        if offline:
            out[name] = OfflineClient(hostname=name)
        else:
            out[name] = EApiClient(
                hostname=name,
                host_ip=data["hostname"],
                username=username,
                password=password,
            )
    return out


@pytest.fixture(scope="session")
def operational(clients, hosts) -> dict:
    """Per-host operational state, fetched once per pytest run."""
    return {name: load_operational_state(clients[name], name) for name in hosts}
