from __future__ import annotations

from typing import Optional

import httpx

from app.core.docker.config import DockerServiceConfig, DockerStatsConfig
from app.models.docker import DockerServiceStatItem, DockerServiceStats


async def fetch_service_stats(cfg: DockerServiceConfig) -> Optional[DockerServiceStats]:
    stats_cfg = cfg.stats
    if not stats_cfg or not stats_cfg.type:
        return None

    if stats_cfg.type == "emby":
        return await _fetch_emby_stats(stats_cfg)

    return None


async def _fetch_emby_stats(stats_cfg: DockerStatsConfig) -> Optional[DockerServiceStats]:
    if not stats_cfg.url or not stats_cfg.api_key:
        return None

    base = stats_cfg.url.rstrip("/")
    params = {"api_key": stats_cfg.api_key}
    try:
        async with httpx.AsyncClient(timeout=5.0, verify=False) as client:
            counts = await client.get(f"{base}/Items/Counts", params=params)
            sessions = await client.get(f"{base}/Sessions", params=params)
    except httpx.HTTPError:
        return None

    counts_json = counts.json() if counts.is_success else {}
    sessions_json = sessions.json() if sessions.is_success else []

    playing = [
        sess.get("NowPlayingItem", {}).get("Name")
        for sess in sessions_json
        if sess.get("NowPlayingItem")
    ]

    items = [
        DockerServiceStatItem(label="影片", value=str(counts_json.get("MovieCount", 0))),
        DockerServiceStatItem(label="影集", value=str(counts_json.get("SeriesCount", 0))),
        DockerServiceStatItem(
            label="正在播放",
            value=str(len(playing)),
            hint=", ".join(playing[:3]) if playing else "暂无播放",
        ),
    ]

    return DockerServiceStats(
        title="Emby",
        headline=f"{len(playing)} 人在看剧" if playing else "暂无播放",
        items=items,
        highlights=playing[:5],
    )
