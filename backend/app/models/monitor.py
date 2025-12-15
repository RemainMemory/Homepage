# backend/app/models/monitor.py
from datetime import datetime
from typing import Optional, Literal, List

from pydantic import BaseModel


TargetType = Literal["http", "tcp"]


class MonitorTargetConfig(BaseModel):
    name: str
    type: TargetType
    url: Optional[str] = None       # type=http 时使用
    host: Optional[str] = None      # type=tcp 时使用
    port: Optional[int] = None      # type=tcp 时使用
    timeout: float = 3.0


class MonitorTargetStatus(BaseModel):
    name: str
    type: TargetType

    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None

    status: Literal["online", "offline"]
    code: Optional[int] = None          # HTTP 状态码; TCP 时可为 None
    latency_ms: Optional[float] = None

    checked_at: datetime


class MonitorSummary(BaseModel):
    total: int
    online: int
    offline: int
    avg_latency_ms: Optional[float] = None


class MonitorOverview(BaseModel):
    summary: MonitorSummary
    targets: List[MonitorTargetStatus]
