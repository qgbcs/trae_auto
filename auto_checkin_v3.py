"""
Trae IDE 自动签到脚本 v3
使用正确的 Python 语法
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
        return {"error": f"HTTP {e.code}", "body": e.read().decode()[:500]}
    except Exception as e:
        return {"error": str(e)}


def main():
    # 核心签到脚本
    code = r'''
import requests
import json
import time

# 读取配置
with open(r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json", "r") as f:
    config = json.load(f)

host = config["host"]
device_id = config["device_id"]

# 读取JWT Token
with open(r"C:\Users\Administrator\.trae-cn\trae-jwt-token", "r") as f:
    jwt_token = f.read().strip()

print(f"Host: {host}")
print(f"Device ID: {device_id}")
print(f"JWT: {jwt_token[:40]}...")

headers = {
    "Authorization": f"Cloud-IDE-JWT {jwt_token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

# 根据之前分析的代码和 storage.json 中的信息
api_endpoints = [
    f"{host}/api/v1/activity/checkin/claim",
    f"{host}/api/v1/activity/checkin",
    f"{host}/trae/api/v1/activity/checkin",
    f"{host}/icube/api/v1/checkin/credits",
    f"{host}/api/v1/credits/checkin",
]

results = []
for endpoint in api_endpoints:
    try:
        resp = requests.post(
            endpoint,
            headers=headers,
            json={"activityId": "checkin_credits"},
            timeout=10
        )
        result = {
            "endpoint": endpoint,
            "status": resp.status_code,
            "response": resp.text[:300]
        }
        results.append(result)
        print(f"\nPOST {endpoint}")
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        results.append({"endpoint": endpoint, "error": str(e)})
        print(f"\nPOST {endpoint}: Error - {e}")

# 也尝试 GET 方法获取签到状态
print("\n\n--- 检查签到状态 ---")
status_endpoints = [
    f"{host}/api/v1/activity/checkin/status",
    f"{host}/api/v1/activity/checkin",
]

for endpoint in status_endpoints:
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
        print(f"GET {endpoint}: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        print(f"GET {endpoint}: Error - {e}")

return {"results": results}
'''

    print("=" * 60)
    print("Trae IDE 自动签到脚本 v3")
    print("=" * 60)
    print()

    print("[步骤 1] 尝试签到...")
    result = execute_via_proxy(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 分析结果
    if isinstance(result, dict) and "results" in result:
        successful = [r for r in result["results"] if r.get("status") == 200]
        if successful:
            print("\n[成功] 找到可用的签到API!")
            for s in successful:
                print(f"  - {s['endpoint']}")
        else:
            print("\n[提示] 没有找到200状态的API，可能需要其他认证方式")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
