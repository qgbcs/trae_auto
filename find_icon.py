#!/usr/bin/env python3
"""
定位 Trae 用户图标位置
用模板匹配找到紫色用户图标
"""

import pyautogui
import time
import sys

pyautogui.PAUSE = 0.2
pyautogui.FAILSAFE = True


def find_icon_position():
    """Find the user icon by template matching"""
    # Take a screenshot of the top area
    print("Taking screenshot of top area...")
    ss = pyautogui.screenshot(region=(0, 0, 1920, 100))
    ss.save(r'C:\test\github\trae_auto\top_bar.png')
    print("Saved: top_bar.png")

    # Based on your screenshot, the user icon is purple and to the left of the credits number
    # Credits are at approximately x=1850, y=15 (from your screen)
    # User icon is about 80px to the left of credits

    # Let's try different positions
    # Screen resolution appears to be 1920x1080 based on the screenshot
    screen_width, screen_height = pyautogui.size()
    print(f"Screen size: {screen_width}x{screen_height}")

    # Try clicking at various positions near the top-right
    # Credits number "393" appears at approximately x=1850, y=15
    test_positions = []

    # Start from the right edge and move left
    for offset in [30, 60, 90, 120, 150, 180, 210]:
        x = screen_width - offset
        y = 18  # Top bar height
        test_positions.append((x, y, f"-{offset}px from right"))

    print("\nTest positions (from right edge, y=18):")
    for x, y, desc in test_positions:
        print(f"  ({x}, {y}): {desc}")

    # Try each position
    for i, (x, y, desc) in enumerate(test_positions):
        print(f"\n[{i+1}] Trying ({x}, {y}) - {desc}")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.3)

        # Screenshot before
        ss_before = pyautogui.screenshot(region=(x-150, y-10, 300, 60))
        ss_before.save(rf'C:\test\github\trae_auto\test_pos_{i+1}_{x}_{y}.png')

        # Click
        pyautogui.click()
        time.sleep(0.8)

        # Screenshot after
        ss_after = pyautogui.screenshot(region=(x-150, y-10, 300, 100))
        ss_after.save(rf'C:\test\github\trae_auto\test_pos_{i+1}_after.png')

        # Check if menu appeared (look for dropdown)
        # The menu should appear below the clicked position
        menu_y = y + 30
        ss_menu = pyautogui.screenshot(region=(x-100, menu_y, 200, 80))
        ss_menu.save(rf'C:\test\github\trae_auto\test_pos_{i+1}_menu.png')

    print("\nDone! Check screenshots to see which position opened the menu")


if __name__ == '__main__':
    find_icon_position()
