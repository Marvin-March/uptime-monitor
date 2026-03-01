# /Dev/uptime-monitor/backend/scheduler/task.py
# 运维监控系统 - 定时任务模块
# 核心功能：读取监控配置 → 按间隔执行监控 → 存储结果到数据库
import sys
import os
import time
import json
# 新增邮件相关import
import smtplib
from email.mime.text import MIMEText
from email.header import Header

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 邮件配置
EMAIL_FROM = "2199363809@qq.com"  
EMAIL_PWD = "gwfwwbfvvulbdhgg"
EMAIL_TO = "2199363809@qq.com" 

# 新增邮件发送函数
def send_alert_email(monitor_name, error_msg):
    """发送告警邮件"""
    try:
        # 邮件内容
        subject = f"【监控告警】{monitor_name} 服务异常！"
        content = f"""
        监控名称：{monitor_name}
        异常原因：{error_msg}
        告警时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
        """
        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        # 发送邮件
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(EMAIL_FROM, EMAIL_PWD)
        server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        server.quit()
        print(f"✅ 告警邮件已发送到 {EMAIL_TO}")
    except Exception as e:
        print(f"❌ 邮件发送失败：{str(e)}")
# 添加backend目录到Python路径（避免导入模块报错）
sys.path.append("/Dev/uptime-monitor/backend")

from apscheduler.schedulers.background import BackgroundScheduler
from core import ping_monitor, http_monitor, tcp_monitor, dns_monitor
from db.database import get_all_monitors, add_monitor_log

def run_monitor(monitor):
    """
    执行单个监控，并存储结果到数据库
    :param monitor: 监控配置字典（从数据库查询的结果）
    """
    monitor_id = monitor["id"]
    monitor_type = monitor["type"]
    target = monitor["target"]
    timeout = monitor["timeout"]
    params = monitor["params"]  # 额外参数（JSON解析后的字典）

    print(f"\n=== 开始执行监控：{monitor['name']}（ID：{monitor_id}）===")
    try:
        # 根据监控类型调用对应的监控函数
        if monitor_type == "ping":
            result = ping_monitor(target, timeout=timeout)
            extra_data = {}  # Ping无额外数据
        elif monitor_type == "http":
            result = http_monitor(target, timeout=timeout)
            extra_data = {"status_code": result["status_code"]}
        elif monitor_type == "tcp":
            port = params.get("port", 80)  # 从参数取端口，默认80
            result = tcp_monitor(target, port, timeout=timeout)
            extra_data = {"port": port}
        elif monitor_type == "dns":
            record_type = params.get("record_type", "A")
            result = dns_monitor(target, record_type, timeout)
            extra_data = {"resolved_ips": result["resolved_ips"]}
        else:
            print(f"❌ 不支持的监控类型：{monitor_type}")
            return

        # 打印监控结果（方便调试）
        print(f"状态：{result['status']} | 响应时间：{result['response_time']}ms | 错误：{result['error']}")
        if result["status"] == "down":
            send_alert_email(monitor["name"], result["error"])

        # 存储结果到数据库
        log_id = add_monitor_log(
            monitor_id=monitor_id,
            status=result["status"],
            response_time=result["response_time"],
            error=result["error"],
            extra_data=extra_data
        )
        if log_id:
            print(f"✅ 监控结果已存储（日志ID：{log_id}）")
        else:
            print(f"❌ 监控结果存储失败")

    except Exception as e:
        print(f"❌ 执行监控失败：{str(e)}")
        # 存储失败结果到数据库
        add_monitor_log(
            monitor_id=monitor_id,
            status="down",
            response_time=0.0,
            error=f"执行监控异常：{str(e)}",
            extra_data={}
        )
        send_alert_email(monitor["name"], f"执行监控异常：{str(e)}")

def start_scheduler():
    """
    启动定时任务调度器
    """
    # 1. 创建后台调度器（不阻塞主线程）
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    print("🔄 初始化定时任务调度器...")

    # 2. 读取所有启用的监控配置
    monitors = get_all_monitors(is_active=1)
    if not monitors:
        print("⚠️  未找到启用的监控配置，请先添加监控！")
        return

    # 3. 为每个监控添加定时任务
    for monitor in monitors:
        interval = monitor["interval"]  # 检测间隔（秒）
        # 添加定时任务：每隔interval秒执行一次run_monitor(monitor)
        scheduler.add_job(
            func=run_monitor,  # 要执行的函数
            args=(monitor,),   # 函数参数
            trigger="interval",  # 触发类型：间隔执行
            seconds=interval,    # 间隔时间（秒）
            id=f"monitor_{monitor['id']}",  # 任务ID（唯一）
            name=monitor["name"]  # 任务名称
        )
        print(f"✅ 添加定时任务：{monitor['name']} | 间隔：{interval}秒")

    # 4. 启动调度器
    scheduler.start()
    print("\n🚀 定时任务调度器已启动！按 Ctrl+C 停止...")

    # 5. 保持主线程运行（防止调度器退出）
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # 捕获Ctrl+C，优雅停止调度器
        scheduler.shutdown()
        print("\n🛑 定时任务调度器已停止！")

# 测试代码（直接运行该文件时执行）
if __name__ == "__main__":
    start_scheduler()
