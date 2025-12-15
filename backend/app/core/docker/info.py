# backend/app/core/docker/info.py
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

import httpx

from app.core.docker.config import (
    DockerServiceConfig,
    load_service_configs,
)
from app.core.docker.stats import fetch_service_stats
from app.models.docker import (
    DockerOverview,
    DockerServiceStatus,
    DockerSummary,
)
import logging

logger = logging.getLogger(__name__)

_DOCKER_BIN = shutil.which("docker")


def _docker_cli_available() -> bool:
    return _DOCKER_BIN is not None


def _inspect_container_sync(container: str) -> Dict:
    cmd = ["docker", "container", "inspect", container]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}

    if proc.returncode != 0:
        return {"error": proc.stderr.strip() or f"docker inspect failed for {container}"}

    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"error": "failed to parse docker inspect output"}

    if not parsed:
        return {}

    payload = parsed[0]
    state = payload.get("State", {}) or {}
    config = payload.get("Config", {}) or {}
    return {
        "Status": state.get("Status"),
        "Running": state.get("Running"),
        "Health": state.get("Health"),
        "Error": state.get("Error"),
        "StartedAt": state.get("StartedAt"),
        "FinishedAt": state.get("FinishedAt"),
        "Name": (payload.get("Name") or "").lstrip("/"),
        "Image": payload.get("Image") or config.get("Image"),
    }


async def _inspect_container(container: Optional[str]) -> Dict:
    if not container:
        return {}
    if not _docker_cli_available():
        return {"error": "docker CLI not found"}
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _inspect_container_sync, container)


async def _probe_http(
    url: str,
    method: str,
    timeout: float,
    expect_status: List[int],
) -> Dict:
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            verify=False,
        ) as client:
            resp = await client.request(method, url)
        latency_ms = (time.perf_counter() - start) * 1000
        if expect_status:
            ok = resp.status_code in expect_status
        else:
            ok = 200 <= resp.status_code < 400
        return {
            "ok": ok,
            "status_code": resp.status_code,
            "latency_ms": latency_ms,
            "message": None if ok else f"HTTP {resp.status_code}",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "status_code": None,
            "latency_ms": None,
            "message": str(exc),
        }


def _state_from_status(state_raw: Optional[str]) -> str:
    if not state_raw:
        return "unknown"
    text = state_raw.lower()
    if text.startswith("running"):
        return "running"
    if text.startswith("exited"):
        return "exited"
    if text.startswith("paused"):
        return "paused"
    if text.startswith("dead"):
        return "dead"
    return text.split()[0]


def _parse_healthy(state_info: Dict) -> Optional[bool]:
    health = state_info.get("Health") if isinstance(state_info, dict) else None
    if not health:
        return None
    status = (health.get("Status") or "").lower()
    if status == "healthy":
        return True
    if status == "unhealthy":
        return False
    return None


def _resolve_online(
    running: Optional[bool],
    probe_ok: Optional[bool],
    require_probe: bool,
) -> bool:
    if require_probe:
        return bool(probe_ok)

    if running is True:
        return probe_ok if probe_ok is not None else True
    if running is False:
        return bool(probe_ok)

    return bool(probe_ok)


async def _build_service_status(cfg: DockerServiceConfig) -> DockerServiceStatus:
    inspected = await _inspect_container(cfg.container)
    state_raw = inspected.get("Status") if isinstance(inspected, dict) else None
    state = _state_from_status(state_raw)
    running = inspected.get("Running") if isinstance(inspected, dict) else None
    healthy = _parse_healthy(inspected) if inspected else None
    docker_message = None
    if isinstance(inspected, dict):
        docker_message = inspected.get("Error") or inspected.get("error")
    elif inspected:
        docker_message = str(inspected)

    now = datetime.utcnow()
    probe_cfg = cfg.probe
    probe_result = None
    endpoint = probe_cfg.url if probe_cfg else None
    if probe_cfg and probe_cfg.url:
        probe_result = await _probe_http(
            probe_cfg.url,
            probe_cfg.method,
            probe_cfg.timeout,
            probe_cfg.expect_status,
        )

    probe_ok = probe_result["ok"] if probe_result else None
    online = _resolve_online(running, probe_ok, cfg.require_probe)
    response_code = probe_result["status_code"] if probe_result else None
    latency_ms = probe_result["latency_ms"] if probe_result else None
    message = docker_message
    if probe_result and probe_result.get("message"):
        message = (message + "; " if message else "") + probe_result["message"]

    stats = None
    try:
        stats = await fetch_service_stats(cfg)
    except Exception as exc:  # noqa: BLE001
        logger.exception("failed to fetch stats for %s: %s", cfg.name, exc)

    return DockerServiceStatus(
        slug=cfg.slug,
        name=cfg.name,
        container=inspected.get("Name") if isinstance(inspected, dict) and inspected.get("Name") else cfg.container,
        image=inspected.get("Image") if isinstance(inspected, dict) else None,
        state=state,
        status_text=state_raw or message or "unknown",
        healthy=healthy if healthy is not None else probe_ok,
        online=online,
        latency_ms=latency_ms,
        response_code=response_code,
        endpoint=endpoint,
        access_url=cfg.access_url,
        description=cfg.description,
        message=message,
        last_checked=now,
        managed=cfg.managed,
        icon=cfg.icon,
        tags=cfg.tags,
        stats=stats,
    )


async def get_docker_overview() -> DockerOverview:
    configs = load_service_configs()
    tasks = [_build_service_status(cfg) for cfg in configs]
    services = await asyncio.gather(*tasks) if tasks else []

    total = len(services)
    running = sum(1 for svc in services if svc.state == "running")
    online = sum(1 for svc in services if svc.online)
    unhealthy = sum(1 for svc in services if svc.healthy is False or not svc.online)

    summary = DockerSummary(
        total=total,
        running=running,
        online=online,
        unhealthy=unhealthy,
    )

    overview_message = None
    if not _docker_cli_available():
        overview_message = "docker CLI not found，已降级为探活结果"

    return DockerOverview(summary=summary, services=services, message=overview_message)
