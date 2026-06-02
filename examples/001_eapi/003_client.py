"""A small eAPI client, provided for you to read and reuse."""

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


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv
    from rich import print as rprint

    load_dotenv()

    DEVICE_USERNAME = os.getenv("DEVICE_USERNAME")
    DEVICE_PASSWORD = os.getenv("DEVICE_PASSWORD")
    HOST = f"172.29.165.{os.getenv('STUDENT_ID')}"

    # Example usage: run "show version" and print the hostname and version.
    client = EApiClient(HOST, DEVICE_USERNAME, DEVICE_PASSWORD)
    response = client.run(["show interfaces"])
    rprint(response)
