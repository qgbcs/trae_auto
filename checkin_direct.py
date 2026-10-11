import subprocess
import json
import time
import requests

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# 根据storage.json中的信息，签到活动ID是 checkin_credits
endpoints = [
    f"{host}/api/v1/activity/checkin",
    f"{host}/api/v1/credits/checkin",
    f"{host}/api/v1/checkin",
    f"{host}/icube/api/v1/activity/checkin",
    f"{host}/icube/api/v1/checkin",
    f"{host}/icube/api/v1/checkin/credits",
    f"{host}/trae/api/v1/activity/checkin",
    f"{host}/trae/api/v1/checkin",
    f"{host}/api/v1/activity/checkin/claim",
    f"{host}/api/v1/credits/checkin/claim",
    f"{host}/api/v1/activity/checkin/claim?activityId=checkin_credits",
    f"{host}/api/v1/activity/checkin?activityId=checkin_credits",
]

status_endpoints = [
    f"{host}/api/v1/activity/checkin/status",
    f"{host}/api/v1/credits/checkin/status",
    f"{host}/icube/api/v1/checkin/status",
]

user_endpoints = [
    f"{host}/api/v1/user/info",
    f"{host}/api/v1/user/credits",
    f"{host}/api/v1/user/points",
    f"{host}/icube/api/v1/user/info",
]

results = []

print("\n=== 尝试签到（POST）===")
for endpoint in endpoints:
    try:
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
                print(f"\nPOST {endpoint}")
                print(f"  Body: {body}")
                print(f"  Status: {resp.status_code}")
                print(f"  Response: {resp.text[:150]}")

                if resp.status_code in [200, 201, 204]:
                    print("  >>> SUCCESS!")
                    print("\n结果:", json.dumps(results, indent=2, ensure_ascii=False))
                    exit(0)
            except Exception as e:
                pass
    except Exception as e:
        pass

print("\n\n=== 检查签到状态（GET）===")
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

print("\n\n=== 获取用户信息 ===")
for endpoint in user_endpoints:
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10, verify=False)
        print(f"GET {endpoint}: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        print(f"GET {endpoint}: Error - {e}")

print("\n\n所有结果:", json.dumps(results, indent=2, ensure_ascii=False))
