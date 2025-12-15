from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re
import uuid

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "docker_services.yaml"


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or uuid.uuid4().hex[:8]


@dataclass
class DockerProbeConfig:
    url: Optional[str] = None
    method: str = "GET"
    timeout: float = 3.0
    expect_status: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> "DockerProbeConfig":
        if not data:
            return cls()
        return cls(
            url=data.get("url"),
            method=(data.get("method") or "GET").upper(),
            timeout=float(data.get("timeout", 3.0)),
            expect_status=list(data.get("expect_status", [])),
        )

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "method": self.method,
            "timeout": self.timeout,
            "expect_status": self.expect_status,
        }


@dataclass
class DockerStatsConfig:
    type: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    extra: Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> Optional["DockerStatsConfig"]:
        if not data:
            return None
        return cls(
            type=data.get("type"),
            url=data.get("url"),
            api_key=data.get("api_key"),
            extra=data.get("extra") or {},
        )

    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "url": self.url,
            "api_key": self.api_key,
            "extra": self.extra,
        }


@dataclass
class DockerServiceConfig:
    slug: str
    name: str
    container: Optional[str] = None
    description: Optional[str] = None
    access_url: Optional[str] = None
    icon: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    probe: DockerProbeConfig = field(default_factory=DockerProbeConfig)
    stats: Optional[DockerStatsConfig] = None
    require_probe: bool = False
    managed: bool = True

    @classmethod
    def from_dict(cls, data: Dict) -> "DockerServiceConfig":
        slug = data.get("slug") or _slugify(data.get("name", uuid.uuid4().hex[:6]))
        return cls(
            slug=slug,
            name=data.get("name", slug),
            container=data.get("container"),
            description=data.get("description"),
            access_url=data.get("access_url"),
            icon=data.get("icon"),
            tags=list(data.get("tags", [])),
            probe=DockerProbeConfig.from_dict(data.get("probe") or {
                "url": data.get("probe_url"),
                "method": data.get("probe_method"),
                "timeout": data.get("probe_timeout"),
                "expect_status": data.get("expect_status"),
            }),
            stats=DockerStatsConfig.from_dict(data.get("stats")),
            require_probe=bool(data.get("require_probe", False)),
            managed=bool(data.get("managed", True)),
        )

    def to_dict(self) -> Dict:
        base = {
            "slug": self.slug,
            "name": self.name,
            "container": self.container,
            "description": self.description,
            "access_url": self.access_url,
            "icon": self.icon,
            "tags": self.tags,
            "probe": self.probe.to_dict(),
            "require_probe": self.require_probe,
            "managed": self.managed,
        }
        if self.stats:
            base["stats"] = self.stats.to_dict()
        return base


def _ensure_config_path():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        with CONFIG_PATH.open("w", encoding="utf-8") as fh:
            yaml.safe_dump({"services": []}, fh, allow_unicode=True, sort_keys=False)


def load_service_configs() -> List[DockerServiceConfig]:
    _ensure_config_path()
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    items = raw.get("services") if isinstance(raw, dict) else raw
    configs: List[DockerServiceConfig] = []
    for item in items or []:
        try:
            configs.append(DockerServiceConfig.from_dict(item or {}))
        except Exception:
            continue
    return configs


def save_service_configs(configs: List[DockerServiceConfig]) -> None:
    data = {"services": [cfg.to_dict() for cfg in configs]}
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)


def get_service_by_slug(slug: str) -> Optional[DockerServiceConfig]:
    for cfg in load_service_configs():
        if cfg.slug == slug:
            return cfg
    return None


def upsert_service(config: DockerServiceConfig) -> DockerServiceConfig:
    configs = load_service_configs()
    updated = False
    for idx, existing in enumerate(configs):
        if existing.slug == config.slug:
            configs[idx] = config
            updated = True
            break
    if not updated:
        configs.append(config)
    save_service_configs(configs)
    return config


def remove_service(slug: str) -> bool:
    configs = load_service_configs()
    new_configs = [cfg for cfg in configs if cfg.slug != slug]
    if len(new_configs) == len(configs):
        return False
    save_service_configs(new_configs)
    return True


def create_service_from_payload(payload: Dict) -> DockerServiceConfig:
    slug = payload.get("slug") or _slugify(payload.get("name", uuid.uuid4().hex[:6]))
    config = DockerServiceConfig.from_dict({**payload, "slug": slug})
    return upsert_service(config)


def update_service_from_payload(slug: str, payload: Dict) -> Optional[DockerServiceConfig]:
    existing = get_service_by_slug(slug)
    if not existing:
        return None
    base = existing.to_dict()
    base.update(payload)
    base["slug"] = slug
    config = DockerServiceConfig.from_dict(base)
    return upsert_service(config)
