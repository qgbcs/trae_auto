# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v7 - 直接 API 调用方案
基于从 workbench.desktop.main.js 逆向的工程出的 API 路径和认证方式
"""
import json
import requests
import time
import sys
import os

API_HOST = "https://trae-api-cn.mchost.guru"
JWT_TOKEN_PATH = r"C:\Users\Administrator\.trae-cn\trae-jwt-token"
USER_ID = "3273694480187068"
DEVICE_ID = "3326471038840857"

# 读取 JWT token
with open(JWT_TOKEN_PATH, "r", encoding="utf-8") as f:
    JWT_TOKEN = f.read().strip()

print(f"JWT Token: {JWT_TOKEN[:50]}...")
print(f"User ID: {USER_ID}")
print(f"Device ID: {DEVICE_ID}")
print()

# 构造请求头（与 Trae 客户端一致）
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Cloud-IDE-JWT {JWT_TOKEN}",
    "x-device-id": DEVICE_ID,
    "User-Agent": "Trae-CN/1.0",
}

def make_request(method, path, data=None):
    """发送 API 请求"""
    url = f"{API_HOST}{path}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data or {}, timeout=10)
        else:
            return {"error": f"Unknown method: {method}"}
        print(f"  {method} {path} -> {resp.status_code}")
        try:
            body = resp.json()
            return body
        except:
            return {"raw": resp.text[:500]}
    except Exception as e:
        return {"error": str(e)}

# ========== 1. 先获取用户信息和活动列表 ==========
print("=== 步骤1: 获取用户信息 ===")
info = make_request("GET", "/api/v1/user/info")
print(json.dumps(info, indent=2, ensure_ascii=False)[:500])

print("\n=== 步骤2: 获取活动列表 ===")
# 尝试多个可能的活动 API 端点
activity_endpoints = [
    "/api/v1/activities",
    "/api/v1/icube/activities",
    "/api/v1/marketplace/activities",
    "/api/v1/commerce/activities",
    "/api/v1/user/activities",
]
for ep in activity_endpoints:
    result = make_request("GET", ep)
    if result and "error" not in result:
        print(f"  Found at {ep}: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}")
    else:
        print(f"  {ep}: {result.get('error', '404')}")

# ========== 2. 尝试签到状态查询 ==========
print("\n=== 步骤3: 查询签到状态 ===")
checkin_status_endpoints = [
    ("/api/v1/checkin/status", None),
    ("/api/v1/activities/checkin/status", None),
    ("/api/v1/icube/checkin/status", None),
    ("/api/v1/user/checkin/status", None),
    ("/api/v1/credits/checkin/status", None),
]
for ep, data in checkin_status_endpoints:
    result = make_request("GET", ep)
    print(f"  {ep}: {json.dumps(result, ensure_ascii=False)[:200]}")

# ========== 3. 尝试直接签到 ==========
print("\n=== 步骤4: 尝试签到 ===")
claim_endpoints = [
    ("/api/v1/checkin/claim", {"userId": USER_ID, "deviceId": DEVICE_ID}),
    ("/api/v1/activities/checkin/claim", {"userId": USER_ID, "deviceId": DEVICE_ID}),
    ("/api/v1/icube/checkin/claim", {"userId": USER_ID, "deviceId": DEVICE_ID}),
    ("/api/v1/user/checkin/claim", {"userId": USER_ID, "deviceId": DEVICE_ID}),
    ("/api/v1/credits/checkin/claim", {"userId": USER_ID, "deviceId": DEVICE_ID}),
]
for ep, data in claim_endpoints:
    result = make_request("POST", ep, data)
    print(f"  {ep}: {json.dumps(result, ensure_ascii=False)[:300]}")

# ========== 4. 尝试已知的使用量 API（可能包含签到信息）==========
print("\n=== 步骤5: 尝试使用量 API ===")
usage_result = make_request("POST", "/trae/api/v1/pay/ide_user_ent_usage", {"require_usage": True})
print(json.dumps(usage_result, indent=2, ensure_ascii=False)[:1000])
