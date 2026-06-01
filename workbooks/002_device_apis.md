# Workbook 2: Working with Device REST APIs

## Learning Objectives

By the end of this workbook, you will be able to:

- POST a JSON-RPC call to the Arista eAPI with `requests`.
- Parse the response and pull individual fields from the result.
- Handle non-2xx responses and command-level errors.
- Wrap the calls in a small client class.
- Swap the live client for an offline replay client.

## Overview

Pytest gives you a runner. eAPI gives the runner something real to assert
against. eAPI is Arista's JSON-RPC interface: you POST a list of CLI commands
in a JSON body to `/command-api`, and the device replies with a list of
parsed results, one per command. The same flow works for any HTTP-based
device API; eAPI is the one in front of you in this lab.

```
   request body                       response body
{                                   {
  "method": "runCmds",     ─POST─►    "result": [
  "params": {                          {"hostname": "rtr001", ...}
    "cmds": ["show version"]         ],
  }                                   "id": 1
}                                   }
```

## Before You Begin

- Open a session to your lab environment directly within your browser.
- The workshop repository is already cloned, with the Python environment
  installed via `uv`.
- Copy the credential template and add your lab credentials:

```bash
cp final-project/.env.example final-project/.env
```

| Variable | Value |
|----------|-------|
| `DEVICE_USERNAME` | Enter your lab username. |
| `DEVICE_PASSWORD` | Enter your lab password. |

- Open a terminal and start an interactive Python session:

```bash
task shell
```

> **Note:** Your username and password would have been supplied to you previously.

> **Warning:** The lab uses self-signed certificates, so `requests` will warn on every
> call. This workbook calls `urllib3.disable_warnings()` to silence the
> noise; never disable verification on a production endpoint.

## Exercise 1: Call eAPI by Hand

The eAPI endpoint is `https://<device>/command-api`. The body is a JSON-RPC
2.0 envelope: a `method` (always `runCmds`), `params` (the command list and
the format), and an `id`. The response is the same shape with a `result`
list, one entry per command.

### Task 1 – POST a JSON-RPC body and read the response

`requests.post(url, json=..., auth=..., verify=False)` sends the request,
adds HTTP Basic auth, and accepts the self-signed cert.
`response.raise_for_status()` turns a 4xx / 5xx into an exception you can
catch. `response.json()` parses the JSON body into Python dicts and lists.

1. At the IPython prompt, suppress the self-signed cert warning and load the
   credentials:

```python
import os
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv("final-project/.env")

USERNAME = os.getenv("DEVICE_USERNAME")
PASSWORD = os.getenv("DEVICE_PASSWORD")
```

2. Build the JSON-RPC body and POST it to `rtr001`:

```python
payload = {
    "jsonrpc": "2.0",
    "method": "runCmds",
    "params": {"version": 1, "cmds": ["show version"], "format": "json"},
    "id": 1,
}
response = requests.post(
    "https://172.29.163.101/command-api",
    json=payload,
    auth=(USERNAME, PASSWORD),
    verify=False,
    timeout=10,
)
response.raise_for_status()
```

3. Inspect the parsed response:

```python
body = response.json()
list(body.keys())
```

**Expected output:**

```
['jsonrpc', 'result', 'id']
```

<details>
<summary><b>Solution</b></summary>

The code in steps 1 and 2 is the solution; step 3 is the verification. If
`raise_for_status()` raises, check the credentials in `.env`.

</details>

### Task 2 – Pull the hostname and version from the result

`body["result"]` is a list, one entry per command. `show version` returns a
dict with `hostname`, `version`, `model`, and several other facts.

1. Pull the single result out of the list:

```python
[version] = body["result"]
```

2. Print the hostname and EOS version:

```python
print(version["hostname"], version["version"])
```

**Expected output:**

```
rtr001 4.28.0F
```

3. Issue two commands in one call and walk both results:

```python
payload["params"]["cmds"] = ["show version", "show ip bgp summary"]
body = requests.post(
    "https://172.29.163.101/command-api",
    json=payload, auth=(USERNAME, PASSWORD), verify=False, timeout=10,
).json()

version, bgp = body["result"]
print(version["hostname"])
print(list(bgp["vrfs"]["default"]["peers"]))
```

**Expected output:**

```
rtr001
['10.0.12.2']
```

<details>
<summary><b>Solution</b></summary>

```python
[version] = body["result"]
print(version["hostname"], version["version"])

payload["params"]["cmds"] = ["show version", "show ip bgp summary"]
body = requests.post(
    "https://172.29.163.101/command-api",
    json=payload, auth=(USERNAME, PASSWORD), verify=False, timeout=10,
).json()
version, bgp = body["result"]
print(version["hostname"])
print(list(bgp["vrfs"]["default"]["peers"]))
```

</details>

### Task 3 – Handle a bad command

When a command fails, eAPI returns a `200` HTTP status but puts an `error`
key in the JSON body. A robust caller checks for that key and raises.

1. Send a deliberately invalid command:

```python
payload["params"]["cmds"] = ["show nonsense"]
response = requests.post(
    "https://172.29.163.101/command-api",
    json=payload, auth=(USERNAME, PASSWORD), verify=False, timeout=10,
)
body = response.json()
"error" in body
```

**Expected output:**

```
True
```

2. Inspect the error details:

```python
body["error"]["data"][0]["errors"]
```

**Expected output:**

```
["Invalid input ..."]
```

**Question:** the HTTP status was `200` even though the command failed. Why
does eAPI not return a 4xx in that case?

<details>
<summary><b>Answer</b></summary>

The HTTP layer succeeded: the request reached the device, the device parsed
it, and it replied. The failure was at the JSON-RPC layer: one of the
commands in the batch was not valid. eAPI signals that by putting an `error`
key in the JSON body instead of a `result` key. Callers must check both
layers: `raise_for_status()` for HTTP failures, an `"error" in body` check
for command failures.

</details>

## Exercise 2: Wrap the Calls in a Client

Repeating that JSON-RPC body for every call is noise. A small class captures
the URL, credentials, and `requests.Session()` in one place and exposes a
clean `.run(commands)` method. A second class with the same interface reads
captured payloads from disk: tests don't know (or care) which one is wired
in. Both live in `final-project/client.py`.

### Task 1 – Build the EApiClient class

1. Open `final-project/client.py` in the editor. The `EApiClient` and
   `OfflineClient` classes are complete. Read them.
2. Confirm `EApiClient.run(cmds)`:
   - builds the JSON-RPC body,
   - sends one `requests.post(...)` call with auth and `verify=False`,
   - raises on a non-2xx response,
   - raises on an `error` key in the body, and
   - returns `body["result"]`, a list.

**Question:** the class stores a `requests.Session()` in `__init__` rather
than calling `requests.post()` directly each time. Why?

<details>
<summary><b>Answer</b></summary>

A `Session` reuses a TCP connection between calls. When the validation suite
issues `show version`, `show interfaces`, and `show ip bgp summary` against
each of four devices, a fresh connection per call would be twelve TCP
handshakes (and twelve TLS handshakes on top). One session per host turns
that into four. Same correctness, less overhead.

</details>

### Task 2 – Run the same commands through both clients

1. In the IPython session, import both clients:

```python
import sys
sys.path.insert(0, "final-project")

from client import EApiClient, OfflineClient
```

2. Build an `EApiClient` for `rtr001` and run a command:

```python
live = EApiClient(
    hostname="rtr001",
    host_ip="172.29.163.101",
    username=USERNAME,
    password=PASSWORD,
)
[version] = live.run(["show version"])
print(version["hostname"])
```

**Expected output:**

```
rtr001
```

3. Build an `OfflineClient` for the same host and run the same command:

```python
offline = OfflineClient(hostname="rtr001")
[version] = offline.run(["show version"])
print(version["hostname"])
```

**Expected output:**

```
rtr001
```

4. Both clients returned a `result` list with the same structure. Confirm
   they accept the same multi-command call:

```python
results = offline.run(["show version", "show interfaces", "show ip bgp summary"])
len(results)
```

**Expected output:**

```
3
```

> **Tip:** `OfflineClient` reads from `data/api_responses/<host>_<slug>.json`. To
> capture a new command, call the live client once and write its result to
> the matching filename. Workbook 3 builds on that captured set.

<details>
<summary><b>Solution</b></summary>

The blocks of code in steps 2 to 4 are the solution. Both clients expose the
same `.run(cmds)` method and return the same shape, which is what makes
swapping them at the fixture layer (Workbook 3) effortless.

</details>
