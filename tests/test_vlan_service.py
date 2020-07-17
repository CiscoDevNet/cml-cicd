#!/usr/bin/env python

from genie.testbed import load as tbload
import os
import json
import logging
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    devices = []
    vlans = []
    with open("hq-topology.yaml") as fd:
        devices = load(fd, Loader=Loader)["devices"]

    with open("hq-vlan-service.yaml") as fd:
        vlans = load(fd, Loader=Loader)["vlan"]

    device_details = {"devices": {}}
    for dev in devices:
        device_details["devices"][dev["name"]] = {
            "protocol": "ssh",
            "ip": dev["address"],
            "username": os.environ["HQ_USERNAME"],
            "password": os.environ["HQ_PASSWORD"],
            "os": dev["os"],
            "ssh_options": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
        }

    testbed = tbload(device_details)

    # Get the VLAN
    error_occurred = False
    for topo_dev in devices:
        log.info(f"Testing to {topo_dev['name']}...")
        d = testbed.devices[topo_dev["name"]]
        d.connect(
            learn_hostname=True, log_stdout=False, ssh_options="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
        )

        spantree = d.parse("show spanning-tree summary")
        num_trunks = 0
        if "uplink_trunk" in topo_dev:
            num_trunks += 1
        if "downlink_trunks" in topo_dev:
            num_trunks += len(topo_dev["downlink_trunks"])

        for vlan in vlans:
            vname = "VLAN%04d" % vlan["vlanid"]
            if int(spantree["mode"]["rapid_pvst"][vname]["forwarding"]) < num_trunks:
                log.error(
                    f"Spanning-tree test on {topo_dev['name']} for VLAN {vlan['vlanid']} failed: {json.dumps(spantree['mode']['rapid_pvst'][vname])}"
                )
                error_occurred = True

        d.disconnect()

    if error_occurred:
        log.error("At least one test failed!")
        exit(1)

    log.info("All tests passed!")


if __name__ == "__main__":
    main()
