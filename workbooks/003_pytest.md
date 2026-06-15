# Workbook 3: Testing with Pytest

## Learning Objectives

By the end of this workbook, you will be able to:

- Write and run a test with `pytest` and `assert`.
- Share setup across tests with fixtures and `conftest.py`.
- Run one test against many inputs with `parametrize`.
- Compare intended state from YAML against operational state.
- Produce an Allure report and run the suite against a live device.
- Fan the whole suite across every leaf in your pod with a parametrized fixture.

## Overview

Pytest is the test runner that ties this session together. A test is a plain
function whose name starts with `test_`; it passes when its `assert` statements
hold and fails otherwise. You start with a static interface list so the
mechanics are clear, then layer on the tools that turn a handful of asserts into
a validation suite: fixtures to share data, `parametrize` to fan one check across
every interface, a YAML source of truth to compare against, Allure for reporting,
and finally a fixture that pulls live state over the eAPI client and JSONata
query from Workbooks 1 and 2. The tests never change in that last step, only
where their data comes from.

```
static list  ->  fixture  ->  parametrize  ->  expected_state.yaml  ->  Allure  ->  live eAPI + JSONata  ->  whole pod
 Exercise 1     Exercise 2    Exercise 3        Exercise 4              Ex 5         Exercise 6              Exercise 7
```

## Before You Begin

- Open a session to your lab environment directly within your browser.
- The workshop repository is already cloned, with the Python environment
  installed via `uv`.
- Your `STUDENT_ID`, `DEVICE_USERNAME`, and `DEVICE_PASSWORD` are injected into
  your session as environment variables (see `.env.example` for the full list).
  Your device is reachable at `172.29.165.<STUDENT_ID>`. To view the values set
  in your session, run `env | grep -E "STUDENT|DEVICE"` from the repo root.
- Open a terminal: open the menu (hamburger **☰**, top-left) → **Terminal** →
  **New Terminal**.
- You work in `workspace/003_pytest/`, filling in the stub files. A complete
  worked version of every stage lives under `examples/003_pytest/`.
- Run all commands from the repo root.
- Exercise 5 builds an HTML report you view in the editor. Install the
  **Live Preview** extension once so you can open it: click the **Extensions**
  icon in the left sidebar (or menu **☰** → **View** → **Extensions**), search
  for `ms-vscode.live-server`, and click **Install**.

> **Note:** pytest discovers any file named `test_*.py` and runs any function in
> it named `test_*`. A fixture defined in `conftest.py` is handed to any test in
> the same directory that names it as a parameter, no import needed.

## Exercise 1: Write and Run Your First Test

A test is a function. It passes when no `assert` fails and no exception escapes.
`assert <expr>` raises `AssertionError` when `<expr>` is falsy; that is the whole
mechanism. Work in `workspace/003_pytest/test_basics.py`.

### Task 1 – Write a passing test

The form of a test is `def test_<name>():` with one or more `assert` lines in the
body.

1. In `test_basics.py`, write a test that asserts `2 + 2 == 4`:

```python
def test_two_plus_two():
    assert 2 + 2 == 4
```

2. Run just this file:

```bash
uv run pytest workspace/003_pytest/test_basics.py -v
```

**Expected output:** one passing test:

```
test_basics.py::test_two_plus_two PASSED
```

<details>
<summary><b>Solution</b></summary>

The code above is the test. The answer key is
`examples/003_pytest/001_basic/test_hello_world.py`.

</details>

### Task 2 – Attach a failure message

A second argument to `assert` is shown only when the assert fails:
`assert <expr>, "<message>"`. It turns a bare `AssertionError` into something
readable.

1. Add a second test with a custom message:

```python
def test_assertion_can_carry_a_message():
    interfaces_up = 4
    assert interfaces_up == 4, f"expected 4 up interfaces, got {interfaces_up}"
```

2. Re-run the file.

**Expected output:** two passing tests:

```
test_basics.py::test_two_plus_two PASSED
test_basics.py::test_assertion_can_carry_a_message PASSED
```

<details>
<summary><b>Answer</b></summary>

**Question:** when would you ever see that message?

Only on failure. Change `interfaces_up` to `3` and re-run: the message prints
beside the failing assert, telling you the expected and actual counts without you
opening the code. Set it back to `4` before moving on.

</details>

### Task 3 – Run the whole directory

Pointing pytest at a directory discovers every `test_*.py` under it.

1. Run the whole workspace folder:

```bash
uv run pytest workspace/003_pytest/ -v
```

**Expected output:** both tests from `test_basics.py` collected and passing. (The
other stub files hold empty tests for now and are filled in next.)

<details>
<summary><b>Answer</b></summary>

**Question:** how does pytest decide what to run without you listing files?

Discovery by convention: it walks the directory for files matching `test_*.py`,
imports each, and collects functions named `test_*`. Naming is the contract; no
registration is needed.

</details>

## Exercise 2: Share Setup with Fixtures

Real tests need data to act on. A fixture is a function decorated with
`@pytest.fixture` that returns a value; any test that names the fixture as a
parameter receives that value. Put it in `conftest.py` and every test in the
folder can use it without importing it.

### Task 1 – Move an interface list into a fixture

Work in `workspace/003_pytest/conftest.py`.

1. Write an `interfaces` fixture returning three interface dicts:

```python
import pytest


@pytest.fixture
def interfaces():
    return [
        {"name": "Ethernet1", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Ethernet2", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Loopback0", "status": "up", "fcs_errors": 0, "in_discards": 0},
    ]
```

2. In `test_interface_status.py`, write a test that names the fixture and asserts
   every interface is up:

```python
def test_interface_up(interfaces):
    for i in interfaces:
        assert i["status"] == "up"
```

3. Run the two files.

**Expected output:** `test_interface_up` passes.

<details>
<summary><b>Solution</b></summary>

```bash
uv run pytest workspace/003_pytest/test_interface_status.py -v
```

Answer key: `examples/003_pytest/002_fixtures/001_conftest/`.

</details>

### Task 2 – Reuse the fixture from a second file

The same fixture serves every test in the directory tree. That is the reason it
lives in `conftest.py` rather than in one test file.

1. In `test_interface_errors.py`, write a test that reuses `interfaces` and
   checks the error counters:

```python
def test_no_interface_error(interfaces):
    for i in interfaces:
        assert i["fcs_errors"] == 0
        assert i["in_discards"] == 0
```

2. Run the whole folder.

**Expected output:** both `test_interface_up` and `test_no_interface_error` pass,
each fed by the one fixture.

<details>
<summary><b>Solution</b></summary>

Answer key: `examples/003_pytest/002_fixtures/001_conftest/test_interface_errors.py`.

</details>

### Task 3 – Control how often the fixture runs

Fixture scope sets how often the function is called: `function` (the default,
once per test), `module` (once per file), or `session` (once per run). A fixture
that reads a device should be `session`-scoped so the call happens once.

1. Add a print to the fixture so you can see it fire, and run with `-s`:

```python
@pytest.fixture
def interfaces():
    print("Setting up interfaces fixture")
    return [
        {"name": "Ethernet1", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Ethernet2", "status": "up", "fcs_errors": 0, "in_discards": 0},
        {"name": "Loopback0", "status": "up", "fcs_errors": 0, "in_discards": 0},
    ]
```

```bash
uv run pytest workspace/003_pytest/ -v -s
```

2. Count how many times "Setting up" prints. Then change the decorator to
   `@pytest.fixture(scope="session")` and re-run.

**Expected output:** with the default scope the line prints once per test; with
`scope="session"` it prints once for the whole run.

<details>
<summary><b>Answer</b></summary>

**Question:** why does session scope matter once the fixture hits a real device?

Each call to a `function`-scoped device fixture is another API round trip. With
two tests and three interfaces that is wasteful; across a full suite it is slow
and hammers the device. `scope="session"` reads the state once and shares it.
Leave the fixture at `scope="session"` and remove the print before moving on.

Answer key: `examples/003_pytest/002_fixtures/002_scope/`.

</details>

## Exercise 3: Parametrize Your Tests

A loop inside one test fails as a single unit: when interface 7 is bad, the whole
test fails and you do not know which interface. `@pytest.mark.parametrize` runs
the test once per value instead, so each interface is its own pass or fail.

### Task 1 – One test per interface

`@pytest.mark.parametrize("<arg>", [<values>])` adds `<arg>` as a parameter and
runs the test once for each value.

1. Rewrite `test_interface_status.py` to parametrize over the interface names:

```python
import pytest


@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
def test_interface_up(interfaces, interface_name):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]
    assert interface_data["status"] == "up"
```

2. Run the file.

**Expected output:** three separate test cases, one per interface:

```
test_interface_status.py::test_interface_up[Ethernet1] PASSED
test_interface_status.py::test_interface_up[Ethernet2] PASSED
test_interface_status.py::test_interface_up[Loopback0] PASSED
```

<details>
<summary><b>Solution</b></summary>

Answer key: `examples/003_pytest/003_parametrization/test_interface_status.py`.

</details>

### Task 2 – Stack decorators to cross interfaces with counters

Two stacked `parametrize` decorators cross-product their values, giving a test
for every interface-and-counter pair. To see how a failure reads, seed one fault
first.

1. In `conftest.py`, change Ethernet1's `in_discards` from `0` to `1`. This
   stands in for a real device showing dropped packets.
2. Rewrite `test_interface_errors.py` with stacked parametrization:

```python
import pytest


@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
@pytest.mark.parametrize("interface_error", ["fcs_errors", "in_discards"])
def test_no_interface_error(interfaces, interface_name, interface_error):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]
    assert interface_data[interface_error] == 0
```

3. Run the file.

**Expected output:** six cases, with exactly one failure naming the bad pair:

```
test_no_interface_error[in_discards-Ethernet1] FAILED
test_no_interface_error[in_discards-Ethernet2] PASSED
...
```

<details>
<summary><b>Answer</b></summary>

**Question:** what did parametrize buy you over a loop?

The failing case is named `[in_discards-Ethernet1]`: pytest pins the failure to
the exact interface and counter, while every other pair still reports as passing.
A single looping test would have failed as one opaque block. Leave the seeded
`in_discards: 1` in place; the next exercises detect it as drift.

Answer key: `examples/003_pytest/003_parametrization/test_interface_errors.py`.

</details>

## Exercise 4: Compare Intended vs Operational State

A validation test asserts that operational state (what the device reports)
matches intended state (what you decided it should be). Hard-coding `0` mixes the
two; pulling intended state from a YAML source of truth separates them, so the
intent is data you can edit without touching test code.

### Task 1 – Load intended state into a fixture

Work in `workspace/003_pytest/expected_state.yaml` and `conftest.py`.

1. Set the intended state in `expected_state.yaml`:

```yaml
status: up
fcs_errors: 0
in_discards: 0
```

2. Add an `expected_state` fixture to `conftest.py` that loads it once per
   session:

```python
from pathlib import Path

import yaml

EXPECTED_STATE_FILE = Path(__file__).parent / "expected_state.yaml"


def load_yaml(file_path):
    with open(file_path) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def expected_state():
    return load_yaml(EXPECTED_STATE_FILE)
```

**Expected output:** no test change yet; the fixture is wired up for the next
Task.

<details>
<summary><b>Solution</b></summary>

Answer key: `examples/003_pytest/004_sot/conftest.py` and `expected_state.yaml`.

</details>

### Task 2 – Assert operational matches intended

Replace the literals in both tests with lookups against `expected_state`. The
comparison is now "does what the device reports equal what the YAML says it
should be".

1. Update `test_interface_status.py` and `test_interface_errors.py` to compare
   against the fixture:

```python
# test_interface_status.py
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
def test_interface_up(interfaces, interface_name, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]
    assert interface_data["status"] == expected_state["status"]
```

```python
# test_interface_errors.py
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
@pytest.mark.parametrize("interface_error", ["fcs_errors", "in_discards"])
def test_no_interface_error(interfaces, interface_name, interface_error, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]
    assert interface_data[interface_error] == expected_state[interface_error]
```

2. Run the whole folder.

**Expected output:** the status tests pass; the seeded Ethernet1 `in_discards`
case still fails, now reported as operational state (`1`) not matching intended
state (`0`), which is exactly the drift a validation suite exists to catch.

<details>
<summary><b>Solution</b></summary>

Answer key: `examples/003_pytest/004_sot/`.

</details>

## Exercise 5: Report the Results with Allure

Pytest's console output is enough during a run, but a handover or a CI pipeline
wants a report. Allure annotations enrich each test, and the run writes raw
results that build into an HTML report.

### Task 1 – Annotate the tests

`@allure.feature(...)` groups tests and `@allure.title(...)` names each case;
`{interface_name}` in the title is filled from the parametrized value.

1. Add the decorators to both tests, for example in `test_interface_status.py`:

```python
import allure
import pytest


@allure.feature("Interface health")
@allure.title("{interface_name} is up")
@pytest.mark.parametrize("interface_name", ["Ethernet1", "Ethernet2", "Loopback0"])
def test_interface_up(interfaces, interface_name, expected_state):
    interface_data = [i for i in interfaces if i["name"] == interface_name][0]
    assert interface_data["status"] == expected_state["status"]
```

2. Do the same in `test_interface_errors.py` with a title like
   `"{interface_name} is error-free"`.

**Expected output:** tests still run as before; the annotations only affect the
report.

<details>
<summary><b>Solution</b></summary>

Answer key: `examples/003_pytest/005_reporting/`.

</details>

### Task 2 – Build and open the report

`--alluredir` writes the raw results; the Allure CLI turns them into a single
HTML file.

1. Run the suite, writing results, then generate the report:

```bash
uv run pytest workspace/003_pytest/ --alluredir=allure-results
allure generate allure-results -o allure-report --single-file --clean
```

2. Open the report in the editor with the Live Preview extension (installed in
   **Before You Begin**): in the **Explorer**, click `allure-report/index.html`
   to open it, then click the **Show Preview** icon at the top-right of the
   editor (a magnifying glass over a page). The rendered report opens in a
   preview tab beside the file. (You can also right-click `index.html` →
   **Show Preview**.)

**Expected output:** an HTML report grouping cases under "Interface health", each
named from its title, with the seeded Ethernet1 failure shown in red.

> **Tip:** `task report` runs this same pipeline against the worked example in
> `examples/003_pytest/005_reporting` if you want a reference report to compare
> against.

<details>
<summary><b>Answer</b></summary>

**Question:** why write raw results and generate separately instead of one step?

The raw `allure-results` are machine-readable and accumulate across runs; the
HTML is a view built from them. In Session D1 the pipeline uploads the raw
results as a build artifact and generates the HTML in CI, so keeping the two
steps apart is what makes the suite CI-ready.

</details>

## Exercise 6: Validate Live EOS State

Everything so far ran against a hard-coded list. The final step swaps that list
for live device state, pulled over the eAPI client (Workbook 1) and reshaped with
the JSONata query (Workbook 2). The tests do not change at all; only the
`interfaces` fixture does.

### Task 1 – Make the fixture read the device

Replace the body of the `interfaces` fixture in `conftest.py` so it pulls
`show interfaces` and flattens the result. The client class is copied in, the way
`examples/003_pytest/006_eos_reporting/conftest.py` does it.

1. Add the imports and the live fixture (the `EApiClient` class and
   `INTERFACE_QUERY` from the answer key go above it):

```python
import os

import jsonatapy
from dotenv import load_dotenv

load_dotenv()

DEVICE_USERNAME = os.getenv("DEVICE_USERNAME")
DEVICE_PASSWORD = os.getenv("DEVICE_PASSWORD")
HOST = f"172.29.165.{os.getenv('STUDENT_ID')}"


@pytest.fixture(scope="session")
def interfaces():
    client = EApiClient(HOST, DEVICE_USERNAME, DEVICE_PASSWORD)
    show_interfaces = client.run(["show interfaces"])[0]
    return jsonatapy.evaluate(INTERFACE_QUERY, show_interfaces)
```

2. Point the parametrized interface names at interfaces your device actually has,
   for example `Ethernet1` and `Management0`, and widen `expected_state.yaml` to
   the full counter set the query emits (`runt_frames`, `rx_pause`, `fcs_errors`,
   `alignment_errors`, `giant_frames`, `symbol_errors`, `in_discards`).

**Expected output:** the fixture now returns live records; no run yet.

<details>
<summary><b>Solution</b></summary>

Copy the complete `conftest.py`, `expected_state.yaml`, and tests from
`examples/003_pytest/006_eos_reporting/`. The `INTERFACE_QUERY` there is the same
flattening query you finished in Workbook 2, `status` field included, so the
status test works against live data.

</details>

### Task 2 – Run the unchanged tests against the device

The tests are the same functions from Exercise 5; only their data source moved.

1. Run the suite against your live leaf:

```bash
uv run pytest workspace/003_pytest/ -v
```

**Expected output:** one case per interface-and-field pair, asserting live device
counters against your intended state. A clean device passes every case; any
non-zero counter fails the exact pair, named in the output.

<details>
<summary><b>Answer</b></summary>

**Question:** what made the same tests work against a real device with no edit?

The fixture. Every test reads `interfaces` by name and does not care where the
list came from. Swapping the fixture body from a literal to a live eAPI call,
reshaped by JSONata, is the only change, which is exactly why fixtures and a flat
record shape were worth building first.

Answer key: `examples/003_pytest/006_eos_reporting/`.

</details>

## Exercise 7: Run the Suite Across the Whole Pod

So far the suite tests one device, your own leaf. In the lab the leaves are
grouped into pods of ten (`pod1` is `leaf1`-`leaf10`, `pod2` is `leaf11`-`leaf20`,
and so on), and your `STUDENT_ID` places you in one of them. This exercise fans
the same suite across every leaf in your pod. The trick is to parametrize the
*fixture* rather than the tests: a parametrized fixture runs once per value, so
every test that names `interfaces` is automatically repeated for each leaf, with
no change to a single test function.

Work in `workspace/003_pytest/`. A complete worked version lives under
`examples/003_pytest/007_multidevice/`.

### Task 1 – Parametrize the fixture over your pod

Two helper files are provided so the lookup is a plain data read: `devices.yaml`
lists every lab leaf with its `host` and `pod`, and `helpers.py` offers
`pod_devices(inventory)`, which reads the `pod` off your own device and returns
every leaf that shares it.

1. Copy `devices.yaml` and `helpers.py` from
   `examples/003_pytest/007_multidevice/` into your workspace folder.

2. In `conftest.py`, resolve your pod once and parametrize the `interfaces`
   fixture over it. `params` makes the fixture run once per device, and `ids`
   labels each run with the leaf name:

```python
from helpers import load_yaml, pod_devices

DEVICES_FILE = Path(__file__).parent / "devices.yaml"
POD = pod_devices(load_yaml(DEVICES_FILE))


@pytest.fixture(scope="session", params=POD, ids=[device["name"] for device in POD])
def interfaces(request):
    device = request.param
    client = EApiClient(device["host"], DEVICE_USERNAME, DEVICE_PASSWORD)
    show_interfaces = client.run(["show interfaces"])[0]
    return jsonatapy.evaluate(INTERFACE_QUERY, show_interfaces)
```

**Expected output:** no run yet; the fixture now yields one device's records per
parametrized value instead of a single fixed host.

<details>
<summary><b>Answer</b></summary>

**Question:** why parametrize the fixture instead of adding a `leaf` parameter to
every test?

Because the tests should not know there is more than one device. The fixture is
the single place the data comes from, so parametrizing it fans every test out at
once, and the test functions stay byte-for-byte identical to Exercise 6.

Answer key: `examples/003_pytest/007_multidevice/conftest.py`.

</details>

### Task 2 – Run the suite across the pod

The test functions are unchanged. Because the fixture is now parametrized, pytest
crosses each leaf with the existing interface and counter parameters.

1. Run the whole folder:

```bash
uv run pytest workspace/003_pytest/ -v
```

**Expected output:** every case is prefixed with its leaf, so a clean pod passes
once per leaf-and-field combination:

```
test_interface_status.py::test_interface_up[leaf1-Ethernet1] PASSED
test_interface_status.py::test_interface_up[leaf2-Ethernet1] PASSED
test_interface_status.py::test_interface_up[leaf3-Ethernet1] PASSED
...
```

<details>
<summary><b>Answer</b></summary>

**Question:** how many tests run now, and where did they come from?

The count is your earlier per-device total multiplied by the ten leaves in your
pod. You wrote no new tests: parametrizing the one fixture multiplied the whole
suite across the pod for free.

Answer key: `examples/003_pytest/007_multidevice/`.

</details>

### Task 3 – Drift the source of truth and re-validate the pod

`expected_state.yaml` is a single shared baseline: the same intended state is
asserted against every leaf. Editing it re-checks the whole pod in one run, and
because each leaf reports independently you can read exactly which leaves match.

1. In `expected_state.yaml`, drift the intended status from `up` to `down`. You
   are changing intent only; the network is untouched.

2. Re-run the suite.

**Expected output:** every leaf's status case now fails, each named on its own
line, while the counter cases still pass:

```
test_interface_up[leaf1-Ethernet1] FAILED
test_interface_up[leaf2-Ethernet1] FAILED
test_interface_up[leaf3-Ethernet1] FAILED
...
```

3. Set the status back to `up` and re-run to confirm a green pod.

<details>
<summary><b>Answer</b></summary>

**Question:** why did every leaf fail, not just one?

Because the baseline is shared, so drifting it drifts the intent for the whole
pod at once. Each leaf is still judged on its own line, so if a single leaf ever
drifted *for real* against an unchanged baseline, only that leaf's cases would go
red, the rest staying green. That is the per-device isolation parametrize buys
you, now applied across the fleet.

Answer key: `examples/003_pytest/007_multidevice/expected_state.yaml`.

</details>

> 🎉 **CONGRATULATIONS!**
> You have built a pytest validation suite that reads live network state over an
> API, reshapes it with JSONata, asserts operational state against an intended
> source of truth, and fans across every leaf in your pod, with an Allure report
> ready for CI.
