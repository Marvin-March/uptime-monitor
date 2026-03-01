Uptime Monitor 🚀

一个轻量、易用的开源运维监控系统，支持 HTTP (s)、TCP、Ping、DNS 四种监控类型，提供现代化 Web 界面和邮件告警功能。

✨ 功能特性
多类型监控：HTTP (s)、TCP 端口、ICMP Ping、DNS 记录
可视化界面：响应式设计，支持 PC 和移动端访问
邮件告警：服务异常时自动发送告警邮件
公开状态页：展示服务实时状态和历史可用性
数据持久化：SQLite 存储，支持 Docker 容器化部署
定时任务：按自定义间隔执行监控，支持异常重试

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
- Flask / FastAPI
