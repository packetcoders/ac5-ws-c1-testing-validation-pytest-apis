"""Shared fixtures for the workspace/003_pytest tests.

A fixture in conftest.py is available to every test in this directory without
being imported. You build this file up across Exercises 2, 4, and 6.

Answer keys, by stage:
  - Exercise 2 (fixture)            -> examples/003_pytest/002_fixtures/001_conftest/
  - Exercise 4 (expected_state)     -> examples/003_pytest/004_sot/
  - Exercise 6 (live eAPI + JSONata)-> examples/003_pytest/006_eos_reporting/
"""

import pytest


# TODO (Exercise 2): write an `interfaces` fixture that returns a list of three
#                    interface dicts, each with name / status / fcs_errors /
#                    in_discards. Start with function scope, then switch to
#                    scope="session" in Task 3.
@pytest.fixture
def interfaces():
    ...


# TODO (Exercise 4): add an `expected_state` fixture that loads expected_state.yaml.


# TODO (Exercise 6): swap the `interfaces` fixture body to pull `show interfaces`
#                    over the eAPI client and reshape it with the JSONata query.
