#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v25
直接点击用量管理页面的"每日签到"按钮
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
    print("Trae CN 签到 v25 - 直接点击每日签到")
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

    # 截图确认
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v25_before.png')

    # 点击"每日签到"按钮
    # 根据截图，"每日签到"在用量管理页面右侧，大约在 y=430 附近
    print("\n[2] 点击'每日签到'按钮...")
    click_x, click_y = 950, 430
    pyautogui.click(click_x, click_y)
    print(f"  点击 ({click_x}, {click_y})")

    time.sleep(3)

    # 截图确认
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v25_after.png')

    # 验证
    print("\n[3] 验证签到状态...")
    final = read_credits_status()
    print(f"  状态: {'已签到' if final else '未签到'}")

    if final:
        print("\n✓ 签到成功！")
        return True
    else:
        print("\n✗ 签到失败")
        return False

if __name__ == '__main__':
    checkin()
