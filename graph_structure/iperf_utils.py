import re
from abc import ABC, abstractmethod
from typing import Dict, List
from havoc.autoval.lib.utils.autoval_exceptions import TestError
from havoc.autoval.lib.test_utils.network.bandwidth import Bandwidth, BandwidthUnit


class IperfUtilsException(TestError):
    pass


class IperfUtils(ABC):

    def unpack_args(self, args: Dict) -> str:
        # Use long options such as --time instead of -t
        # for a short unpacking method
        # `man iperf3` for iperf3 options
        # `man iperf` for iperf2 arguments
        arg_str = []
        for opt, val in args.items():
            if val == "" or val is True:
                arg_str.append(f"--{opt}")
            else:
                arg_str.append(f"--{opt} {val}")
        return " ".join(arg_str)

    def get_combined_sender_bandwidth(self, logs: List[str]) -> Bandwidth:
        bandwidth = Bandwidth(0, BandwidthUnit.MBIT)
        for log in logs:
            bandwidth += self.get_sender_bandwidth(log)
        return bandwidth

    def get_combined_recv_bandwidth(self, logs: List[str]) -> Bandwidth:
        bandwidth = Bandwidth(0, BandwidthUnit.MBIT)
        for log in logs:
            bandwidth += self.get_recv_bandwidth(log)
        return bandwidth

    @abstractmethod
    def build_cmd(self, args: Dict) -> str:
        pass

    @abstractmethod
    def get_sender_bandwidth(self, log: str) -> Bandwidth:
        pass

    @abstractmethod
    def get_recv_bandwidth(self, log: str) -> Bandwidth:
        pass


class IperfUtilsV2(IperfUtils):

    def build_cmd(self, args: Dict) -> str:
        args_str = self.unpack_args(args)
        return f"iperf {args_str}"

    def get_sender_bandwidth(self, log: str) -> Bandwidth:
        return self._get_bandwidth(log)

    def get_recv_bandwidth(self, log: str) -> Bandwidth:
        return self._get_bandwidth(log)

    def _get_bandwidth(self, log: str) -> Bandwidth:
        bandwidth_regex = [
            r"(?P<bandwidth>\d*\.?\d*)\s(?P<unit>\wbits)\/sec",
            # Match for the line with 'SUM' if
            # --parallel option is used
            # Example
            # [SUM]  0.0- 0.0 sec  0.00 Bytes  0.00 bits/sec
            (
                r"\[SUM\]\s+\d*\.\d*-\s?\d*\.\d*\s+sec\s+\s+\d*\.?\d*\s\w?Bytes\s+"
                r"(?P<bandwidth>\d*\.?\d*)\s(?P<unit>\w?bits)\/sec"
            ),
        ]
        match = None
        with open(log, "r") as f:
            content = f.read()
        while not match and bandwidth_regex:
            match = re.search(bandwidth_regex.pop(), content)
            if match:
                bandwidth = float(match.group("bandwidth"))
                unit = Bandwidth.unit_from_str(match.group("unit"))
                return Bandwidth(bandwidth, unit)
        raise IperfUtilsException(f"Failed to get bandwidth from {log}")


class IperfUtilsV3(IperfUtils):

    def build_cmd(self, args: Dict) -> str:
        args_str = self.unpack_args(args)
        return f"iperf3 {args_str}"

    def get_sender_bandwidth(self, log: str) -> Bandwidth:
        bandwidth_regex = [
            #  [ ID] Interval           Transfer     Bandwidth       Retr
            #  [  8]   0.00-60.00  sec  50.4 GBytes  7.22 Gbits/sec    9   sender
            (
                r"(?P<bandwidth>\d*\.?\d*)\s(?P<unit>\wbits)\/sec"
                r"\s+(?:\d+)?\s+sender"
            ),
            # if --parallel param is used
            #  [ ID] Interval           Transfer     Bandwidth       Retr
            #  [SUM]   0.00-120.00 sec   104 GBytes  7.46 Gbits/sec  31836   sender
            (
                r"\[SUM\]\s+\d*\.\d*-\d*\.\d*\s+sec\s+\d*\.?\d*\s\wBytes\s+"
                r"(?P<bandwidth>\d*\.?\d*)\s(?P<unit>\wbits)\/sec"
                r"\s+(?:\d+)?\s+sender"
            ),
        ]
        match = None
        with open(log, "r") as f:
            content = f.read()
            while not match and bandwidth_regex:
                match = re.search(bandwidth_regex.pop(), content)
                if match:
                    bandwidth = float(match.group("bandwidth"))
                    unit = Bandwidth.unit_from_str(match.group("unit"))
                    return Bandwidth(bandwidth, unit)
        raise IperfUtilsException(f"Failed to get bandwidth from {log}")

    def get_recv_bandwidth(self, log: str) -> Bandwidth:
        # [  5]   0.00-20.04  sec  22.5 GBytes  9.63 Gbits/sec receiver
        regex = r"(?P<bandwidth>\d*\.?\d*)\s(?P<unit>\wbits)\/sec\s+receiver"
        match = None
        with open(log, "r") as f:
            content = f.read()
            match = re.search(regex, content)
            if match:
                bandwidth = float(match.group("bandwidth"))
                unit = Bandwidth.unit_from_str(match.group("unit"))
                return Bandwidth(bandwidth, unit)
        raise IperfUtilsException(f"Failed to get bandwidth from {log}")
