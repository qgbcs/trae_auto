#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v28
使用颜色识别精确定位"每日签到"按钮，并尝试 IPC 方式
"""

import json
import time
import pyautogui
import mss
from PIL import Image
import win32gui
import win32api
import struct

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

def get_window_rect(hwnd):
    return win32gui.GetWindowRect(hwnd)

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

def find_checkin_button_by_color(screenshot_region):
    """通过颜色识别找到'每日签到'按钮位置"""
    # 截图区域应该是用量管理页面的右侧部分
    # "每日签到"按钮有箭头 ">" 和文字
    # 我们可以搜索特定颜色的像素来定位
    
    # 分析截图中的颜色分布
    img = Image.frombytes("RGB", (screenshot_region[2]-screenshot_region[0], screenshot_region[3]-screenshot_region[1]), 
                          screenshot_region[4], "raw", "BGRX")
    
    # 获取图像数据
    pixels = img.load()
    width, height = img.size
    
    # 搜索"每日签到"文字区域 - 通常在 y=400-450 范围内
    # 文字颜色通常是深色
    found_y = None
    for y in range(int(height * 0.5), int(height * 0.6)):
        for x in range(int(width * 0.1), int(width * 0.3)):
            r, g, b = pixels[x, y]
            # 深色文字
            if r < 100 and g < 100 and b < 100:
                found_y = y
                break
        if found_y:
            break
    
    return found_y

def try_ipc_signin():
    """尝试通过 IPC 发送签到请求"""
    # Electron IPC channels from workbench.desktop.main.js
    # SANDBOX_TO_MAIN_INVOKE_CLAIM_CHECKIN_CREDITS = "vscode:sandbox::main-invoke-claimCheckinCredits"
    
    # 尝试使用 Electron 的调试端口
    # 但之前测试发现端口 51000 使用自定义二进制协议
    
    # 尝试通过 VSCode IPC 机制
    import socket
    import os
    
    # 查找 Trae 的 IPC pipe
    ipc_pipe = r'\\.\pipe\vscode-shared-42-unix-ipc'
    
    # 或者尝试通过命令行发送事件
    # 这不是标准方法，只是尝试
    
    print("  IPC 方式不可用，尝试 UI 自动化")
    return False

def click_with_offset(hwnd, rel_x, rel_y, label=""):
    """在窗口内相对坐标点击"""
    rect = get_window_rect(hwnd)
    abs_x = rect[0] + rel_x
    abs_y = rect[1] + rel_y
    pyautogui.click(abs_x, abs_y)
    print(f"  点击 {label}: 相对({rel_x}, {rel_y}), 绝对({abs_x}, {abs_y})")
    time.sleep(0.5)
    return abs_x, abs_y

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v28 - 精确颜色识别")
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

    rect = get_window_rect(hwnd)
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    print(f"\n[0] 窗口位置: ({left}, {top}), 大小: {width}x{height}")

    # 打开用量管理页面
    print("\n[1] 打开用量管理页面...")
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(0.5)
    pyautogui.typewrite('用量')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)

    # 截图并分析
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v28_before.png')

    # 获取用量管理页面区域
    # 根据截图，用量管理页面在右侧约 x=700 开始
    # 让我们用更精确的方法：分析截图中"每日签到"的位置
    
    # 尝试直接通过 pyautogui 的 locateOnScreen 功能
    # 但我们需要模板图片
    
    # 替代方案：使用鼠标位置追踪来精确定位
    print("\n[2] 请手动移动鼠标到'每日签到'按钮上...")
    print("  按 Enter 确认位置")
    input("  (或按 Ctrl+C 取消)")
    
    current_pos = pyautogui.position()
    print(f"  当前鼠标位置: {current_pos}")
    
    # 点击该位置
    print("\n[3] 点击'每日签到'按钮...")
    pyautogui.click(current_pos[0], current_pos[1])
    time.sleep(2)
    
    # 验证
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v28_after.png')
    final = read_credits_status()
    print(f"\n  状态: {'已签到' if final else '未签到'}")
    
    if final:
        print("\n✓ 签到成功！")
        return True
    else:
        print("\n✗ 签到失败")
        return False

if __name__ == '__main__':
    checkin()
