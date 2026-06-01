# C1 Rebuild Punch-List

Remaining work after the examples/ restructure (2026-06-01). The examples tree
is sorted and the WB001/WB002/005-reporting examples are authored and passing.
The items below are the deferred harness + workbook rebuild.

## 1. Rebuild the end-state code (KEYSTONE — unblocks everything else)
`final-project/client.py` and `final-project/state.py` were **never committed**
(only stale `.pyc` remained). The root `conftest.py` and the whole `tests/`
suite import them, so `pytest` currently crashes at collection.

- [ ] **`999_final/client.py`** — online-only `EApiClient`. ⚠️ The root conftest
      calls `EApiClient(hostname=name, host_ip=data["hostname"], username=, password=)`,
      but the teaching client in `examples/001_eapi/client.py` is the simpler
      `EApiClient(host, username, password)`. Decide: make them match, or keep
      teaching=simple / end-state=inventory-driven and document why.
- [ ] **`999_final/state.py`**:
  - `load_intended_state()` — read `inventory/hosts.yaml` + `groups.yaml` +
    `defaults.yaml`, resolve group inheritance, return `{host: {...data, hostname}}`.
  - `load_operational_state(client, host)` — run the `show` commands and reshape
    the nested eAPI JSON into the intended shape (interfaces: name/ip_address/
    enabled; bgp.peers: peer_ip/remote_as/peerState). Natural place to reuse
    `jsonatapy` like `examples/002_jsonata/`.
- [ ] **Rewire `conftest.py`**: import from `999_final` not `final-project`;
      delete `OfflineClient`, the `--offline` option, the `offline` fixture, and
      the offline branch in the `clients` fixture.

## 2. `examples/003_pytest/004_sot/`
- [ ] Add `intended.yaml` (the SoT) + a local `conftest.py` providing `intended`
      and `operational` (inline, or wired to `999_final`).
- [ ] `test_intended_vs_operational.py` still has a stale docstring
      (`examples/003_validation_suite/`, `--offline`) and leans on the broken
      root fixtures — fix once item 1 lands.

## 3. `examples/003_pytest/005_reporting/`
- [ ] Authored and passing, but today must run with `--noconftest` because of the
      broken root conftest. Runs normally once item 1 is done.

## 4. final-project/ -> 999_final/ migration (approved, deferred — coupled to item 1)
- [ ] Move `final-project/.env.example` (its only tracked file) to the repo root
      (examples + `eapi_call.py` now load `ROOT/.env`), or into `999_final/`.
- [ ] Delete `final-project/`.
- [ ] Update `conftest.py` `.env` path + `sys.path` to the new location.
- [ ] Update the C1 legacy notes: `CONTENT_PLAN.md` (the "C1 predates this
      convention / final-project/" line) and `REPO_TEMPLATE.md §2`.

## 5. tests/ suite
- [ ] Verify `test_facts/interfaces/bgp` go green once item 1 exists.
- [ ] Confirm nothing still passes `--offline` (marker already removed from
      `pyproject.toml`).

## 6. Workbooks + workspace (separate pass)
- [ ] Workbook `.md` files are on the OLD ordering (`001_pytest_fundamentals`,
      `002_device_apis`, `003_validation_suite`) — re-author to the new plan
      (001 = eAPI/JSONata, 002 = pytest, 003 = validation) and to the new
      `examples/00N_*` paths; drop `final-project/` + `--offline` references.
- [ ] `workspace/` stubs mirror the old ordering — redo to match.

## 7. Housekeeping
- [ ] `.python-version` is pinned to **3.13** (jsonatapy 2.1.4 has no cp314
      wheel). Ensure the lab image uses 3.13.
- [ ] `data/api_responses/` was only used by `OfflineClient` — delete once
      offline is fully gone.
