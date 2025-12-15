# backend/app/core/system_events.py
import platform
import subprocess
from datetime import datetime
from typing import List

from app.models.system import SystemEvent, SystemEventsOverview


def _parse_linux_journal(lines: List[str]) -> List[SystemEvent]:
    events: List[SystemEvent] = []
    for line in lines:
        # journalctl -o short-iso: 2025-12-11T17:00:00+08:00 hostname process[pid]: message
        if not line.strip():
            continue
        try:
            ts_str, rest = line.split(" ", 1)
            timestamp = datetime.fromisoformat(ts_str)
        except Exception:
            # fallback: 当前时间
            timestamp = datetime.utcnow()
            rest = line

        events.append(SystemEvent(timestamp=timestamp, message=rest.strip()))
    return events


def _parse_macos_log(lines: List[str]) -> List[SystemEvent]:
    events: List[SystemEvent] = []
    for line in lines:
        if not line.strip():
            continue
        # macOS log show 格式比较复杂，这里简单直接把整行当 message
        events.append(
            SystemEvent(
                timestamp=datetime.utcnow(),
                message=line.strip(),
            )
        )
    return events


def get_system_events(limit: int = 100) -> SystemEventsOverview:
    system = platform.system().lower()
    events: List[SystemEvent] = []

    try:
        if system == "linux":
            result = subprocess.run(
                ["journalctl", "-n", str(limit), "-o", "short-iso"],
                capture_output=True,
                text=True,
                check=False,
            )
            lines = result.stdout.splitlines()
            events = _parse_linux_journal(lines)
        elif system == "darwin":
            result = subprocess.run(
                ["log", "show", "--style", "compact", "--last", "1h"],
                capture_output=True,
                text=True,
                check=False,
            )
            lines = result.stdout.splitlines()[-limit:]
            events = _parse_macos_log(lines)
        else:
            # Windows / 其它平台：暂时返回空列表
            events = []
    except Exception:
        events = []

    return SystemEventsOverview(items=events)
