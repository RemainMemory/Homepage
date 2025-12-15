# backend/app/core/disks_info.py
import os
from datetime import datetime, timezone
from typing import List, Set

import psutil

from app.models.system import DiskDevice, DiskDevicesSnapshot


# 模块级变量：保存上一轮的 device 集合，用于计算 added/removed
_last_devices: Set[str] = set()


def _guess_is_removable(partition: psutil._common.sdiskpart) -> bool:
    """
    粗略判断分区是否为可移动设备（U盘/移动硬盘等）。
    不同平台信息不完全一致，只做“尽力而为”的猜测：
    - Windows: opts 中包含 'removable'
    - Linux: /media 或 /run/media 下挂载
    - macOS: /Volumes 下挂载，或 device 名带 usb 等
    """
    opts = (partition.opts or "").lower()
    mount = partition.mountpoint
    device = partition.device.lower()

    # Windows: removable 设备
    if "removable" in opts:
        return True

    # Linux: 常见 U 盘挂载路径
    if mount.startswith("/media/") or mount.startswith("/run/media/"):
        return True

    # macOS: 外接盘常见挂载路径
    if mount.startswith("/Volumes/"):
        if "usb" in device or "external" in device:
            return True

    # 兜底：device 名里带 usb
    if "usb" in device:
        return True

    return False


def list_disk_devices() -> List[DiskDevice]:
    """
    列出当前系统所有“正常挂载”的磁盘分区。
    自动适配 mac / Linux / Windows，文件系统类型由 OS 决定。
    """
    devices: List[DiskDevice] = []

    partitions = psutil.disk_partitions(all=False)

    for p in partitions:
        mount = p.mountpoint
        try:
            usage = psutil.disk_usage(mount)
        except (PermissionError, FileNotFoundError):
            continue

        total_gb = usage.total / 1024**3
        used_gb = usage.used / 1024**3
        free_gb = usage.free / 1024**3

        is_removable = _guess_is_removable(p)

        devices.append(
            DiskDevice(
                device=p.device,
                mount=mount,
                fsType=p.fstype or "unknown",
                usagePct=round(usage.percent, 1),
                totalGb=round(total_gb, 1),
                usedGb=round(used_gb, 1),
                freeGb=round(free_gb, 1),
                isRemovable=is_removable,
            )
        )

    return devices


def get_disk_devices_snapshot() -> DiskDevicesSnapshot:
    """
    返回当前设备列表 + 和上一轮相比的新增/删除。
    变化记录只保存在进程内存中，重启服务后会重新开始计算。
    """
    global _last_devices

    devices = list_disk_devices()
    current_ids = {d.device for d in devices}

    if not _last_devices:
        added = list(current_ids)
        removed: List[str] = []
    else:
        added = list(current_ids - _last_devices)
        removed = list(_last_devices - current_ids)

    _last_devices = current_ids

    snapshot_id = datetime.now(timezone.utc).isoformat()

    return DiskDevicesSnapshot(
        devices=devices,
        added=sorted(added),
        removed=sorted(removed),
        snapshotId=snapshot_id,
    )
