#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v33
修正：精确点击"每日签到"按钮的右侧箭头区域
"""

import json
import time
import pyautogui
import mss
from PIL import Image
import win32gui

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

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v33 - 精确点击箭头")
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

    # 打开用量管理页面
    print("\n[1] 打开用量管理页面...")
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(0.5)
    pyautogui.typewrite('用量')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v33.png')

    # 根据之前的分析，"每日签到 >" 按钮在:
    # - 文字 "每日签到" 在 x=936-1049, y=400-410
    # - 箭头 ">" 在更右侧
    # 点击箭头区域应该能触发签到

    print("\n[2] 点击'每日签到'按钮区域...")

    # 尝试点击按钮的不同位置
    # 根据截图，"每日签到 >" 是一整行，点击任何位置都应该触发
    test_positions = [
        (950, 405),   # 文字左侧
        (1000, 405),  # 文字中间
        (1030, 405),  # 文字右侧
        (1045, 405),  # 箭头处
        (1050, 405),  # 箭头右侧
    ]

    for x, y in test_positions:
        print(f"  尝试 ({x}, {y})...")
        pyautogui.click(x, y)
        time.sleep(1.5)

        if read_credits_status():
            save_screenshot(r'C:\test\github\trae_auto\screenshot_v33_success.png')
            print(f"\n✓ 签到成功！点击位置: ({x}, {y})")
            return True

    # 如果都没成功，尝试点击更大的区域
    print("\n[3] 尝试更大区域...")
    for dy in [-10, 0, 10]:
        for dx in [-20, 0, 20]:
            x = 1000 + dx
            y = 405 + dy
            print(f"  尝试 ({x}, {y})...")
            pyautogui.click(x, y)
            time.sleep(1)

            if read_credits_status():
                save_screenshot(r'C:\test\github\trae_auto\screenshot_v33_success2.png')
                print(f"\n✓ 签到成功！点击位置: ({x}, {y})")
                return True

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v33_failed.png')
    print("\n✗ 所有尝试失败")
    return False

if __name__ == '__main__':
    checkin()
