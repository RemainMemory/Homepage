# backend/app/models/host.py
from pydantic import BaseModel
from typing import Optional

from app.models.system import (
    SystemSummary,
    DiskDevicesSnapshot,
    ProcessesOverview,
    SensorsOverview,
    UptimeInfo,
)
from app.models.network import NetworkOverview
from app.models.monitor import MonitorOverview
from app.models.docker import DockerOverview


class HostOverview(BaseModel):
    """
    首页用的一次性聚合视图：
      - system: CPU/内存/主盘摘要
      - disks: 当前磁盘列表（用于侧边栏/弹窗）
      - processes: Top 进程（有限条）
      - sensors: 温度/电池（有多少算多少）
      - uptime: 开机时间/已运行时长
      - network: 主机网络概览
      - monitor: 外部服务监控总览（如果你有配置）
    """
    system: SystemSummary
    disks: DiskDevicesSnapshot
    processes: ProcessesOverview
    sensors: SensorsOverview
    uptime: UptimeInfo
    network: NetworkOverview
    monitor: Optional[MonitorOverview] = None
    docker: Optional[DockerOverview] = None
