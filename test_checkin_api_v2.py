# -*- coding: utf-8 -*-
"""
通过本地代理拦截网络请求，找到正确的签到 API 路径
"""
import json
import requests
import time

API_HOST = "https://trae-api-cn.mchost.guru"
JWT_TOKEN_PATH = r"C:\Users\Administrator\.trae-cn\trae-jwt-token"

with open(JWT_TOKEN_PATH, "r") as f:
    JWT_TOKEN = f.read().strip()

headers = {
    "Authorization": f"Cloud-IDE-JWT {JWT_TOKEN}",
    "Content-Type": "application/json",
}

# 先尝试获取用户信息，看看有什么数据
print("=== 获取用户信息 ===")
try:
    resp = requests.get(f"{API_HOST}/api/v1/user/info", headers=headers, timeout=10)
    print(f"GET /api/v1/user/info: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")

print("\n=== 获取活动列表 ===")
try:
    resp = requests.get(f"{API_HOST}/api/v1/activities", headers=headers, timeout=10)
    print(f"GET /api/v1/activities: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")

print("\n=== 获取商业活动列表 ===")
try:
    resp = requests.get(f"{API_HOST}/api/v1/commerce/activities", headers=headers, timeout=10)
    print(f"GET /api/v1/commerce/activities: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")

print("\n=== 获取 marketplace 活动 ===")
try:
    resp = requests.get(f"{API_HOST}/api/v1/marketplace/activities", headers=headers, timeout=10)
    print(f"GET /api/v1/marketplace/activities: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")

print("\n=== 获取 ICube 活动 ===")
try:
    resp = requests.get(f"{API_HOST}/api/v1/icube/activities", headers=headers, timeout=10)
    print(f"GET /api/v1/icube/activities: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")

print("\n=== 尝试 GET checkin 状态 ===")
try:
    resp = requests.get(f"{API_HOST}/api/v1/checkin/status", headers=headers, timeout=10)
    print(f"GET /api/v1/checkin/status: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")

print("\n=== 尝试带 userId 的 checkin ===")
try:
    resp = requests.get(f"{API_HOST}/api/v1/activities/checkin?userId={JWT_TOKEN.split('.')[0]}", headers=headers, timeout=10)
    print(f"GET /api/v1/activities/checkin: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")
