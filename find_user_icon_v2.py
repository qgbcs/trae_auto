# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v7 - 直接 UI 自动化，正确点击用户图标
根据用户反馈：用户图标在 Trae 窗口顶部中间，点击弹出二级菜单有签到按钮
"""
import pyautogui
import win32gui
import win32con
import win32api
import time
from datetime import datetime
import sys

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False  # 关闭安全移动

def find_trae_window():
    """找到 Trae 主窗口"""
    windows = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'Trae' in title:
                rect = win32gui.GetWindowRect(hwnd)
                results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, windows)
    return windows

print("=== 查找 Trae 窗口 ===")
windows = find_trae_window()
if not windows:
    print("ERROR: 找不到 Trae 窗口!")
    sys.exit(1)

# 找最大的窗口（主窗口）
main_window = max(windows, key=lambda x: (x[2][2]-x[2][0]) * (x[2][3]-x[2][1]))
hwnd, title, rect = main_window
left, top, right, bottom = rect
width = right - left
height = bottom - top

print(f"主窗口: {title}")
print(f"位置: ({left}, {top}), 大小: {width}x{height}")
print(f"关闭按钮区域: ({right-80}, {top+5}) 到 ({right-10}, {top+35})")

# 用户图标位置：
# 用户说点击 (780, 20) 屏幕坐标弹出二级菜单
# 这是相对屏幕的坐标，不是相对窗口的
# 需要根据 Trae 窗口位置来调整
TRAEE_X = left
TRAEE_Y = top

# 根据用户反馈，用户图标在屏幕坐标 (780, 20) 附近
# 但 (780, 20) 是之前 Trae 窗口的位置，现在窗口可能在不同位置
# 用户图标在 Trae 顶部工具栏，大约在窗口宽度中间偏右
USER_ICON_RELATIVE_X = int(width * 0.58)  # 大约 58% 宽度处
USER_ICON_RELATIVE_Y = 20  # 窗口顶部

USER_ICON_SCREEN_X = TRAEE_X + USER_ICON_RELATIVE_X
USER_ICON_SCREEN_Y = TRAEE_Y + USER_ICON_RELATIVE_Y

print(f"\n=== 用户图标位置 ===")
print(f"窗口内相对坐标: ({USER_ICON_RELATIVE_X}, {USER_ICON_RELATIVE_Y})")
print(f"屏幕坐标: ({USER_ICON_SCREEN_X}, {USER_ICON_SCREEN_Y})")
print(f"关闭按钮在: ({right-10}, {top+15})")

time.sleep(1)

# 截图记录当前位置
screenshot_path = f"C:\\test\\github\\trae_auto\\trae_window_{int(time.time())}.png"
pyautogui.screenshot().save(screenshot_path)
print(f"当前屏幕截图: {screenshot_path}")

# 移动鼠标到用户图标位置
print(f"\n移动鼠标到用户图标位置...")
pyautogui.moveTo(USER_ICON_SCREEN_X, USER_ICON_SCREEN_Y, duration=0.3)
time.sleep(0.5)

# 点击
print(f"点击用户图标...")
pyautogui.click()
time.sleep(1.5)  # 等待菜单弹出

# 截图查看菜单
menu_screenshot = f"C:\\test\\github\\trae_auto\\checkin_menu_{int(time.time())}.png"
pyautogui.screenshot().save(menu_screenshot)
print(f"菜单截图: {menu_screenshot}")

# 现在寻找"签到"按钮
# 通常在弹出的下拉菜单中
# 尝试在用户图标下方点击
print(f"\n等待手动确认菜单状态...")
print(f"请查看 {menu_screenshot} 确认是否弹出了签到菜单")
print(f"当前鼠标位置: {pyautogui.position()}")

time.sleep(3)
