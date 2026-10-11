#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v30
使用 Electron IPC 机制直接调用签到 API
"""

import json
import time
import pyautogui
import mss
from PIL import Image
import win32gui
import win32con
import win32api
import struct
import socket
import os
import threading

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

def try_electron_ipc():
    """尝试通过 Electron IPC 发送签到请求"""
    print("\n[IPC] 尝试 Electron IPC 方式...")

    # Electron 调试端口
    ports = [51000, 51001, 51002, 9222]

    for port in ports:
        try:
            # 尝试 WebSocket 连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect(('127.0.0.1', port))
            sock.close()
            print(f"  端口 {port} 开放")

            # 尝试 HTTP 请求
            try:
                import urllib.request
                req = urllib.request.Request(f'http://127.0.0.1:{port}/json')
                resp = urllib.request.urlopen(req, timeout=2)
                print(f"  HTTP 响应: {resp.read().decode()[:200]}")
            except Exception as e:
                print(f"  HTTP 失败: {e}")

            # 尝试 WebSocket
            try:
                import websocket
                ws = websocket.create_connection(f'ws://127.0.0.1:{port}', timeout=2)
                print(f"  WebSocket 连接成功")
                ws.close()
            except ImportError:
                print(f"  需要安装 websocket-client")
            except Exception as e:
                print(f"  WebSocket 失败: {e}")

        except Exception as e:
            pass

    # 查找 IPC pipe
    print("\n[IPC] 查找 VSCode IPC pipes...")
    try:
        import glob
        pipes = glob.glob(r'\\.\pipe\vscode-*')
        for pipe in pipes:
            print(f"  找到 pipe: {pipe}")
    except:
        pass

    return False

def try_webview_inspector():
    """尝试通过 WebView 检查器发送消息"""
    print("\n[WebView] 尝试 WebView 检查器...")

    # 查找 Trae 进程
    import subprocess
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Trae CN.exe', '/FO', 'CSV'],
                          capture_output=True, text=True)
    print(f"  Trae 进程列表:")
    for line in result.stdout.split('\n'):
        if 'Trae CN.exe' in line:
            print(f"    {line}")

    return False

def checkin_via_keyboard():
    """通过键盘快捷键导航到签到"""
    print("\n[键盘] 尝试键盘导航...")

    # 先打开用量管理页面
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(0.5)
    pyautogui.typewrite('用量')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)

    # 使用 Tab 键导航到"每日签到"
    # 根据截图，"每日签到"在右侧面板
    print("  按 Tab 键导航...")
    for i in range(10):
        pyautogui.press('tab')
        time.sleep(0.3)

    # 按回车确认
    print("  按 Enter 确认...")
    pyautogui.press('enter')
    time.sleep(2)

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v30_keyboard.png')
    return read_credits_status()

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v30 - 多策略尝试")
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

    # 策略1: Electron IPC
    try_electron_ipc()

    # 策略2: 键盘导航
    print("\n[策略2] 键盘导航签到...")
    if checkin_via_keyboard():
        print("\n✓ 签到成功！")
        return True

    # 策略3: 精确坐标点击（根据颜色分析）
    print("\n[策略3] 精确坐标点击...")
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v30_before.png')

    # 根据颜色分析，"每日签到"文字在 (937, 400) 附近
    # 但按钮可能需要点击更大的区域
    # 尝试点击"每日签到 >"整个按钮区域
    test_points = [
        (937, 400, "文字中心"),
        (950, 400, "文字右侧"),
        (920, 400, "文字左侧"),
        (937, 395, "文字上方"),
        (937, 405, "文字下方"),
        (1020, 400, "箭头位置"),
        (1000, 400, "箭头左侧"),
    ]

    for x, y, label in test_points:
        print(f"  尝试 {label}: ({x}, {y})")
        pyautogui.click(x, y)
        time.sleep(1)

        if read_credits_status():
            save_screenshot(r'C:\test\github\trae_auto\screenshot_v30_success.png')
            print(f"\n✓ 签到成功！点击位置: ({x}, {y})")
            return True

    # 策略4: 双击
    print("\n[策略4] 双击尝试...")
    pyautogui.doubleClick(937, 400)
    time.sleep(2)

    if read_credits_status():
        save_screenshot(r'C:\test\github\trae_auto\screenshot_v30_dblclick.png')
        print("\n✓ 签到成功！")
        return True

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v30_failed.png')
    print("\n✗ 所有策略失败")
    return False

if __name__ == '__main__':
    checkin()
