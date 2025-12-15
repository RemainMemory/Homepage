# backend/app/core/resource_trend.py
from collections import deque
from datetime import datetime
from typing import Deque

import psutil

from app.models.system import ResourcePoint, ResourceTrend

# 最多保存多少个点，例如 3600 = 最近 1 小时（按 1 秒一次）
_MAX_POINTS = 3600
_points: Deque[ResourcePoint] = deque(maxlen=_MAX_POINTS)


def push_resource_point():
    cpu = psutil.cpu_percent(interval=0.0)
    mem = psutil.virtual_memory().percent

    # 网络用总 io 变化会更准，这里简单不做速率，只做占位
    # 你可以和之前 network_info 复用逻辑
    net = psutil.net_io_counters()
    # 为避免复杂计算，先填 0，未来你可改成基于差值的 Mbps
    rx = 0.0
    tx = 0.0

    pt = ResourcePoint(
        ts=datetime.utcnow(),
        cpu_pct=cpu,
        memory_pct=mem,
        net_rx_mbps=rx,
        net_tx_mbps=tx,
    )
    _points.append(pt)


def get_resource_trend(limit: int = 100) -> ResourceTrend:
    """
    返回最近 limit 个点，调用前自动 push 当前点。
    建议你在前端轮询这个接口，间隔 3~5 秒即可。
    """
    push_resource_point()
    pts = list(_points)[-limit:]
    return ResourceTrend(points=pts)
