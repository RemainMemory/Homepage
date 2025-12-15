# backend/app/models/system.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# =========================
# 1) 系统摘要 /system/summary
# =========================
class CpuSummary(BaseModel):
    # CPU 概览 + 详细
    usagePct: float              # 总使用率 %
    load1: float                 # 1 分钟平均负载
    load5: float                 # 5 分钟平均负载
    load15: float                # 15 分钟平均负载
    cores: int                   # 逻辑核心数
    perCoreUsage: List[float]    # 每个核心的使用率 %
    userPct: float               # 用户态 CPU %
    systemPct: float             # 内核态 CPU %
    idlePct: float               # 空闲 %
    iowaitPct: float             # IO 等待 %（在 macOS 上通常为 0）


class MemorySummary(BaseModel):
    # 内存概览 + 详细
    usagePct: float              # 内存使用率 %
    totalGb: float               # 总内存 GB
    usedGb: float                # 已用 GB
    availableGb: float           # 可用 GB
    cachedGb: float              # 缓存/缓冲区 GB（近似）
    swapUsagePct: float          # 交换分区使用率 %
    swapTotalGb: float           # 交换分区总量 GB
    swapUsedGb: float            # 交换分区已用 GB


class DiskSummary(BaseModel):
    # 单个“主盘”摘要（系统盘或指定挂载点/盘符）
    device: str                  # 设备名: /dev/disk3s1, C:\, D:\ 等
    mount: str                   # 挂载点: /, /Volumes/USB, C:\ 等
    fsType: str                  # 文件系统类型: apfs/ext4/ntfs/exfat 等
    usagePct: float              # 使用率 %
    totalGb: float               # 总容量 GB
    usedGb: float                # 已用 GB
    freeGb: float                # 剩余 GB


class SystemSummary(BaseModel):
    cpu: CpuSummary
    memory: MemorySummary
    disk: DiskSummary


# ========= 磁盘列表 + 新设备检测 =========

class DiskDevice(BaseModel):
    device: str        # 设备名: /dev/disk3s1, C:\, D:\ 等
    mount: str         # 挂载点: /, /Volumes/USB, C:\ 等
    fsType: str        # 文件系统类型: apfs/ext4/ntfs/exfat 等
    usagePct: float    # 分区使用率 %
    totalGb: float     # 总容量 GB
    usedGb: float      # 已用 GB
    freeGb: float      # 剩余 GB
    isRemovable: bool  # 是否推测为可移动设备/USB


class DiskDevicesSnapshot(BaseModel):
    devices: List[DiskDevice]  # 当前所有设备
    added: List[str]           # 新增的 device 名称列表
    removed: List[str]         # 消失的 device 名称列表
    snapshotId: str            # 时间戳或 UUID，用于标记这次快照

# =========================
# 1) 进程监控 /system/processes
# =========================

class ProcessInfo(BaseModel):
    pid: int
    name: str
    username: Optional[str] = None

    cpu_pct: float         # 单进程 CPU 占用百分比
    memory_mb: float       # 常驻内存，单位 MB
    memory_pct: float      # 占总内存百分比

    cmdline: Optional[str] = None  # 完整命令行（可用于详情弹窗）


class ProcessesOverview(BaseModel):
    """
    进程监控概览：
      - summary：整体统计
      - top_by_cpu：按 CPU 排序的前 N 个进程
      - top_by_memory：按内存排序的前 N 个进程
    """
    total: int
    collected_at: datetime

    top_by_cpu: List[ProcessInfo]
    top_by_memory: List[ProcessInfo]


# =========================
# 2) 传感器监控 /system/sensors
# =========================

class TemperatureSensor(BaseModel):
    """
    单个温度传感器点，比如一个核心或者一个 NVMe 控制器
    """
    label: str                 # 标签，例如 "core0" / "Package id 0" / "nvme0"
    current: float             # 当前温度
    high: Optional[float] = None
    critical: Optional[float] = None
    group: Optional[str] = None  # 来自哪个组，例如 "coretemp" / "nvme"


class FanSensor(BaseModel):
    name: str                  # 风扇名称，例如 "cpu_fan"
    rpm: int                   # 当前转速，RPM


class BatteryStatus(BaseModel):
    present: bool              # 是否存在电池（台式机一般为 False）
    percent: Optional[float] = None      # 剩余电量百分比
    secs_left: Optional[int] = None      # 预计剩余秒数（-1/None 表示未知）
    power_plugged: Optional[bool] = None # 是否接入电源


class SensorsOverview(BaseModel):
    """
    传感器总览：
      - temperatures：所有温度点列表（CPU / NVMe / 芯片组等）
      - fans：风扇转速（如果支持）
      - battery：笔记本电池状态（如果有）
    不同平台支持程度不同，无法获取的字段会是空列表或 None。
    """
    collected_at: datetime

    temperatures: List[TemperatureSensor]
    fans: List[FanSensor]
    battery: Optional[BatteryStatus] = None


# =========================
# 3) 开机时长 /system/uptime
# =========================

class UptimeInfo(BaseModel):
    boot_time: datetime        # 开机时间（UTC 或你 FastAPI 默认时区）
    uptime_seconds: float      # 运行了多少秒
    uptime_human: str          # 已格式化的人类可读描述，例如 "3 days 4 hours 12 minutes"


class SystemEvent(BaseModel):
    timestamp: datetime
    level: Optional[str] = None   # info / warning / error ...
    source: Optional[str] = None
    message: str

# =========================
# 4) 系统事件 /system/events
# =========================
class SystemEventsOverview(BaseModel):
    items: List[SystemEvent]


class ResourcePoint(BaseModel):
    ts: datetime
    cpu_pct: float
    memory_pct: float
    net_rx_mbps: float
    net_tx_mbps: float


class ResourceTrend(BaseModel):
    points: List[ResourcePoint]


class ScheduleEntry(BaseModel):
    expression: str           # "* * * * *"
    command: str
    comment: Optional[str] = None


class ScheduleOverview(BaseModel):
    entries: List[ScheduleEntry]


class FileEntry(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: Optional[int] = None


class FileList(BaseModel):
    base_path: str
    entries: List[FileEntry]


class LoginRecord(BaseModel):
    username: str
    host: str
    timestamp: datetime
    tty: Optional[str] = None
    duration: Optional[str] = None


class LoginHistory(BaseModel):
    records: List[LoginRecord]