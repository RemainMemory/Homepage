# backend/app/core/network/__init__.py

from .overview import get_network_overview
from .lan_devices import get_lan_devices
from .speedtest import run_speedtest

__all__ = [
    "get_network_overview",
    "get_lan_devices",
    "run_speedtest",
]
