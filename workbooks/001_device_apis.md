# Workbook 1: Device APIs with eAPI

## Learning Objectives

By the end of this workbook, you will be able to:

- Make a REST `GET` call with `requests` and parse the JSON response.
- Read the outcome of a call from its HTTP status code.
- Build a JSON-RPC request and `POST` a `show` command to Arista eAPI.
- Pull a field out of the nested eAPI `result`.
- Reuse a provided eAPI client and handle a failed call gracefully.

## Overview

Every test in this session reads device state, and every device exposes that
state through an API. This workbook starts at the network's edge: a plain REST
`GET` against a public sample endpoint so you see a request and response end to
end, then the real thing, Arista's eAPI, against your own lab leaf. eAPI is a
JSON-RPC interface: you `POST` a list of CLI commands and get back structured
JSON instead of screen-scraped text. The workbook closes
with a small client class that wraps the call, the same client every later
workbook reuses.

```
sample REST API                 Arista eAPI (your device)
───────────────                 ─────────────────────────
GET /sample/interfaces/         POST /command-api
flat JSON list                  JSON-RPC: {"cmds": ["show ..."]}
response.json()["interfaces"]   response.json()["result"][0]
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
  **New Terminal**, then start an interactive Python session from the repo root:

```bash
task shell
```

> **Note:** `task shell` opens IPython, an enhanced Python prompt. Type code at the
> `In [1]:` prompt and press Enter to run it. A multi-line block runs once you
> press Enter on a blank line after it. Every Task reuses this one session, so
> variables and imports carry forward.

## Exercise 1: Make a REST Call

A REST API is a request and a response over HTTP. The request names a resource
with a URL and an action with a verb; `GET` reads. The response carries a status
code (`200` means OK) and, almost always, a JSON body. Before touching a device,
call a public sample endpoint that returns an already-flat list of interface
records, so the only new thing is the HTTP round trip.

### Task 1 – GET the sample data

`requests.get(<url>)` sends a `GET` and returns a `Response`. The form of a
call that you keep is `<name> = requests.get(<url>, timeout=<seconds>)`.

1. Import the client and a pretty-printer:

```python
import requests
from rich import print as rprint
```

2. Store the sample URL:

```python
URL = "https://tools.packetcoders.io/api/v1/sample/interfaces/"
```

3. Send a `GET`, store the response in `response`, and print
   `response.status_code`.

**Expected output:**

```
200
```

<details>
<summary><b>Solution</b></summary>

```python
response = requests.get(URL, timeout=10)
rprint(response.status_code)
```

</details>

### Task 2 – Raise on errors, then parse the body

A `200` means the call worked. Rather than checking the code by hand every time,
`response.raise_for_status()` turns any non-2xx into an exception. Once you trust
the response, `response.json()` parses the body into Python dicts and lists.

1. Call `response.raise_for_status()` (it returns nothing on success).
2. Call `response.json()`, store it in `body`, and read the `interfaces` key
   into `interfaces`.
3. Print how many interfaces came back, then the name of the first one.

**Expected output:** a count, then the first interface name, for example:

```
5
GigabitEthernet0/0
```

<details>
<summary><b>Solution</b></summary>

```python
response.raise_for_status()
body = response.json()
interfaces = body["interfaces"]

rprint(len(interfaces))
rprint(interfaces[0]["name"])
```

</details>

## Exercise 2: Call eAPI on Your Device

The sample endpoint handed back a flat list. A real device returns a nested
JSON-RPC result instead. Now you build the JSON-RPC request in Python. Arista's
eAPI listens for an HTTPS `POST` at `/command-api`; the body names the CLI
commands to run and the format to return them in. This exercise calls your own
lab leaf.

### Task 1 – POST a show command

A JSON-RPC body has a fixed shape: `method` is always `runCmds`, and `params`
carries the `cmds` list and the `format`. The lab certificates are self-signed,
so the call passes `verify=False` and you silence the matching warning once.

1. Load your credentials and build the device URL:

```python
import os

import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOST = f"172.29.165.{os.getenv('STUDENT_ID')}"
URL = f"https://{HOST}/command-api"
```

2. Build the JSON-RPC payload for `show version`:

```python
PAYLOAD = {
    "jsonrpc": "2.0",
    "method": "runCmds",
    "params": {"version": 1, "cmds": ["show version"], "format": "json"},
    "id": 1,
}
```

3. `POST` it with your credentials, store the response, and call
   `raise_for_status()`.

**Expected output:** no output yet (a successful `POST` raises nothing). You read
the result in the next Task.

<details>
<summary><b>Solution</b></summary>

```python
response = requests.post(
    URL,
    json=PAYLOAD,
    auth=(os.getenv("DEVICE_USERNAME"), os.getenv("DEVICE_PASSWORD")),
    verify=False,
    timeout=10,
)
response.raise_for_status()
```

</details>

### Task 2 – Read a field from the result

The response body carries a `result` list with one entry per command, in the
same order you sent them. You sent a single command, so the entry you want is
`result[0]`.

1. Parse the body into `body` with `response.json()`.
2. Print the device's EOS version from `body["result"][0]["version"]`.

**Expected output:** your leaf's EOS version string, for example:

```
4.34.0F
```

<details>
<summary><b>Solution</b></summary>

```python
body = response.json()
rprint(body["result"][0]["version"])
```

</details>

### Task 3 – Handle a failed call

A call can fail before you ever see a `result`: the device may be unreachable
(`requests.exceptions.ConnectionError`) or reject your credentials (HTTP `401`,
raised by `raise_for_status()`). A `try` / `except` keeps the session alive and
tells you which happened.

1. Point at an address with nothing listening and wrap the call so the error is
   reported, not raised:

```python
BAD_URL = "https://172.29.165.254/command-api"

try:
    requests.post(BAD_URL, json=PAYLOAD, verify=False, timeout=3).raise_for_status()
except requests.exceptions.RequestException as error:
    rprint(f"call failed: {type(error).__name__}")
```

**Expected output:** a single line naming the failure, for example:

```
call failed: ConnectionError
```

<details>
<summary><b>Answer</b></summary>

**Question:** why catch `requests.exceptions.RequestException` rather than
`ConnectionError` alone?

`RequestException` is the base class for every error `requests` raises:
connection failures, timeouts, and the HTTP errors from `raise_for_status()`.
Catching the base handles all of them with one `except`, so an auth `401` and an
unreachable host are both reported instead of crashing the suite.

</details>

## Exercise 3: Reuse the Provided eAPI Client

Building that payload by hand every time is noise. A small client class is
provided so the rest of the session stays focused on testing, not plumbing. You
read it rather than write it, then reuse it. It lives at
`examples/001_eapi/003_client.py`.

### Task 1 – Read the client

Open `examples/001_eapi/003_client.py` in the lab editor. It is the call you
just made, wrapped in a class.

```python
class EApiClient:
    def __init__(self, host, username, password, timeout=10):
        self.url = f"https://{host}/command-api"
        self.auth = (username, password)
        self.timeout = timeout

    def run(self, cmds):
        payload = {
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": {"version": 1, "cmds": cmds, "format": "json"},
            "id": 1,
        }
        response = requests.post(
            self.url, json=payload, auth=self.auth,
            verify=False, timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["result"]
```

**Question:** how much work does `__init__` do over the network?

<details>
<summary><b>Answer</b></summary>

None. `__init__` only stores configuration: the URL, the credentials, and the
timeout. No request is sent until you call `run()`. Building the client is free;
the network call happens once you ask it to run a command.

</details>

### Task 2 – Run a command with the client

`run(cmds)` takes a list of commands and returns the parsed `result` list, so the
payload and the `raise_for_status()` you wrote in Exercise 2 are now one method
call.

1. Paste the `EApiClient` class from Task 1 into your session so the name is
   defined (it is the same class shown above). Later workbooks copy it into a
   `conftest.py` the same way, exactly as `examples/003_pytest/006_eos_reporting/`
   does.

> **Note:** the client is copied into each consuming file rather than imported,
> because `examples/` is a folder of standalone scripts, not an installed
> package. Keeping the class self-contained is what lets a fixture drop it in.

2. Build a client for your device and run `show interfaces`:

```python
client = EApiClient(HOST, os.getenv("DEVICE_USERNAME"), os.getenv("DEVICE_PASSWORD"))
result = client.run(["show interfaces"])
```

3. Print the keys of the first result entry.

**Expected output:** the top-level keys of a `show interfaces` response,
including `interfaces`:

```
dict_keys(['interfaces'])
```

<details>
<summary><b>Solution</b></summary>

```python
result = client.run(["show interfaces"])
rprint(result[0].keys())
```

</details>

The `show interfaces` result is deeply nested: a dictionary keyed by interface
name, each value another dictionary of counters. That shape is awkward to write
tests against, which is exactly the problem the next workbook solves with
JSONata.
