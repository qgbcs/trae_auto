"""
Trae CN 签到IPC调试脚本 v1
分析源码并尝试通过不同方式调用签到API
"""
import subprocess
import json
import time
import urllib.request
import urllib.error
import ssl
import http.client
from pathlib import Path

def get_trae_processes():
    """获取Trae进程信息"""
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq Trae CN.exe', '/V', '/FO', 'JSON'],
        capture_output=True, text=True, encoding='utf-8'
    )
    try:
        data = json.loads(result.stdout)
        return data.get('Process', [])
    except:
        return []

def test_port_connection(port, timeout=2):
    """测试端口连接"""
    try:
        conn = http.client.HTTPConnection('127.0.0.1', port, timeout=timeout)
        conn.request('GET', '/json/version')
        resp = conn.getresponse()
        body = resp.read().decode('utf-8')
        conn.close()
        return {
            'status': resp.status,
            'body': body[:200] if body else '',
            'headers': dict(resp.getheaders())
        }
    except Exception as e:
        return {
            'error': str(e),
            'type': type(e).__name__
        }

def test_http_api(base_url, endpoint, method='GET', data=None):
    """测试HTTP API"""
    try:
        url = f"{base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        req_data = json.dumps(data).encode('utf-8') if data else None

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url,
            data=req_data,
            headers=headers,
            method=method
        )

        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            body = resp.read().decode('utf-8')
            return {
                'status': resp.status,
                'body': body[:500] if body else ''
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        return {
            'error': f'HTTP {e.code}',
            'body': body[:500]
        }
    except Exception as e:
        return {
            'error': f'{type(e).__name__}: {str(e)[:100]}'
        }

def get_jwt_token():
    """获取JWT Token"""
    token_path = Path.home() / '.trae-cn' / 'trae-jwt-token'
    if token_path.exists():
        return token_path.read_text().strip()
    return None

def read_storage_data():
    """读取storage.json中的icube数据"""
    storage_path = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
    if storage_path.exists():
        data = json.loads(storage_path.read_text())
        icube_data = data.get('iCubeServerData://icube.cloudide', '')
        if icube_data:
            try:
                return json.loads(icube_data)
            except:
                pass
    return None

def main():
    print("=" * 60)
    print("Trae CN 签到IPC调试")
    print("=" * 60)

    # 1. 获取进程信息
    print("\n[1] 检查Trae进程...")
    processes = get_trae_processes()
    if processes:
        for p in processes:
            print(f"  PID: {p.get('PID')}, Name: {p.get('ProcessName')}")
    else:
        print("  未找到Trae进程")
        return

    pid = processes[0].get('PID')

    # 2. 扫描已知端口
    print("\n[2] 扫描端口...")
    ports_to_check = [51000, 62900, 9229, 60883, 52883, 44445, 37315, 16371]
    port_results = {}

    for port in ports_to_check:
        result = test_port_connection(port)
        port_results[port] = result
        status = 'OK' if 'status' in result else 'FAIL'
        print(f"  端口 {port}: {status}")
        if 'error' in result:
            print(f"    错误: {result['error']}")
        if 'status' in result and result['status'] == 200:
            print(f"    Body: {result['body'][:100]}...")

    # 3. 获取JWT Token
    print("\n[3] 获取认证Token...")
    jwt_token = get_jwt_token()
    if jwt_token:
        print(f"  Token存在: {jwt_token[:50]}...")
    else:
        print("  未找到Token")

    # 4. 读取storage数据
    print("\n[4] 读取Storage数据...")
    storage_data = read_storage_data()
    if storage_data:
        commercial = storage_data.get('commercialActivityInfo', {})
        activities = commercial.get('activities', [])
        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                print(f"  签到活动状态:")
                print(f"    activityType: {act.get('activityType')}")
                print(f"    workExtra: {act.get('workExtra')}")
                print(f"    enabled: {act.get('enabled')}")
        server_time = commercial.get('serverTimeInfo', {}).get('serverTime', 0)
        print(f"  Server Time: {server_time}")
    else:
        print("  未找到Storage数据")

    # 5. 尝试各种API端点
    print("\n[5] 尝试API端点...")

    # 可能的API端点列表
    api_endpoints = [
        # iCube API
        ('http://127.0.0.1:51000', '/api/icube/checkin'),
        ('http://127.0.0.1:51000', '/api/icube/activity/claim'),
        ('http://127.0.0.1:51000', '/api/commercial/claimCheckinCredits'),
        ('http://127.0.0.1:51000', '/icube/api/checkin'),
        ('http://127.0.0.1:51000', '/api/v1/checkin'),

        # 尝试不同的端口
        ('http://127.0.0.1:62900', '/api/checkin'),
        ('http://127.0.0.1:62900', '/json'),
        ('http://127.0.0.1:9229', '/json'),

        # 常见的后端端口
        ('http://127.0.0.1:3000', '/api/checkin'),
        ('http://127.0.0.1:8080', '/api/checkin'),
        ('http://127.0.0.1:8888', '/api/checkin'),
    ]

    for base_url, endpoint in api_endpoints:
        result = test_http_api(base_url, endpoint)
        if 'error' in result:
            error_msg = result['error'][:50]
            print(f"  {base_url}{endpoint}: {error_msg}")
        else:
            print(f"  {base_url}{endpoint}: HTTP {result['status']}")
            if result['body']:
                print(f"    Response: {result['body'][:100]}...")

    # 6. 尝试使用JWT Token认证
    print("\n[6] 尝试带Token的API调用...")
    if jwt_token:
        test_endpoints = [
            ('http://127.0.0.1:51000', '/api/icube/checkin'),
            ('http://127.0.0.1:51000', '/api/commercial/checkin'),
        ]

        for base_url, endpoint in test_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                headers = {
                    'Authorization': f'Bearer {jwt_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

                req_data = json.dumps({
                    'activityId': 'checkin_credits',
                    'activityType': 104
                }).encode('utf-8')

                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                req = urllib.request.Request(
                    url,
                    data=req_data,
                    headers=headers,
                    method='POST'
                )

                with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                    body = resp.read().decode('utf-8')
                    print(f"  {endpoint}: HTTP {resp.status}")
                    print(f"    Response: {body[:200]}")
            except urllib.error.HTTPError as e:
                body = e.read().decode('utf-8', errors='ignore')
                print(f"  {endpoint}: HTTP {e.code}")
                print(f"    Response: {body[:200]}")
            except Exception as e:
                print(f"  {endpoint}: {type(e).__name__}: {str(e)[:50]}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
