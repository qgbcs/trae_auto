#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v27
修正：使用窗口相对坐标，并尝试多种点击方式
"""

import json
import time
import pyautogui
import mss
from PIL import Image
import win32gui
import win32con
import win32api

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
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    return rect  # (left, top, right, bottom)

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

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v27 - 窗口相对坐标")
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

    # 获取窗口位置和大小
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

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v27_before.png')

    # 根据截图计算坐标（相对于屏幕）
    # Trae 窗口: x=36, y=0, width=1330, height=768
    # 用量管理页面在右侧，约占右侧 420px 宽度
    # "每日签到"按钮位置估算：
    # - x: 约 900-1000（窗口右侧区域）
    # - y: 约 400-450（页面中部偏上）

    print("\n[2] 点击'每日签到'按钮...")

    # 尝试多个坐标点
    test_points = [
        (950, 420, "'每日签到'文字"),
        (980, 420, "'>'符号附近"),
        (1000, 420, "右侧箭头"),
        (930, 430, "按钮左边缘"),
        (950, 440, "按钮下边缘"),
    ]

    for x, y, label in test_points:
        print(f"  尝试 {label}: ({x}, {y})")
        pyautogui.click(x, y)
        time.sleep(1)

        # 检查是否签到成功
        if read_credits_status():
            save_screenshot(r'C:\test\github\trae_auto\screenshot_v27_success.png')
            print(f"\n✓ 签到成功！点击位置: ({x}, {y})")
            return True

    # 如果都没成功，截图查看当前状态
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v27_failed.png')
    print("\n✗ 所有尝试失败")
    return False

if __name__ == '__main__':
    checkin()
