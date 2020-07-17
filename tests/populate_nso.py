#!/usr/bin/env python
import ncs
import os
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main():
    topology = None
    devices = []

    with open("hq-topology.yaml") as fd:
        topology = load(fd, Loader=Loader)

    topo_name = topology["topology"]

    # Create the authgroup
    with ncs.maapi.single_write_trans("admin", topo_name) as t:
        root = ncs.maagic.get_root(t)
        root.devices.authgroups.group.create(topo_name)
        root.devices.authgroups.group[topo_name].default_map.create()
        root.devices.authgroups.group[topo_name].default_map.remote_name = os.environ["HQ_USERNAME"]
        root.devices.authgroups.group[topo_name].default_map.remote_password = os.environ["HQ_PASSWORD"]
        t.apply()

    # Add each device in the topology to NSO
    for device in topology["devices"]:
        with ncs.maapi.single_write_trans("admin", topo_name) as t:
            root = ncs.maagic.get_root(t)
            root.devices.device.create(device["name"])
            root.devices.device[device["name"]].address = device["address"]
            root.devices.device[device["name"]].authgroup = topo_name
            root.devices.device[device["name"]].device_type.cli.ned_id = device["ned_id"]
            root.devices.device[device["name"]].device_type.cli.protocol = "ssh"
            root.devices.device[device["name"]].ssh.host_key_verification = "none"
            root.devices.device[device["name"]].state.admin_state = "unlocked"
            t.apply()

        # Sync the config from each device
        with ncs.maapi.single_write_trans("admin", topo_name) as t:
            root = ncs.maagic.get_root(t)
            root.devices.device[device["name"]].sync_from()
            t.apply()

        # Build the switch-topology pseudo-service.
        with ncs.maapi.single_write_trans("admin", topo_name) as t:
            root = ncs.maagic.get_root(t)
            root.switch_topology.create(topo_name)
            root.switch_topology[topo_name].switch.create(device["name"])
            if device.get("uplink_trunk"):
                root.switch_topology[topo_name].switch[device["name"]].uplink_trunk = device["uplink_trunk"]

            if device.get("downlink_trunks"):
                for trunk in device["downlink_trunks"]:
                    root.switch_topology[topo_name].switch[device["name"]].downlink_trunk.create(trunk)

            t.apply()


if __name__ == "__main__":
    main()
