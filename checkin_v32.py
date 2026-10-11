#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v32
使用模板匹配精确定位"每日签到"按钮
"""

import json
import time
import pyautogui
import mss
from PIL import Image, ImageChops
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

def find_button_center(img_path, search_region=None):
    """在截图中找到'每日签到'按钮的中心位置"""
    img = Image.open(img_path)

    # 搜索"每日签到"文字区域
    # 根据之前的分析，在 y=395-410, x=920-1000 范围内
    pixels = img.load()
    w, h = img.size

    # 找到深色文字的边界框
    min_x, min_y, max_x, max_y = w, h, 0, 0
    found = False

    for y in range(390, 420):
        for x in range(900, 1050):
            r, g, b = pixels[x, y][:3]
            # 深色文字
            if r < 60 and g < 60 and b < 60:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                found = True

    if found:
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        print(f"  找到按钮区域: ({min_x}, {min_y}) - ({max_x}, {max_y})")
        print(f"  按钮中心: ({center_x}, {center_y})")
        return center_x, center_y
    else:
        print("  未找到按钮")
        return None, None

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v32 - 模板匹配")
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

    # 截图
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v32.png')

    # 找到按钮中心
    print("\n[2] 定位'每日签到'按钮...")
    btn_x, btn_y = find_button_center(r'C:\test\github\trae_auto\screenshot_v32.png')

    if btn_x is None:
        print("  无法定位按钮，使用默认坐标")
        btn_x, btn_y = 950, 400

    # 点击按钮
    print(f"\n[3] 点击按钮 ({btn_x}, {btn_y})...")
    pyautogui.click(btn_x, btn_y)
    time.sleep(2)

    # 验证
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v32_after.png')
    final = read_credits_status()
    print(f"\n[4] 验证状态: {'已签到' if final else '未签到'}")

    if final:
        print("\n✓ 签到成功！")
        return True
    else:
        print("\n✗ 签到失败")
        return False

if __name__ == '__main__':
    checkin()
