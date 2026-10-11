"""
分析Trae CN的签到机制
尝试找到正确的API调用方式
"""
import json
import time
import sys
import socket
import struct
import requests
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# JWT Token
JWT_PATH = Path.home() / '.trae-cn' / 'trae-jwt-token'
token = JWT_PATH.read_text().strip() if JWT_PATH.exists() else ''

# storage.json中的信息
STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'

def parse_storage():
    """解析storage.json获取关键信息"""
    if not STORAGE_JSON.exists():
        return {}

    data = json.loads(STORAGE_JSON.read_text())
    icube_data = data.get('iCubeServerData://icube.cloudide', '{}')

    if isinstance(icube_data, str):
        icube_data = json.loads(icube_data)

    print("\n[storage.json分析]")
    print(f"  serverTime: {icube_data.get('serverTimeInfo', {}).get('serverTime')}")

    commercial = icube_data.get('commercialActivityInfo', {})
    activities = commercial.get('activities', [])

    for act in activities:
        print(f"\n  活动: {act.get('activityId')}")
        print(f"    activityType: {act.get('activityType')}")
        print(f"    enabled: {act.get('enabled')}")
        print(f"    workExtra: {act.get('workExtra')}")

    return icube_data

def try_http_api():
    """尝试通过HTTP API调用签到"""
    print("\n[HTTP API测试]")

    # 从Trae CN的Electron应用中提取的API端点
    api_bases = [
        "https://trae.api.byteintl.net",
        "https://api.trae.ai",
    ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Trae-CN/1.0",
    }

    # 尝试不同的API路径
    paths = [
        "/api/v1/activity/checkin",
        "/api/v1/activities/checkin_credits",
        "/api/v1/checkin",
        "/v1/checkin",
    ]

    for base in api_bases:
        for path in paths:
            url = f"{base}{path}"
            try:
                resp = requests.post(url, headers=headers, json={
                    "activityId": "checkin_credits"
                }, timeout=5)

                if resp.status_code != 404:
                    print(f"  [!] 找到端点: {url}")
                    print(f"      状态码: {resp.status_code}")
                    print(f"      响应: {resp.text[:200]}")

                    if resp.status_code == 200:
                        return resp.json()
            except Exception as e:
                pass

    return None

def main():
    print("="*60)
    print("Trae CN 签到机制分析")
    print("="*60)

    # 1. 分析storage.json
    parse_storage()

    # 2. 尝试HTTP API
    result = try_http_api()

    if result:
        print(f"\n[SUCCESS] API调用成功!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n[-] HTTP API未找到可用端点")

    print("\n" + "="*60)
    print("建议: 使用浏览器开发者工具捕获签到时的网络请求")
    print("      或分析Electron应用的内部IPC调用")
    print("="*60)

if __name__ == '__main__':
    main()
