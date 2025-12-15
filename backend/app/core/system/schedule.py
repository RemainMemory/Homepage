# backend/app/core/schedule_info.py
import platform
import subprocess
from typing import List

from app.models.system import ScheduleEntry, ScheduleOverview


def get_schedule_overview() -> ScheduleOverview:
    system = platform.system().lower()
    entries: List[ScheduleEntry] = []

    if system == "linux":
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 6:
                    continue
                expr = " ".join(parts[:5])
                cmd = " ".join(parts[5:])
                entries.append(ScheduleEntry(expression=expr, command=cmd))
        except Exception:
            pass
    # macOS / Windows: 暂不支持，返回空列表

    return ScheduleOverview(entries=entries)
