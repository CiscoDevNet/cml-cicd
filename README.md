# CML CI/CD Pipeline

## Introduction

NetDevOps seems to be all the rage these days.  NetDevOps is the application of DevOps principles and tools to networking -- specifically configuration and operations.  Part of this approach involves a practice known as Infrastructure as Code (IaC) whereby network configuration is done in a similar manner to writing code.  That is, you commit your configuration changes (or abstracted instances thereof) to a version control system, which then triggers some automation to [hopefully] test, and then deploy the configuration into production.  This whole system forms a Continuous Integration / Continuous Development (CI/CD) pipeline.

This repo contains an example of this testing portion of the IaC pipeline.  It is built using [Drone](https://drone.io) with Drone's [Docker](https://docs.drone.io/runner/docker/overview/) runner.  The network configuration deployment is done using [Network Services Orchestrator](https://developer.cisco.com/site/nso/) (NSO), and the network itself is hosted as a virtual lab within [Cisco Modeling Labs](https://developer.cisco.com/modeling-labs) (CML).  The testing part is done using [pyATS](https://developer.cisco.com/pyats/).

## How It Works

In this repo, there are three YAML files: `hq-topology.yaml`, `hq-vlan-service.yaml`, and `drone.yml`.  The `hq-topology.yaml` file defines a simple three-tiered switch topology, and the `hq-vlan-service.yaml` defines a set of VLANs to be deployed into this topology.  The idea is that when you change either of these files, that will kick off the Drone runner to execute a test pipeline that is defined in the `drone.yaml` file.  The Drone workflow will do the following:

1. Start NSO in the runner's Docker container
2. Fetch the new version of the [virlutils](https://github.com/CiscoDevNet/virlutils) utility, which allows CLI access to Cisco Modeling Labs via its powerful REST API
3. Spins up a CML topology based on `hq-topology.yaml`
4. Populates NSO with the virtual test devices
5. Configures the new VLAN service into NSO, which pushes the device configuration to the virtual devices
6. Tests that the VLAN service was properly deployed using pyATS
7. Cleans up CML when it's all done

All of these steps are controlled by the various scripts and files found in the `tests` subdirectory.



