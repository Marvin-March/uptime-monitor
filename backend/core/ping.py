
import subprocess
import time


def ping_monitor(target: str, timeout: int = 2) -> dict:
    result = {
        "monitor_type": "ping",
        "target": target,
        "response_time": 0.0,
        "error": None,
        "present": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "unknown"
    }
    try:
        start_time = time.time()
        ping_process = subprocess.run(
            ["ping", "-c", "1", "-w", str(timeout), target],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10  # 总超时5秒（防止命令卡死）
        )
        response_time = round((time.time() - start_time) * 1000, 2)
        result["response_time"] = response_time

        if ping_process.returncode == 0:
            result["status"] = "up"
        else:
            result["status"] = "down"
            error_msg=ping_process.stderr.strip() or ping_process.stdout.strip()
            result["error"] =error_msg if error_msg else "Ping 命令执行失败，返回码非零"
    except Exception as e:
        result["status"] = "down"
        result["error"] = f"检测异常：{str(e)}"  # 记录异常信息
    return result


# 测试代码
if __name__ == "__main__":
    print("===FOR TEST TRUE===")
    test1 = ping_monitor("223.5.5.5")
    for key, value in test1.items():
        print(f"{key}:{value}")
    print("===FOR TEST FALSE===")
    test2 = ping_monitor("192.168.99.99")
    for key, value in test2.items():
        print(f"{key}: {value}")






