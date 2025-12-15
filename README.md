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

- 服务清单写在 `backend/app/config/docker_services.yaml`。只要写 `name` + `access_url` 就能渲染卡片，其它字段都可选：

```yaml
services:
  - name: Emby Server
    description: 多媒体服务
    access_url: https://emby.example.com
    icon: https://www.google.com/s2/favicons?sz=128&domain_url=https://emby.example.com
    tags: [media]
    container: emby
    probe:
      url: https://emby.example.com/status   # 仅需 URL，method/timeout 会自动填
    stats:
      type: emby
      url: https://emby.example.com
      api_key: YOUR_EMBY_TOKEN
```

- 需要实时探活时，只写 `probe.url` 即可，其余会在后端套用默认值；`require_probe` 默认 `false`，如无特殊需求可以不写。
- 需要扩展统计（例如 Emby 正在播放）时配置 `stats` 字段，未配置时前端不会展示统计。
- `/docker` 页面新增的“添加服务”弹窗默认只有 3 个必填项，其它高级选项（容器、标签、自定义图标）可折叠展开后填写；表单保存后仍然写回该 YAML 文件。
- 如果主机安装了 docker CLI，系统会自动枚举当前 Docker 容器并生成“临时”卡片，即使它们未写进 `docker_services.yaml` 也能看到运行状态（标记为 `managed: false`，不会落盘）。
- 后端会并发执行 `docker inspect + HTTP 探活` 并兜底第三方统计接口。若系统未安装 docker CLI，会展示 `docker CLI not found` 提示并仅依赖探活结果。
- 首页和 `/docker` 页面都会展示按卡片排布的服务状态，离线/在线状态即刻可见。

## 常见问题

- **speedtest CLI 未安装**：`/network/speedtest` 将返回 `ok=false` 提示，请根据提示安装 `speedtest` 或 `speedtest-cli`。
- **监控目标自定义**：目前写在 `backend/app/core/monitor/targets.py` 的 `MONITOR_TARGETS` 中，可替换为读取配置文件/数据库。
- **Docker 服务为空**：确认 `backend/app/config/docker_services.yaml` 已填充且运行环境已安装 `docker` 命令。
