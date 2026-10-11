#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trae CN 自动签到脚本 - 通过 UI 自动化点击用户图标完成签到"""

import win32gui
import pyautogui
import time
import json
import urllib.request
import os

pyautogui.PAUSE = 0.3

def find_trae_window():
    """Find the main Trae CN window"""
    results = []
    def enum_windows(hwnd, results):
        try:
            title = win32gui.GetWindowText(hwnd)
            if title and 'Trae' in title:
                rect = win32gui.GetWindowRect(hwnd)
                style = win32gui.GetWindowLong(hwnd, win32gui.GWL_STYLE)
                is_visible = bool(style & win32gui.WS_VISIBLE)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                if is_visible and width > 200 and height > 100:
                    results.append({'hwnd': hwnd, 'title': title, 'rect': rect, 'size': (width, height)})
        except:
            pass
    win32gui.EnumWindows(enum_windows, results)
    if not results:
        return None
    # Return the largest visible window
    return max(results, key=lambda x: x['size'][0] * x['size'][1])

def get_user_credits():
    """Get current credits from Trae's API or storage"""
    # Read from storage.json
    storage_path = r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json'
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Look for credits in various keys
        for key in data:
            if 'credit' in key.lower() or 'checkin' in key.lower():
                print(f"  Found {key}: {data[key]}")
    except Exception as e:
        print(f"  Storage read error: {e}")

def click_user_icon():
    """Click the user icon in Trae toolbar to open the menu"""
    window = find_trae_window()
    if not window:
        print("ERROR: No Trae window found!")
        return False

    r = window['rect']
    print(f"Window: {window['title']} at ({r[0]}, {r[1]}) size {r[2]-r[0]}x{r[3]-r[1]}")

    # Take toolbar screenshot for reference
    toolbar_ss = pyautogui.screenshot(region=(r[0], r[1], r[2]-r[0], 80))
    toolbar_ss.save(r'C:\test\github\trae_auto\toolbar.png')

    # User icon is approximately 180px from right edge, 20px from top
    # The credits number is on the right, user icon is to its left
    user_icon_x = r[0] + (r[2] - r[0]) - 180
    user_icon_y = r[1] + 20

    print(f"Clicking user icon at ({user_icon_x}, {user_icon_y})")
    pyautogui.click(user_icon_x, user_icon_y)
    time.sleep(1)

    # Take screenshot after click
    after_ss = pyautogui.screenshot()
    after_ss.save(r'C:\test\github\trae_auto\after_click_user.png')
    print("After click screenshot saved")
    return True

def find_and_click_checkin():
    """Find and click the 签到 button in the dropdown menu"""
    time.sleep(0.5)

    # Search for the checkin button text in the current screen
    # The button should be in the dropdown menu below the user icon
    # Let's try clicking at a position below the user icon
    window = find_trae_window()
    if not window:
        return False

    r = window['rect']
    user_icon_x = r[0] + (r[2] - r[0]) - 180
    menu_y = r[1] + 50  # Dropdown menu starts below the toolbar

    print(f"Looking for checkin button near ({user_icon_x}, {menu_y})")

    # Try multiple positions for the 签到 button
    checkin_positions = [
        (user_icon_x - 20, menu_y),
        (user_icon_x - 20, menu_y + 25),
        (user_icon_x - 20, menu_y + 50),
        (user_icon_x, menu_y + 25),
    ]

    for x, y in checkin_positions:
        print(f"  Trying ({x}, {y})")
        pyautogui.click(x, y)
        time.sleep(1)
        ss = pyautogui.screenshot()
        ss.save(f'C:\\test\\github\\trae_auto\\click_{x}_{y}.png')
        # Check if credits changed
        # We'll verify after all attempts

    return True

def main():
    print("=" * 50)
    print("Trae CN Auto Check-in Script")
    print("=" * 50)

    # Get current credits before
    print("\n[1] Getting current credits...")
    get_user_credits()

    # Click user icon
    print("\n[2] Clicking user icon...")
    click_user_icon()

    # Try to find and click checkin
    print("\n[3] Looking for checkin button...")
    find_and_click_checkin()

    # Wait and verify
    print("\n[4] Waiting for changes...")
    time.sleep(2)

    # Get final state
    print("\n[5] Final state:")
    get_user_credits()
    final_ss = pyautogui.screenshot()
    final_ss.save(r'C:\test\github\trae_auto\final_state.png')
    print("Final screenshot saved")

    print("\nDone!")

if __name__ == '__main__':
    main()
