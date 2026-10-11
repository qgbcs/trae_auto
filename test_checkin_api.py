# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v6 - 直接 API 调用方案
"""
import json
import requests
import sys

API_HOST = "https://trae-api-cn.mchost.guru"
USER_ID = "3273694480187068"
DEVICE_ID = "3326471038840857"

# 读取 JWT token
with open(r"C:\Users\Administrator\.trae-cn\trae-jwt-token", "r", encoding="utf-8") as f:
    JWT_TOKEN = f.read().strip()

print(f"JWT Token: {JWT_TOKEN[:50]}...")
print(f"User ID: {USER_ID}")
print(f"Device ID: {DEVICE_ID}")
print(f"API Host: {API_HOST}")
print()

headers = {
    "Authorization": f"Cloud-IDE-JWT {JWT_TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Trae-CN/1.0",
}

# 测试多个可能的 API 端点
endpoints = [
    # ICube 商业活动相关
    f"/api/v1/activity/checkin",
    f"/api/v1/activities/checkin",
    f"/api/v1/checkin",
    f"/api/v1/icube/activity/checkin",
    f"/api/v1/icube/activities/checkin",
    f"/api/v1/marketplace/activity/checkin",
    f"/api/v1/marketplace/activities/checkin",
    # 商业化活动
    f"/api/v1/commerce/activity/checkin",
    f"/api/v1/commerce/activities/checkin",
    f"/api/v1/biz/activity/checkin",
    # 用户相关
    f"/api/v1/user/checkin",
    f"/api/v1/users/checkin",
    # 尝试不带 /api/v1/
    "/activity/checkin",
    "/activities/checkin",
    "/checkin",
    # ICube 可能的路径
    "/api/v2/icube/activities/checkin",
    "/api/v2/activities/checkin",
]

print("Testing endpoints:")
for ep in endpoints:
    url = API_HOST + ep
    try:
        resp = requests.post(url, headers=headers, json={
            "userId": USER_ID,
            "deviceId": DEVICE_ID,
        }, timeout=5)
        print(f"  {resp.status_code:3d} {ep}")
        if resp.status_code != 404:
            try:
                print(f"        Response: {resp.text[:200]}")
            except:
                pass
    except Exception as e:
        print(f"  ERR  {ep}: {e}")
