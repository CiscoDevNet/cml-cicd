#!/usr/bin/env python

from jinja2 import Environment, PackageLoader
import os
import time


def main():
    j2_env = Environment(loader=PackageLoader(__name__), trim_blocks=False)
    template = j2_env.get_template("topology.j2")

    with open("topology.yaml", "w") as fd:
        fd.write(
            template.render(
                CORE_IP_ADDRESS=os.environ["CORE_IP_ADDRESS"],
                DIST_IP_ADDRESS=os.environ["DIST_IP_ADDRESS"],
                ACCESS_IP_ADDRESS=os.environ["ACCESS_IP_ADDRESS"],
                SUBNET_MASK=os.environ["SUBNET_MASK"],
                TOPOLOGY_NAME=f"HQ Network (CI/CD Start: {time.ctime()})",
            )
        )


if __name__ == "__main__":
    main()
