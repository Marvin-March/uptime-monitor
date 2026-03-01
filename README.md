
# Uptime Monitor 网站可用性监控系统

## 项目简介
一款轻量级网站可用性监控工具，支持定时检测、告警通知等功能，可通过 Docker 快速部署。

## 功能特性
- 定时检测网站可用性（HTTP/HTTPS）
- 支持自定义检测间隔
- 实时展示监控状态与历史记录
- 支持 Docker 容器化部署

## 快速开始

### 方式一：使用 Docker 镜像（推荐）
1.  拉取镜像：
    ```bash
    docker pull marvinher/uptime_monitor:v1
    ```
2.  运行容器（将 8080 端口映射到宿主机）：
    ```bash
    docker run -d -p 8080:8080 marvinher/uptime_monitor:v1
    ```
3.  访问 `http://localhost:8080` 即可使用。

### 方式二：本地构建镜像
1.  克隆仓库：
    ```bash
    git clone https://github.com/Marvin-March/uptime-monitor.git
    cd uptime-monitor
    ```
2.  构建镜像：
    ```bash
    docker build -t marvinher/uptime_monitor:v1 .
    ```
3.  运行容器：
    ```bash
    docker run -d -p 8080:8080 marvinher/uptime_monitor:v1
    ```

## 使用说明
- 启动后访问 `http://服务器IP:8080` 进入管理面板。
- 在面板中添加需要监控的网站 URL，设置检测间隔和告警方式。

## 技术栈
- Python 3.11
- Docker
- Flask / FastAPI（根据你的项目实际情况修改）
