# -*- coding: utf-8 -*-
"""
通过本地代理拦截 Trae 网络请求，找到签到 API 真实路径
方法：用 pyautogui 点击用户图标（已知位置）触发菜单，同时监听代理中的请求
"""
import requests
import json
import sys
import time
import pyautogui
from datetime import datetime

# 获取 Trae 窗口信息
import win32gui
import win32con

# 找到 Trae 主窗口
def find_trae_window():
    """查找 Trae 主窗口"""
    HWND = []
    def enum_windows(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'Trae' in title or 'trae' in title.lower():
                results.append((hwnd, title))
    win32gui.EnumWindows(enum_windows, HWND)
    return HWND

print("=== 查找 Trae 窗口 ===")
windows = find_trae_window()
for hwnd, title in windows:
    rect = win32gui.GetWindowRect(hwnd)
    print(f"  HWND={hwnd}, Title='{title}', Rect={rect}")

# 找到 Trae 主窗口（非最小化的）
TRAhwnd = None
TRA_X, TRA_Y = 0, 0
TRA_W, TRA_H = 1330, 768

for hwnd, title in windows:
    rect = win32gui.GetWindowRect(hwnd)
    # 找最大的、非最小化的窗口
    if rect[2] - rect[0] > 500 and rect[3] - rect[1] > 300:
        TRAhwnd = hwnd
        TRA_X, TRA_Y, TRA_W, TRA_H = rect
        print(f"\n>>> Trae 主窗口: {title}")
        print(f"    Position: ({TRA_X}, {TRA_Y}), Size: {TRA_W}x{TRA_H}")
        break

if TRAhwnd is None:
    print("ERROR: 找不到 Trae 主窗口!")
    sys.exit(1)

# 用户图标位置（相对于 Trae 窗口顶部）
# 根据用户反馈，用户图标在窗口顶部工具栏中间偏右
# 窗口宽度 1330，用户图标大约在 (1330/2 + 一些偏移, 20)
# 之前测试 (780, 20) 是屏幕坐标，对应窗口内大约 (780 - TRA_X, 20)
USER_ICON_OFFSET_X = 620  # 相对于窗口左边缘的偏移
USER_ICON_Y = 20  # 窗口顶部

print(f"\n=== 点击用户图标位置 ===")
print(f"  屏幕坐标: ({TRA_X + USER_ICON_OFFSET_X}, {TRA_Y + USER_ICON_Y})")

# 先让鼠标回到安全位置
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False  # 不要靠移到角落来中断

# 记录当前截图位置
start_pos = pyautogui.position()
print(f"  鼠标当前位置: {start_pos}")

# 点击用户图标
target_x = TRA_X + USER_ICON_OFFSET_X
target_y = TRA_Y + USER_ICON_Y

print(f"\n  即将点击: ({target_x}, {target_y})")
print(f"  警告: 这是顶部工具栏的用户图标，不是关闭按钮！")
print(f"  关闭按钮在 ({TRA_X + TRA_W - 80}, {TRA_Y + 15}) 附近")

time.sleep(1)

# 移动并点击
pyautogui.moveTo(target_x, target_y, duration=0.3)
time.sleep(0.3)
pyautogui.click()
print(f"  已点击用户图标位置 ({target_x}, {target_y})")

time.sleep(1.5)  # 等待菜单弹出

# 截图
now_str = datetime.now().strftime("%H%M%S")
screenshot_path = f"C:\\test\\github\\trae_auto\\checkin_v6_menu_{now_str}.png"
screenshot = pyautogui.screenshot()
screenshot.save(screenshot_path)
print(f"  截图已保存: {screenshot_path}")

print(f"\n  当前鼠标位置: {pyautogui.position()}")
print("  请手动确认弹出的菜单中是否有签到按钮")
print("  按 Ctrl+C 中断")

# 保持窗口激活，等待用户确认
print("\n等待用户确认菜单状态...")
time.sleep(3)
