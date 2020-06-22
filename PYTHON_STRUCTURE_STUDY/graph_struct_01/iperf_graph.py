from typing import Dict, List, NamedTuple, TYPE_CHECKING


if TYPE_CHECKING:
    from havoc.autoval.lib.test_utils.network.iperf_node import IperfNode


class Sled(NamedTuple):
    nodes: List[str]

    def length(self) -> int:
        return len(self.nodes)

    def __eq__(self, other: "Sled") -> bool:
        return self.length() == other.length()

    def __str__(self) -> str:
        return " ".join([f"{node}" for node in self.nodes])


class Rack:

    def __init__(self, sleds: List[List[str]]):
        self.sleds = [Sled(sled) for sled in sleds]

    def length(self) -> int:
        return sum(sled.length() for sled in self.sleds)

    def __iter__(self):
        for sled in self.sleds:
            yield sled

    def __eq__(self, other: "Rack") -> bool:
        try:
            assert self.length() == other.length()
            for ind, sled in enumerate(self.sleds):
                other_sled = other.sleds[ind]
                assert sled == other_sled
        except (IndexError, AssertionError):
            return False
        return True

    def __str__(self) -> str:
        return "\n\t\t".join([
            f"Sled: {sled}" for sled in self.sleds
        ])


class Topology:
    """
    Describe relationship of a list of hosts based on rack and
        sled grouping.
        e.g.
        Input: [
            [['i', 'j', 'k', 'l']],
            [['a', 'b', 'c', 'd'], ['e', 'f', 'g', 'h']],
            [['m']],
        ]
        Output:
            Topology:
                Rack:
                    Sled: ['a', 'b', 'c', 'd']
                    Sled: ['e', 'f', 'g', 'h']
                Rack:
                    Sled: ['i', 'j', 'k', 'l']
                Rack:
                    Sled: ['m']
    """
    def __init__(self, racks: List[List[List[str]]]):
        self.racks = [Rack(rack) for rack in racks]

    def sort(self) -> None:
        """Put racks with longer length at the beginning. This
            helps matching an alphabet topology to DUT's actual topology.
            Matching topologies should have the same shape after being sorted.
        """
        self.racks.sort(reverse=True, key=lambda rack: rack.length())

    def length(self) -> int:
        return sum(rack.length() for rack in self.racks)

    def get_nodes(self) -> List[str]:
        nodes = []
        for rack in self.racks:
            for sled in rack:
                nodes.extend(sled.nodes)
        return nodes

    @staticmethod
    def get_topology(
            host_configs: List[Dict[str, str]],
    ) -> "Topology":
        grouped = []
        try:
            rack_grouping = Topology._group_by_key(host_configs, "rack_id")
            sled_grouping = Topology._group_by_key(host_configs, "sled_id")
        except AssertionError as e:
            raise IperfGraphException(
                "Some host config doesn't have all information"
                f" for grouping: Error: {e}"
            )
        for _, rack_hosts in rack_grouping.items():
            grouped.append([])
            for _, sled_hosts in sled_grouping.items():
                if set(sled_hosts).issubset(rack_hosts):
                    grouped[-1].append(sled_hosts)
        return Topology(grouped)

    @staticmethod
    def _group_by_key(
        configs: List[Dict],
        group_key: str,
    ) -> Dict:
        grouped = {}
        for config in configs:
            assert (
                "hostname" in config
                and group_key in config
            )
            _key = config[group_key]
            grouped.setdefault(_key, []).append(config["hostname"])
        return grouped

    def __eq__(self, other: "Topology") -> bool:
        try:
            assert self.length() == other.length()
            for ind, rack in enumerate(self.racks):
                other_rack = other.racks[ind]
                assert rack == other_rack
        except (IndexError, AssertionError):
            return False
        return True

    def __str__(self) -> str:
        return "\n\t".join([
            f"Rack: {rack}" for rack in self.racks
        ])


class IperfGraphException(Exception):
    pass


class Edge(NamedTuple):
    client: "IperfNode"
    server: "IperfNode"


class IperfGraph:

    def __init__(
            self,
            str_edges: List[List[str]],
            nodes: List["IperfNode"],
            node_hostname_map: Dict[str, str],
    ):
        """
        str_edges: the graph representation using a list of edges
        e.g.
            [
                ['a', 'c'],  # client 'a' -> server 'c'
                ['b', 'c'],  # client 'b' -> server 'c'
                ...
            ]
        nodes: list of IperfNodes obj used in this graph
        node_hostname_map: alphabetic letter to name mapping
        e.g.
            {'a': 'rtptest1', 'b': 'rtptest2'}
        """
        self._graph = self.generate_graph(str_edges, nodes, node_hostname_map)

    def get_graph(self) -> List[Edge]:
        return self._graph

    def generate_graph(
            self,
            str_edges: List[List[str]],
            nodes: List["IperfNode"],
            node_hostname_map: Dict[str, str],
    ) -> List[Edge]:
        """
        Generate a graph of iperf connection based on a list of edges.
        Assign an iperf node object to each alphabetic letter.
        str_edges format:
            [ [<client>, <server>], ...  ]
        example:
        [
            ["a", "b"], ["b", "c"], ["b", "a"], ...
        ] means
            a (client) --> b (server),
            b --> c,
            b --> a, etc.
        """
        _map = self._assign_nodes_to_letters(nodes, node_hostname_map)
        return [
            Edge(
                client=_map[_client],
                server=_map[_server],
            ) for _client, _server in str_edges
        ]

    def _assign_nodes_to_letters(
            self,
            nodes: List["IperfNode"],
            node_hostname_map: Dict[str, str],
    ) -> Dict[str, "IperfNode"]:
        assign = {}
        #  Assign an iperf node object to each alphabetic letter
        if len(node_hostname_map) != len(nodes):
            raise IperfGraphException(
                f"Error generating iperf graph: One node per alphabet letter"
            )
        _copy = [node for node in nodes]
        while _copy:
            _node: "IperfNode" = _copy.pop()
            for letter, hostname in node_hostname_map.items():
                if hostname == _node.hostname:
                    assign[letter] = _node
                    break
        if _copy:
            raise IperfGraphException(
                f"Failed to map {node_hostname_map}"
                f" with {[node.hostname for node in nodes]}"
            )
        return assign

    def __iter__(self):
        for edge in self._graph:
            yield edge

    def __str__(self) -> str:
        # should map traffic between NIC interfaces, not IperfNodes
        return "\n".join(
            [f"\t\t{client} ===> {server}" for client, server in self._graph]
        )
