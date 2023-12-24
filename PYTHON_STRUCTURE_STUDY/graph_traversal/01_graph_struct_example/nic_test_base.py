import time
from havoc.autoval.lib.test_utils.network.iperf_graph import IperfGraph, Topology
from havoc.autoval.lib.test_utils.network.nic_test_base import NICTestBase, Traffic
from havoc.autoval.lib.test_utils.network.nic_interface import NICInterface
from havoc.autoval.lib.test_utils.network.iperf_traffic_log import Filter
from havoc.autoval.lib.test_utils.network.iperf_node import IperfNode
from havoc.autoval.lib.test_utils.network.bandwidth import Bandwidth
from havoc.autoval.lib.utils.autoval_exceptions import TestError
from typing import List, Dict


class NICBufferFairness(NICTestBase):
    """
    This test takes in a graph and run iperf traffic between hosts in that graph

    Test control parameters:
        @type List[List[str]] graph: describe how iperf traffic should be directed
            between the hosts being tested. Using alphabet letters to denote hosts
                being tested.
            The number of distinct nodes in the graph should be equal to the number
                of hosts being tested.
            Example:
                [ ["a", "b"], ["b", "c"], ["b", "a"], ...  ] means these traffic will be
                    served simultaneously:
                    a (client) --> b (server),
                    b (client) --> c (server),
                    b (client) --> a (server), etc.
        @type List[List[List[str]]] topology: how nodes represented by alphabetic
            letters should be positioned relative to one another.
            This should be formatted as a list of racks of sleds:
                [
                    rack[sled[], sled[], ...],
                    ...
                ]
            Example:
                [
                    [['a', 'b', 'c', 'd'], ['e', 'f']],
                    [['g', 'h']]
                ]
                means nodes 'a' to 'f' belongs to a rack, with
                nodes 'a' to 'd' in a sled, and nodes 'e' and 'f' in
                another sled. Similarly, 'g' and 'h' are in the same sled,
                but not in the same rack as nodes 'a' to 'f'.
    Refer to NICTestBase for other test parameters
    """
    def __init__(self, *args, **kwargs) -> None:
        super(NICBufferFairness, self).__init__(*args, **kwargs)
        self.alphabet_topology = Topology([])
        self.node_topology = Topology([])
        self.node_hostname_map = {}
        self.graph = IperfGraph([], [], {})
        self.pass_bw_ratio = self.test_control.get("pass_bandwidth_ratio", .8)
        try:
            self.receivers = self.test_control["receivers"]
            self.recv1 = self.test_control["recv1"]
            self.sender1 = self.test_control["sender1"]
        except KeyError as e:
            raise TestError(f"Missing test params. Error: {e}")
        self.baseline_timestamp = 0
        self.baseline_bandwidth = Bandwidth(0)

    def setup(self) -> None:
        super(NICBufferFairness, self).setup()
        self.validate_in(
            "graph",
            self.test_control,
            "Must provide an iperf graph.",
            log_on_pass=False,
        )
        self.validate_in(
            "topology",
            self.test_control,
            "Must provide a topology for rack and sled mapping of nodes.",
            log_on_pass=False,
        )
        self.alphabet_topology = Topology(self.test_control["topology"])
        self.node_topology = Topology.get_topology(self.hosts)
        self.node_hostname_map = self._get_node_hostname_map()
        self.graph = IperfGraph(
            self.test_control.get("graph"),
            self.iperf_nodes,
            self.node_hostname_map,
        )

    def _get_node_hostname_map(self) -> Dict[str, str]:
        # Sort both topologies so their shapes can match
        self.alphabet_topology.sort()
        self.node_topology.sort()
        if not self.alphabet_topology == self.node_topology:
            raise TestError(
                "iperf nodes topology does not match letter topology."
                f"\nNode topology:\n{self.node_topology}"
                f"\nLetter topology:\n{self.alphabet_topology}"
            )
        return dict(zip(
            self.alphabet_topology.get_nodes(),
            self.node_topology.get_nodes()
        ))

    def execute(self):
        self.log_info(f"Test topology:\n\t{self.alphabet_topology}")
        self.log_info(f"Hosts actual topology:\n\t{self.node_topology}")
        _mapping = "\n\t".join([
            f"{letter} - {node}" for letter, node in self.node_hostname_map.items()
        ])
        self.log_info(f"Alphabet letter mappings:\n\t{_mapping}")
        traffic = self._start_sender1_recv1_traffic()
        self.wait_for_traffic(traffic)
        self.baseline_timestamp = int(time.time())
        self.baseline_bandwidth = self._get_baseline_bw()
        # give some distance between the baseline timestamp and stress timestamp
        time.sleep(2)

        iperf3_traffic = self.test_control.get("proc_per_traffic_list", None)
        if iperf3_traffic is not None:
            for p_traffic in iperf3_traffic:
                self.proc_per_traffic = p_traffic
                traffic = self.start_graph_traffic(self.graph)
                self.wait_for_traffic(traffic)
                self.validate_bandwidth()
        else:
            traffic = self.start_graph_traffic(self.graph)
            self.wait_for_traffic(traffic)
            self.validate_bandwidth()

    def _start_sender1_recv1_traffic(self):
        self.log_info(f"Starting baseline traffic from sender1 to recv1")
        sender1 = self._get_iperf_node_with_letter(self.sender1)
        recv1 = self._get_iperf_node_with_letter(self.recv1)
        return self.start_traffic(
            sender1,
            recv1,
            misc_server_args=self.test_control.get("misc_server_args", {}),
            misc_client_args=self.test_control.get("misc_client_args", {}),
            bind_numa=self.test_control.get("bind_numa", False),
        )

    def start_graph_traffic(self, graph: IperfGraph) -> List[Traffic]:
        # Run iperf traffic based on a graph structure
        # Entries in graph should be tuples of client, server pairs,
        # representing edges of the graph.
        traffic = []
        self.log_info(f"Running traffic from graph:\n{graph}")
        for client, server in graph:
            traffic.extend(
                self.start_traffic(
                    client,
                    server,
                    misc_server_args=self.test_control.get("misc_server_args", {}),
                    misc_client_args=self.test_control.get("misc_client_args", {}),
                    bind_numa=self.test_control.get("bind_numa", False),
                )
            )
        return traffic

    def validate_bandwidth(self) -> None:
        self._validate_sender1_recv1_bw()
        recv_nodes = [
            self._get_iperf_node_with_letter(letter) for letter in self.receivers
        ]
        for node in recv_nodes:
            for nic in node.nic_interfaces:
                self._validate_recv_bw(nic)

    def _validate_sender1_recv1_bw(self) -> None:
        recv1_nic = self._get_iperf_node_with_letter(
            self.recv1
        ).get_first_nic()
        stress_recv_bandwidth = self._get_recv_bw_after_baseline_traffic(recv1_nic)
        pct_change = (
            abs(stress_recv_bandwidth - self.baseline_bandwidth)
            / self.baseline_bandwidth
        ) * 100
        self.log_info(f"Baseline bandwidth to {recv1_nic}: {self.baseline_bandwidth}")
        self.log_info(f"Stress bandwidth to {recv1_nic}: {stress_recv_bandwidth}")
        self.log_info(
            "Bandwidth difference between baseline and stress:"
            f" {pct_change:.2f}%"
        )

    def _validate_recv_bw(self, nic: NICInterface) -> None:
        expected_bw = nic.get_expected_speed()
        actual_bw = self._get_recv_bw_after_baseline_traffic(nic)
        self.validate_greater_equal(
            actual_bw / expected_bw,
            self.pass_bw_ratio,
            (
                f"{nic} bandwidth"
                f" {actual_bw}, is at least {self.pass_bw_ratio* 100}%"
                f" of expected bandwidth {expected_bw}"
            ),
            raise_on_fail=False,
        )

    def _get_recv_bw_after_baseline_traffic(self, nic: NICInterface) -> Bandwidth:
        # use a timestamp filter to avoid getting logs
        # for traffic before the baseline
        recv_bw, _ = self.traffic_log.compute_bandwidth(
            query=[
                Filter("server", "=", nic.hostname),
                Filter("timestamp", ">", self.baseline_timestamp),
            ],
            iperf_version=self.iperf_version,
            log_dir=self.iperf_log_dir,
        )
        return recv_bw

    def _get_iperf_node_with_letter(self, letter: str) -> IperfNode:
        try:
            hostname = [
                hostname for _letter , hostname in self.node_hostname_map.items()
                if _letter == letter
            ].pop()
        except IndexError:
            raise TestError(f"Failed to find a host with {letter}")
        return self.get_iperf_node(hostname=hostname)

    def _get_baseline_bw(self) -> Bandwidth:
        recv_nic = self._get_iperf_node_with_letter(self.recv1).get_first_nic()
        recv_bw, _ = self.traffic_log.compute_bandwidth(
            query=[
                Filter("server", "=", recv_nic.hostname),
            ],
            iperf_version=self.iperf_version,
            log_dir=self.iperf_log_dir
        )
        return recv_bw
