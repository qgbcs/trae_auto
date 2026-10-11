#!/usr/bin/env python3
"""
Trae CN 自动签到 v8 - 通过本地代理 + HTTP API 调用
分析实际的 API 调用流程
"""

import json
import time
import sys
import os
import urllib.request
import urllib.error

LOCAL_PROXY = "http://localhost:2255"
TRAJ_PATH = os.path.expanduser(r"C:\Users\Administrator\.trae-cn\trae-jwt-token")
ENV_PATH = os.path.expanduser(r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json")


def rpc_call(code):
    """通过本地代理执行 Python 代码"""
    url = f"{LOCAL_PROXY}/r="
    data = code.encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}"
    except Exception as e:
        return f"Error: {e}"


def read_jwt():
    try:
        with open(TRAJ_PATH, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None


def read_env():
    try:
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def main():
    print("=" * 60)
    print("Trae CN 签到分析 v8 (HTTP API)")
    print("=" * 60)

    jwt = read_jwt()
    env = read_env()

    if not jwt:
        print("[错误] 无法读取 JWT")
        return 1
    if not env:
        print("[错误] 无法读取环境配置")
        return 1

    host = env.get('host', '')
    device_id = env.get('device_id', '')
    user_id = env.get('user_id', '3273694480187068')

    print(f"[配置] Host: {host}")
    print(f"[配置] Device ID: {device_id}")
    print(f"[配置] User ID: {user_id}")

    # 尝试多种 API 端点
    endpoints = [
        # 可能的签到端点
        f"{host}/api/v1/activity/checkin",
        f"{host}/api/v1/activity/checkin/claim",
        f"{host}/icube/api/v1/checkin/credits",
        f"{host}/api/v1/credits/checkin",
        f"{host}/api/v1/checkin",
        f"{host}/api/user/checkin",
        # 可能的活动端点
        f"{host}/api/v1/activity",
        f"{host}/api/v1/activities",
        # 可能的商业化端点
        f"{host}/api/commerce/checkin",
        f"{host}/api/v1/commerce/checkin",
        # 可能的积分端点
        f"{host}/api/v1/points/checkin",
        f"{host}/api/v1/credits/status",
        f"{host}/api/v1/credits/checkin",
    ]

    headers = {
        "Authorization": f"Cloud-IDE-JWT {jwt}",
        "Content-Type": "application/json",
        "User-Agent": "Trae-CN/1.0",
        "X-Device-Id": device_id,
        "X-User-Id": user_id,
    }

    print("\n[测试] 尝试查询签到状态...")

    # 先尝试 GET 查询状态
    for endpoint in endpoints[:5]:
        try:
            url = f"{endpoint}/status" if '/checkin' not in endpoint else endpoint
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=10)
            data = resp.read().decode('utf-8')
            print(f"[OK] {url}")
            print(f"     Status: {resp.status}")
            print(f"     Response: {data[:200]}")
            return 0
        except urllib.error.HTTPError as e:
            print(f"[{e.code}] {url}")
        except Exception as e:
            print(f"[ERR] {url}: {e}")

    # 尝试 POST claim
    print("\n[测试] 尝试 POST claim...")
    for endpoint in endpoints:
        if 'checkin' in endpoint.lower():
            try:
                payload = json.dumps({
                    "activityId": "checkin_credits",
                    "deviceId": device_id,
                    "userId": user_id
                }).encode()

                req = urllib.request.Request(
                    endpoint,
                    data=payload,
                    headers={**headers, "Content-Length": str(len(payload))}
                )
                resp = urllib.request.urlopen(req, timeout=10)
                data = resp.read().decode('utf-8')
                print(f"[成功] {endpoint}")
                print(f"       Response: {data}")
                return 0
            except urllib.error.HTTPError as e:
                body = e.read().decode('utf-8', errors='replace')[:100]
                print(f"[{e.code}] {endpoint}: {body}")
            except Exception as e:
                print(f"[ERR] {endpoint}: {e}")

    print("\n[信息] 所有 API 端点测试完毕")
    print("建议: 使用 Fiddler/Charles 抓包手动签到，获取正确的 API 路径")
    return 1


if __name__ == "__main__":
    sys.exit(main())
