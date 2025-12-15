# backend/app/models/docker.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DockerServiceStatItem(BaseModel):
    label: str
    value: str
    hint: Optional[str] = None


class DockerServiceStats(BaseModel):
    title: str
    headline: Optional[str] = None
    items: List[DockerServiceStatItem] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)


class DockerServiceStatus(BaseModel):
    slug: str
    name: str
    container: Optional[str] = None
    image: Optional[str] = None
    state: str
    status_text: Optional[str] = None
    healthy: Optional[bool] = None
    online: bool
    latency_ms: Optional[float] = None
    response_code: Optional[int] = None
    endpoint: Optional[str] = None
    access_url: Optional[str] = None
    description: Optional[str] = None
    message: Optional[str] = None
    last_checked: datetime
    managed: bool = False
    icon: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    stats: Optional[DockerServiceStats] = None


class DockerSummary(BaseModel):
    total: int
    running: int
    online: int
    unhealthy: int


class DockerOverview(BaseModel):
    summary: DockerSummary
    services: List[DockerServiceStatus]
    message: Optional[str] = None


class DockerProbeConfigModel(BaseModel):
    url: Optional[str] = None
    method: str = "GET"
    timeout: float = 3.0
    expect_status: List[int] = Field(default_factory=list)


class DockerStatsConfigModel(BaseModel):
    type: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class DockerServiceConfigPayload(BaseModel):
    name: str
    container: Optional[str] = None
    description: Optional[str] = None
    access_url: Optional[str] = None
    icon: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    probe: DockerProbeConfigModel = DockerProbeConfigModel()
    stats: Optional[DockerStatsConfigModel] = None
    require_probe: bool = False
    managed: bool = True


class DockerServiceConfigModel(DockerServiceConfigPayload):
    slug: str
