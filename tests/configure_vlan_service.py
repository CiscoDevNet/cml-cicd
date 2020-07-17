#!/usr/bin/env python

import requests
import os
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main():
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }
    service = None

    with open("hq-vlan-service.yaml") as fd:
        service = load(fd, Loader=Loader)

    # Wrap the service in the YAML file with namespaces.
    vlan_service = {"vlan-service:vlan-service": [service]}

    try:
        # Use RESTCONF to deploy the VLAN service to NSO
        r = requests.request(
            "POST",
            "http://127.0.0.1:8080/restconf/data",
            headers=headers,
            json=vlan_service,
            auth=(os.environ["NSO_USERNAME"], os.environ["NSO_PASSWORD"]),
        )
        r.raise_for_status()
    except Exception as e:
        print(f"ERROR: Failed to create VLAN service: '{getattr(e, 'message', repr(e))}'")
        print(r.text)
        exit(1)

    print(f"VLAN Service {service['name']} created successfully.")


if __name__ == "__main__":
    main()
