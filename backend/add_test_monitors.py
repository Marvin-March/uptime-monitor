# 添加TCP/DNS测试监控
from db.database import init_db, add_monitor

# 初始化数据库（确保表存在）
init_db()

# 1. 添加TCP监控（百度80端口，间隔30秒）
tcp_params = {"port": 80}
tcp_id = add_monitor(
    name="百度TCP 80端口监控",
    my_type="tcp",
    target="www.baidu.com",
    params=tcp_params,
    interval=30,
    timeout=3
)

# 2. 添加DNS监控（百度A记录，间隔40秒）
dns_params = {"record_type": "A", "expected_ip": "14.215.177.38"}
dns_id = add_monitor(
    name="百度DNS解析监控",
    my_type="dns",
    target="www.baidu.com",
    params=dns_params,
    interval=40,
    timeout=5
)

print(f"\n✅ 新增监控ID：TCP={tcp_id}，DNS={dns_id}")
