from typing import List

from fastapi import APIRouter, HTTPException

from app.core.docker import get_docker_overview
from app.core.docker.config import (
    create_service_from_payload,
    load_service_configs,
    remove_service,
    update_service_from_payload,
)
from app.models.docker import (
    DockerOverview,
    DockerServiceConfigModel,
    DockerServiceConfigPayload,
)

router = APIRouter()


@router.get("/overview", response_model=DockerOverview)
async def docker_overview():
    return await get_docker_overview()


@router.get("/services", response_model=List[DockerServiceConfigModel])
async def list_docker_services():
    configs = load_service_configs()
    return [DockerServiceConfigModel(**cfg.to_dict()) for cfg in configs]


@router.post("/services", response_model=DockerServiceConfigModel)
async def create_docker_service(payload: DockerServiceConfigPayload):
    config = create_service_from_payload(payload.model_dump())
    return DockerServiceConfigModel(**config.to_dict())


@router.put("/services/{slug}", response_model=DockerServiceConfigModel)
async def update_docker_service(slug: str, payload: DockerServiceConfigPayload):
    updated = update_service_from_payload(slug, payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="service not found")
    return DockerServiceConfigModel(**updated.to_dict())


@router.delete("/services/{slug}", status_code=204)
async def delete_docker_service(slug: str):
    if not remove_service(slug):
        raise HTTPException(status_code=404, detail="service not found")
