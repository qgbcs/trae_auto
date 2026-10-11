"""
Trae IDE 自动签到脚本 v4 - 使用IPC调用
"""
import json
import urllib.request
import urllib.error
import sys

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
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "body": e.read().decode()[:1000]}
    except Exception as e:
        return {"error": str(e)}


def main():
    # 尝试通过executeCommand调用IPC
    code = '''
import subprocess
import json
import time

# 方法1: 尝试通过命令行触发签到
# 方法2: 直接调用Trae的API

# 读取配置
with open(r"C:\\Users\\Administrator\\AppData\\Roaming\\Trae CN\\ModularData\\ckg_server\\local_env.json", "r") as f:
    config = json.load(f)

host = config["host"]
device_id = config["device_id"]

# 读取JWT Token
with open(r"C:\\Users\\Administrator\\.trae-cn\\trae-jwt-token", "r") as f:
    jwt_token = f.read().strip()

print(f"Host: {host}")
print(f"Device ID: {device_id}")
print(f"JWT: {jwt_token[:40]}...")

# 尝试所有可能的API端点
import requests

headers = {
    "Authorization": f"Cloud-IDE-JWT {jwt_token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# 根据storage.json中的信息，签到活动ID是 checkin_credits
# 尝试更多API端点
endpoints = [
    # 基础路径
    f"{host}/api/v1/activity/checkin",
    f"{host}/api/v1/credits/checkin",
    f"{host}/api/v1/checkin",
    
    # ICube路径
    f"{host}/icube/api/v1/activity/checkin",
    f"{host}/icube/api/v1/checkin",
    f"{host}/icube/api/v1/checkin/credits",
    
    # Trae路径
    f"{host}/trae/api/v1/activity/checkin",
    f"{host}/trae/api/v1/checkin",
    
    # 带claim后缀
    f"{host}/api/v1/activity/checkin/claim",
    f"{host}/api/v1/credits/checkin/claim",
    
    # 带活动ID
    f"{host}/api/v1/activity/checkin/claim?activityId=checkin_credits",
    f"{host}/api/v1/activity/checkin?activityId=checkin_credits",
]

# 也尝试POST到状态查询端点
status_endpoints = [
    f"{host}/api/v1/activity/checkin/status",
    f"{host}/api/v1/credits/checkin/status",
    f"{host}/icube/api/v1/checkin/status",
]

results = []

print("\\n=== 尝试签到（POST）===")
for endpoint in endpoints:
    try:
        # 尝试不同的请求体
        for body in [{}, {"activityId": "checkin_credits"}, {"activity_id": "checkin_credits"}]:
            try:
                resp = requests.post(
                    endpoint,
                    headers=headers,
                    json=body,
                    timeout=10,
                    verify=False
                )
                result = {
                    "endpoint": endpoint,
                    "body": str(body),
                    "status": resp.status_code,
                    "response": resp.text[:200]
                }
                results.append(result)
                print(f"\\nPOST {endpoint}")
                print(f"  Body: {body}")
                print(f"  Status: {resp.status_code}")
                print(f"  Response: {resp.text[:150]}")
                
                # 如果成功，停止尝试
                if resp.status_code in [200, 201, 204]:
                    print("  >>> SUCCESS!")
                    return results
            except Exception as e:
                pass
    except Exception as e:
        pass

print("\\n\\n=== 检查签到状态（GET）===")
for endpoint in status_endpoints:
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10, verify=False)
        print(f"GET {endpoint}: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
        results.append({
            "endpoint": endpoint,
            "method": "GET",
            "status": resp.status_code,
            "response": resp.text[:200]
        })
    except Exception as e:
        print(f"GET {endpoint}: Error - {e}")

# 也尝试获取用户信息和积分
print("\\n\\n=== 获取用户信息 ===")
user_endpoints = [
    f"{host}/api/v1/user/info",
    f"{host}/api/v1/user/credits",
    f"{host}/api/v1/user/points",
    f"{host}/icube/api/v1/user/info",
]

for endpoint in user_endpoints:
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10, verify=False)
        print(f"GET {endpoint}: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        print(f"GET {endpoint}: Error - {e}")

return results
'''

    print("=" * 60)
    print("Trae IDE 自动签到脚本 v4 - IPC调用")
    print("=" * 60)
    print()

    print("[步骤 1] 尝试通过IPC调用签到...")
    result = execute_via_proxy(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
