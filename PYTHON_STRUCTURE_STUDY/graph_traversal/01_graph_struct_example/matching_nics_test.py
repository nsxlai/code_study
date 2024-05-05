import re
import time
from typing import List
from pprint import pformat
from havoc.autoval.lib.test_utils.network.iperf_node import IperfNode
from havoc.autoval.lib.test_utils.network.nic_test_base import NICTestBase
from havoc.autoval.lib.test_utils.network.nic_interface import NICInterface
from havoc.autoval.lib.test_utils.network.iperf_traffic_log import Filter


class MatchingNICTest(NICTestBase):
    """
    Serve traffic between matching NIC interfaces of two hosts of the same type.
        e.g.: eth1 Host1 --> eth1 Host2, etc.
    Command iperf3 is used to simulate network traffic.
    Each iperf process can be bound to a cpu using the `numactl` command.
    """

    def setup(self):
        super(MatchingNICTest, self).setup()
        self.validate_less_equal(
            len(self.iperf_nodes),
            2,
            "Testing matching NICs on two hosts of same type",
            log_on_pass=False,
        )
        self.log_info("Adding required routes and kill existing iperf processes...")
        for node in self.iperf_nodes:
            self.add_preferred_routes(node)
        node1, node2 = self.iperf_nodes
        self.check_matching_eths(node1, node2)

    def get_preferred_routes(self, node: IperfNode) -> List[str]:
        routes = []
        for nic in node.nic_interfaces:
            ip6 = nic.ip6
            gw = node.gateway_ip6
            routes.append(
                (
                    f"default from {ip6} via {gw}"
                    f" dev {nic.name} metric 1024 pref medium"
                )
            )
        return routes

    def add_preferred_routes(self, node: IperfNode):
        # Add a dedicated route for each NIC interface
        routes = self.get_preferred_routes(node)
        for route in routes:
            node.add_route(route)
        routing_table = node.get_routing_table()
        for route in routes:
            self.validate_condition(
                re.search(route, routing_table),
                f"<{route}> added to {node.hostname}'s routing table",
                log_on_pass=False,
            )

    def execute(self):
        client, server = self.iperf_nodes
        bind_numa = self.test_control.get("bind_numa", False)
        traffic = []
        for client_nic in client.nic_interfaces:
            server_nic = server.get_nic_interface(client_nic.name)
            traffic.extend(
                self.start_traffic(
                    client,
                    server,
                    client_nic=client_nic,
                    server_nic=server_nic,
                    bi_dir=True,
                    bind_numa=bind_numa,
                    misc_server_args=self.misc_server_args,
                    misc_client_args=self.misc_client_args,
                )
            )
        self.wait_for_traffic(traffic, delay=self.runtime)
        self.validate_bandwidth()

    def check_matching_eths(self, node1: IperfNode, node2: IperfNode):
        for interface in node1.nic_interfaces:
            intf_name = interface.name
            self.validate_condition(
                node2.get_nic_interface(intf_name) is not None,
                f"Both {node1.hostname} and {node2.hostname} have {intf_name}.",
                log_on_pass=False,
            )

    def delete_preferred_routes(self, node: IperfNode):
        for route in self.get_preferred_routes(node):
            node.remove_route(route)
            self.validate_condition(
                not re.search(route, node.get_routing_table()),
                f"Removed <{route}> from {node.hostname}'s routing table",
                log_on_pass=False,
            )

    def validate_bandwidth(self):
        for node in self.iperf_nodes:
            self.log_info(f"Validating {node.hostname} NICs bandwidth")
            for nic in node.nic_interfaces:
                self.validate_nic_bandwidth(nic)

    def validate_nic_bandwidth(self, nic: NICInterface):
        expected_bandwidth = nic.get_expected_speed()
        query = [
            Filter("client", "=", nic.hostname),
            Filter("client_nic", "=", nic.name),
        ]
        actual_bandwidth, _ = self.traffic_log.compute_bandwidth(
            query=query,
            iperf_version=self.iperf_version,
            log_dir=self.iperf_log_dir,
        )
        actual_bandwidth = actual_bandwidth.convert_to(expected_bandwidth.unit)
        pass_ratio = self.test_control.get(
            "pass_bandwidth_ratio", self.DEFAULT_BW_PASS_RATIO
        )
        actual_ratio = actual_bandwidth / expected_bandwidth
        self.validate_greater_equal(
            actual_ratio,
            pass_ratio,
            (
                f" {actual_bandwidth}, is at least {pass_ratio * 100}%"
                f" of expected bandwidth {expected_bandwidth}"
            ),
            raise_on_fail=False,
        )

    def cleanup(self):
        self.log_info("Removing added routes from routing table...")
        for node in self.iperf_nodes:
            self.delete_preferred_routes(node)
            node.kill_all_iperf_proc()
        super(MatchingNICTest, self).cleanup()


def main():
    test = MatchingNICTest()
    test.lifecycle()


if __name__ == "__main__":
    main()
