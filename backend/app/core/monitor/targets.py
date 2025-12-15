# backend/app/core/monitor/targets.py
import asyncio
import socket
import time
from datetime import datetime
from typing import List

import httpx

from app.models.monitor import (
    MonitorOverview,
    MonitorSummary,
    MonitorTargetConfig,
    MonitorTargetStatus,
)

# TODO: 后面可以改为从配置文件 / 数据库读取
MONITOR_TARGETS: List[MonitorTargetConfig] = [
    MonitorTargetConfig(
        name="Google",
        type="http",
        url="https://www.google.com",
        timeout=3.0,
    ),
]


async def _check_http_target(cfg: MonitorTargetConfig) -> MonitorTargetStatus:
    assert cfg.url, "http target must have url"
    start = time.monotonic()
    status = "offline"
    code = None
    latency_ms = None

    try:
        async with httpx.AsyncClient(
            verify=False,
            follow_redirects=True,
            timeout=cfg.timeout,
        ) as client:
            resp = await client.get(cfg.url)
        end = time.monotonic()
        code = resp.status_code
        latency_ms = (end - start) * 1000.0
        status = "online" if 200 <= code < 400 else "offline"
    except Exception:
        status = "offline"

    return MonitorTargetStatus(
        name=cfg.name,
        type="http",
        url=cfg.url,
        status=status,
        code=code,
        latency_ms=latency_ms,
        checked_at=datetime.utcnow(),
    )


async def _check_tcp_target(cfg: MonitorTargetConfig) -> MonitorTargetStatus:
    assert cfg.host and cfg.port, "tcp target must have host & port"
    start = time.monotonic()
    status = "offline"
    latency_ms = None

    try:
        with socket.create_connection((cfg.host, cfg.port), timeout=cfg.timeout):
            end = time.monotonic()
            latency_ms = (end - start) * 1000.0
            status = "online"
    except OSError:
        status = "offline"

    return MonitorTargetStatus(
        name=cfg.name,
        type="tcp",
        host=cfg.host,
        port=cfg.port,
        status=status,
        code=None,
        latency_ms=latency_ms,
        checked_at=datetime.utcnow(),
    )


async def get_monitor_overview() -> MonitorOverview:
    # 没有配置目标时直接返回空
    if not MONITOR_TARGETS:
        summary = MonitorSummary(
            total=0,
            online=0,
            offline=0,
            avg_latency_ms=None,
        )
        return MonitorOverview(summary=summary, targets=[])

    tasks = []
    for cfg in MONITOR_TARGETS:
        if cfg.type == "http":
            tasks.append(_check_http_target(cfg))
        else:
            tasks.append(_check_tcp_target(cfg))

    # 关键：await asyncio.gather
    results: List[MonitorTargetStatus] = await asyncio.gather(
        *tasks,
        return_exceptions=False,
    )

    online = sum(1 for r in results if r.status == "online")
    offline = len(results) - online
    latencies = [r.latency_ms for r in results if r.latency_ms is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else None

    summary = MonitorSummary(
        total=len(results),
        online=online,
        offline=offline,
        avg_latency_ms=avg_latency,
    )
    return MonitorOverview(summary=summary, targets=results)
