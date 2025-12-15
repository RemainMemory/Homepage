# backend/app/core/lan_devices.py
import platform
import re
import socket
import subprocess
from datetime import datetime
from typing import List

from app.models.network import LanDevice, LanDevicesOverview


def _parse_arp_output(output: str) -> List[LanDevice]:
    devices: List[LanDevice] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # Linux/macOS arp -a 格式: ? (192.168.50.1) at xx:xx:xx:xx:xx:xx on en0 ...
        m = re.search(r"\((?P<ip>\d+\.\d+\.\d+\.\d+)\)\s+at\s+(?P<mac>([0-9a-f]{2}:){5}[0-9a-f]{2})", line, re.I)
        if m:
            ip = m.group("ip")
            mac = m.group("mac")
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except OSError:
                hostname = None
            devices.append(LanDevice(ip=ip, mac=mac, hostname=hostname))
            continue

        # Windows arp -a 格式: 192.168.50.1       xx-xx-xx-xx-xx-xx     dynamic
        parts = line.split()
        if len(parts) >= 3 and re.match(r"\d+\.\d+\.\d+\.\d+", parts[0]):
            ip = parts[0]
            mac = parts[1].replace("-", ":")
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except OSError:
                hostname = None
            devices.append(LanDevice(ip=ip, mac=mac, hostname=hostname))

    return devices


def get_lan_devices() -> LanDevicesOverview:
    system = platform.system().lower()
    output = ""

    try:
        if system in ("linux", "darwin", "windows"):
            # 三大平台 arp 命令名字都叫 arp
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout
    except Exception:
        output = ""

    devices = _parse_arp_output(output)
    return LanDevicesOverview(
        collected_at=datetime.utcnow(),
        devices=devices,
    )
