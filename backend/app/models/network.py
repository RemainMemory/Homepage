# app/models/network.py
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class NetTraffic(BaseModel):
    bytes: int
    rate_mbps: float
    errors: Optional[int] = None
    dropped: Optional[int] = None


class NetworkInterface(BaseModel):
    name: str                   # 系统里的接口名，例如 eth0 / en0 / Ethernet0
    display_name: Optional[str] = None  # 预留：如果你以后想自定义友好名称
    role: Optional[str] = None          # "wan" | "lan" | "mgmt" | "virtual" | ...
    type: Optional[str] = None          # "ethernet" | "wifi" | "loopback" | "virtual"
    is_primary: bool = False

    state: str                  # "up" | "down"
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None
    mac: Optional[str] = None
    mtu: Optional[int] = None
    speed_mbps: Optional[int] = None     # 网卡物理/逻辑速率

    rx: NetTraffic
    tx: NetTraffic
    utilization_pct: Optional[float] = None   # 当前速率 / speed_mbps * 100


class Connectivity(BaseModel):
    internet_ok: bool
    gateway_ok: bool
    dns_ok: bool

    internet_latency_ms: Optional[float] = None   # 主机 → 外网
    gateway_latency_ms: Optional[float] = None    # 主机 → 默认网关
    dns_latency_ms: Optional[float] = None        # DNS 解析耗时

    jitter_ms: Optional[float] = None             # 预留：如有 ping 统计可填
    packet_loss_pct: Optional[float] = None       # 预留：如有 ping 统计可填

    tested_internet_target: Optional[str] = None  # 例如 "1.1.1.1:443"
    tested_dns_target: Optional[str] = None       # 例如 "example.com"


class Route(BaseModel):
    dst: str                               # 目的网段，例如 "0.0.0.0/0"
    gateway: Optional[str] = None
    interface: Optional[str] = None
    metric: Optional[int] = None


class Routes(BaseModel):
    default_gateway: Optional[str] = None
    default_interface: Optional[str] = None
    public_ip: Optional[str] = None

    routes: List[Route] = []              # 非必须，可为空列表


class NetworkSummary(BaseModel):
    primary_interface: Optional[str] = None

    wan_rx_mbps: float                    # 主出口上的速率（如果能识别）
    wan_tx_mbps: float

    total_rx_mbps: float                  # 所有接口合计
    total_tx_mbps: float

    internet_ok: bool
    internet_latency_ms: Optional[float] = None

    gateway_latency_ms: Optional[float] = None
    public_ip: Optional[str] = None


class NetworkOverview(BaseModel):
    """
    主机网络总览，推荐暴露为 /network/overview:
    - summary: 顶部总览卡用
    - interfaces: 网卡列表/详情
    - connectivity: 连通性 & 延迟
    - routes: 默认网关 / 公网 IP / 路由表（可选）
    """
    summary: NetworkSummary
    interfaces: List[NetworkInterface]
    connectivity: Connectivity
    routes: Routes


class LanDevice(BaseModel):
    ip: str
    mac: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None


class LanDevicesOverview(BaseModel):
    collected_at: datetime
    devices: List[LanDevice]


class SpeedTestResult(BaseModel):
    ok: bool
    message: Optional[str] = None
    ping_ms: Optional[float] = None
    download_mbps: Optional[float] = None
    upload_mbps: Optional[float] = None
    raw_output: Optional[str] = None
