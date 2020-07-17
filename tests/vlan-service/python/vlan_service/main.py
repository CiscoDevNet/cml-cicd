# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class DataServiceCallbacks(Service):
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        return


class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info("Service create(service=", service._path, ")")

        vars = ncs.template.Variables()
        vars.add("DUMMY", "127.0.0.1")
        template = ncs.template.Template(service)

        vlans = service.vlan

        for vlan in vlans:
            self.log.info(f"Looking at VLAN {vlan.vlanid} ({vlan.name})")
            vlan_vars = ncs.template.Variables()
            vlan_vars.add("VLAN_ID", vlan.vlanid)
            vlan_vars.add("VLAN_NAME", vlan.name)
            switches = root.switch_topology[service.topology].switch
            self.log.info(f"Switches = {switches}")

            for switch in switches:
                vlan_vars.add("DEVICE_NAME", switch.device)
                self.log.info(
                    f"Applying VLAN config to {switch.device} (VLAN ID: {vlan.vlanid}, VLAN Name: {vlan.name})"
                )
                template.apply("vlan-service-template", vlan_vars)
                trunks = []
                if switch.uplink_trunk:
                    trunks.append(switch.uplink_trunk)
                elif switch.uplink_trunk_name:
                    trunks.append(switch.uplink_trunk_name)

                if switch.downlink_trunk and len(switch.downlink_trunk) > 0:
                    trunks += switch.downlink_trunk
                elif switch.downlink_trunk_name and len(switch.downlink_trunk_name) > 0:
                    trunks += switch.downlink_trunk_name
                trunk_vars = ncs.template.Variables()
                trunk_vars.add("VLAN_ID", vlan.vlanid)
                trunk_vars.add("DEVICE_NAME", switch.device)
                for trunk in trunks:
                    trunk_vars.add("TRUNK_PORT", trunk)
                    self.log.info(
                        f"Adding VLAN {vlan.vlanid} to port {trunk} on {switch.device}"
                    )
                    template.apply("trunk-port-template", trunk_vars)


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info("Main RUNNING")

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service("vlan-service-servicepoint", ServiceCallbacks)
        self.register_service("switch-topology-servicepoint", DataServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info("Main FINISHED")
