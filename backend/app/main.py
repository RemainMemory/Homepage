# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import system as system_api
from app.api import network as network_api
from app.api import monitor as monitor_api
from app.api import docker_api
from app.api import host as host_api

app = FastAPI()

# 允许的前端来源
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # 生产环境建议写死域名，不用 ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由挂载
app.include_router(system_api.router, prefix="/system", tags=["system"])
app.include_router(network_api.router, prefix="/network", tags=["network"])
app.include_router(monitor_api.router, prefix="/monitor", tags=["monitor"])
app.include_router(docker_api.router,  prefix="/docker",  tags=["docker"])
app.include_router(host_api.router,    prefix="/host",    tags=["host"])
