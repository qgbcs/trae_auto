#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v34
使用 pyautogui locateCenterOnScreen 精确定位按钮
"""

import json
import time
import pyautogui
import mss
from PIL import Image, ImageDraw
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

def find_button_by_color_pattern():
    """通过颜色模式找到按钮位置"""
    # 截图
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    pixels = img.load()
    w, h = img.size

    # "每日签到"按钮的特征：
    # - 文字是深色的
    # - 右侧有 ">" 箭头
    # - 背景可能是浅灰色

    # 搜索 y=380-430 区域
    button_positions = []
    for y in range(380, 430):
        for x in range(900, 1100):
            r, g, b = pixels[x, y][:3]
            # 深色文字
            if r < 50 and g < 50 and b < 50:
                # 检查右侧是否有箭头
                # ">" 箭头通常是浅色或灰色
                if x + 5 < w:
                    ar, ag, ab = pixels[x + 5, y][:3]
                    # 箭头颜色可能不同
                    button_positions.append((x, y))

    if button_positions:
        # 找到按钮的中心
        min_x = min(p[0] for p in button_positions)
        max_x = max(p[0] for p in button_positions)
        min_y = min(p[1] for p in button_positions)
        max_y = max(p[1] for p in button_positions)
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        print(f"  找到按钮: ({min_x}, {min_y}) - ({max_x}, {max_y})")
        print(f"  中心: ({center_x}, {center_y})")
        return center_x, center_y

    return None, None

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v34 - 颜色模式识别")
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

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v34.png')

    # 找到按钮位置
    print("\n[2] 定位按钮...")
    btn_x, btn_y = find_button_by_color_pattern()

    if btn_x is None:
        # 使用固定坐标
        btn_x, btn_y = 1000, 405

    # 尝试点击
    print(f"\n[3] 点击按钮 ({btn_x}, {btn_y})...")
    pyautogui.click(btn_x, btn_y)
    time.sleep(2)

    # 验证
    final = read_credits_status()
    print(f"\n[4] 状态: {'已签到' if final else '未签到'}")

    if final:
        save_screenshot(r'C:\test\github\trae_auto\screenshot_v34_success.png')
        print("\n✓ 签到成功！")
        return True
    else:
        save_screenshot(r'C:\test\github\trae_auto\screenshot_v34_failed.png')
        print("\n✗ 签到失败")
        return False

if __name__ == '__main__':
    checkin()
