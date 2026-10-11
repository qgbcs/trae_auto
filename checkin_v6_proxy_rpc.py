# -*- coding: utf-8 -*-
"""
通过本地代理（端口 2255）发送签到请求
本地代理有 RPC 接口，可以执行任意 Python 代码
"""
import requests
import json
import time
import sys

PROXY_URL = "http://127.0.0.1:2255"

def rpc_call(method, **kwargs):
    """通过本地代理执行 RPC"""
    url = f"{PROXY_URL}/r={method}"
    try:
        resp = requests.post(url, json=kwargs, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# 测试 RPC 接口
print("=== 测试本地代理 RPC ===")
result = rpc_call("dir", path=r"C:\test\github\trae_auto")
print(f"dir: {result}")

# 获取 Trae 窗口信息
print("\n=== 获取 Trae 窗口 ===")
result = rpc_call("get_trae_window_info")
print(result)

# 尝试通过 pyautogui 执行操作
print("\n=== 尝试执行 pyautogui 操作 ===")
test_code = '''
import pyautogui
import win32gui
import win32con
import time

# 找到 Trae 窗口
def find_trae():
    results = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Trae" in title or "trae" in title.lower():
                rect = win32gui.GetWindowRect(hwnd)
                results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, results)
    return results

windows = find_trae()
print(f"找到 {len(windows)} 个 Trae 窗口:")
for hwnd, title, rect in windows:
    w, h = rect[2]-rect[0], rect[3]-rect[1]
    print(f"  HWND={hwnd}, Title='{title}', Size={w}x{h}, Pos=({rect[0]}, {rect[1]})")

if windows:
    hwnd, title, rect = windows[0]
    w, h = rect[2]-rect[0], rect[3]-rect[1]
    print(f"\\n主窗口: {title}")
    print(f"大小: {w}x{h}")
    print(f"位置: 左上({rect[0]}, {rect[1]}), 右下({rect[2]}, {rect[3]})")
    
    # 用户图标位置：在窗口顶部工具栏，大约在 x=窗口宽度/2 到 2/3 处
    # 窗口宽度约 1330，用户图标大约在 (800-1000, 20) 屏幕坐标
    # 用户说点击 (780, 20) 弹出二级菜单
    print(f"\\n建议点击用户图标位置: ({rect[0]+780-rect[0]}, {rect[1]+20})")
    print(f"即屏幕坐标: (780, 20)")
'''

result = rpc_call("exec_code", code=test_code)
print(result)

# 尝试获取 Trae 窗口截图
print("\n=== 获取 Trae 窗口截图 ===")
screenshot_code = '''
import pyautogui
import win32gui
import time

# 找到 Trae 主窗口
windows = []
def enum(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if "Trae" in title:
            rect = win32gui.GetWindowRect(hwnd)
            results.append((hwnd, title, rect))
win32gui.EnumWindows(enum, windows)

if windows:
    hwnd, title, rect = max(windows, key=lambda x: (x[2][2]-x[2][0])*(x[2][3]-x[2][1]))
    w, h = rect[2]-rect[0], rect[3]-rect[1]
    # 截取窗口区域（减去标题栏）
    left, top, right, bottom = rect
    # 截图整个屏幕
    img = pyautogui.screenshot()
    img.save(r"C:\\test\\github\\trae_auto\\trae_screenshot_now.png")
    print(f"截图已保存: trae_screenshot_now.png")
    print(f"窗口大小: {w}x{h}, 位置: ({left}, {top})")
'''

result = rpc_call("exec_code", code=screenshot_code)
print(result)
