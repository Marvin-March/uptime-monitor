# 基础镜像：Python 3.11 轻量版（适配所有依赖）
FROM python:3.11-slim

# 设置环境变量（避免Python输出缓冲，方便看日志）
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 设置工作目录
WORKDIR /app

# 先复制依赖文件（利用Docker缓存，改代码不用重新装依赖）
COPY backend/requirements.txt /app/backend/

# 安装系统依赖（解决ping/dns等命令依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制整个项目代码到容器
COPY . /app/

# 暴露Web服务端口
EXPOSE 8000

# 启动脚本（同时运行定时任务和Web服务）
COPY start.sh /app/
RUN chmod +x /app/start.sh

# 启动容器时执行脚本
CMD ["/app/start.sh"]



