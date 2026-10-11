# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v13 - 基于实际截图的精确定位
从截图中识别用户头像和签到按钮位置
"""
import pyautogui
import win32gui
import win32con
import time
from datetime import datetime
import sys

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False

def find_trae_window():
    windows = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title.upper():
                rect = win32gui.GetWindowRect(hwnd)
                w, h = rect[2]-rect[0], rect[3]-rect[1]
                if w > 600 and h > 300:
                    results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, windows)
    if not windows:
        return None
    return max(windows, key=lambda x: (x[2][2]-x[2][0]) * (x[2][3]-x[2][1]))

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v13 ===\n")

# 找窗口
print("查找 Trae 窗口...")
result = find_trae_window()
if not result:
    print("ERROR: 找不到 Trae 窗口!")
    sys.exit(1)

hwnd, title, rect = result
left, top, right, bottom = rect
width = right - left
height = bottom - top
print(f"窗口: {title}")
print(f"位置: ({left}, {top}), 大小: {width}x{height}")

# 记录当前积分截图（使用 pyautogui 全屏截图）
print("\n截取当前状态...")
shot_before = f"C:\\test\\github\\trae_auto\\v13_before_{now_str}.png"
pyautogui.screenshot(shot_before)
print(f"截图1（签到前）: {shot_before}")
time.sleep(0.5)

# 激活 Trae 窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.3)

# ========== 关键发现 ==========
# 从截图可以看到：
# 1. Trae 窗口是当前的活动窗口
# 2. 用户头像在顶部工具栏中间偏右位置
# 3. 积分 384 在右上角显示

# 屏幕分辨率 1366x768
# Trae 窗口位置 (28, -8), 大小 1346x784
# 窗口客户区 (36, 0), 大小 1330x768

# 根据截图，用户头像大约在屏幕中央偏右
# 让我们尝试使用不同的点击策略

# 策略1: 在 Trae 窗口顶部栏中间偏右位置点击（用户头像区域）
# 窗口宽度 1330，用户头像大约在 55-60% 处
USER_REL_X = int(1330 * 0.58)  # 约 772
USER_REL_Y = 15  # 顶部工具栏

# 客户区屏幕坐标
client_left = 36
client_top = 0  # 窗口顶部在屏幕外，客户区从 y=0 开始

screen_x = client_left + USER_REL_X
screen_y = client_top + USER_REL_Y
print(f"\n尝试点击用户头像: 窗口内({USER_REL_X}, {USER_REL_Y}), 屏幕({screen_x}, {screen_y})")

# 先移动鼠标到该位置
pyautogui.moveTo(screen_x, screen_y, duration=0.3)
time.sleep(0.3)

# 点击
print("点击用户头像...")
pyautogui.click()
time.sleep(1.5)

# 截图查看菜单
shot_menu = f"C:\\test\\github\\trae_auto\\v13_menu_{now_str}.png"
pyautogui.screenshot(shot_menu)
print(f"截图2（菜单）: {shot_menu}")

# 策略2: 如果菜单出现，在菜单中查找"签到"按钮
# 菜单通常在头像下方，宽度约 200px，每个菜单项约 30px 高
MENU_X = screen_x  # 对齐头像
MENU_START_Y = screen_y + 35
MENU_ITEM_H = 32

print(f"\n扫描菜单项...")
for i in range(10):
    item_y = MENU_START_Y + i * MENU_ITEM_H
    print(f"  尝试 {i}: ({MENU_X}, {item_y})")

    # 移动鼠标并点击
    pyautogui.moveTo(MENU_X, item_y, duration=0.05)
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.4)

    # 截图检查
    shot = f"C:\\test\\github\\trae_auto\\v13_scan{i}_{now_str}.png"
    pyautogui.screenshot(shot)
    print(f"    截图: {shot}")

    # 检查是否签到成功（积分增加）
    time.sleep(0.3)

# 最终截图
shot_final = f"C:\\test\\github\\trae_auto\\v13_final_{now_str}.png"
pyautogui.screenshot(shot_final)
print(f"\n最终截图: {shot_final}")

win32gui.SetForegroundWindow(hwnd)
print("\n完成！请检查截图确认签到结果")
