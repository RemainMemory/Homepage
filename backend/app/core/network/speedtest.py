# backend/app/core/speedtest_info.py
import json
import shutil
import subprocess
from typing import Optional

from app.models.network import SpeedTestResult


def run_speedtest() -> SpeedTestResult:
    if not shutil.which("speedtest"):
        # Ookla 的官方 CLI 通常命令名为 speedtest
        # 如果你用的是 speedtest-cli，把上面改成 "speedtest-cli"
        return SpeedTestResult(
            ok=False,
            message="speedtest CLI not found. Please install 'speedtest' or 'speedtest-cli'.",
        )

    try:
        # 尝试使用 JSON 输出
        # 对于 Ookla CLI: speedtest -f json
        result = subprocess.run(
            ["speedtest", "-f", "json"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        raw = result.stdout
        data = json.loads(raw)

        ping_ms = float(data.get("ping", {}).get("latency", 0.0))
        download_bps = float(data.get("download", {}).get("bandwidth", 0.0)) * 8
        upload_bps = float(data.get("upload", {}).get("bandwidth", 0.0)) * 8

        return SpeedTestResult(
            ok=True,
            ping_ms=ping_ms,
            download_mbps=download_bps / 1_000_000,
            upload_mbps=upload_bps / 1_000_000,
            raw_output=raw,
        )
    except Exception as e:
        return SpeedTestResult(
            ok=False,
            message=f"speedtest failed: {e}",
        )
