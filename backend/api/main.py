# backend/api/main.py
# 运维监控系统 - Web API 模块
# 核心功能：提供监控配置/日志的Web界面和API接口
import sys
import os
# 1. 把项目根目录添加到Python路径（关键！确保能找到所有模块）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 2. 直接从db/database.py导入函数（避免包导入问题）
from db.database import (
    get_all_monitors,
    get_monitor_by_id,
    sqlite3,
    DB_PATH
)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 初始化FastAPI应用
app = FastAPI(title="运维监控系统", version="0.1.0")

# 配置模板引擎（用于渲染HTML页面）
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
# ---------------------- 网页路由（可视化界面） ----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页：展示所有监控配置和实时状态"""
    # 1. 获取所有启用的监控
    monitors = get_all_monitors(is_active=1)
    
    # 2. 给每个监控补充最新状态（从日志表取最后一条记录）
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    for monitor in monitors:
        # 查询该监控的最新日志
        cursor.execute("""
            SELECT status, response_time, check_time 
            FROM monitor_logs 
            WHERE monitor_id = ? 
            ORDER BY id DESC LIMIT 1
        """, (monitor["id"],))
        latest_log = cursor.fetchone()
        
        if latest_log:
            monitor["latest_status"] = latest_log["status"]
            monitor["latest_response_time"] = latest_log["response_time"]
            monitor["latest_check_time"] = latest_log["check_time"]
        else:
            monitor["latest_status"] = "unknown"
            monitor["latest_response_time"] = 0.0
            monitor["latest_check_time"] = "未检测"
    
    conn.close()
    
    # 3. 渲染HTML模板
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "monitors": monitors}
    )

@app.get("/logs", response_class=HTMLResponse)
async def logs(request: Request, monitor_id: int = None):
    """日志页面：展示历史检测日志（可选按监控ID过滤）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 按监控ID过滤日志
    if monitor_id:
        cursor.execute("""
            SELECT ml.*, m.name as monitor_name
            FROM monitor_logs ml
            LEFT JOIN monitors m ON ml.monitor_id = m.id
            WHERE ml.monitor_id = ?
            ORDER BY ml.id DESC LIMIT 100
        """, (monitor_id,))
    else:
        # 取最新100条日志
        cursor.execute("""
            SELECT ml.*, m.name as monitor_name
            FROM monitor_logs ml
            LEFT JOIN monitors m ON ml.monitor_id = m.id
            ORDER BY ml.id DESC LIMIT 100
        """)
    
    logs = cursor.fetchall()
    conn.close()
    
    # 渲染日志页面
    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "logs": logs, "monitor_id": monitor_id}
    )

# ---------------------- API 接口（JSON格式） ----------------------
@app.get("/api/monitors")
async def api_monitors(is_active: int = None):
    """获取所有监控配置（JSON接口）"""
    monitors = get_all_monitors(is_active=is_active)
    return {"code": 200, "data": monitors}

@app.get("/api/monitors/{monitor_id}")
async def api_monitor_detail(monitor_id: int):
    """获取单个监控详情（JSON接口）"""
    monitor = get_monitor_by_id(monitor_id)
    if monitor:
        return {"code": 200, "data": monitor}
    else:
        return {"code": 404, "msg": "监控不存在"}

@app.get("/api/logs")
async def api_logs(monitor_id: int = None):
    """获取监控日志（JSON接口）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if monitor_id:
        cursor.execute("""
            SELECT * FROM monitor_logs 
            WHERE monitor_id = ? 
            ORDER BY id DESC LIMIT 100
        """, (monitor_id,))
    else:
        cursor.execute("""
            SELECT * FROM monitor_logs 
            ORDER BY id DESC LIMIT 100
        """)
    
    logs = [dict(log) for log in cursor.fetchall()]
    conn.close()
    
    return {"code": 200, "data": logs}

# 启动服务（直接运行该文件时执行）
if __name__ == "__main__":
    import uvicorn
    # 监听所有网卡的8000端口，允许外部访问
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式：修改代码自动重启
    )
