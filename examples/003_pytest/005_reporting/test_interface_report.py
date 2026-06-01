"""Generate an Allure report from a small interface check.

Allure is not a different kind of test, it is a richer way to *report* a run.
You tag tests with features and steps, then point pytest at a results dir.

Write the Allure result files (self-contained, uses inline data):

    uv run pytest examples/003_pytest/005_reporting/ --alluredir=allure-results

Then open the HTML report (needs the `allure` CLI, https://allurereport.org):

    allure serve allure-results
"""

import allure
import pytest

INTERFACES = [
    {"name": "Ethernet1", "status": "up", "fcs_errors": 0},
    {"name": "Ethernet2", "status": "up", "fcs_errors": 0},
    {"name": "Loopback0", "status": "up", "fcs_errors": 0},
]
IDS = [intf["name"] for intf in INTERFACES]


@allure.feature("Interface health")
@allure.title("{intf[name]} is up")
@pytest.mark.parametrize("intf", INTERFACES, ids=IDS)
def test_interface_up(intf):
    # allure.step groups assertions into labelled sections in the report.
    with allure.step(f"check {intf['name']} line protocol"):
        assert intf["status"] == "up"


@allure.feature("Interface health")
@allure.title("{intf[name]} is error-free")
@pytest.mark.parametrize("intf", INTERFACES, ids=IDS)
def test_interface_error_free(intf):
    with allure.step(f"check {intf['name']} fcs errors"):
        assert intf["fcs_errors"] == 0
