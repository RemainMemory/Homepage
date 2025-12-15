# backend/app/api/system.py
from fastapi import APIRouter, Query

from app.core.system import (
    get_system_summary,
    get_disk_devices_snapshot,
    get_processes_overview,
    get_sensors_overview,
    get_uptime_info,
    get_system_events,
    get_resource_trend,
    get_schedule_overview,
    list_files,
    get_login_history,
)

from app.models.system import (
    SystemSummary,
    DiskDevicesSnapshot,
    ProcessesOverview,
    SensorsOverview,
    UptimeInfo,
    SystemEventsOverview,
    ResourceTrend,
    ScheduleOverview,
    FileList,
    LoginHistory,
)

router = APIRouter()


@router.get("/summary", response_model=SystemSummary)
async def system_summary(
    mount: str | None = Query(
        None,
        description="要监控的磁盘挂载点/盘符，例如 '/', '/data', 'C', 'C:', 'C:\\' 等",
    )
):
    """
    返回主机监控信息（CPU + 内存 + 单个主磁盘摘要）。
    mount:
      - 不传时：自动选择当前系统主盘（mac/Linux 用 '/', Windows 用系统盘 C:\\）
      - 类 Unix: '/', '/data'
      - Windows: 'C', 'C:', 'C:\\' 均可
    """
    summary = get_system_summary(mount=mount)
    return summary


@router.get("/disks", response_model=DiskDevicesSnapshot)
async def system_disks():
    """
    返回当前所有已挂载磁盘设备列表，
    并给出相较于上一次调用时新增/移除的设备。
    可用于前端轮询检测 U 盘/移动硬盘接入/拔出。
    """
    snapshot = get_disk_devices_snapshot()
    return snapshot


@router.get("/processes", response_model=ProcessesOverview)
async def system_processes(
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="返回前 N 个占用最高的进程（1~50，默认 10）",
    )
):
    """
    返回当前主机的 Top 进程信息：
      - top_by_cpu: 按 CPU 排序的前 N 个进程
      - top_by_memory: 按内存排序的前 N 个进程
    """
    overview = get_processes_overview(limit=limit)
    return overview


@router.get("/sensors", response_model=SensorsOverview)
async def system_sensors():
    """
    返回当前主机的温度 / 风扇 / 电池信息。
    不同平台支持程度不同：
      - Linux: 通常可以获取温度 / 风扇 / 电池
      - Windows / macOS: 可能仅电池可用，其余为空
    """
    overview = get_sensors_overview()
    return overview


@router.get("/uptime", response_model=UptimeInfo)
async def system_uptime():
    """
    返回当前主机的开机时间与已运行时长。
    """
    info = get_uptime_info()
    return info


@router.get("/events", response_model=SystemEventsOverview)
async def system_events(
    limit: int = Query(
        100,
        ge=10,
        le=1000,
        description="返回最近的系统事件条数（10~1000，默认 100）",
    )
):
    """
    系统事件 / 日志概要。
      - Linux: 使用 journalctl -n
      - macOS: 使用 log show --last 1h
      - 其它平台: 返回空列表
    """
    return get_system_events(limit=limit)


@router.get("/resource-trend", response_model=ResourceTrend)
async def system_resource_trend(
    limit: int = Query(
        100,
        ge=10,
        le=1000,
        description="返回最近的资源采样点数量（10~1000，默认 100）",
    )
):
    """
    CPU / 内存 / 网络的简易趋势。
    每次调用会 push 一个新的点，然后返回最近 limit 个点。
    建议前端 3~5 秒轮询一次。
    """
    return get_resource_trend(limit=limit)


@router.get("/schedule", response_model=ScheduleOverview)
async def system_schedule():
    """
    定时任务：
      - Linux: 当前用户 crontab -l
      - 其它平台: 暂不支持，返回空列表
    """
    return get_schedule_overview()


@router.get("/files", response_model=FileList)
async def system_files(
    path: str | None = Query(
        None,
        description="要浏览的目录路径（会限制在后端配置的 ROOT_PATH 内）",
    )
):
    """
    简易只读文件浏览。
    出于安全考虑，路径会限制在 ROOT_PATH 子目录内。
    """
    return list_files(path or "/")


@router.get("/security/logins", response_model=LoginHistory)
async def system_login_history(
    limit: int = Query(
        50,
        ge=10,
        le=200,
        description="返回最近的登录记录数量（10~200，默认 50）",
    )
):
    """
    登录历史：
      - Linux: 使用 last -n
      - 其它平台: 暂不支持，返回空列表
    """
    return get_login_history(limit=limit)
