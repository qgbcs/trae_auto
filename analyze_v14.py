#!/usr/bin/env python3
"""
Trae CN 自动签到 v14 - 通过本地代理分析实际 API 调用
使用 browserdiff 或网络拦截方式找到正确的 API
"""

import json
import urllib.request
import urllib.error

LOCAL_PROXY = "http://localhost:2255"


def rpc_exec(code):
    url = f"{LOCAL_PROXY}/r="
    data = code.encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:1000]}"
    except Exception as e:
        return f"Error: {e}"


def main():
    print("=" * 60)
    print("Trae CN 签到分析 v14 (网络拦截)")
    print("=" * 60)

    # 方法 1: 检查本地代理是否已经有拦截网络请求的能力
    code1 = '''
import urllib.request
import json

# 尝试获取本地代理的状态
req = urllib.request.Request("http://localhost:2255/status")
resp = urllib.request.urlopen(req, timeout=5)
print("Proxy status:", resp.read().decode())
'''
    result = rpc_exec(code1)
    print("Proxy status:", result)

    # 方法 2: 检查 Trae 是否有 HTTP 代理配置
    code2 = '''
import os
import json

# 检查系统代理设置
proxy_env = os.environ.get('HTTP_PROXY', os.environ.get('HTTPS_PROXY', ''))
print(f"HTTP_PROXY: {{proxy_env}}")
print(f"HTTPS_PROXY: {{proxy_env}}")

# 检查 Trae 的配置
trae_config = r"C:\\Users\\Administrator\\AppData\\Roaming\\Trae CN\\User\\globalStorage\\storage.json"
with open(trae_config, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 查找代理相关配置
for key in config:
    if 'proxy' in key.lower():
        print(f"{{key}}: {{config[key]}}")

# 检查是否有 network 相关的配置
for key in config:
    if 'network' in key.lower() or 'http' in key.lower():
        print(f"{{key}}: {{str(config[key])[:200]}}")
'''
    result = rpc_exec(code2)
    print("\nProxy config:", result)

    # 方法 3: 尝试通过 Python requests 库添加代理拦截
    code3 = '''
import requests
import json

jwt = open(r"C:\\Users\\Administrator\\.trae-cn\\trae-jwt-token").read().strip()
env = json.load(open(r"C:\\Users\\Administrator\\AppData\\Roaming\\Trae CN\\ModularData\\ckg_server\\local_env.json"))
host = env["host"]
did = env["device_id"]

# 尝试通过不同的认证方式调用
headers_list = [
    {
        "Authorization": f"Cloud-IDE-JWT {{jwt}}",
        "Content-Type": "application/json",
        "X-Device-Id": did,
    },
    {
        "Authorization": f"Bearer {{jwt}}",
        "Content-Type": "application/json",
        "X-Device-Id": did,
    },
    {
        "Cookie": f"token={{jwt}}",
        "Content-Type": "application/json",
    },
    {
        "Authorization": f"JWT {{jwt}}",
        "Content-Type": "application/json",
    },
]

paths = [
    "/api/v1/activity/checkin/claim",
    "/api/v1/checkin/claim",
    "/icube/api/v1/checkin/credits/claim",
    "/api/v1/commerce/checkin",
]

print("Testing different auth methods...")
for h_idx, headers in enumerate(headers_list):
    for path in paths:
        url = host + path
        data = json.dumps({{"activityId": "checkin_credits"}}).encode()
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=5)
            print(f"Auth {{h_idx}} POST {{path}}: {{resp.status_code}} - {{resp.text[:150]}}")
        except Exception as e:
            print(f"Auth {{h_idx}} POST {{path}}: ERROR - {{e}}")
'''
    result = rpc_exec(code3)
    print("\nAuth methods:", result)


if __name__ == "__main__":
    main()
