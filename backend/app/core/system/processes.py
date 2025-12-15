# app/core/processes_info.py
from datetime import datetime
from typing import List

import psutil

from app.models.system import ProcessesOverview, ProcessInfo


def get_processes_overview(limit: int = 10) -> ProcessesOverview:
    """
    获取当前主机的进程概览（Top 进程）。
    - limit：返回前多少个占用最高的进程（CPU & 内存各 limit 个）
    注意：CPU 百分比需要多次采样才能绝对准确，这里采用 psutil 的
          非阻塞模式，随着你的接口被周期性调用，数值会逐渐稳定。
    """
    processes: List[ProcessInfo] = []

    # 预取一部分字段，避免频繁系统调用
    for proc in psutil.process_iter(
        ["pid", "name", "username", "memory_info", "memory_percent", "cmdline"]
    ):
        try:
            with proc.oneshot():
                pid = proc.info["pid"]
                name = proc.info.get("name") or f"pid-{pid}"
                username = proc.info.get("username")

                mem_info = proc.info.get("memory_info")
                mem_bytes = getattr(mem_info, "rss", 0) if mem_info else 0
                mem_mb = mem_bytes / (1024 * 1024)
                mem_pct = float(proc.info.get("memory_percent") or 0.0)

                # 这里使用 0.0 非阻塞采样，
                # 如果你每隔几秒轮询一次，这个值会相对合理
                cpu_pct = float(proc.cpu_percent(interval=0.0))

                cmdline_list = proc.info.get("cmdline") or []
                cmdline = " ".join(cmdline_list) if cmdline_list else None

                processes.append(
                    ProcessInfo(
                        pid=pid,
                        name=name,
                        username=username,
                        cpu_pct=cpu_pct,
                        memory_mb=mem_mb,
                        memory_pct=mem_pct,
                        cmdline=cmdline,
                    )
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # 某些进程在采集过程中退出或者无权限，直接跳过即可
            continue

    # 排序 & 取 Top N
    processes_by_cpu = sorted(
        processes, key=lambda p: p.cpu_pct, reverse=True
    )[:limit]

    processes_by_mem = sorted(
        processes, key=lambda p: p.memory_mb, reverse=True
    )[:limit]

    overview = ProcessesOverview(
        total=len(processes),
        collected_at=datetime.utcnow(),
        top_by_cpu=processes_by_cpu,
        top_by_memory=processes_by_mem,
    )
    return overview
