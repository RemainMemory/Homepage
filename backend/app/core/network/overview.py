# app/core/network_info.py
import platform
import socket
import subprocess
import time
from typing import Dict, Optional, Tuple, List
from urllib import request as urllib_request
from urllib.error import URLError

import psutil

from app.models.network import (
    NetworkOverview,
    NetworkSummary,
    NetworkInterface,
    NetTraffic,
    Connectivity,
    Routes,
    Route,
)

# 计速缓存：上一次的网卡统计与时间戳
# 计速缓存：每个网卡上一次的统计 + 时间戳
# name -> (io, timestamp)
_LAST_IO: Dict[str, Tuple[psutil._common.snetio, float]] = {}



def _measure_tcp_latency(host: str, port: int, timeout: float = 2.0) -> Tuple[Optional[float], bool]:
    """
    使用 TCP 三次握手测量延迟，跨平台可用。
    返回: (latency_ms, ok)
    """
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            end = time.monotonic()
        latency_ms = (end - start) * 1000.0
        return latency_ms, True
    except OSError:
        return None, False


def _get_default_gateway_and_routes() -> Routes:
    """
    尽量跨平台获取默认网关 / 出口接口 / 路由表（路由表细节可以为空）。
    - Linux:   ip route
    - macOS:   route -n get default
    - Windows: route print 0.0.0.0
    """
    system = platform.system().lower()
    default_gateway: Optional[str] = None
    default_interface: Optional[str] = None
    routes: List[Route] = []

    if system == "linux":
        try:
            result = subprocess.run(
                ["ip", "route"],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if not parts:
                    continue

                if parts[0] == "default" and "via" in parts and "dev" in parts:
                    # default via 192.168.1.1 dev eth0 ...
                    try:
                        gw = parts[parts.index("via") + 1]
                        dev = parts[parts.index("dev") + 1]
                        default_gateway = gw
                        default_interface = dev
                    except (ValueError, IndexError):
                        pass

                # 简单解析一部分路由记录
                if parts[0] == "default":
                    dst = "0.0.0.0/0"
                    gw = None
                    dev = None
                    metric = None
                    if "via" in parts:
                        gw = parts[parts.index("via") + 1]
                    if "dev" in parts:
                        dev = parts[parts.index("dev") + 1]
                    if "metric" in parts:
                        try:
                            metric = int(parts[parts.index("metric") + 1])
                        except (ValueError, IndexError):
                            metric = None
                    routes.append(Route(dst=dst, gateway=gw, interface=dev, metric=metric))
                elif "/" in parts[0]:
                    # 例如 192.168.1.0/24 dev eth0 ...
                    dst = parts[0]
                    gw = None
                    dev = None
                    metric = None
                    if "via" in parts:
                        gw = parts[parts.index("via") + 1]
                    if "dev" in parts:
                        dev = parts[parts.index("dev") + 1]
                    if "metric" in parts:
                        try:
                            metric = int(parts[parts.index("metric") + 1])
                        except (ValueError, IndexError):
                            metric = None
                    routes.append(Route(dst=dst, gateway=gw, interface=dev, metric=metric))
        except Exception:
            # 失败就留默认为 None / []
            pass

    elif system == "darwin":  # macOS
        try:
            result = subprocess.run(
                ["route", "-n", "get", "default"],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("gateway:"):
                    default_gateway = line.split()[-1]
                elif line.startswith("interface:"):
                    default_interface = line.split()[-1]
            # macOS 上路由表不强行解析，routes 保持空列表即可
        except Exception:
            pass

    elif system == "windows":
        try:
            # 仅解析默认路由行，不尝试还原完整路由表
            result = subprocess.run(
                ["route", "print", "0.0.0.0"],
                capture_output=True,
                text=True,
                check=False,
            )
            # Windows 输出比较复杂，这里粗略查找 0.0.0.0 开头的记录行
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                parts = line.split()
                # 典型行: 0.0.0.0   0.0.0.0   192.168.1.1   192.168.1.100  25
                if parts[0] == "0.0.0.0" and len(parts) >= 4:
                    default_gateway = parts[2]
                    # 第 3/4 列之间一般有“接口 IP”，但不是接口名；接口名恢复较麻烦，这里就不搞了
                    break
        except Exception:
            pass

    return Routes(
        default_gateway=default_gateway,
        default_interface=default_interface,
        public_ip=_get_public_ip(),
        routes=routes,
    )


def _get_public_ip(timeout: float = 2.0) -> Optional[str]:
    """
    获取公网 IP（如果机器可以访问外网）。
    不可达 / 超时时返回 None。
    """
    try:
        with urllib_request.urlopen("https://api.ipify.org", timeout=timeout) as resp:
            ip = resp.read().decode("ascii").strip()
            if ip:
                return ip
    except (URLError, OSError, ValueError):
        pass
    return None


def _is_loopback_interface(name: str, addrs: list[psutil._common.snicaddr]) -> bool:
    """
    粗略判断是否是 loopback 接口：
    - 接口名 lo / lo0
    - 或者只有 127.0.0.1 / ::1 地址
    """
    lname = name.lower()
    if lname in ("lo", "lo0", "loopback"):
        return True

    only_loopback = True
    for addr in addrs:
        if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
            only_loopback = False
        elif addr.family == socket.AF_INET6 and not addr.address.startswith("::1"):
            only_loopback = False
    return only_loopback


def _infer_interface_type(name: str, is_loopback: bool) -> str:
    lname = name.lower()
    if is_loopback:
        return "loopback"
    if "wifi" in lname or "wlan" in lname or "wl" in lname:
        return "wifi"
    if lname.startswith("br") or lname.startswith("docker") or lname.startswith("veth"):
        return "virtual"
    return "ethernet"


def _calc_rates(io_now: psutil._common.snetio, io_prev: Optional[psutil._common.snetio], interval: float) -> Tuple[float, float]:
    """
    根据两次 io 统计计算速率（Mbps）。interval 为秒。
    """
    if io_prev is None or interval <= 0:
        return 0.0, 0.0
    rx_bytes_diff = io_now.bytes_recv - io_prev.bytes_recv
    tx_bytes_diff = io_now.bytes_sent - io_prev.bytes_sent
    rx_rate_mbps = (rx_bytes_diff * 8) / 1_000_000 / interval
    tx_rate_mbps = (tx_bytes_diff * 8) / 1_000_000 / interval
    return max(rx_rate_mbps, 0.0), max(tx_rate_mbps, 0.0)


def _build_interfaces(routes: Routes) -> Tuple[List[NetworkInterface], float, float, float, float]:
    global _LAST_IO

    if_addrs = psutil.net_if_addrs()
    if_stats = psutil.net_if_stats()
    if_io = psutil.net_io_counters(pernic=True)
    # if_errors = psutil.net_io_counters(pernic=True, nowrap=True)  # 你现在没用到，可以先去掉或留着

    interfaces: List[NetworkInterface] = []

    total_rx_mbps = 0.0
    total_tx_mbps = 0.0
    wan_rx_mbps = 0.0
    wan_tx_mbps = 0.0

    default_iface_name = routes.default_interface
    now_ts = time.monotonic()  # 每次调用获取当前时间

    for name, addrs in if_addrs.items():
        stats = if_stats.get(name)
        io = if_io.get(name)
        if stats is None or io is None:
            continue

        # 判断是否 loopback
        is_loopback = _is_loopback_interface(name, addrs)
        iface_type = _infer_interface_type(name, is_loopback)

        ipv4 = None
        ipv6 = None
        mac = None
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ipv4 = addr.address
            elif addr.family == socket.AF_INET6:
                ipv6 = addr.address.split("%")[0]  # 去掉接口后缀
            elif hasattr(psutil, "AF_LINK") and addr.family == psutil.AF_LINK:
                mac = addr.address

        # ==== 关键：按网卡计算 dt ====
        prev_record = _LAST_IO.get(name)
        if prev_record is not None:
            prev_io, prev_ts = prev_record
            dt = max(now_ts - prev_ts, 1e-3)  # 至少 1ms，避免除 0
            rx_rate_mbps, tx_rate_mbps = _calc_rates(io, prev_io, dt)
        else:
            rx_rate_mbps, tx_rate_mbps = 0.0, 0.0

        # 更新缓存（这一步一定要在最后）
        _LAST_IO[name] = (io, now_ts)

        total_rx_mbps += rx_rate_mbps
        total_tx_mbps += tx_rate_mbps

        is_primary = (default_iface_name is not None and name == default_iface_name)

        if is_primary:
            wan_rx_mbps = rx_rate_mbps
            wan_tx_mbps = tx_rate_mbps

        errors = getattr(io, "errin", None)
        dropped = getattr(io, "dropin", None)

        utilization_pct = None
        if stats.speed and stats.speed > 0:
            max_mbps = float(stats.speed)
            utilization_pct = (rx_rate_mbps + tx_rate_mbps) / max_mbps * 100.0

        iface = NetworkInterface(
            name=name,
            display_name=None,
            role=None,
            type=iface_type,
            is_primary=is_primary,
            state="up" if stats.isup else "down",
            ipv4=ipv4,
            ipv6=ipv6,
            mac=mac,
            mtu=stats.mtu,
            speed_mbps=stats.speed if stats.speed > 0 else None,
            rx=NetTraffic(
                bytes=io.bytes_recv,
                rate_mbps=rx_rate_mbps,
                errors=errors,
                dropped=dropped,
            ),
            tx=NetTraffic(
                bytes=io.bytes_sent,
                rate_mbps=tx_rate_mbps,
                errors=getattr(io, "errout", None),
                dropped=getattr(io, "dropout", None),
            ),
            utilization_pct=utilization_pct,
        )
        interfaces.append(iface)

    return interfaces, total_rx_mbps, total_tx_mbps, wan_rx_mbps, wan_tx_mbps


def _build_connectivity(routes: Routes) -> Connectivity:
    """
    连通性检查（跨平台）：
    - gateway_ok: 连接默认网关（如果有）
    - internet_ok: 连接外网固定 IP（例如 1.1.1.1:443）
    - dns_ok: 解析 example.com
    """
    gateway_ok = False
    gateway_latency: Optional[float] = None

    internet_ok = False
    internet_latency: Optional[float] = None
    internet_target = "1.1.1.1:443"

    dns_ok = False
    dns_latency: Optional[float] = None
    dns_target = "example.com"

    # 默认网关
    if routes.default_gateway:
        latency, ok = _measure_tcp_latency(routes.default_gateway, 80, timeout=1.5)
        gateway_ok = ok
        gateway_latency = latency

    # 外网连通性（不依赖 DNS）
    latency, ok = _measure_tcp_latency("1.1.1.1", 443, timeout=2.0)
    internet_ok = ok
    internet_latency = latency

    # DNS 检查
    start = time.monotonic()
    try:
        socket.gethostbyname(dns_target)
        dns_ok = True
        dns_latency = (time.monotonic() - start) * 1000.0
    except OSError:
        dns_ok = False
        dns_latency = None

    return Connectivity(
        internet_ok=internet_ok,
        gateway_ok=gateway_ok,
        dns_ok=dns_ok,
        internet_latency_ms=internet_latency,
        gateway_latency_ms=gateway_latency,
        dns_latency_ms=dns_latency,
        jitter_ms=None,
        packet_loss_pct=None,
        tested_internet_target=internet_target,
        tested_dns_target=dns_target,
    )


def get_network_overview() -> NetworkOverview:
    """
    主入口：返回 NetworkOverview，兼容 Linux / macOS / Windows。
    每个网卡各自根据上一次采样计算速率。
    """
    routes = _get_default_gateway_and_routes()
    interfaces, total_rx, total_tx, wan_rx, wan_tx = _build_interfaces(routes)
    connectivity = _build_connectivity(routes)

    summary = NetworkSummary(
        primary_interface=routes.default_interface,
        wan_rx_mbps=wan_rx,
        wan_tx_mbps=wan_tx,
        total_rx_mbps=total_rx,
        total_tx_mbps=total_tx,
        internet_ok=connectivity.internet_ok,
        internet_latency_ms=connectivity.internet_latency_ms,
        gateway_latency_ms=connectivity.gateway_latency_ms,
        public_ip=routes.public_ip,
    )

    return NetworkOverview(
        summary=summary,
        interfaces=interfaces,
        connectivity=connectivity,
        routes=routes,
    )

