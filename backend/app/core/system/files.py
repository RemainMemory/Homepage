# backend/app/core/files_info.py
import os
from typing import List

from app.models.system import FileEntry, FileList

# 你可以改成配置项
ROOT_PATH = "/"  # 或者 "/Users/xxx"


def list_files(base_path: str) -> FileList:
    # 防止越权访问：如果 base_path 不在 ROOT_PATH 下，强制用 ROOT_PATH
    norm_root = os.path.abspath(ROOT_PATH)
    norm_base = os.path.abspath(base_path or ROOT_PATH)
    if not norm_base.startswith(norm_root):
        norm_base = norm_root

    entries: List[FileEntry] = []

    try:
        for name in os.listdir(norm_base):
            path = os.path.join(norm_base, name)
            try:
                st = os.stat(path)
                entries.append(
                    FileEntry(
                        name=name,
                        path=path,
                        is_dir=os.path.isdir(path),
                        size=None if os.path.isdir(path) else st.st_size,
                    )
                )
            except OSError:
                continue
    except OSError:
        # 目录不存在或无权限
        entries = []

    return FileList(base_path=norm_base, entries=entries)
