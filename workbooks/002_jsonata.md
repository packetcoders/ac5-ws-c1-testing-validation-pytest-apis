# Workbook 2: Reshaping Responses with JSONata

## Learning Objectives

By the end of this workbook, you will be able to:

- Explain why a nested eAPI response is awkward to assert against.
- Write a JSONata expression that flattens a response into one record per interface.
- Rename device fields to the keys your tests will use.
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

The expression above is the finished query. It matches
`examples/002_jsonata/query.jsonata` exactly. `**.fcsErrors` reaches
`interfaceCounters.inputErrorsDetail.fcsErrors` without you naming every level,
and the quoted key `"fcs_errors"` renames it on the way out.

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
{'name': 'Ethernet1', 'runt_frames': 0, 'rx_pause': 0, 'fcs_errors': 0, 'alignment_errors': 0, 'giant_frames': 0, 'symbol_errors': 0, 'in_discards': 0}
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
