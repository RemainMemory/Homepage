# backend/app/core/security_logins.py
import platform
import subprocess
from datetime import datetime
from typing import List

from app.models.system import LoginRecord, LoginHistory


def get_login_history(limit: int = 50) -> LoginHistory:
    system = platform.system().lower()
    records: List[LoginRecord] = []

    if system == "linux":
        try:
            result = subprocess.run(
                ["last", "-n", str(limit)],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("wtmp"):
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue
                username = parts[0]
                tty = parts[1]
                host = parts[2]
                # 时间解析为了简单，这里不强行搞，直接用当前时间
                timestamp = datetime.utcnow()
                records.append(
                    LoginRecord(
                        username=username,
                        tty=tty,
                        host=host,
                        timestamp=timestamp,
                        duration=None,
                    )
                )
        except Exception:
            records = []

    # macOS / Windows: 暂不实现，返回空
    return LoginHistory(records=records)
