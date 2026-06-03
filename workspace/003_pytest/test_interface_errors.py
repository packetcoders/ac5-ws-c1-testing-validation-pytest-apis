"""Interface error-counter checks. You grow this test across Exercises 2-6.

Run from the workshop root:

    uv run pytest workspace/003_pytest/test_interface_errors.py -v

Answer keys, by stage:
  - Exercise 2 (fixture)        -> examples/003_pytest/002_fixtures/001_conftest/test_interface_errors.py
  - Exercise 3 (stacked params) -> examples/003_pytest/003_parametrization/test_interface_errors.py
  - Exercise 4 (expected_state) -> examples/003_pytest/004_sot/test_interface_errors.py
  - Exercise 5 (Allure)         -> examples/003_pytest/005_reporting/test_interface_errors.py
"""


# TODO (Exercise 2): write `test_no_interface_error(interfaces)` that asserts
#                    fcs_errors and in_discards are 0 for every interface.
#
# TODO (Exercise 3): stack two @pytest.mark.parametrize decorators to cross each
#                    interface name with each error counter.
#
# TODO (Exercise 4): compare against the `expected_state` fixture.
#
# TODO (Exercise 5): annotate with @allure.feature and @allure.title.
def test_no_interface_error(interfaces):
    ...
