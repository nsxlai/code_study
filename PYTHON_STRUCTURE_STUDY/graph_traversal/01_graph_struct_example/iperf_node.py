import os
import re
from typing import Dict, List, Optional, Callable
import time
from multiprocessing import Manager, Process
from havoc.autoval.lib.utils.autoval_exceptions import (
    TestError,
    GlusterFsError,
)
from havoc.autoval.lib.test_utils.numactl_utils import NUMACtlUtils
from havoc.autoval.lib.test_utils.network.iperf_utils import IperfUtils
from havoc.autoval.lib.utils.autoval_utils import AutovalUtils
from havoc.autoval.lib.utils.autoval_log import AutovalLog
from havoc.autoval.lib.test_utils.network.nic_interface import NICInterface
from havoc.autoval.lib.utils.decorators import retry
from havoc.autoval.lib.host.host import Host
from havoc.autoval.lib.test_utils.network.iperf_utils import (
    IperfUtilsV3,
    IperfUtilsV2,
)


class IperfNodeException(TestError):
    pass


class IperfServerProcess(Process):
    def __init__(
        self,
        cmd: str,
        node: "IperfNode",
        nic: NICInterface,
        port: int,
        runtime: int,
        log_file: str,
        copy_log_to: Optional[str],
    ):
        self.log_file = log_file
        self.cmd = f"{cmd} > {self.log_file}"
        self.node = node
        self.port = port
        self.nic = nic
        # iperf logs are stored on the node that runs iperf,
        # but allow an option to copy that log to other directory
        # when the server finishes execution or is terminated
        self.copy_log_to = copy_log_to
        AutovalLog.log_debug(self.cmd)
        super(IperfServerProcess, self).__init__(
            target=node.run_cmd,
            args=(self.cmd,),
            kwargs={
                "in_thread": True,
                # TODO Terminating server processes take time (running command
                # back and forth). If there are too many processes started
                # some servers will timed out. Increasing slack time only
                # temporary solves the problem. Need to terminate server processes
                # in parallel.
                "timeout": runtime + 600,  # give some slack time for setup/cleanup
            },
        )

    def is_ready(self) -> bool:
        # iperf server is started when there are more than one
        # process with string {self.cmd}
        return len(self._get_cmd_processes()) > 0

    def run(self) -> None:
        AutovalLog.log_info(f"[iperf Server] {self.nic}:{self.port} started")
        super(IperfServerProcess, self).run()
        self._cleanup()

    def terminate(self) -> None:
        super(IperfServerProcess, self).terminate()
        self._kill_server_processes()
        # Terminated commands won't be recorded in cmdlog.log
        # Log command manually here
        AutovalLog.log_as_cmd(f"[{self.node.hostname}][{self.cmd}]:\nTerminated.")
        self._cleanup()

    def _kill_server_processes(self):
        AutovalLog.log_debug(f"Terminating {self}.")
        for pid in self._get_cmd_processes():
            self.node.run_cmd(f"kill -s 9 {pid}", in_thread=True)

    def _get_cmd_processes(self) -> List[str]:
        # return a list of process ID associated with this server process command
        return re.findall(
            # e.g.
            # root     3280374 ... bash -c iperf3  ...
            r"^root\s+(\d+)",
            self.node.run_cmd(
                (
                    "ps aux | grep -v grep | grep iperf | grep server"
                    f" | grep 'port {self.port}'"
                ),
                in_thread=True,
                ignore_status=True,
            ),
            re.M,
        )

    def _cleanup(self) -> None:
        self.node.release_port(self.port)
        if self.copy_log_to is not None:
            self.node.copy_to_result_dir(file=self.log_file, dest=self.copy_log_to)

    def __str__(self) -> str:
        return f"[iperf Server Proc]{self.nic}:{self.port}"


class IperfClientProcess(Process):
    def __init__(
        self,
        cmd: str,
        node: "IperfNode",
        nic: NICInterface,
        server_nic: NICInterface,
        server_port: int,
        runtime: int,
        log_file: str,
        copy_log_to: Optional[str] = None,
        server_process: Optional[IperfServerProcess] = None,
    ):
        self.log_file = log_file
        self.cmd = f"{cmd} > {self.log_file}"
        AutovalLog.log_debug(self.cmd)
        self.node = node
        self.nic = nic
        self.server_nic = server_nic
        self.server_port = server_port
        # server_process should be the destination of this client process
        # if this is provided, client will wait for this process to setup
        self.server_process = server_process
        # iperf logs are stored on the node that runs iperf,
        # but allow an option to copy that log to other directory
        # when the client finishes execution
        self.copy_log_to = copy_log_to
        super(IperfClientProcess, self).__init__(
            target=node.run_cmd,
            args=(self.cmd,),
            kwargs={
                "in_thread": True,
                "timeout": runtime + 30,  # give some slack time for setup
            },
        )

    def run(self) -> None:
        if self.server_process is not None:
            self._wait_for_server_process()
        AutovalLog.log_info(
            f"[iperf Client] {self.nic} ====> {self.server_nic}:{self.server_port}"
        )
        super(IperfClientProcess, self).run()

    def join(self, *args, **kwargs) -> None:
        super(IperfClientProcess, self).join(*args, **kwargs)
        if self.copy_log_to is not None:
            self.node.copy_to_result_dir(file=self.log_file, dest=self.copy_log_to)

    def _wait_for_server_process(self):
        timeout = 20
        for _ in range(timeout):
            time.sleep(1)
            if self.server_process.is_ready():
                break
        else:
            raise IperfNodeException(
                f"Waited for {self.server_process} for more than {timeout} sec(s)"
            )


class IperfNode:

    DEFAULT_NIC = "eth0"

    def __init__(self, host: Dict):
        self.host = Host(host)
        self.hostname = self.host.hostname
        self.gateway_ip6 = self.get_gateway_ip6()
        self.nic_interfaces = self.create_nic_interface_objs()
        self.free_ports = Manager().list([port for port in range(5501, 5200, -1)])
        self.tmp_log_dir = f"/tmp/{int(time.time())}_iperf_log"
        self.run_cmd(f"mkdir -p {self.tmp_log_dir}")

    def get_gateway_ip6(self) -> str:
        ip6 = ""
        gateway_re = r"default via ((?:(?:\w+)?:)+\w+) dev (eth\d{1,2})"
        # e.g. default via fe80::90:fbff:fe66:ab08
        for line in self.run_cmd("ip -6 route | grep default").splitlines():
            m = re.search(gateway_re, line)
            if m:
                if ip6:
                    # keep looking to see if a different gateway is found
                    eth = m.group(2)
                    AutovalUtils.validate_equal(
                        m.group(1),
                        ip6,
                        f"Different gateway {ip6} for {eth}.",
                        log_on_pass=False,
                    )
                else:
                    # assign initial found gateway
                    ip6 = m.group(1)
        return ip6

    def get_net_interfaces(self) -> List[str]:
        eth_re = r"^(eth\d{1,2}):"
        return re.findall(eth_re, self.run_cmd(f"ifconfig"), re.M)

    def create_nic_interface_objs(self) -> List[str]:
        nics = []
        for eth in self.get_net_interfaces():
            nics.append(NICInterface(self.host, eth))
        return nics

    def get_nic_interface(self, eth: str) -> NICInterface:
        filtered = [nic for nic in self.nic_interfaces if nic.name == eth]
        if not filtered:
            raise IperfNodeException(f"No {eth} NIC found on {self.hostname}.")
        if len(filtered) > 1:
            raise IperfNodeException(
                f"More than one NICInterface found with name {eth}"
            )
        return filtered.pop()

    def get_routing_table(self) -> str:
        return self.run_cmd(f"ip -6 route")

    def add_route(self, route: str):
        # `add` command will fail if current host has a config related to
        # new route being added. Use `replace` instead
        self.run_cmd(f"ip -6 route replace {route}")

    def remove_route(self, route: str):
        self.run_cmd(f"ip -6 route delete {route}")

    def start_server(
        self,
        log_file: str,
        port: int,
        copy_log_to: Optional[str] = None,
        nic: Optional[NICInterface] = None,
        misc_args: Optional[Dict] = None,
        bind_numa: bool = False,
        runtime: int = 60,
        iperf_version: int = 3,
    ) -> IperfServerProcess:
        """
        Create an iperf server process on a NIC in this iperf node.
        If no <nic> is provided will use the IperfNode.DEFAULT_NIC.
        If bind_numa is True, will bind the iperf process to the NUMA node associated
            with server's NIC using `numactl`.
        """
        if nic is None:
            nic = self.get_nic_interface(self.DEFAULT_NIC)
        numa_index = nic.numa_node if bind_numa else None
        iperf_args = self._make_iperf_server_args(nic.ip6, port, misc_args=misc_args)
        proc = IperfServerProcess(
            cmd=self.build_iperf_cmd(
                iperf_args,
                numa_index=numa_index,
                version=iperf_version,
            ),
            node=self,
            nic=nic,
            port=port,
            runtime=runtime,
            log_file=os.path.join(
                self.tmp_log_dir,
                log_file,
            ),
            copy_log_to=copy_log_to,
        )
        proc.start()
        return proc

    def _make_iperf_server_args(
        self, ip6: int, port: int, misc_args: Optional[Dict] = None
    ) -> Dict:
        args = {"server": True, "bind": ip6, "port": port}
        args.update(misc_args if misc_args is not None else {})
        return args

    def start_client(
        self,
        server: "IperfNode",
        server_port: int,
        log_file: str,
        copy_log_to: Optional[str] = None,
        misc_args: Optional[Dict] = None,
        client_nic: Optional[NICInterface] = None,
        server_nic: Optional[NICInterface] = None,
        bind_numa: bool = False,
        server_proc: Optional[IperfServerProcess] = None,
        runtime: int = 60,
        iperf_version: int = 3,
    ) -> IperfClientProcess:
        """
        Start iperf3 traffic from this IperfNode to an iperf server.
        Default NIC for both client (this node) and server is IperfNode.DEFAULT_NIC
        If bind_numa is True, will bind the iperf process to the NUMA node associated
            with client's NIC using `numactl`
        """
        if client_nic is None:
            client_nic = self.get_nic_interface(self.DEFAULT_NIC)
        if server_nic is None:
            server_nic = server.get_nic_interface(self.DEFAULT_NIC)
        numa_index = client_nic.numa_node if bind_numa else None
        iperf_args = self._make_iperf_client_args(
            client_nic.ip6, server_nic.ip6, server_port, misc_args=misc_args
        )
        proc = IperfClientProcess(
            cmd=self.build_iperf_cmd(
                iperf_args,
                numa_index=numa_index,
                version=iperf_version,
            ),
            node=self,
            nic=client_nic,
            server_nic=server_nic,
            server_port=server_port,
            runtime=runtime,
            server_process=server_proc,
            log_file=os.path.join(
                self.tmp_log_dir,
                log_file,
            ),
            copy_log_to=copy_log_to,
        )
        proc.start()
        return proc

    def _make_iperf_client_args(
        self,
        client_ip6: int,
        server_ip6: str,
        server_port: int,
        misc_args: Optional[Dict] = None,
    ) -> Dict:
        args = {
            "client": server_ip6,  # --client argument should point to server's ip
            "port": server_port,
            "bind": client_ip6,
        }
        args.update(misc_args if misc_args is not None else {})
        return args

    def get_free_port(self) -> int:
        return self.free_ports.pop()

    def release_port(self, port: int):
        self.free_ports.append(port)

    def kill_all_iperf_proc(self):
        # kill iperf2 and iperf3
        self.run_cmd("killall iperf", ignore_status=True)
        self.run_cmd("killall iperf3", ignore_status=True)

    def build_iperf_cmd(
        self,
        iperf_args: Dict,
        version: int = 3,
        numa_index: Optional[int] = None
    ) -> str:
        """
        If <numa_index> is provided, will bind iperf command to that NUMA node
            using `numactl`. This is use allocate particular CPU/memory to this iperf
            command.
        """
        cmd = ""
        if version == 3:
            iperf_cmd = IperfUtilsV3().build_cmd(iperf_args)
        elif version == 2:
            iperf_cmd = IperfUtilsV2().build_cmd(iperf_args)
        else:
            raise IperfNodeException(f"Invalid version {version}")
        if numa_index is not None:
            numactl_args = {"cpunodebind": numa_index, "membind": numa_index}
            cmd += NUMACtlUtils.build_cmd(numactl_args) + " "
        cmd += iperf_cmd
        return cmd

    def run_cmd(self, cmd: str, in_thread: bool = False, **kwargs):
        if in_thread:
            # create a new Host obj to avoid Thrift Unknown Client Type error
            thread_host = Host({"hostname": self.hostname})
            return thread_host.run(cmd, **kwargs)
        return self.host.run(cmd, **kwargs)  # noqa

    def do_for_all_nics(self, func: Callable, *args, **kwargs):
        # Apply a method on all NICs
        for nic in self.nic_interfaces:
            func(nic, *args, **kwargs)

    def dump_data(self) -> Dict:
        data = {"gateway": self.gateway_ip6, "interfaces": []}
        for nic in self.nic_interfaces:
            data["interfaces"].append(nic.dump_data())
        return data

    @retry(tries=4, sleep_seconds=5, exceptions=GlusterFsError, exponential=True)
    def copy_to_result_dir(
        self,
        file: str,
        # shouldn't be optional, but pyre can't detect
        # whether we're checking for None type before calling the function
        dest: Optional[str],
    ) -> None:
        if not dest:
            raise IperfNodeException(f"{self}: Can't copy {file} because no `dest` is provided")
        try:
            AutovalLog.log_debug(f"Copying {file} to {dest}")
            self.run_cmd(
                f"cp {file} {dest}",
                in_thread=True,
            )
        except Exception as e:
            error = str(e)
            error_msg = (
                f"Failed to copy {file} to {dest}.\n"
                f"Exception: {error}"
            )
            if "cp: failed to access" in error or "Stale file handle" in error:
                raise GlusterFsError(error_msg)
            raise IperfNodeException(error_msg)

    def get_first_nic(self) -> NICInterface:
        try:
            return self.nic_interfaces[0]
        except IndexError:
            raise LookupError(f"No NIC found on {self}")

    def __str__(self) -> str:
        return f"[IperfNode]: {self.hostname}"

    async def install_iperf(self, version: int = 3) -> None:
        if version == 3:
            package = "iperf3"
        elif version == 2:
            package = "iperf"
        else:
            raise IperfNodeException(f"Unsupported iperf version {version}")
        # Use a new 'host' to avoid UnknownClientType exc
        _host = Host({"hostname": self.hostname})
        AutovalUtils.run_on_host(
            _host,
            AutovalUtils.install_rpms,
            rpm_list=[package],
        )
