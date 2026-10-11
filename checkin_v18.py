# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v18 - 正确版本
根据截图分析：
- 用户图标在窗口顶部中间偏右，屏幕坐标约 (850, 15)
- 点击后弹出菜单，第一项是"每日领 100 积分"
- 或者点击用量管理页面的"每日签到"按钮
"""
import pyautogui
import win32gui
import win32con
import time
import sys
import json
import os

pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = False

def get_current_credits():
    """读取当前积分"""
    try:
        storage_path = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'iCubeServerData://icube.cloudide' in data:
            server_data = json.loads(data['iCubeServerData://icube.cloudide'])
            # 总积分 = 奖励积分 + 基础积分
            total_credits = server_data.get('totalCredits', 0)
            return total_credits
    except Exception as e:
        print(f"  读取积分失败: {e}")
    return 0

def find_trae_window():
    """查找Trae主窗口"""
    windows = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title.upper():
                rect = win32gui.GetWindowRect(hwnd)
                w, h = rect[2]-rect[0], rect[3]-rect[1]
                if w > 800 and h > 400:
                    results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, windows)
    if not windows:
        return None
    return max(windows, key=lambda x: (x[2][2]-x[2][0]) * (x[2][3]-x[2][1]))

def checkin():
    now_str = time.strftime("%Y%m%d_%H%M%S")
    print(f"=== Trae CN 签到脚本 v18 ===\n")

    # 步骤1: 获取当前积分
    print("步骤1: 获取当前积分...")
    current_credits = get_current_credits()
    print(f"  当前积分: {current_credits}")
    if current_credits >= 483:
        print("  ✓ 积分已超过483，可能已经签到过了")
        return True

    # 步骤2: 查找并激活Trae窗口
    print("\n步骤2: 查找Trae窗口...")
    result = find_trae_window()
    if not result:
        print("ERROR: 找不到Trae窗口!")
        sys.exit(1)

    hwnd, title, rect = result
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    print(f"  窗口: {title}")
    print(f"  大小: {width}x{height}")

    # 步骤3: 点击用户图标打开菜单
    print("\n步骤3: 点击用户图标...")
    # 从截图看，用户图标在屏幕顶部中间偏右，约 (850, 15)
    user_icon_x, user_icon_y = 850, 15
    print(f"  点击: ({user_icon_x}, {user_icon_y})")
    pyautogui.click(user_icon_x, user_icon_y)
    time.sleep(1)

    # 截图确认菜单
    shot_menu = f"C:\\test\\github\\trae_auto\\v18_menu_{now_str}.png"
    pyautogui.screenshot(shot_menu)
    print(f"  截图: {shot_menu}")

    # 步骤4: 点击"每日领 100 积分"
    print("\n步骤4: 点击'每日领 100 积分'...")
    # 从截图看，菜单第一项在用户图标下方约60像素处
    checkin_item_x = user_icon_x
    checkin_item_y = user_icon_y + 60
    print(f"  点击: ({checkin_item_x}, {checkin_item_y})")
    pyautogui.click(checkin_item_x, checkin_item_y)
    time.sleep(2)

    # 截图确认
    shot_after = f"C:\\test\\github\\trae_auto\\v18_after_{now_str}.png"
    pyautogui.screenshot(shot_after)
    print(f"  截图: {shot_after}")

    # 步骤5: 检查积分是否增加
    print("\n步骤5: 检查积分变化...")
    time.sleep(1)
    new_credits = get_current_credits()
    print(f"  新积分: {new_credits}")

    if new_credits > current_credits:
        print(f"\n✓ 签到成功！积分从 {current_credits} 增加到 {new_credits}")
        return True
    else:
        print(f"\n✗ 签到可能失败，积分未变化")
        return False

if __name__ == "__main__":
    checkin()
