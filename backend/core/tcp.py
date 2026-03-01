import socket
import time

def tcp_monitor(target:str,port:int,timeout:int = 3) -> dict:
    result={
            "monitor_type":"tcp",
            "target":f"{target}:{port}",
            "status":"unknown",
            "port":"port",
            "error":None,
            "response_time": 0.0,
            "check_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM) # 创建TCP socket对象（AF_INET=IPv4，SOCK_STREAM=TCP）
    sock.settimeout(timeout)
    
    try:
        start_time=time.time()

        # 尝试连接目标IP+端口（核心！检测端口是否开放）
        connect_result = sock.connect_ex((target, port))

        response_time = round((time.time() - start_time) * 1000, 2)
        result["response_time"] = response_time

        if connect_result == 0:
            result["status"] = "up"  
        else:
            result["status"] = "down"
            result["error"] = f"端口{port}未开放（错误码：{connect_result}）"
        # 超时异常
    except socket.timeout:
        result["status"] = "down"
        result["error"] = f"连接超时（超时时间：{timeout}秒）"

    # 域名解析失bai
    except socket.gaierror:
        result["status"] = "down"
        result["error"] = f"域名解析失败：{target}"

    # 其他
    except Exception as e:
        result["status"] = "down"
        result["error"] = f"检测异常：{str(e)}"

    finally:
        # 关闭socket连接（避免资源泄露）
        sock.close()
    return result

if __name__ == "__main__":
    print("===FOR TEST TRUE===")
    test1 = tcp_monitor("www.baidu.com", 80)
    for key, value in test1.items():
        print(f"{key}: {value}")
    print("===FOR TEST FALSE===")
    test2 = tcp_monitor("192.168.99.99", 8888)
    for key, value in test2.items():
        print(f"{key}: {value}")
