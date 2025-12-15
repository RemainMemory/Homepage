# app/core/sensors_info.py
from datetime import datetime
from typing import List

import psutil

from app.models.system import (
    SensorsOverview,
    TemperatureSensor,
    FanSensor,
    BatteryStatus,
)


def get_sensors_overview() -> SensorsOverview:
    """
    获取当前主机的传感器信息。
    - 在 Linux 上支持最好（温度 / 风扇）。
    - Windows / macOS 上，部分接口可能返回 None，此时返回空列表或 battery=None。
    """
    temperatures: List[TemperatureSensor] = []
    fans: List[FanSensor] = []
    battery: BatteryStatus | None = None

    # 温度（Linux 上最有效）
    try:
        temps = psutil.sensors_temperatures(fahrenheit=False)  # dict[str, list[shwtemp]]
        if temps:
            for group_name, entries in temps.items():
                for entry in entries:
                    temperatures.append(
                        TemperatureSensor(
                            label=entry.label or group_name,
                            current=entry.current,
                            high=entry.high,
                            critical=entry.critical,
                            group=group_name,
                        )
                    )
    except (AttributeError, NotImplementedError):
        # 当前平台不支持温度
        pass

    # 风扇（同样主要在 Linux 有用）
    try:
        fans_info = psutil.sensors_fans()
        if fans_info:
            for group_name, entries in fans_info.items():
                for entry in entries:
                    fans.append(
                        FanSensor(
                            name=entry.label or group_name,
                            rpm=entry.current,
                        )
                    )
    except (AttributeError, NotImplementedError):
        # 当前平台不支持风扇
        pass

    # 电池（笔记本上通常可用，台式机大多为 None）
    try:
        b = psutil.sensors_battery()
        if b is not None:
            secs_left = None
            if b.secsleft not in (psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED):
                secs_left = int(b.secsleft)
            battery = BatteryStatus(
                present=True,
                percent=float(b.percent) if b.percent is not None else None,
                secs_left=secs_left,
                power_plugged=b.power_plugged,
            )
        else:
            battery = BatteryStatus(present=False)
    except (AttributeError, NotImplementedError):
        battery = None

    return SensorsOverview(
        collected_at=datetime.utcnow(),
        temperatures=temperatures,
        fans=fans,
        battery=battery,
    )
