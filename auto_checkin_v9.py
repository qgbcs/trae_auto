#!/usr/bin/env python3
"""
Trae CN 自动签到 v9 - 精确 UI 自动化
先截图分析，再精确点击
"""

import win32gui
import win32con
import pyautogui
import time
import json
import os
import sys

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True  # 移到左上角可紧急停止

TRAJ_STORAGE = r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json'


def find_trae_main_window():
    """Find the main Trae window (largest visible window with Trae in title)"""
    results = []

    def enum_proc(hwnd, results):
        try:
            title = win32gui.GetWindowText(hwnd)
            if 'Trae' in title:
                rect = win32gui.GetWindowRect(hwnd)
                style = win32gui.GetWindowLong(hwnd, win32gui.GWL_STYLE)
                # Check if visible and not minimized
                is_visible = bool(style & win32gui.WS_VISIBLE)
                is_minimized = bool(style & win32gui.WS_MINIMIZE)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                if is_visible and not is_minimized and width > 400 and height > 300:
                    results.append({
                        'hwnd': hwnd,
                        'title': title,
                        'rect': rect,
                        'size': (width, height)
                    })
        except Exception:
            pass

    win32gui.EnumWindows(enum_proc, results)

    if not results:
        # Fallback: find any window with Trae in title
        for hwnd in win32gui.EnumWindows():
            try:
                title = win32gui.GetWindowText(hwnd[0])
                if 'Trae' in title:
                    rect = win32gui.GetWindowRect(hwnd[0])
                    results.append({
                        'hwnd': hwnd[0],
                        'title': title,
                        'rect': rect,
                        'size': (rect[2]-rect[0], rect[3]-rect[1])
                    })
            except:
                pass

    if not results:
        return None

    # Return largest window
    return max(results, key=lambda x: x['size'][0] * x['size'][1])


def bring_windowToFront(hwnd):
    """Bring window to front and restore if minimized"""
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)


def get_current_credits_from_storage():
    """Read credits from storage.json"""
    try:
        with open(TRAJ_STORAGE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Look for checkin_credits or activity data
        for key, value in data.items():
            if 'checkin' in key.lower() or 'credit' in key.lower() or 'activity' in key.lower():
                print(f"  {key}: {json.dumps(value, ensure_ascii=False)[:200]}")

        # Also check for total credits in common keys
        for key in ['commerce.activityStates', 'checkin_credits', 'activityStates']:
            if key in data:
                print(f"  {key}: {json.dumps(data[key], ensure_ascii=False)[:300]}")

    except Exception as e:
        print(f"  Storage read error: {e}")


def click_and_verify():
    """Main check-in flow"""
    print("\n[1] Finding Trae window...")
    window = find_trae_main_window()

    if not window:
        print("  ERROR: No Trae window found!")
        return False

    hwnd = window['hwnd']
    title = window['title']
    rect = window['rect']

    print(f"  Window: {title}")
    print(f"  Position: ({rect[0]}, {rect[1]})")
    print(f"  Size: {rect[2]-rect[0]}x{rect[3]-rect[1]}")

    # Bring to front
    bring_windowToFront(hwnd)
    time.sleep(0.5)

    # Take initial screenshot
    print("\n[2] Taking initial screenshot...")
    initial_ss = pyautogui.screenshot()
    initial_ss.save(r'C:\test\github\trae_auto\v9_initial.png')
    print("  Saved: v9_initial.png")

    # Get current credits from storage
    print("\n[3] Current credits info:")
    get_current_credits_from_storage()

    # Click user icon - positioned near top-right
    # Based on the screenshot: user icon is to the left of credits number
    # Credits are at approximately x=95% of window width, y=15px from top
    # User icon is about 150px to the left of credits

    window_width = rect[2] - rect[0]
    window_height = rect[3] - rect[1]

    # User icon position (approximate based on screenshot analysis)
    user_icon_x = rect[0] + int(window_width * 0.88)  # ~88% from left
    user_icon_y = rect[1] + 20  # ~20px from top

    print(f"\n[4] Clicking user icon at ({user_icon_x}, {user_icon_y})...")

    # Move mouse smoothly
    pyautogui.moveTo(user_icon_x, user_icon_y, duration=0.3)
    time.sleep(0.3)

    # Click
    pyautogui.click()
    time.sleep(0.8)

    # Take screenshot after click
    after_click_ss = pyautogui.screenshot()
    after_click_ss.save(r'C:\test\github\trae_auto\v9_after_click.png')
    print("  Saved: v9_after_click.png")

    # Check if menu opened - look for "签到" text in screenshot
    print("\n[5] Looking for check-in button...")

    # The dropdown menu should appear below the user icon
    # Try clicking at different positions where 签到 might be
    menu_positions = [
        (user_icon_x - 30, user_icon_y + 35),   # First menu item
        (user_icon_x - 30, user_icon_y + 60),   # Second menu item
        (user_icon_x - 50, user_icon_y + 40),   # Alternative position
        (user_icon_x - 20, user_icon_y + 50),   # Another alternative
    ]

    checkin_clicked = False
    for i, (x, y) in enumerate(menu_positions):
        print(f"  Trying position {i+1}: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.3)

        # Take screenshot before click
        ss_before = pyautogui.screenshot(region=(x-100, y-10, 200, 40))
        ss_before.save(rf'C:\test\github\trae_auto\v9_menu_pos_{i}.png')

        pyautogui.click()
        time.sleep(1)

        # Take screenshot after click
        ss_after = pyautogui.screenshot()
        ss_after.save(rf'C:\test\github\trae_auto\v9_after_click_{i}.png')

        # Check if credits changed
        checkin_clicked = True
        break

    if not checkin_clicked:
        print("  WARNING: Could not find check-in button")
        return False

    # Wait for animation
    time.sleep(1)

    # Final screenshot and credits check
    print("\n[6] Verifying result...")
    final_ss = pyautogui.screenshot()
    final_ss.save(r'C:\test\github\trae_auto\v9_final.png')
    print("  Saved: v9_final.png")

    get_current_credits_from_storage()

    print("\n" + "=" * 50)
    print("Screenshots saved to C:\\test\\github\\trae_auto\\")
    print("Check v9_initial.png, v9_after_click.png, v9_final.png")
    print("=" * 50)

    return True


def main():
    print("=" * 50)
    print("Trae CN Auto Check-in v9 (精确点击)")
    print("=" * 50)

    try:
        success = click_and_verify()
        if success:
            print("\n[OK] Check-in flow completed")
            return 0
        else:
            print("\n[FAIL] Check-in failed")
            return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
