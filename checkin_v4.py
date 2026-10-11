import requests
import json
import time
from pathlib import Path

# 读取配置
config_path = Path(r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json")
jwt_path = Path(r"C:\Users\Administrator\.trae-cn\trae-jwt-token")

with open(config_path, "r") as f:
    config = json.load(f)

with open(jwt_path, "r") as f:
    jwt_token = f.read().strip()

host = config["host"]
device_id = config["device_id"]

print(f"Host: {host}")
print(f"Device ID: {device_id}")
print(f"JWT: {jwt_token[:40]}...")

headers = {
    "Authorization": f"Cloud-IDE-JWT {jwt_token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

# 尝试多个签到API
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

# 检查签到状态
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

print("\nResults:", json.dumps(results, indent=2))
