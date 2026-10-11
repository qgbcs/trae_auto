"""
Trae IDE 自动签到脚本 - 简单版本
直接通过本地代理执行Python代码
"""
import json
import urllib.request
import urllib.error

LOCAL_PROXY_PORT = 2255


def execute_via_proxy(code):
    """通过本地代理执行代码"""
    req_data = json.dumps({"code": code}).encode()
    req = urllib.request.Request(
        f"http://localhost:{LOCAL_PROXY_PORT}/r=",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}


def main():
    # 完整的签到脚本
    code = '''
import requests
import json
from pathlib import Path
import time

# 配置路径
JWT_PATH = r"C:\\Users\\Administrator\\.trae-cn\\trae-jwt-token"
ENV_PATH = r"C:\\Users\\Administrator\\AppData\\Roaming\\Trae CN\\ModularData\\ckg_server\\local_env.json"

# 读取JWT Token
with open(JWT_PATH, 'r') as f:
    jwt_token = f.read().strip()

# 读取环境配置
with open(ENV_PATH, 'r') as f:
    config = json.load(f)

host = config['host']
device_id = config['device_id']
user_id = config.get('user_id', '')

print(f"Host: {host}")
print(f"Device ID: {device_id}")
print(f"JWT Token: {jwt_token[:30]}...")

headers = {
    "Authorization": f"Cloud-IDE-JWT {jwt_token}",
    "Content-Type": "application/json",
    "User-Agent": "Trae-CN/1.0",
    "X-Device-Id": device_id
}

# 尝试多个可能的签到API端点
endpoints = [
    f"{host}/api/v1/activity/checkin",
    f"{host}/api/v1/credits/checkin",
    f"{host}/api/v1/user/checkin",
]

results = []
for endpoint in endpoints:
    try:
        resp = requests.post(endpoint, headers=headers, json={}, timeout=10)
        result = {
            "endpoint": endpoint,
            "status": resp.status_code,
            "response": resp.text[:300]
        }
        results.append(result)
        print(f"POST {endpoint}: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        results.append({"endpoint": endpoint, "error": str(e)})
        print(f"POST {endpoint}: Error - {e}")

# 尝试GET方法获取积分信息
print("\\n--- 尝试GET获取积分信息 ---")
credit_endpoints = [
    f"{host}/api/v1/user/credits",
    f"{host}/api/v1/user/points",
    f"{host}/api/v1/activity/checkin/status",
]

for endpoint in credit_endpoints:
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
        print(f"GET {endpoint}: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        print(f"GET {endpoint}: Error - {e}")

return {"checkin_results": results}
'''

    print("执行签到脚本...")
    result = execute_via_proxy(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
