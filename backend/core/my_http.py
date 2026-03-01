import requests
import time

def http_monitor(url:str,timeout:int=5) -> dict:
    result={
            "monitor_type":"http",
            "target":url,
            "status":"unknown",
            "response_time":0.0,
            "status_code":None,
            "error":None,
            "check_time":time.strftime("%Y-%m-%d %H:%M:%S")
            }
    try:
        start_time=time.time()
        response=requests.get(
                url=url,
                timeout=timeout,
                allow_redirects=False,
                verify=True #!!!
                )
        response_time = round((time.time() - start_time) * 1000, 2)
        result["response_time"] = response_time
        result["status_code"] = response.status_code

        if response.status_code == 200:
            result["status"]="up"
        else:
            result["status"]="down"
            result["error"] = f"HTTP状态码异常：{response.status_code}"
    #COMMON CASES:
    except requests.exceptions.Timeout as e:
        result["status"] = "down"
        result["error"] = f"请求超时:{str(e)}"
    except requests.exceptions.ConnectionError as e:
        result["status"] = "down"
        result["error"] = f"连接失败:{str(e)}"
    #FINALLY:
    except Exception as e:
        result["status"] = "down"
        result["error"] = f"检测异常：{str(e)}"
    return result
if __name__=="__main__":
    print("===FOR TEST TRUE===")
    test1 = http_monitor("https://www.baidu.com")
    for key, value in test1.items():
        print(f"{key}: {value}")

    print("===FOR TEST False===")
    test2 = http_monitor("http://192.168.99.99:8080")
    for key, value in test2.items():
        print(f"{key}: {value}")

