# Workbook 3: Building a Validation Suite

## Learning Objectives

By the end of this workbook, you will be able to:

- Load intended state from the YAML inventory into a session fixture.
- Load operational state from eAPI into a session fixture.
- Write parametrized tests that diff intended against operational.
- Run the suite against the live lab and against captured payloads.
- Read a failure message and trace it back to the field that drifted.

## Overview

Pytest is the runner (Workbook 1). eAPI is the data source (Workbook 2).
This workbook combines them into the validation suite the rest of the
session was building towards. The shape of every test is the same: one side
of the assertion comes from the inventory (intended), the other side from
eAPI (operational), and the assertion succeeds when the two agree.

```
inventory/  ──► load_intended_state() ──► intended (dict-per-host)
                                                              \
                                                               ── assert ==
                                                              /
eAPI    ──► load_operational_state() ──► operational (dict-per-host)
```

## Before You Begin

- Open a session to your lab environment directly within your browser.
- The workshop repository is already cloned, with the Python environment
  installed via `uv`.
- The `final-project/.env` file from Workbook 2 holds your lab credentials.
- The captured payloads in `data/api_responses/` already exist; the suite
  uses them when run with `--offline`.
- Workbook 3 is delivered as file editing: you write tests under
  `workspace/003_validation_suite/` and run them with `pytest --offline`.
- The complete answer key is in `examples/003_validation_suite/` and the
  full production suite is in `tests/`.

> **Note:** The `conftest.py` at the repo root already wires the `intended`,
> `clients`, and `operational` fixtures, so any test under `workspace/`
> or `tests/` that names them as parameters receives them.

## Exercise 1: Read the State Fixtures

The session-scoped fixtures in `conftest.py` do the heavy lifting: they
load the inventory and call eAPI once per pytest run, then hand the same
dicts to every test that asks for them. Reading those fixtures first
makes the diff tests in Exercise 2 easy to write.

### Task 1 – Inspect the intended state fixture

1. Open `conftest.py` at the repo root. Find the `intended` fixture and read
   it. It calls `load_intended_state()` from `final-project/state.py`.
2. Open `final-project/state.py` and read `load_intended_state()`. It loads
   `inventory/hosts.yaml` and `inventory/groups.yaml`, merges group data
   into per-host data, and returns one dict per host keyed by name.
3. From the workshop root, drop into a quick IPython session and call it
   directly:

```bash
task shell
```

```python
import sys
sys.path.insert(0, "final-project")
from state import load_intended_state

intended = load_intended_state()
list(intended.keys())
```

**Expected output:**

```
['rtr001', 'rtr002', 'rtr003', 'rtr004']
```

4. Inspect rtr001's intended state:

```python
intended["rtr001"]["loopback_ip"]
# '10.255.0.1/32'
[intf["name"] for intf in intended["rtr001"]["interfaces"]]
# ['Ethernet1']
intended["rtr001"]["bgp"]["peers"]
# [{'peer_ip': '10.0.12.2', 'remote_as': 65002}]
```

<details>
<summary><b>Solution</b></summary>

The four shell / Python lines in steps 3 and 4 are the verification. The
loader code is already in `final-project/state.py`; reading it is the goal,
not rewriting it.

</details>

### Task 2 – Inspect the operational state fixture

1. In the same IPython session, build an `OfflineClient` (so this runs without
   a live device) and call `load_operational_state()`:

```python
from client import OfflineClient
from state import load_operational_state

client = OfflineClient(hostname="rtr001")
operational = load_operational_state(client, "rtr001")

operational["loopback_ip"]
# '10.255.0.1/32'
[intf["name"] for intf in operational["interfaces"]]
# ['Ethernet1']
operational["bgp"]["peers"]
# [{'peer_ip': '10.0.12.2', 'remote_as': 65002, 'state': 'Established'}]
```

2. Confirm the keys on the operational dict match the keys on the intended
   dict: `loopback_ip`, `interfaces`, `bgp`.

**Question:** the two dicts have the same keys but the operational dict was
built from eAPI JSON. Where did that shape come from?

<details>
<summary><b>Answer</b></summary>

From `load_operational_state()` in `final-project/state.py`. The function
issues three eAPI commands (`show version`, `show interfaces`, `show ip bgp
summary`) and reshapes the raw responses into the same form as the intended
state. That reshape is what turns "device JSON" into "comparable state": both
sides of every assertion share the same keys, so the diff is one line of
Python.

</details>

## Exercise 2: Write the Diff Tests

A validation test is short. One side comes from `intended`, the other from
`operational`, both keyed by host. Parametrize over the host list and the
same test runs across the whole fleet.

### Task 1 – Diff the loopback IPs

1. Open `workspace/003_validation_suite/test_intended_vs_operational.py`.
2. Find `TODO 1` and complete `test_loopback_matches`:

```python
@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_loopback_matches(host, intended, operational):
    assert (
        intended[host]["loopback_ip"]
        == operational[host]["loopback_ip"]
    ), (
        f"{host} loopback drift: "
        f"intended={intended[host]['loopback_ip']} "
        f"operational={operational[host]['loopback_ip']}"
    )
```

3. Run the test against the captured payloads:

```bash
uv run pytest workspace/003_validation_suite/ -v --offline
```

**Expected output:** four `PASSED` lines, one per host.

<details>
<summary><b>Solution</b></summary>

The code block in step 2 is the solution. The marker `intended_vs_operational`
is declared in `pyproject.toml`, so pytest does not warn about it.

</details>

### Task 2 – Diff intended interfaces against operational

`set` comparisons are the cleanest way to express "every intended thing
appears on the device". Build a set of `(name, ip_address)` pairs on each
side and assert the intended set is a subset of the operational set.

1. At `TODO 2`, complete `test_full_intended_interfaces_subset`:

```python
@pytest.mark.intended_vs_operational
@pytest.mark.parametrize("host", HOSTS)
def test_full_intended_interfaces_subset(host, intended, operational):
    intended_pairs = {
        (intf["name"], intf["ip_address"])
        for intf in intended[host]["interfaces"]
    }
    operational_pairs = {
        (intf["name"], intf["ip_address"])
        for intf in operational[host]["interfaces"]
    }
    missing = intended_pairs - operational_pairs
    assert not missing, f"{host}: missing intended interfaces {missing}"
```

2. Rerun the suite:

```bash
uv run pytest workspace/003_validation_suite/ -v --offline
```

**Expected output:** eight `PASSED` lines, four per test.

<details>
<summary><b>Solution</b></summary>

The block in step 1 is the solution. The `missing = intended_pairs -
operational_pairs` expression is the diff, and the assertion message lists
exactly which pairs failed to match, host by host.

</details>

### Task 3 – Run the live suite and read a failure

The production suite under `tests/` carries every check this session
teaches. Workbook 3 ends by running it for real and reading what the failure
output looks like when the network actually drifts.

1. Run the full live suite (it needs `.env` credentials):

```bash
uv run pytest tests/ -v
```

**Expected output:** ~40 `PASSED` lines covering facts, interfaces, and BGP.

2. Run the same suite against the captured payloads:

```bash
uv run pytest tests/ -v --offline
```

**Expected output:** the same set of tests, all `PASSED`, but no network was
touched.

3. Introduce a deliberate drift to see a failure: open
   `inventory/hosts.yaml`, change `rtr001`'s loopback to `10.255.0.99/32`,
   and rerun the suite in offline mode:

```bash
uv run pytest tests/test_interfaces.py -v --offline
```

**Expected output:** `test_loopback_ip_matches[rtr001]` fails with an
assertion message naming both sides of the drift, while the other three
hosts pass.

4. Revert the inventory change.

🎉 **CONGRATULATIONS!**
You have now built a working validation suite: pytest is the runner, eAPI is
the data source, and every test asserts the live network agrees with the
inventory. The same suite is what Session D1 will run as a CI gate, so a
deploy that produces drift fails the pipeline before it ships.

> **Tip:** When a real drift appears, fix the intent or fix the network, then rerun
> the suite. A clean run is what closes the deploy loop, the failing test is
> the audit trail of what was wrong.

<details>
<summary><b>Solution</b></summary>

The three shell commands plus the inventory edit and revert are the
solution. The failing-test message is the take-home: it names the host, the
field, and both sides of the drift. That same message is what an operator
sees in the CI summary in Session D1.

</details>
