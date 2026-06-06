"""Inventory helpers for the multi-device tests (provided - no need to edit).

Kept local to this example so the folder is self-contained:

    load_yaml(path)            - read the YAML inventory into Python objects.
    pod_devices(inv, sid=None) - the inventory entries that share your pod.

Each device in devices.yaml carries a `pod`, so finding your pod is a plain
data lookup: read the pod off your own device, then keep every device with a
matching pod. The lab injects STUDENT_ID as the last octet of your device's IP
(101-170), so your device is at 172.29.165.<STUDENT_ID>.
"""

import os

import yaml


def load_yaml(path):
    """Read a YAML file and return its contents."""
    with open(path) as file:
        return yaml.safe_load(file)


def pod_devices(inventory, student_id=None):
    """Return the inventory entries that share this student's pod.

    student_id defaults to the STUDENT_ID environment variable the lab injects.
    """
    if student_id is None:
        student_id = int(os.environ["STUDENT_ID"])

    my_host = f"172.29.165.{student_id}"

    my_pod = next(device["pod"] for device in inventory if device["host"] == my_host)
    return [device for device in inventory if device["pod"] == my_pod]
