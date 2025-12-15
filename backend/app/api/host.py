# backend/app/api/host.py
import logging

from fastapi import APIRouter

from app.core.system import (
    get_system_summary,
    get_disk_devices_snapshot,
    get_processes_overview,
    get_sensors_overview,
    get_uptime_info,
)
from app.core.network import get_network_overview
from app.core.monitor import get_monitor_overview
from app.core.docker import get_docker_overview

from app.models.host import HostOverview

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/overview", response_model=HostOverview)
async def host_overview():
    # system 系列
    system_summary = get_system_summary(mount=None)
    disks = get_disk_devices_snapshot()
    processes = get_processes_overview(limit=10)
    sensors = get_sensors_overview()
    uptime = get_uptime_info()

    # network
    network = get_network_overview()

    # monitor：增加保护，监控模块异常时只影响自身
    try:
        monitor = await get_monitor_overview()
    except Exception as exc:  # noqa: BLE001
        logger.exception("failed to load monitor overview: %s", exc)
        monitor = None

    try:
        docker = await get_docker_overview()
    except Exception as exc:  # noqa: BLE001
        logger.exception("failed to load docker overview: %s", exc)
        docker = None

    return HostOverview(
        system=system_summary,
        disks=disks,
        processes=processes,
        sensors=sensors,
        uptime=uptime,
        network=network,
        monitor=monitor,   # 关键：一定要传 monitor
        docker=docker,
    )
