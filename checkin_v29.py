#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v29
修正：使用颜色识别找到的精确坐标 (937, 400)
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
    print("Trae CN 签到 v29 - 精确坐标 (937, 400)")
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

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v29_before.png')

    # 使用颜色识别找到的精确坐标
    print("\n[2] 点击'每日签到'按钮 (937, 400)...")
    pyautogui.click(937, 400)
    time.sleep(2)

    # 截图验证
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v29_after.png')

    # 验证
    print("\n[3] 验证签到状态...")
    final = read_credits_status()
    print(f"  状态: {'已签到' if final else '未签到'}")

    if final:
        print("\n✓ 签到成功！")
        return True
    else:
        print("\n✗ 签到失败，尝试其他坐标...")
        # 尝试在附近区域点击
        for dx in [-20, 0, 20]:
            for dy in [-20, 0, 20]:
                x, y = 937 + dx, 400 + dy
                print(f"  尝试 ({x}, {y})...")
                pyautogui.click(x, y)
                time.sleep(1)
                if read_credits_status():
                    save_screenshot(r'C:\test\github\trae_auto\screenshot_v29_success.png')
                    print(f"\n✓ 签到成功！点击位置: ({x}, {y})")
                    return True
        return False

if __name__ == '__main__':
    checkin()
