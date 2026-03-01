#!/bin/bash
set -e

# 1. 后台启动定时监控任务
echo "🚀 启动监控定时任务..."
python3 /app/backend/scheduler/task.py &

# 2. 前台启动Web服务（保持容器运行）
echo "🌐 启动Web可视化服务..."
python3 /app/backend/api/main.py
