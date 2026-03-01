import dns.resolver
import time

def dns_monitor(
        domain:str,
        record_type: str = "A",
        timeout:int=5
) -> dict:
    result = {
            "monitor_type":"dns",
            "target":f"{domain}({record_type})",
            "status":"unknown",
            "response_time": 0.0, 
            "resolved_ips": [],
            "error": None,
            "check_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    try:
        resolver=dns.resolver.Resolver()
        resolver.timeout=timeout
        resolver.lifetime=timeout

        start_time = time.time()

        answers=resolver.resolve(domain,record_type)

        resolved_ips=[str(answer) for answer in answers]
        result["resolved_ips"] = resolved_ips

        response_time = round((time.time() - start_time) * 1000, 2)
        result["response_time"] = response_time

        if len(resolved_ips)>0:
            result["status"]="up"
        else :
            result["status"] = "down"
            result["error"] = "DNS解析成功，但未返回任何IP"

    except dns.exception.Timeout:
        result["status"] = "down"
        result["error"] = f"DNS解析超时（超时时间：{timeout}秒）"
    except dns.resolver.NXDOMAIN:
        result["status"] = "down"
        result["error"] = f"域名不存在：{domain}"
    except dns.resolver.NoAnswer:
        result["status"] = "down"
        result["error"] = f"域名{domain}无{record_type}类型记录"
    except Exception as e:
        result["status"] = "down"
        result["error"] = f"DNS解析异常：{str(e)}"
    return result


if __name__ == "__main__":
    print("===FOR TEST TRUE===")
    test1 = dns_monitor("www.baidu.com")
    for key, value in test1.items():
        print(f"{key}: {value}")

    print("===FOR TEST FALSE===")
    test3 = dns_monitor("xx.abcdef.com")
    for key, value in test3.items():
        print(f"{key}:{value}")
