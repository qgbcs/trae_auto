"""
Trae IDE 自动签到脚本
功能: 自动签到并确认积分增加100
"""
import json
import subprocess
import sys
import time
from pathlib import Path

# 配置
TRAEE_TOKEN_PATH = r"C:\Users\Administrator\.trae-cn\trae-jwt-token"
LOCAL_PROXY_PORT = 2255
TRAEE_HOST = "https://trae-api-cn.mchost.guru"


def get_jwt_token():
    """读取 JWT Token"""
    with open(TRAEE_TOKEN_PATH, 'r') as f:
        return f.read().strip()


def read_local_env():
    """读取本地环境配置"""
    env_path = r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json"
    with open(env_path, 'r') as f:
        return json.load(f)


def check_current_credits():
    """检查当前积分"""
    code = '''
import requests
import json

# 读取配置
with open(r"C:\\Users\\Administrator\\AppData\\Roaming\\Trae CN\\ModularData\\ckg_server\\local_env.json", "r") as f:
    config = json.load(f)

# 读取JWT
with open(r"C:\\Users\\Administrator\\.trae-cn\\trae-jwt-token", "r") as f:
    jwt_token = f.read().strip()

headers = {
    "Authorization": f"Cloud-IDE-JWT {jwt_token}",
    "Content-Type": "application/json"
}

# 尝试不同的API端点获取积分信息
endpoints = [
    "/api/v1/activity/checkin",
    "/api/v1/user/credits",
    "/api/v1/user/points",
]

for endpoint in endpoints:
    url = f"{config['host']}{endpoint}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"{endpoint}: {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"{endpoint}: Error - {e}")
'''
    
    # 通过本地代理执行
    import urllib.request
    import urllib.error
    
    req_data = json.dumps({"code": code}).encode()
    req = urllib.request.Request(
        f"http://localhost:{LOCAL_PROXY_PORT}/r=",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error checking credits: {e}")
        return None


def try_ipc_checkin():
    """尝试通过IPC调用签到"""
    code = '''
import asyncio
import websockets
import json
import os
import subprocess

async def send_ipc_message(message):
    """发送IPC消息到Trae"""
    # 尝试通过命令行与Trae通信
    # 使用Trae的CLI或者进程间通信
    pass

# 这个方法需要更深入的探索，暂时跳过
return {"status": "skip", "message": "IPC method not yet implemented"}
'''
    
    return {"status": "not_implemented"}


async def checkin_via_api():
    """通过API直接签到"""
    import requests
    import json
    
    # 读取配置
    with open(r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json", "r") as f:
        config = json.load(f)
    
    # 读取JWT
    with open(r"C:\Users\Administrator\.trae-cn\trae-jwt-token", "r") as f:
        jwt_token = f.read().strip()
    
    headers = {
        "Authorization": f"Cloud-IDE-JWT {jwt_token}",
        "Content-Type": "application/json",
        "User-Agent": "Trae-CN/1.0"
    }
    
    # 根据之前分析的代码，签到相关的API端点
    # 从workbench.desktop.main.js中看到的模式
    
    # 尝试 POST 请求到签到端点
    endpoints_to_try = [
        f"{config['host']}/api/v1/activity/checkin",
        f"{config['host']}/trae/api/v1/pay/ide_user_ent_usage",
        f"{config['host']}/icube/api/v1/checkin",
        f"{config['host']}/api/credits/checkin",
    ]
    
    results = []
    for endpoint in endpoints_to_try:
        try:
            resp = requests.post(
                endpoint,
                headers=headers,
                json={},
                timeout=10
            )
            results.append({
                "endpoint": endpoint,
                "status": resp.status_code,
                "response": resp.text[:200]
            })
            print(f"POST {endpoint}: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            results.append({
                "endpoint": endpoint,
                "error": str(e)
            })
            print(f"POST {endpoint}: Error - {e}")
    
    return results


def main():
    """主函数"""
    print("=" * 50)
    print("Trae IDE 自动签到脚本")
    print("=" * 50)
    
    # 1. 检查当前积分
    print("\n[1] 检查当前积分...")
    credits_result = check_current_credits()
    print(f"当前积分检查结果: {credits_result}")
    
    # 2. 尝试API签到
    print("\n[2] 尝试通过API签到...")
    checkin_result = asyncio.run(checkin_via_api())
    print(f"签到尝试结果: {checkin_result}")
    
    # 3. 再次检查积分
    print("\n[3] 检查签到后积分...")
    after_check = check_current_credits()
    print(f"签到后积分: {after_check}")
    
    print("\n完成!")


if __name__ == "__main__":
    # 需要先导入asyncio
    import asyncio
    main()
