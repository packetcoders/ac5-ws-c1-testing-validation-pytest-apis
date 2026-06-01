# Workbook 1: Pytest Fundamentals

## Learning Objectives

By the end of this workbook, you will be able to:

- Write a test function and run it with `pytest`.
- Use `assert` with messages so failures are readable.
- Group shared setup into a fixture and pick its scope.
- Run the same test against many inputs with `parametrize`.
- Tag and select tests with markers.

## Overview

Pytest is the runner the rest of this session depends on. A test is a Python
function whose name starts with `test_`; pytest finds it, runs it, and reports
the outcome. There is no test base class, no setup ceremony: just functions
and `assert` statements. This workbook builds the foundation by writing tests
that have nothing to do with the network, so the focus stays on the runner
itself. Workbook 2 brings the eAPI in; Workbook 3 wires both together into
the validation suite.

```
test_*.py  ──►  pytest  ──►  PASSED / FAILED   (exit code 0 / non-zero)
```

## Before You Begin

- Open a session to your lab environment directly within your browser.
- The workshop repository is already cloned, with the Python environment
  installed via `uv`.
- Workbook 1 is delivered as file editing: you write tests under
  `workspace/001_pytest_fundamentals/` and run them with `pytest`.
- Open a terminal and change into the working directory:

```bash
cd workspace/001_pytest_fundamentals
```

> **Note:** Workbook 1 has no live device dependency. Everything runs locally on the
> lab VM. The matching answer key is in
> `examples/001_pytest_fundamentals/`.

## Exercise 1: Your First Test File

A test file is a regular Python file whose name starts with `test_`. Inside
it, every function whose name starts with `test_` is a test pytest will run.
A test passes when every `assert` is true and no exception escapes the body.

### Task 1 – Write a test and run pytest

1. Open `workspace/001_pytest_fundamentals/test_first.py` in the editor.
2. Find `TODO 1` and add a function `test_two_plus_two`:

```python
def test_two_plus_two():
    assert 2 + 2 == 4
```

3. From the workshop root, run pytest against just this file:

```bash
uv run pytest workspace/001_pytest_fundamentals/test_first.py -v
```

**Expected output:**

```
workspace/001_pytest_fundamentals/test_first.py::test_two_plus_two PASSED
============================== 1 passed in 0.01s ==============================
```

<details>
<summary><b>Solution</b></summary>

```python
def test_two_plus_two():
    assert 2 + 2 == 4
```

</details>

### Task 2 – Add a fixture and a test that uses it

A fixture is a function decorated with `@pytest.fixture` that returns a value.
A test receives that value by listing the fixture's name as one of its
parameters.

1. Still in `test_first.py`, find `TODO 2` and write the `devices` fixture:

```python
@pytest.fixture
def devices():
    return [
        {"name": "rtr001", "platform": "eos"},
        {"name": "rtr002", "platform": "eos"},
        {"name": "rtr003", "platform": "eos"},
        {"name": "rtr004", "platform": "eos"},
    ]
```

2. At `TODO 3`, add a test that consumes the fixture:

```python
def test_inventory_has_four_devices(devices):
    assert len(devices) == 4
```

3. Rerun pytest and confirm both tests pass.

**Expected output:** two `PASSED` lines, ending with `2 passed`.

<details>
<summary><b>Solution</b></summary>

```python
import pytest

@pytest.fixture
def devices():
    return [
        {"name": "rtr001", "platform": "eos"},
        {"name": "rtr002", "platform": "eos"},
        {"name": "rtr003", "platform": "eos"},
        {"name": "rtr004", "platform": "eos"},
    ]

def test_inventory_has_four_devices(devices):
    assert len(devices) == 4
```

</details>

### Task 3 – Parametrize a test over the host list

`@pytest.mark.parametrize("<arg>", [<value>, <value>, ...])` runs the same
test once per value, with each value bound to the named argument. Each
parametrized case appears as its own line in the report.

1. At `TODO 4`, add a parametrized test:

```python
@pytest.mark.parametrize("host", ["rtr001", "rtr002", "rtr003", "rtr004"])
def test_host_name_starts_with_rtr(host):
    assert host.startswith("rtr")
```

2. Rerun pytest. The parametrized test should appear four times in the report,
   once per host.

**Expected output:**

```
test_first.py::test_two_plus_two PASSED
test_first.py::test_inventory_has_four_devices PASSED
test_first.py::test_host_name_starts_with_rtr[rtr001] PASSED
test_first.py::test_host_name_starts_with_rtr[rtr002] PASSED
test_first.py::test_host_name_starts_with_rtr[rtr003] PASSED
test_first.py::test_host_name_starts_with_rtr[rtr004] PASSED
============================== 6 passed in 0.02s ==============================
```

**Question:** the test body never mentions `rtr001` or `rtr002`. How does pytest
know to run it four times, with a different value each time?

<details>
<summary><b>Answer</b></summary>

The `@pytest.mark.parametrize` decorator tells pytest to generate one test per
value in the list, binding each value to the named argument (`host`). At
collection time pytest sees one parametrized test definition and expands it
into four real tests, each with `host` set to a different name. The body is
unchanged: the runner just calls it once per value.

</details>

## Exercise 2: Markers and Selection

A marker is a tag you attach to a test with `@pytest.mark.<name>`. Markers
let you run a subset of the suite with `pytest -m <name>`. Custom markers
must be declared in `pyproject.toml` to keep pytest from warning about
them. The shared `pyproject.toml` already declares the markers used in this
session (`online`, `offline`, `bgp`, `intended_vs_operational`).

### Task 1 – Tag tests with markers

1. Open `workspace/001_pytest_fundamentals/test_markers.py` in the editor.
2. At `TODO 1`, tag `test_a_slow_check` with `@pytest.mark.slow` and have it
   assert `True`:

```python
@pytest.mark.slow
def test_a_slow_check():
    assert True
```

3. At `TODO 2`, leave `test_a_fast_check` untagged and have it assert `True`.
4. At `TODO 3`, tag `test_a_bgp_check` with `@pytest.mark.bgp` and parametrize
   it over `["rtr001", "rtr002"]`:

```python
@pytest.mark.bgp
@pytest.mark.parametrize("host", ["rtr001", "rtr002"])
def test_a_bgp_check(host):
    assert host.startswith("rtr")
```

5. Run the file as-is:

```bash
uv run pytest workspace/001_pytest_fundamentals/test_markers.py -v
```

**Expected output:** four `PASSED` lines: the slow test, the fast test, and
the two parametrized bgp cases. Pytest may print a warning about `slow` not
being a registered marker, which is harmless for this Task.

<details>
<summary><b>Solution</b></summary>

```python
import pytest

@pytest.mark.slow
def test_a_slow_check():
    assert True

def test_a_fast_check():
    assert True

@pytest.mark.bgp
@pytest.mark.parametrize("host", ["rtr001", "rtr002"])
def test_a_bgp_check(host):
    assert host.startswith("rtr")
```

</details>

### Task 2 – Select tests with `-m` and `-k`

`-m <name>` runs only tests with that marker. `-k <expr>` runs only tests
whose name matches the substring expression. Both can be combined.

1. Run only the slow tests:

```bash
uv run pytest workspace/001_pytest_fundamentals/test_markers.py -m slow -v
```

**Expected output:** one PASS line for `test_a_slow_check`, plus a
`deselected` summary line covering the other three tests.

2. Run only the bgp tests:

```bash
uv run pytest workspace/001_pytest_fundamentals/test_markers.py -m bgp -v
```

**Expected output:** two PASS lines (`[rtr001]` and `[rtr002]`).

3. Run by name substring, picking up every test whose name contains `check`:

```bash
uv run pytest workspace/001_pytest_fundamentals/test_markers.py -k check -v
```

**Expected output:** every test in the file (all four match the substring
`check`).

> **Tip:** The session's main `pyproject.toml` declares `online`, `offline`, `bgp`,
> and `intended_vs_operational` as official markers. Add your own there
> before relying on them so pytest doesn't warn.

<details>
<summary><b>Solution</b></summary>

The three shell commands in steps 1 to 3 are the solution. Compare the
`PASSED` and `deselected` lines pytest prints in each case: the same file
yields a different subset of tests under each flag.

</details>
