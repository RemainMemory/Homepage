# backend/app/core/system_info.py
import os
from typing import Optional

import psutil

from app.models.system import (
    CpuSummary,
    MemorySummary,
    DiskSummary,
    SystemSummary,
)


# ========= CPU =========

def get_cpu_summary() -> CpuSummary:
    """
    获取 CPU 详细信息：
    - usagePct: 总使用率
    - load1/load5/load15: 1/5/15 分钟平均负载
    - cores: 逻辑核心数
    - perCoreUsage: 每个核心的使用率
    - userPct/systemPct/idlePct/iowaitPct: 各类 CPU 时间占比
    """
    # 总使用率（短暂采样）
    usage = psutil.cpu_percent(interval=0.2)

    # 每个核心的使用率
    per_core = psutil.cpu_percent(interval=None, percpu=True)

    # load average（Windows 上没有）
    try:
        load1, load5, load15 = psutil.getloadavg()
    except (AttributeError, OSError):
        load1 = load5 = load15 = 0.0

    cores = psutil.cpu_count(logical=True) or 0

    # 各类 CPU 时间占比
    times_percent = psutil.cpu_times_percent(interval=0.0)
    user_pct = getattr(times_percent, "user", 0.0)
    system_pct = getattr(times_percent, "system", 0.0)
    idle_pct = getattr(times_percent, "idle", 0.0)
    iowait_pct = getattr(times_percent, "iowait", 0.0) if hasattr(times_percent, "iowait") else 0.0

    return CpuSummary(
        usagePct=round(usage, 1),
        load1=round(load1, 2),
        load5=round(load5, 2),
        load15=round(load15, 2),
        cores=cores,
        perCoreUsage=[round(v, 1) for v in per_core],
        userPct=round(user_pct, 1),
        systemPct=round(system_pct, 1),
        idlePct=round(idle_pct, 1),
        iowaitPct=round(iowait_pct, 1),
    )


# ========= Memory =========

def get_memory_summary() -> MemorySummary:
    """
    获取内存详细信息：
    - 使用率 / 总量 / 已用 / 可用
    - 缓存/缓冲区
    - swap 使用情况
    """
    mem = psutil.virtual_memory()
    total_gb = mem.total / 1024**3
    used_gb = (mem.total - mem.available) / 1024**3
    available_gb = mem.available / 1024**3

    # 尝试估算缓存（不同平台字段略有差异）
    cached_bytes = getattr(mem, "cached", 0) + getattr(mem, "buffers", 0)
    cached_gb = cached_bytes / 1024**3

    swap = psutil.swap_memory()
    swap_total_gb = swap.total / 1024**3
    swap_used_gb = swap.used / 1024**3
    swap_usage_pct = swap.percent

    return MemorySummary(
        usagePct=round(mem.percent, 1),
        totalGb=round(total_gb, 1),
        usedGb=round(used_gb, 1),
        availableGb=round(available_gb, 1),
        cachedGb=round(cached_gb, 1),
        swapUsagePct=round(swap_usage_pct, 1),
        swapTotalGb=round(swap_total_gb, 1),
        swapUsedGb=round(swap_used_gb, 1),
    )


# ========= Disk（主盘摘要，跨平台） =========

def _default_mount_for_current_os() -> str:
    """
    不传 mount 时，根据当前操作系统选一个“主盘”挂载点：
    - Windows: 系统盘（C:\）或环境变量 SystemDrive
    - 其他: 根挂载点 "/"
    """
    if os.name == "nt":  # Windows
        system_drive = os.environ.get("SystemDrive", "C:")
        system_drive = system_drive.strip()
        if not system_drive.endswith("\\"):
            system_drive = system_drive.rstrip(":") + ":\\"
        return system_drive
    else:
        return "/"


def _normalize_mount_for_os(mount: Optional[str]) -> str:
    """
    将 mount 统一成当前 OS 可接受的格式：
    - 如果为 None 或空字符串，则使用默认盘
    - Windows 上将 'C' / 'C:' 正规化为 'C:\\'
    - 其他系统保持原样（默认 '/'）
    """
    if not mount:
        return _default_mount_for_current_os()

    if os.name == "nt":
        m = mount.strip()
        # 去尾部斜杠
        m = m.rstrip("\\/")
        # 补冒号
        if not m.endswith(":"):
            if len(m) == 1:  # "C"
                m = m + ":"
        # 补反斜杠
        m = m + "\\"
        return m

    # 非 Windows 下，直接返回
    return mount


def get_disk_summary(mount: Optional[str] = None) -> DiskSummary:
    """
    获取指定挂载点对应卷的磁盘使用情况（跨平台）：
    - mount 为空时，自动选择主盘：
        - Windows: 系统盘（C:\）
        - 其他："/"
    - 文件系统类型 fsType 通过 psutil.disk_partitions 获取：
        - 支持 NTFS / APFS / ext4 / exFAT / FAT32 等所有系统能识别的格式
    """
    norm_mount = _normalize_mount_for_os(mount)

    usage = psutil.disk_usage(norm_mount)
    total_gb = usage.total / 1024**3
    used_gb = usage.used / 1024**3
    free_gb = usage.free / 1024**3

    device = norm_mount
    fs_type = "unknown"

    try:
        partitions = psutil.disk_partitions(all=False)
        norm_target = os.path.normcase(norm_mount.rstrip("\\/"))
        for p in partitions:
            mp = os.path.normcase(p.mountpoint.rstrip("\\/"))
            if mp == norm_target:
                device = p.device
                fs_type = p.fstype or "unknown"
                break
    except Exception:
        pass

    return DiskSummary(
        device=device,
        mount=norm_mount,
        fsType=fs_type,
        usagePct=round(usage.percent, 1),
        totalGb=round(total_gb, 1),
        usedGb=round(used_gb, 1),
        freeGb=round(free_gb, 1),
    )


# ========= System 汇总 =========

def get_system_summary(mount: Optional[str] = None) -> SystemSummary:
    """
    汇总整个主机状态：CPU + 内存 + 指定磁盘（跨平台友好）
    """
    cpu = get_cpu_summary()
    memory = get_memory_summary()
    disk = get_disk_summary(mount=mount)
    return SystemSummary(cpu=cpu, memory=memory, disk=disk)
