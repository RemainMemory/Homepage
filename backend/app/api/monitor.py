# backend/app/api/monitor.py
from fastapi import APIRouter

from app.core.monitor import get_monitor_overview
from app.models.monitor import MonitorOverview

router = APIRouter()

@router.get("/targets", response_model=MonitorOverview)
async def monitor_targets():
    overview = await get_monitor_overview()
    return overview
