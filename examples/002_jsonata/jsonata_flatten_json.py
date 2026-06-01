"""Example: flatten a nested eAPI response with JSONata.

`eapi_call.py` showed that a device returns deeply nested JSON: interfaces are
a dict keyed by name, and the error counters sit several levels down under
`interfaceCounters.inputErrorsDetail`. That shape is awkward to assert against.

JSONata is an expression language for querying and reshaping JSON. Build and
test the expression below interactively in the validator first, then run the
exact same expression here with `jsonatapy`:

    https://tools.packetcoders.io/jsonata-validator/s_sample_eapi/

Run from the workshop root:

    uv run examples/002_jsonata/jsonata_flatten_json.py
"""

import json
from pathlib import Path

import jsonatapy

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "interfaces.json").read_text())

# `interfaces.*` maps over each interface object; `**.<field>` reaches down to
# a field wherever it is nested, so the counters come up without naming every
# parent key. The result is one flat record per interface.
EXPRESSION = """interfaces.*.{
    "name": **.name,
    "runt_frames": **.runtFrames,
    "rx_pause": **.rxPause,
    "fcs_errors": **.fcsErrors,
    "alignment_errors": **.alignmentErrors,
    "giant_frames": **.giantFrames,
    "symbol_errors": **.symbolErrors,
    "in_discards": **.inDiscards
}"""

records = jsonatapy.evaluate(EXPRESSION, data)

for record in records:
    print(f"{record['name']:<12} fcs={record['fcs_errors']:<3} discards={record['in_discards']}")
# Ethernet1    fcs=0   discards=0
# Ethernet2    fcs=22  discards=12
# Ethernet3    fcs=0   discards=0

# Flat records are easy to filter: keep only the interfaces showing errors.
dirty = [r for r in records if r["fcs_errors"] > 0 or r["in_discards"] > 0]
print(f"\ninterfaces with errors: {[r['name'] for r in dirty]}")
# interfaces with errors: ['Ethernet2']
