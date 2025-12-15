# backend/app/core/system/uptime.py
from __future__ import annotations

from datetime import datetime, timezone

import psutil

from app.models.system import UptimeInfo


def get_uptime_info() -> UptimeInfo:
    boot_ts = psutil.boot_time()
    boot_dt = datetime.fromtimestamp(boot_ts, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)

    uptime_seconds = int((now - boot_dt).total_seconds())

    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes or not parts:
        parts.append(f"{minutes}m")

    uptime_human = " ".join(parts)

    # 关键：这里改成 snake_case 字段名
    return UptimeInfo(
        boot_time=boot_dt,
        uptime_seconds=uptime_seconds,
        uptime_human=uptime_human,
    )
