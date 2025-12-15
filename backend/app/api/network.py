# app/api/network.py
from fastapi import APIRouter

from app.core.network import (
    get_network_overview,
    get_lan_devices,
    run_speedtest,
)
from app.models.network import (
    NetworkOverview,
    LanDevicesOverview,
    SpeedTestResult,
)

router = APIRouter()


@router.get("/overview", response_model=NetworkOverview)
async def network_overview():
    """
    返回当前主机的网络总览信息：
      - summary: 顶部总览卡（主出口速率 / 公网 IP / 延迟）
      - interfaces: 网卡列表（物理 / 虚拟 / loopback）
      - connectivity: 连通性与延迟
      - routes: 默认网关 / 公网 IP / 路由表（最佳努力）
    """
    overview = get_network_overview()
    return overview


@router.get("/lan-devices", response_model=LanDevicesOverview)
async def network_lan_devices():
    """
    返回基于 ARP 表的局域网设备列表（最佳努力）。
    注意：只能看到近期有过通信的设备。
    """
    return get_lan_devices()


@router.get("/speedtest", response_model=SpeedTestResult)
async def network_speedtest():
    """
    运行一次网络测速。
    依赖外部 speedtest/speedtest-cli 命令存在。
    """
    return run_speedtest()