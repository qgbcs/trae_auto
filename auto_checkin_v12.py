#!/usr/bin/env python3
"""
Trae CN 自动签到 v12 - 通过本地代理执行完整分析
"""

import json
import time
import sys
import os
import urllib.request
import urllib.error

LOCAL_PROXY = "http://localhost:2255"


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
    print("Trae CN 签到分析 v12 (完整)")
    print("=" * 60)

    # 读取配置
    jwt = open(r"C:\Users\Administrator\.trae-cn\trae-jwt-token").read().strip()
    env = json.load(open(r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json"))
    host = env['host']
    did = env['device_id']

    print(f"Host: {host}")
    print(f"Device ID: {did}")

    # 完整的 API 探测脚本
    code = f'''
import urllib.request
import json

jwt = r"{jwt}"
host = "{host}"
did = "{did}"

# 基于 VSCode/Trae 商业化系统的常见 API 模式
paths = [
    # 活动相关
    "/api/v1/activity",
    "/api/v1/activities",
    "/api/v1/activity/checkin",
    "/api/v1/activity/checkin/claim",
    "/api/v1/activity/checkin/status",
    "/api/v1/activity/checkin_credits",
    "/api/v1/activity/claim",
    "/api/v1/activities/checkin",
    "/api/v1/activities/checkin/claim",
    # ICube 相关
    "/icube/api/v1/checkin",
    "/icube/api/v1/checkin/credits",
    "/icube/api/v1/checkin/credits/claim",
    "/icube/api/v1/checkin/credits/status",
    "/icube/api/v1/activities",
    "/icube/api/v1/activities/checkin",
    "/icube/api/v1/activity/checkin",
    # 商业化相关
    "/api/v1/commerce",
    "/api/v1/commerce/activities",
    "/api/v1/commerce/checkin",
    "/api/v1/commerce/activity/checkin",
    "/api/v1/commerce/activity/checkin/claim",
    # Credits 相关
    "/api/v1/credits",
    "/api/v1/credits/checkin",
    "/api/v1/credits/checkin/claim",
    "/api/v1/credits/status",
    "/api/v1/credits/checkin/status",
    # 用户相关
    "/api/v1/user/activity",
    "/api/v1/user/activities",
    "/api/v1/user/activities/checkin",
    "/api/v1/user/checkin",
    "/api/v1/user/checkin/claim",
    # Marketplace 相关
    "/api/v1/marketplace",
    "/api/v1/marketplace/activities",
    "/api/v1/marketplace/checkin",
    "/api/v1/marketplace/activity/checkin",
    # 可能的其他模式
    "/act/v1/checkin",
    "/act/v1/activity/checkin",
    "/v1/checkin",
    "/v1/activity/checkin",
    "/api/checkin",
    "/api/activity/checkin",
]

headers = {{
    "Authorization": f"Cloud-IDE-JWT {{jwt}}",
    "Content-Type": "application/json",
    "X-Device-Id": did,
    "X-User-Id": "3273694480187068",
}}

results = {{}}

# Test GET endpoints
print("=== Testing GET endpoints ===")
for path in paths:
    url = host + path
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode("utf-8", errors="replace")
        results[f"GET{{path}}"] = {{
            "status": resp.status,
            "body": body[:300]
        }}
        print(f"✓ GET {{path}}: {{resp.status}}")
        print(f"  {{body[:200]}}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:150]
        results[f"GET{{path}}"] = {{
            "status": e.code,
            "error": body
        }}
        if e.code not in [404]:  # 只显示非 404 的错误
            print(f"{{e.code}} GET {{path}}: {{body}}")
    except Exception as e:
        results[f"GET{{path}}"] = {{
            "error": str(e)
        }}
        print(f"ERR GET {{path}}: {{e}}")

# Test POST claim endpoints
print("\\n=== Testing POST claim endpoints ===")
for path in paths:
    if "checkin" in path.lower() or "claim" in path.lower():
        url = host + path
        # 尝试不同的请求体
        payloads = [
            json.dumps({{"activityId": "checkin_credits"}}),
            json.dumps({{"activity_id": "checkin_credits"}}),
            json.dumps({{"activityId": "checkin_credits", "deviceId": did}}),
            json.dumps({{"id": "checkin_credits"}}),
        ]
        for i, payload in enumerate(payloads):
            data = payload.encode()
            try:
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={{**headers, "Content-Length": str(len(data))}}
                )
                resp = urllib.request.urlopen(req, timeout=5)
                body = resp.read().decode("utf-8")
                results[f"POST{{path}}_{{i}}"] = {{
                    "status": resp.status,
                    "body": body[:300]
                }}
                print(f"✓ POST {{path}} (payload {{i}}): {{resp.status}}")
                print(f"  {{body[:200]}}")
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")[:150]
                results[f"POST{{path}}_{{i}}"] = {{
                    "status": e.code,
                    "error": body
                }}
                if e.code not in [404]:
                    print(f"{{e.code}} POST {{path}} (payload {{i}}): {{body}}")
            except Exception as e:
                results[f"POST{{path}}_{{i}}"] = {{
                    "error": str(e)
                }}

print("\\n=== Summary ===")
success_paths = [k for k in results if results[k].get("status") not in [404, None]]
if success_paths:
    print(f"Found {{len(success_paths)}} working endpoints:")
    for p in success_paths[:10]:
        print(f"  {{p}}: {{results[p]}}")
else:
    print("No working endpoints found (all 404)")
    print("\\nTrying with different headers...")

    # 尝试不同的认证头
    alt_headers = [
        {{
            "Authorization": f"Bearer {{jwt}}",
            "Content-Type": "application/json",
            "X-Device-Id": did,
        }},
        {{
            "Authorization": f"JWT {{jwt}}",
            "Content-Type": "application/json",
            "X-Device-Id": did,
        }},
        {{
            "Cookie": f"token={{jwt}}",
            "Content-Type": "application/json",
        }},
    ]

    for h_idx, h in enumerate(alt_headers):
        for path in ["/api/v1/activity/checkin", "/api/v1/checkin", "/icube/api/v1/checkin/credits"]:
            url = host + path
            data = json.dumps({{"activityId": "checkin_credits"}}).encode()
            try:
                req = urllib.request.Request(url, data=data, headers={{**h, "Content-Length": str(len(data))}})
                resp = urllib.request.urlopen(req, timeout=5)
                body = resp.read().decode("utf-8")
                print(f"✓ Header {{h_idx}} POST {{path}}: {{resp.status}} - {{body[:200]}}")
            except Exception as e:
                print(f"✗ Header {{h_idx}} POST {{path}}: {{e}}")
'''

    result = rpc_exec(code)
    print(result)


if __name__ == "__main__":
    main()
