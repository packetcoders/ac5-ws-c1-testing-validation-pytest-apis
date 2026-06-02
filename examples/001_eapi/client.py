"""A small eAPI client, provided for you to read and reuse.
"""

import requests
import urllib3

# Lab certs are self-signed, so requests warns on every call. Silence it once
# here so example output stays readable.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EApiClient:
    """Issue eAPI commands against one device and return parsed JSON results."""

    def __init__(self, host, username, password, timeout=10):
        # __init__ just stores configuration; no network call happens yet.
        self.url = f"https://{host}/command-api"
        self.auth = (username, password)
        self.timeout = timeout

    def run(self, cmds):
        """POST a list of CLI commands; return the list of per-command results."""
        payload = {
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": {"version": 1, "cmds": cmds, "format": "json"},
            "id": 1,
        }
        response = requests.post(
            self.url,
            json=payload,
            auth=self.auth,
            verify=False,
            timeout=self.timeout,
        )
        response.raise_for_status()
        # result is a list, one entry per command in the same order as cmds.
        return response.json()["result"]
