#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v26
修正：精确点击"每日签到"按钮
根据截图，用量管理页面在右侧，"每日签到"在奖励积分区域
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

def click_safe(x, y, label=""):
    pyautogui.click(x, y)
    print(f"  点击 {label}: ({x}, {y})")
    time.sleep(0.5)

def checkin():
    print("=" * 50)
    print("Trae CN 签到 v26 - 精确点击")
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

    save_screenshot(r'C:\test\github\trae_auto\screenshot_v26_before.png')

    # 根据截图分析坐标：
    # 用量管理页面在右侧，宽度约 420px
    # "每日签到"按钮在奖励积分区域
    # 从截图看：
    # - 总可用积分 383.56 在 y≈280
    # - 每日签到 > 在 y≈420 附近
    # 但需要相对于 Trae 窗口位置
    # Trae 窗口位置: x=36, y=0, width=1330, height=768
    # 用量管理页面在右侧约 x=700-1120 范围

    print("\n[2] 尝试点击'每日签到'按钮...")

    # 方案1: 直接点击"每日签到"文字区域
    # 根据截图比例估算
    click_safe(950, 420, "'每日签到'按钮")

    # 等待看看是否有变化
    time.sleep(2)
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v26_after1.png')

    # 方案2: 如果没反应，尝试点击箭头 ">"
    print("\n[3] 尝试点击'>'符号...")
    click_safe(1020, 420, "'>'符号")

    time.sleep(2)
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v26_after2.png')

    # 验证
    print("\n[4] 验证签到状态...")
    final = read_credits_status()
    print(f"  状态: {'已签到' if final else '未签到'}")

    if final:
        print("\n✓ 签到成功！")
        return True
    else:
        print("\n✗ 签到失败，尝试其他方式...")
        return False

if __name__ == '__main__':
    checkin()
