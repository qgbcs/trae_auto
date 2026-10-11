#!/usr/bin/env python3
"""
Trae CN 自动签到 v11 - 深度 API 分析 + 精确 UI 自动化
"""

import json
import time
import sys
import os
import urllib.request
import urllib.error

LOCAL_PROXY = "http://localhost:2255"
TRAJ_PATH = r"C:\Users\Administrator\.trae-cn\trae-jwt-token"
ENV_PATH = r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json"


def rpc_exec(code):
    """通过本地代理执行 Python 代码"""
    url = f"{LOCAL_PROXY}/r="
    data = code.encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}"
    except Exception as e:
        return f"Error: {e}"


def main():
    print("=" * 60)
    print("Trae CN 签到分析 v11")
    print("=" * 60)

    # 读取配置
    jwt = open(TRAJ_PATH).read().strip()
    env = json.load(open(ENV_PATH))
    host = env['host']
    did = env['device_id']

    print(f"Host: {host}")
    print(f"Device ID: {did}")
    print(f"JWT: {jwt[:40]}...")

    # 通过本地代理执行更全面的 API 探测
    code = f'''
import urllib.request
import json
import re

jwt = r"{jwt}"
host = "{host}"
did = "{did}"

paths = [
    "/api/v1/activity/checkin",
    "/api/v1/activity/checkin/claim",
    "/api/v1/activity/checkin/status",
    "/api/v1/activity/claim",
    "/api/v1/activities/checkin",
    "/api/v1/activities/checkin/claim",
    "/api/v1/checkin",
    "/api/v1/checkin/claim",
    "/icube/api/v1/checkin/credits",
    "/icube/api/v1/checkin/credits/claim",
    "/icube/api/v1/activities/checkin",
    "/api/v1/commerce/checkin",
    "/api/v1/commerce/activity/checkin",
    "/api/v1/commerce/activities",
    "/api/v1/user/activity",
    "/api/v1/user/activities",
    "/api/v1/user/activities/checkin",
    "/api/v1/marketplace/activity",
    "/api/v1/marketplace/activities",
    "/api/v1/marketplace/checkin",
    "/api/v1/market/activities",
    "/act/v1/checkin",
    "/act/v1/activity/checkin",
    "/v1/checkin",
    "/v1/activity/checkin",
]

headers = {{
    "Authorization": f"Cloud-IDE-JWT {{jwt}}",
    "Content-Type": "application/json",
    "X-Device-Id": did,
}}

results = {{}}

# Test GET
for path in paths:
    url = host + path
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode("utf-8", errors="replace")
        results[path] = {{"method": "GET", "status": resp.status, "body": body[:200]}}
        print(f"GET {{path}}: {{resp.status}} - {{body[:100]}}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:100]
        results[path] = {{"method": "GET", "status": e.code, "error": body}}
        print(f"GET {{path}}: {{e.code}} - {{body}}")
    except Exception as e:
        results[path] = {{"method": "GET", "error": str(e)}}
        print(f"GET {{path}}: ERROR - {{e}}")

# Test POST claim
for path in paths:
    if "checkin" in path.lower() or "claim" in path.lower():
        url = host + path
        data = json.dumps({{"activityId": "checkin_credits"}}).encode()
        try:
            req = urllib.request.Request(url, data=data, headers={{**headers, "Content-Length": str(len(data))}})
            resp = urllib.request.urlopen(req, timeout=5)
            body = resp.read().decode("utf-8")
            results[f"POST{{path}}"] = {{"status": resp.status, "body": body[:200]}}
            print(f"POST {{path}}: {{resp.status}} - {{body[:150]}}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:100]
            results[f"POST{{path}}"] = {{"status": e.code, "error": body}}
            print(f"POST {{path}}: {{e.code}} - {{body}}")
        except Exception as e:
            results[f"POST{{path}}"] = {{"error": str(e)}}
            print(f"POST {{path}}: ERROR - {{e}}")

print("\\n=== RESULTS ===")
print(json.dumps(results, indent=2, ensure_ascii=False))
'''

    print("\n执行 API 探测...")
    result = rpc_exec(code)
    print(result)


if __name__ == "__main__":
    main()
