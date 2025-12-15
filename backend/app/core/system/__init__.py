# backend/app/core/system/__init__.py

from .summary import get_system_summary
from .disks import get_disk_devices_snapshot
from .processes import get_processes_overview
from .sensors import get_sensors_overview
from .uptime import get_uptime_info
from .events import get_system_events
from .resource_trend import get_resource_trend
from .schedule import get_schedule_overview
from .files import list_files
from .security_logins import get_login_history

__all__ = [
    "get_system_summary",
    "get_disk_devices_snapshot",
    "get_processes_overview",
    "get_sensors_overview",
    "get_uptime_info",
    "get_system_events",
    "get_resource_trend",
    "get_schedule_overview",
    "list_files",
    "get_login_history",
]
