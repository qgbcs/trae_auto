"""
直接发送HTTP请求到Trae API
尝试找到正确的签到API端点
"""
import requests
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# 读取JWT token
JWT_PATH = Path.home() / '.trae-cn' / 'trae-jwt-token'
token = JWT_PATH.read_text().strip() if JWT_PATH.exists() else ''
print(f"[+] JWT token: {token[:30]}...")

# Trae API基础URL（从网络抓包获取）
BASE_URLS = [
    "https://trae.api.byteintl.net",
    "https://api.trae.ai",
    "https://icube.cloudide.com",
]

# 可能的签到API路径
CHECKIN_PATHS = [
    "/api/v1/activity/checkin",
    "/api/v1/activities/checkin",
    "/api/v1/credits/checkin",
    "/icube/api/v1/checkin",
    "/icube/api/v1/activities/checkin_credits",
    "/act/v1/checkin",
    "/v1/checkin",
]

HEADERS = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Trae-CN/1.0",
}

def try_checkin(url_base, path):
    """尝试调用签到API"""
    url = f"{url_base}{path}"
    try:
        # 尝试POST请求
        resp = requests.post(url, headers=HEADERS, json={"activityId": "checkin_credits"}, timeout=5)
        if resp.status_code != 404:
            print(f"[+] 找到可用端点: {url}")
            print(f"    状态码: {resp.status_code}")
            print(f"    响应: {resp.text[:200]}")
            return resp
    except Exception as e:
        pass
    return None

def main():
    print("\n=== 尝试所有可能的API端点 ===\n")

    for base in BASE_URLS:
        print(f"\n[>] 测试基础URL: {base}")
        for path in CHECKIN_PATHS:
            resp = try_checkin(base, path)
            if resp:
                print(f"\n[SUCCESS] {base}{path}")
                return

    print("\n[-] 未找到可用的签到API端点")
    print("\n建议: 使用浏览器开发者工具捕获签到时的网络请求，获取准确的API端点")

if __name__ == '__main__':
    main()
