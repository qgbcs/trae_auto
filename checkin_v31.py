#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v31
尝试直接发送 HTTP 请求到签到 API
"""

import json
import time
import pyautogui
import mss
from PIL import Image
import win32gui
import urllib.request
import urllib.error
import http.client

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

def find_trae_window():
    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title or 'Trae' in title:
                results.append((hwnd, title))
    results = []
    win32gui.EnumWindows(enum_callback, results)
    return results[0] if results else None

def read_credits_status():
    try:
        with open(r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        icube_raw = data.get('iCubeServerData://icube.cloudide', '{}')
        icube_data = json.loads(icube_raw)
        for act in icube_data.get('commercialActivityInfo', {}).get('activities', []):
            if act.get('activityId') == 'checkin_credits':
                return act.get('workExtra', {}).get('granted', False)
        return False
    except:
        return False

def save_screenshot(path):
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(path, "PNG")
    print(f"  截图: {path}")

def get_jwt_token():
    """获取 JWT Token"""
    try:
        with open(r'C:\Users\Administrator\.trae-cn\trae-jwt-token', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

def try_api_endpoint(url, method="POST", headers=None):
    """尝试 API 端点"""
    if headers is None:
        headers = {}

    token = get_jwt_token()
    if token:
        headers['Authorization'] = f'Cloud-IDE-JWT {token}'

    try:
        req = urllib.request.Request(url, method=method, headers=headers, data=b'{}' if method == "POST" else None)
        if method == "POST":
            req.data = req.data.encode('utf-8') if isinstance(req.data, str) else req.data

        resp = urllib.request.urlopen(req, timeout=5)
        result = resp.read().decode('utf-8')
        print(f"  ✓ {url}")
        print(f"    状态: {resp.status}")
        print(f"    响应: {result[:200]}")
        return json.loads(result) if result else {}
    except urllib.error.HTTPError as e:
        print(f"  ✗ {url}")
        print(f"    状态: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"  ✗ {url}: {e}")
        return None

def try_local_proxy():
    """尝试本地代理"""
    print("\n[代理] 尝试本地代理...")

    # 本地代理端口
    proxy_port = 2255

    # 尝试 RPC 接口
    endpoints = [
        f'http://127.0.0.1:{proxy_port}/api/checkin',
        f'http://127.0.0.1:{proxy_port}/api/claim-checkin',
        f'http://127.0.0.1:{proxy_port}/checkin',
        f'http://127.0.0.1:{proxy_port}/claim',
    ]

    for url in endpoints:
        try_api_endpoint(url)

    # 尝试 Health check
    try_api_endpoint(f'http://127.0.0.1:{proxy_port}/health')
    try_api_endpoint(f'http://127.0.0.1:{proxy_port}/')

    return False

def try_electron_api():
    """尝试 Electron 内部 API"""
    print("\n[Electron] 尝试 Electron API...")

    token = get_jwt_token()
    if not token:
        print("  无法获取 JWT Token")
        return False

    # 可能的 API 端点
    base_urls = [
        'https://trae-api-cn.mchost.guru',
        'https://api.trae.cn',
        'https://icube.cloudide.io',
    ]

    paths = [
        '/api/v1/checkin',
        '/api/v1/credits/checkin',
        '/api/v1/activity/checkin',
        '/api/v1/claim-checkin',
        '/commercial/checkin',
        '/credits/checkin',
        '/checkin',
    ]

    for base in base_urls:
        for path in paths:
            url = base + path
            try_api_endpoint(url)

    # 尝试使用 fetch-like 请求
    print("\n  尝试 POST JSON 请求...")
    for base in base_urls:
        url = base + '/api/v1/checkin'
        try:
            import urllib.request
            req = urllib.request.Request(url, method='POST')
            req.add_header('Authorization', f'Cloud-IDE-JWT {token}')
            req.add_header('Content-Type', 'application/json')
            resp = urllib.request.urlopen(req, timeout=5)
            print(f"  ✓ {url}: {resp.read().decode()[:200]}")
        except Exception as e:
            print(f"  ✗ {url}: {e}")

    return False

def try_vscode_ipc():
    """尝试 VSCode IPC"""
    print("\n[IPC] 尝试 VSCode IPC...")

    # 查找 VSCode IPC pipe
    import glob
    pipes = glob.glob(r'\\.\pipe\vscode-*')
    print(f"  找到的 pipes: {pipes[:5]}")

    # 尝试连接到 IPC
    for pipe in pipes:
        if 'ipc' in pipe.lower():
            try:
                import socket
                # Windows named pipe
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(pipe)
                print(f"  连接到 {pipe}")

                # 发送 IPC 消息
                # vscode:sandbox::main-invoke-claimCheckinCredits
                msg = json.dumps({
                    'type': 'invoke',
                    'channel': 'vscode:sandbox::main-invoke-claimCheckinCredits',
                    'args': []
                }).encode()
                sock.send(msg)
                time.sleep(1)

                # 读取响应
                response = sock.recv(4096)
                print(f"  响应: {response.decode()[:200]}")
                sock.close()
                return True
            except Exception as e:
                print(f"  {pipe}: {e}")

    return False

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v31 - API 尝试")
    print("=" * 50)

    if read_credits_status():
        print("今天已签到")
        return True

    # 查找窗口
    result = find_trae_window()
    if not result:
        print("未找到窗口")
        return False
    hwnd, title = result
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)

    # 策略1: 本地代理
    try_local_proxy()

    # 策略2: Electron API
    try_electron_api()

    # 策略3: VSCode IPC
    try_vscode_ipc()

    # 策略4: UI 自动化作为最后手段
    print("\n[UI] 尝试 UI 自动化...")
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(0.5)
    pyautogui.typewrite('用量')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v31_ui.png')

    # 精确点击"每日签到"按钮
    # 根据之前的分析，按钮在 (937, 400) 附近
    # 但我们需要找到按钮的可点击区域
    # 尝试点击按钮的中心点

    print("\n  点击'每日签到'按钮...")
    # 尝试多个位置
    positions = [
        (937, 400),
        (950, 400),
        (937, 405),
        (945, 400),
    ]

    for x, y in positions:
        print(f"  尝试 ({x}, {y})...")
        pyautogui.click(x, y)
        time.sleep(1)

        if read_credits_status():
            save_screenshot(r'C:\test\github\trae_auto\screenshot_v31_success.png')
            print(f"\n✓ 签到成功！")
            return True

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v31_failed.png')
    print("\n✗ 所有尝试失败")
    return False

if __name__ == '__main__':
    checkin()
