# Homepage

一个由 **FastAPI** 提供系统/网络监控接口、**Vue 3 + Vite** 绘制数据看板的全栈工程。后端负责采集 CPU、内存、磁盘、传感器、网络以及可配置的探活任务，前端调用 REST API 渲染主机概览。

## 目录结构

- `backend/` —— FastAPI 应用，核心逻辑在 `app/core/*`
- `frontend/` —— Vue 3 + Vite 前端，API 调用集中在 `src/api`
- `env/` ——（可选）Python 3.10 虚拟环境，可删除后按需重建

## 环境要求

- Python 3.10+
- Node.js 20+（Vite 7 推荐的版本线）
- [speedtest CLI](https://www.speedtest.net/apps/cli)（可选，用于 `/network/speedtest`）

## 本地开发

### 1. 后端 API

```bash
cd backend
python3.10 -m venv ../env        # 已存在时可跳过
source ../env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 开发时可访问 `http://localhost:8000/docs` 获取 Swagger 文档。
- 也可使用 `fastapi dev app/main.py`，同样会读取 `app.main:app` 并支持热重载。

### 2. 前端

```bash
cd frontend
npm install
npm run dev -- --host
```

- 默认 API 地址为 `http://localhost:8000`，如需修改可在 `frontend/.env.local` 中添加 `VITE_API_BASE_URL="http://your-backend:8000"`。
- Vite DEV 服务器运行在 `:5173`，浏览器打开 `http://localhost:5173` 即可看到页面。

### 3. 构建

- **后端**：`uvicorn app.main:app --host 0.0.0.0 --port 8000` 即可在生产环境运行，按需使用 systemd/supervisor 守护。
- **前端**：执行 `npm run build`，静态文件会生成到 `frontend/dist/`，交由任意静态站点托管。

## Docker 服务监控

- 服务清单写在 `backend/app/config/docker_services.yaml`，也可以在前端 `/docker` 页面通过表单增删，表单会直接调用 `/docker/services` API 写回该文件。配置项包括：
  - `name`：展示名称
  - `container`：对应 docker 容器名，用于 `docker inspect`
  - `probe_url` + `probe_method`：可选的 HTTP 探活地址，支持自定义状态码 `expect_status`
  - `access_url`：前端“快捷接入”按钮链接
-  - `require_probe`: `true` 时必须探活成功才算在线，`false` 则以容器运行状态为主
-  - `stats`：可选扩展统计，目前内置 `type: emby`（需要配置 `url` 与 `api_key`，页面会展示正在播放/影片数等）
- 后端会并发执行 `docker inspect + HTTP 探活` 并兜底第三方统计接口。若系统未安装 docker CLI，会展示 `docker CLI not found` 提示并仅依赖探活结果。
- 前端：
  - 首页新增“Docker 服务”卡片，显示运行中/在线/异常数量、标签、扩展统计，并提供快捷入口。
  - `/docker` 页面以卡片形式显示每个服务的在线状态、延迟、扩展统计（例如 Emby 正在播放），并附带复制探活、打开面板、删除等操作；下方管理区可以增删配置，无需手改 YAML。

## 常见问题

- **speedtest CLI 未安装**：`/network/speedtest` 将返回 `ok=false` 提示，请根据提示安装 `speedtest` 或 `speedtest-cli`。
- **监控目标自定义**：目前写在 `backend/app/core/monitor/targets.py` 的 `MONITOR_TARGETS` 中，可替换为读取配置文件/数据库。
- **Docker 服务为空**：确认 `backend/app/config/docker_services.yaml` 已填充且运行环境已安装 `docker` 命令。
