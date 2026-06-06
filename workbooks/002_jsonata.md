# Workbook 2: Reshaping Responses with JSONata

## Learning Objectives

By the end of this workbook, you will be able to:

- Explain why a nested eAPI response is awkward to assert against.
- Write a JSONata expression that flattens a response into one record per interface.
- Rename device fields to the keys your tests will use.
- Filter records with a predicate and add a computed field.
- Run the same expression from Python with `jsonatapy`.

## Overview

The `show interfaces` result you pulled in Workbook 1 is nested: a dictionary
keyed by interface name, each value holding more dictionaries of counters buried
several levels down. A test wants the opposite shape, a flat list of records, one
per interface, with the fields it checks sitting at the top. JSONata is a small
expression language for exactly this: you write a query that walks the nested
JSON and emits the flat shape you want, renaming fields as you go. You draft the
query live in a browser validator, then run the identical expression in Python
with `jsonatapy` so it can drop straight into a test fixture later.

```
nested eAPI JSON                 JSONata query              flat records
───────────────                  ─────────────              ────────────
interfaces:                      interfaces.*.{             [
  Ethernet1:                       "name": **.name,           {"name": "Ethernet1",
    interfaceCounters:             "fcs_errors": **.fcsErrors  "fcs_errors": 0, ...},
      inputErrorsDetail:         }                            ...
        fcsErrors: 0                                         ]
```

## Before You Begin

- Open a session to your lab environment directly within your browser.
- The workshop repository is already cloned, with the Python environment
  installed via `uv`.
- A saved sample `show interfaces` response lives at
  `examples/002_jsonata/interfaces.json`. Exercise 1 runs entirely in the
  browser; Exercise 2 uses a terminal.
- The finished query lives at `examples/002_jsonata/query.jsonata`.

## Exercise 1: Flatten a Response in the Validator

The JSONata validator loads JSON on the left, takes an expression in the middle,
and shows the evaluated result on the right. Drafting the query here means you
see each change immediately before committing it to Python.

Open the validator:

`https://tools.packetcoders.io/jsonata-validator`

Load the sample response by pasting the contents of
`examples/002_jsonata/interfaces.json` into the input pane. Its shape is a single
`interfaces` object keyed by interface name:

```json
{
  "interfaces": {
    "Ethernet1": {
      "name": "Ethernet1",
      "lineProtocolStatus": "up",
      "interfaceCounters": {
        "inDiscards": 0,
        "inputErrorsDetail": {
          "runtFrames": 0, "rxPause": 0, "fcsErrors": 0,
          "alignmentErrors": 0, "giantFrames": 0, "symbolErrors": 0
        }
      }
    },
    "Ethernet2": { "...": "..." }
  }
}
```

### Task 1 – Select every interface

`interfaces.*` reads the value of every key under `interfaces`, turning the
name-keyed object into a sequence of interface objects. This is the step that
drops the interface-name layer so the result becomes a list.

1. In the expression box, type:

```
interfaces.*
```

**Expected output:** an array of the interface objects (Ethernet1, Ethernet2,
Ethernet3, ...), no longer keyed by name.

<details>
<summary><b>Answer</b></summary>

**Question:** where did the interface names go?

`interfaces.*` keeps the *values* and discards the *keys*, so the names are gone
from the structure. You bring each name back as a field in the next Task with
`**.name`, which reads the `name` value that lives inside each object.

</details>

### Task 2 – Build one flat record per interface

`<sequence>.{ "<key>": <path>, ... }` maps each item in the sequence to a new
object. Inside the braces, `**.fieldName` searches downward for `fieldName` at
any depth, so you can pull a deeply nested counter up to the top level and give
it the snake_case name your tests expect.

1. Replace the expression with a mapping that emits `name` and the error
   counters, renaming each device field to snake_case:

```
interfaces.*.{
    "name": **.name,
    "runt_frames": **.runtFrames,
    "rx_pause": **.rxPause,
    "fcs_errors": **.fcsErrors,
    "alignment_errors": **.alignmentErrors,
    "giant_frames": **.giantFrames,
    "symbol_errors": **.symbolErrors,
    "in_discards": **.inDiscards
}
```

**Expected output:** one flat object per interface, each with `name` and seven
counter fields at the top level, for example Ethernet2 showing its non-zero
counters:

```json
{
  "name": "Ethernet2",
  "runt_frames": 5,
  "rx_pause": 0,
  "fcs_errors": 22,
  "alignment_errors": 3,
  "giant_frames": 1,
  "symbol_errors": 6,
  "in_discards": 12
}
```

<details>
<summary><b>Solution</b></summary>

The expression above is the core flat-record mapping. You add a `status` field in
Task 4 to reach the finished query that matches `examples/002_jsonata/query.jsonata`.
`**.fcsErrors` reaches `interfaceCounters.inputErrorsDetail.fcsErrors` without you
naming every level, and the quoted key `"fcs_errors"` renames it on the way out.

</details>

### Task 3 – Filter to the interfaces that have errors

A test often cares only about the interfaces with a problem. A predicate in square
brackets, `<sequence>[<condition>]`, keeps only the items where the condition is
true. Applied to your flat records, it filters by the snake_case names you just
created.

1. Wrap your Task 2 mapping in parentheses and append a predicate that keeps only
   interfaces whose `fcs_errors` are non-zero:

```
(interfaces.*.{
    "name": **.name,
    "runt_frames": **.runtFrames,
    "rx_pause": **.rxPause,
    "fcs_errors": **.fcsErrors,
    "alignment_errors": **.alignmentErrors,
    "giant_frames": **.giantFrames,
    "symbol_errors": **.symbolErrors,
    "in_discards": **.inDiscards
})[fcs_errors > 0]
```

**Expected output:** only `Ethernet2` survives, the one interface with errors in
the sample:

```json
{
  "name": "Ethernet2",
  "runt_frames": 5,
  "rx_pause": 0,
  "fcs_errors": 22,
  "alignment_errors": 3,
  "giant_frames": 1,
  "symbol_errors": 6,
  "in_discards": 12
}
```

**Note:** you will *not* keep this filter in the finished query. The tests in
Workbook 3 assert on every interface, so the query they consume returns them all.
Filtering is a tool to reach for when a check only wants the interfaces in a
certain state.

### Task 4 – Add the interface status

The tests also check whether each interface is up, so the records need a `status`
field. Unlike the counters, `lineProtocolStatus` sits at the top of each interface
object, so it is a direct field reference with no `**` search needed.

1. Drop the filter from Task 3 and add a `status` field to the mapping, reading
   `lineProtocolStatus` directly:

```
interfaces.*.{
    "name": **.name,
    "status": lineProtocolStatus,
    "runt_frames": **.runtFrames,
    "rx_pause": **.rxPause,
    "fcs_errors": **.fcsErrors,
    "alignment_errors": **.alignmentErrors,
    "giant_frames": **.giantFrames,
    "symbol_errors": **.symbolErrors,
    "in_discards": **.inDiscards
}
```

**Expected output:** every record now carries a `status`, for example `Ethernet3`,
which is down in the sample:

```json
{
  "name": "Ethernet3",
  "status": "down",
  "runt_frames": 0,
  "rx_pause": 0,
  "fcs_errors": 0,
  "alignment_errors": 0,
  "giant_frames": 0,
  "symbol_errors": 0,
  "in_discards": 0
}
```

This is now the finished query. It matches `examples/002_jsonata/query.jsonata`
exactly, and it is the same expression the later sections run live against your
pod.

The remaining tasks step beyond flatten-and-rename. None of them changes the
query the tests consume; each is a JSONata technique worth knowing for when a
check wants the data in a different shape.

### Task 5 – Roll the counters into one number

A check that only asks "any errors at all?" wants a single field, not seven.
`$sum([...])` adds the values of an array, so you can total the counters into one
`total_errors` field.

1. Total the error counters per interface:

```
interfaces.*.{
    "name": **.name,
    "total_errors": $sum([**.runtFrames, **.fcsErrors, **.alignmentErrors, **.giantFrames, **.symbolErrors])
}
```

**Expected output:** one rollup per interface; only `Ethernet2` is non-zero:

```json
[
  {"name": "Ethernet1", "total_errors": 0},
  {"name": "Ethernet2", "total_errors": 37},
  {"name": "Ethernet3", "total_errors": 0}
]
```

<details>
<summary><b>Answer</b></summary>

**Question:** would you assert against `total_errors` or the individual counters?

Both have a place. `total_errors == 0` is a fast single gate for "is this interface
clean"; the per-counter fields tell you *which* error fired when it is not. The
query the tests consume keeps the individual counters; reach for a rollup when a
check only needs the yes or no.

</details>

### Task 6 – Turn raw state into a pass/fail flag

A conditional, `<condition> ? <then> : <else>`, computes a value from the data.
Use it to derive a boolean verdict rather than carrying the raw status string.

1. Add an `alert` flag that is true whenever an interface is not up:

```
interfaces.*.{
    "name": **.name,
    "alert": lineProtocolStatus = "up" ? false : true
}
```

**Expected output:** `Ethernet3`, which is down, is the only one flagged:

```json
[
  {"name": "Ethernet1", "alert": false},
  {"name": "Ethernet2", "alert": false},
  {"name": "Ethernet3", "alert": true}
]
```

<details>
<summary><b>Answer</b></summary>

**Question:** why compute a flag instead of comparing the string in the test?

Either works, but pushing the rule into the query keeps the test trivial: it
asserts `alert == false` and never has to know what counts as healthy. Moving
logic into the reshaping step is the same idea as renaming fields, the test just
reads the answer.

</details>

### Task 7 – Summarise the whole response

The tasks so far returned one record per interface. JSONata can also reduce the
entire response to a single summary object with `$count` and `$sum`.
`interfaces.**.fcsErrors` reaches every `fcsErrors` at any depth, and a predicate
counts a subset.

1. Build a one-object health summary:

```
{
    "interface_count": $count(interfaces.*),
    "total_fcs_errors": $sum(interfaces.**.fcsErrors),
    "down": $count(interfaces.*[lineProtocolStatus = "down"])
}
```

**Expected output:**

```json
{
  "interface_count": 3,
  "total_fcs_errors": 22,
  "down": 1
}
```

<details>
<summary><b>Answer</b></summary>

**Question:** when is a summary like this more useful than per-interface records?

For a top-level gate: a single assert that `total_fcs_errors == 0` or `down == 0`
fails the whole device fast, before you drill into which interface. Per-interface
records pinpoint; a summary triages.

</details>

## Exercise 2: Run the Same Query from Python

The expression you drafted in the browser runs unchanged in Python through
`jsonatapy`. That is the point of drafting it in the validator first: what you
see there is what a fixture will return.

### Task 1 – Evaluate the query with jsonatapy

`jsonatapy.evaluate(<expression>, <data>)` takes the expression as a string and
the parsed JSON as a Python object, and returns the flattened result as Python
lists and dicts. Start an interactive session from the repo root:

```bash
task shell
```

1. Load the sample response and the query:

```python
import json

import jsonatapy

with open("examples/002_jsonata/interfaces.json") as f:
    data = json.load(f)

with open("examples/002_jsonata/query.jsonata") as f:
    query = f.read()
```

2. Evaluate the query against the data, store the result in `records`, and print
   how many records came back.

**Expected output:**

```
3
```

<details>
<summary><b>Solution</b></summary>

```python
records = jsonatapy.evaluate(query, data)
print(len(records))
```

</details>

### Task 2 – Confirm the records are ready to assert against

A flat record with named fields is something a test can index directly, which is
what every test in Workbook 3 does.

1. Print the first record, then read its `fcs_errors` field on its own.

**Expected output:** a flat dict followed by its `fcs_errors` value, for example:

```
{'name': 'Ethernet1', 'status': 'up', 'runt_frames': 0, 'rx_pause': 0, 'fcs_errors': 0, 'alignment_errors': 0, 'giant_frames': 0, 'symbol_errors': 0, 'in_discards': 0}
0
```

<details>
<summary><b>Solution</b></summary>

```python
print(records[0])
print(records[0]["fcs_errors"])
```

</details>

The records are now a plain list of dicts with the field names your tests will
assert on. In Workbook 3 this exact `jsonatapy.evaluate(...)` call moves into a
pytest fixture, so a live device response arrives at your tests already flattened.
