import os
from enum import Enum
from datetime import datetime
from typing import NamedTuple, List, Tuple, Union
from havoc.autoval.lib.test_utils.network.bandwidth import Bandwidth
from havoc.autoval.lib.test_utils.network.iperf_utils import (
    IperfUtilsV2,
    IperfUtilsV3,
)

TIME_FORMAT = "%H:%M:%S"


class Operator(Enum):
    EQUAL = "="
    GREATER = ">"
    LESS = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="


class Filter:

    def __init__(
        self,
        key: str,
        operator: Union[Operator, str],
        value: Union[int, str],
    ):
        self.key = key
        if type(operator) is Operator:
            self.operator = operator
        elif type(operator) is str:
            self.operator = Operator(operator)
        else:
            raise TypeError(f"{operator} should be of type string or Operator")
        self.value = value

    def apply(self, other_val: Union[int, str]) -> bool:
        if type(self.value) is not type(other_val):
            raise TypeError(
                f"{self.value} does not have the same type as {other_val}"
            )
        if (
            type(other_val) is str
            and type(self.value) is str
        ):
            # Would have just access self.value instead of passing self.value
            # as argument but pyre is so unforgiving
            return self._compare_str(self.value, other_val)  # pyre-fixme
        elif (
            type(other_val) is int
            and type(self.value) is int
        ):
            return self._compare_int(self.value, other_val)  # pyre-fixme
        else:
            raise TypeError("Only support int and str comparison.")

    def _compare_int(self, val: int, other_val: int) -> bool:
        if self.operator is Operator.EQUAL:
            return other_val == val
        elif self.operator is Operator.GREATER:
            return other_val > val
        elif self.operator is Operator.LESS:
            return other_val < val
        elif self.operator is Operator.GREATER_EQUAL:
            return other_val >= val
        elif self.operator is Operator.LESS_EQUAL:
            return other_val <= val
        else:
            raise NotImplementedError(f"{self.operator} is not implemented")

    def _compare_str(self, val: str, other_val: str) -> bool:
        if self.operator is Operator.EQUAL:
            return other_val == val
        raise TypeError(f"{self.operator} is not supported for str comparison")


class Entry(NamedTuple):
    conn_hash: str
    server: str
    client: str
    server_nic: str
    client_nic: str
    port: int
    timestamp: int

    def match(self, query: List[Filter]) -> bool:
        return all(
            self._match(_filter) for _filter in query
        )

    def _match(self, _filter: Filter) -> bool:
        entry_attr = getattr(self, _filter.key, None)
        if entry_attr is None:
            raise TypeError(f"An invalid <Entry> attribute is provided. {_filter.key}")
        return _filter.apply(entry_attr)

    def get_client_log_file_name(self) -> str:
        time_str = self._get_time_str()
        return (
            f"{self.server}:{self.server_nic}"
            f"---{self.client}:{self.client_nic}:{self.port}"
            f"-{time_str}.client.log"
        )

    def get_server_log_file_name(self) -> str:
        time_str = self._get_time_str()
        return (
            f"{self.server}:{self.server_nic}:{self.port}"
            f"-{time_str}.server.log"
        )

    def _get_time_str(self) -> str:
        return datetime.fromtimestamp(self.timestamp).strftime(TIME_FORMAT)


class TrafficLog:

    def __init__(self) -> None:
        self.log: List[Entry] = []

    def add(self, *entries: Entry) -> None:
        for entry in entries:
            self.log.append(entry)

    def search(self, query: List[Filter]) -> List[Entry]:
        return [entry for entry in self.log if entry.match(query)]

    def compute_bandwidth(
        self,
        query: List[Filter],
        log_dir: str = "",
        iperf_version: int = 3,
    ) -> Tuple[Bandwidth, Bandwidth]:
        # Search for logs that match a 'query'
        # calculate send and recv bandwidth for those log entries
        # and return a tuple of sender bandwidth and recv bandwidth
        entries = self.search(query)
        recv_logs = [
            os.path.join(log_dir, entry.get_server_log_file_name())
            for entry in entries
        ]
        sender_logs = [
            os.path.join(log_dir, entry.get_client_log_file_name())
            for entry in entries
        ]
        if iperf_version == 3:
            iperf_utils = IperfUtilsV3()
        elif iperf_version == 2:
            iperf_utils = IperfUtilsV2()
        else:
            raise ValueError(f"Invalid iperf_version {iperf_version}.")
        return (
            iperf_utils.get_combined_recv_bandwidth(recv_logs),
            iperf_utils.get_combined_sender_bandwidth(sender_logs),
        )
