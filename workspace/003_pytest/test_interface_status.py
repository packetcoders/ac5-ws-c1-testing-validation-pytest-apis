"""Interface status checks. You grow this test across Exercises 2-6.

Run from the workshop root:

    uv run pytest workspace/003_pytest/test_interface_status.py -v

Answer keys, by stage:
  - Exercise 2 (fixture)        -> examples/003_pytest/002_fixtures/001_conftest/test_interface_status.py
  - Exercise 3 (parametrize)    -> examples/003_pytest/003_parametrization/test_interface_status.py
  - Exercise 4 (expected_state) -> examples/003_pytest/004_sot/test_interface_status.py
  - Exercise 5 (Allure)         -> examples/003_pytest/005_reporting/test_interface_status.py
"""


# TODO (Exercise 2): write `test_interface_up(interfaces)` that asserts every
#                    interface in the fixture has status "up".
#
# TODO (Exercise 3): parametrize the test over each interface name so each
#                    interface is a separate test case.
#
# TODO (Exercise 4): compare against the `expected_state` fixture instead of the
#                    literal "up".
#
# TODO (Exercise 5): annotate with @allure.feature and @allure.title.
def test_interface_up(interfaces): ...
