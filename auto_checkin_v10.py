#!/usr/bin/env python3
"""
Trae CN 自动签到 v10 - 基于实际截图精确定位
窗口: 36,0,1330,768 (1294x768)
积分 545 在右上角，紫色用户图标在其左侧
"""

import win32gui
import win32con
import pyautogui
import time
import json
import os
import sys

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True

# 窗口信息
WIN_LEFT = 36
WIN_TOP = 0
WIN_RIGHT = 1330
WIN_BOTTOM = 768
WIN_WIDTH = WIN_RIGHT - WIN_LEFT  # 1294
WIN_HEIGHT = WIN_BOTTOM - WIN_TOP  # 768


def find_trae_window():
    """Find Trae main window"""
    results = []

    def enum_proc(hwnd, results):
        try:
            title = win32gui.GetWindowText(hwnd)
            if 'Trae' in title:
                rect = win32gui.GetWindowRect(hwnd)
                style = win32gui.GetWindowLong(hwnd, win32gui.GWL_STYLE)
                is_visible = bool(style & win32gui.WS_VISIBLE)
                is_minimized = bool(style & win32gui.WS_MINIMIZE)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                if is_visible and not is_minimized and w > 800 and h > 500:
                    results.append({'hwnd': hwnd, 'title': title, 'rect': rect, 'size': (w, h)})
        except:
            pass

    win32gui.EnumWindows(enum_proc, results)
    if not results:
        return None
    return max(results, key=lambda x: x['size'][0] * x['size'][1])


def get_credits_from_storage():
    """Get credits from storage.json"""
    storage_path = r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json'
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Look for checkin credits
        for key in data:
            if 'checkin' in key.lower() and 'credit' in key.lower():
                val = data[key]
                if isinstance(val, dict):
                    for k2, v2 in val.items():
                        if isinstance(v2, dict):
                            for k3, v3 in v2.items():
                                if k3 == 'currentCredits' or k3 == 'totalCredits' or k3 == 'credits':
                                    print(f"  {key}.{k2}.{k3} = {v3}")
                                elif 'credit' in k3.lower():
                                    print(f"  {key}.{k2}.{k3} = {v3}")

        # Also check activityStates
        if 'activityStates' in data:
            acts = data['activityStates']
            if isinstance(acts, dict):
                for act_id, state in acts.items():
                    if 'checkin' in act_id.lower():
                        print(f"  Activity {act_id}: {json.dumps(state, ensure_ascii=False)[:200]}")

    except Exception as e:
        print(f"  Storage error: {e}")


def main():
    print("=" * 60)
    print("Trae CN Auto Check-in v10")
    print("=" * 60)

    # Step 1: Find window
    print("\n[1] Finding Trae window...")
    window = find_trae_window()

    if not window:
        # Use known position
        print("  Using known window position")
        rect = (WIN_LEFT, WIN_TOP, WIN_RIGHT, WIN_BOTTOM)
        hwnd = None
    else:
        rect = window['rect']
        hwnd = window['hwnd']
        print(f"  Found: {window['title']} at {rect}")

    # Step 2: Bring to front
    if hwnd:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)

    # Step 3: Get current credits
    print("\n[2] Current credits:")
    get_credits_from_storage()

    # Step 4: Screenshot before
    print("\n[3] Taking screenshot before...")
    ss_before = pyautogui.screenshot()
    ss_before.save(r'C:\test\github\trae_auto\v10_before.png')

    # Step 5: Calculate user icon position
    # Based on screenshot:积分 545 在右上角，用户图标在其左侧
    # 积分数字大约在 x=1150-1200, y=15-35
    # 用户图标在积分左侧约 100-120px

    right_edge = rect[2] - 5  # 5px from right
    top_offset = 18  # 18px from top

    # User icon is to the left of credits number
    # Credits number width is about 60px (for "545")
    # User icon center is about 80px left of credits right edge
    user_icon_x = right_edge - 90
    user_icon_y = top_offset + 12  # Center of icon

    print(f"\n[4] User icon position: ({user_icon_x}, {user_icon_y})")
    print(f"    Window: ({rect[0]}, {rect[1]}) size {rect[2]-rect[0]}x{rect[3]-rect[1]}")

    # Step 6: Move to user icon and click
    print("\n[5] Clicking user icon...")
    pyautogui.moveTo(user_icon_x, user_icon_y, duration=0.3)
    time.sleep(0.3)

    # Click once
    pyautogui.click()
    time.sleep(0.8)

    # Screenshot after click
    ss_after = pyautogui.screenshot()
    ss_after.save(r'C:\test\github\trae_auto\v10_after_click.png')

    # Step 7: Try to find and click 签到 button
    print("\n[6] Looking for 签到 button...")

    # Dropdown menu typically appears below the clicked element
    # Try multiple positions
    menu_y_start = user_icon_y + 30

    positions = [
        (user_icon_x, menu_y_start),           # First item
        (user_icon_x, menu_y_start + 28),      # Second item
        (user_icon_x, menu_y_start + 56),      # Third item
    ]

    for i, (x, y) in enumerate(positions):
        print(f"  Trying position {i+1}: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.3)
        pyautogui.click()
        time.sleep(0.8)

        # Screenshot
        ss = pyautogui.screenshot()
        ss.save(rf'C:\test\github\trae_auto\v10_try_{i+1}.png')

        # Check if credits changed
        get_credits_from_storage()

    # Final state
    print("\n[7] Final state:")
    get_credits_from_storage()

    ss_final = pyautogui.screenshot()
    ss_final.save(r'C:\test\github\trae_auto\v10_final.png')

    print("\n" + "=" * 60)
    print("Screenshots: v10_before.png, v10_after_click.png, v10_final.png")
    print("=" * 60)


if __name__ == '__main__':
    main()
