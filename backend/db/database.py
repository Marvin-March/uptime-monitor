import sqlite3
import os
from datetime import datetime

#数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uptime_monitor.db")

def init_db():
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()

    cursor.execute('''
    create table if not exists monitors(
        id integer primary key autoincrement,
        name text not null,
        type text not null,
        target TEXT NOT NULL,
        params text not null default '{}',
        interval INTEGER NOT NULL DEFAULT 60,
        timeout INTEGER NOT NULL DEFAULT 5,
        alert_threshold INTEGER NOT NULL DEFAULT 3,  
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
    ''')
    cursor.execute('''
    create table if not exists monitor_logs(
        id integer primary key autoincrement,
        monitor_id integer not null,
        status text not null,
        response_time REAL NOT NULL DEFAULT 0.0,  
        error TEXT,                            
        extra_data TEXT DEFAULT '{}',          
        check_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        foreign key (monitor_id) references monitors (id) on delete cascade);
        ''')

    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化成功！文件路径：{DB_PATH}")

def add_monitor(name: str, my_type: str, target: str, params: dict = None, interval: int = 60, timeout: int = 5,alert_email=None):
    import json
    params=params or {}
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    try:
        cursor.execute('''
        insert into monitors(name, type, target, params, interval, timeout,alert_email) values (?, ?, ?, ?, ?, ?,?)
        ''',(name, my_type, target, json.dumps(params), interval, timeout,alert_email))
        conn.commit()
        monitor_id=cursor.lastrowid
        print(f"✅ 添加监控成功！ID：{monitor_id}")
        return monitor_id
    except Exception as e:
        print(f"❌ 添加监控失败：{e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def add_monitor_log(monitor_id: int, status: str, response_time: float = 0.0, error: str = None, extra_data: dict = None):
    import json
    extra_data = extra_data or {}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO monitor_logs (monitor_id, status, response_time, error, extra_data)
        VALUES (?, ?, ?, ?, ?)
        ''', (monitor_id, status, response_time, error, json.dumps(extra_data)))
        conn.commit()
        log_id = cursor.lastrowid
        return log_id
    except Exception as e:
        print(f"❌ 存储日志失败：{e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_monitor_by_id(monitor_id: int):
    import json
    conn=sqlite3.connect(DB_PATH)#####
    conn.row_factory=sqlite3.Row######
    cursor=conn.cursor()
    try:
        cursor.execute('select * from monitors where id =?',(monitor_id,))
        row=cursor.fetchone()#####
        if row:
            monitor=dict(row)
            monitor["params"]=json.loads(monitor["params"])
            return monitor
        return None
    finally:
        conn.close()

def get_all_monitors(is_active: bool = None):
    import json
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        if is_active is not None:
            cursor.execute('SELECT * FROM monitors WHERE is_active = ?', (is_active,))
        else:
            cursor.execute('SELECT * FROM monitors')
        rows = cursor.fetchall()
        # 转换为字典列表，解析JSON参数
        monitors = []
        for row in rows:
            monitor = dict(row)
            monitor["params"] = json.loads(monitor["params"])
            monitors.append(monitor)
        return monitors
    except Exception as e:
        print(f"❌ 查询所有监控失败：{e}")
        return []
    finally:
        conn.close()
# scheduler/task.py 新增邮件告警函数
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_email_alert(monitor_name, status, error, response_time, threshold, to_email):
    """发送告警邮件"""
    # 配置你的邮箱（以163为例）
    smtp_server = "smtp.163.com"
    smtp_port = 465
    from_email = "18163876797@163.com"
    from_pwd = "setpassw0rd!"

    # 邮件内容
    subject = f"【运维监控告警】{monitor_name} 状态异常"
    content = f"""
    监控项：{monitor_name}
    状态：{status}
    错误信息：{error or '无'}
    响应时间：{response_time}ms（阈值：{threshold}ms）
    告警时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
    """
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = from_email
    msg["To"] = to_email

    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_email, from_pwd)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        print(f"✅ 告警邮件已发送至 {to_email}")
    except Exception as e:
        print(f"❌ 邮件发送失败：{str(e)}")


if __name__=="__main__":
    init_db()

    # 2. 添加测试监控（Ping监控百度IP）
    ping_params = {}
    ping_id = add_monitor(
        name="百度Ping监控",
        my_type="ping",
        target="114.114.114.114",
        params=ping_params,
        interval=60,
        timeout=2
    )

    # 3. 添加测试监控（HTTP监控百度）
    http_params = {}
    http_id = add_monitor(
        name="百度HTTP监控",
        my_type="http",
        target="https://www.baidu.com",
        params=http_params,
        interval=60,
        timeout=5
    )

    # 4. 存储测试日志（Ping监控）
    if ping_id:
        add_monitor_log(
            monitor_id=ping_id,
            status="up",
            response_time=12.56,
            error=None,
            extra_data={}
        )

    # 5. 查询测试监控
    if ping_id:
        monitor = get_monitor_by_id(ping_id)
        print("\n=== 查询测试监控配置 ===")
        for key, value in monitor.items():
            print(f"{key}: {value}")

    # 6. 查询所有监控
    all_monitors = get_all_monitors()
    print("\n=== 所有监控配置 ===")
    for m in all_monitors:
        print(f"ID: {m['id']}, 名称: {m['name']}, 类型: {m['type']}, 目标: {m['target']}")



