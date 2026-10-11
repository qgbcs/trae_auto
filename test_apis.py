#!/usr/bin/env python3
"""
Trae CN 自动签到 v13 - 简化版 API 探测
"""

import json
import urllib.request
import urllib.error

JWT = open(r"C:\Users\Administrator\.trae-cn\trae-jwt-token").read().strip()
ENV = json.load(open(r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json"))
HOST = ENV['host']
DID = ENV['device_id']

HEADERS = {
    "Authorization": f"Cloud-IDE-JWT {JWT}",
    "Content-Type": "application/json",
    "X-Device-Id": DID,
}

# 核心端点列表（基于 VSCode/Trae 商业化系统）
ENDPOINTS = [
    "/api/v1/activity/checkin",
    "/api/v1/activity/checkin/claim",
    "/api/v1/checkin",
    "/api/v1/checkin/claim",
    "/icube/api/v1/checkin/credits",
    "/icube/api/v1/checkin/credits/claim",
    "/api/v1/commerce/checkin",
    "/api/v1/commerce/activity/checkin",
    "/api/v1/credits/checkin",
    "/api/v1/credits/checkin/claim",
]

print(f"Testing {len(ENDPOINTS)} endpoints on {HOST}...")
print()

for path in ENDPOINTS:
    url = HOST + path

    # GET test
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode('utf-8', errors='replace')
        print(f"✓ GET {path}: {resp.status}")
        print(f"  {body[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:100]
        if e.code != 404:
            print(f"{e.code} GET {path}: {body}")

    # POST test
    data = json.dumps({"activityId": "checkin_credits"}).encode()
    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={**HEADERS, "Content-Length": str(len(data))}
        )
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode('utf-8')
        print(f"✓ POST {path}: {resp.status}")
        print(f"  {body[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:100]
        if e.code != 404:
            print(f"{e.code} POST {path}: {body}")

print("\nDone!")
