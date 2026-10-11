# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v8 - UI 自动化方案
通过 pyautogui 点击 Trae 窗口顶部用户图标，然后从菜单中点击签到按钮
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
    """找到 Trae 主窗口"""
    windows = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title.upper() or 'trae' in title.lower():
                rect = win32gui.GetWindowRect(hwnd)
                w, h = rect[2]-rect[0], rect[3]-rect[1]
                if w > 400 and h > 200:
                    results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, windows)
    return windows

print("=== 查找 Trae 窗口 ===")
windows = find_trae_window()
if not windows:
    print("ERROR: 找不到 Trae 窗口!")
    sys.exit(1)

main_window = max(windows, key=lambda x: (x[2][2]-x[2][0]) * (x[2][3]-x[2][1]))
hwnd, title, rect = main_window
left, top, right, bottom = rect
width = right - left
height = bottom - top

print(f"主窗口: {title}")
print(f"位置: ({left}, {top}), 大小: {width}x{height}")

# 记录当前积分截图
now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
before_screenshot = f"C:\\test\\github\\trae_auto\\before_checkin_{now_str}.png"
pyautogui.screenshot().save(before_screenshot)
print(f"签到前截图: {before_screenshot}")

# ========== 步骤1: 找到用户图标位置 ==========
# 用户图标在 Trae 窗口顶部工具栏
# 根据用户反馈，点击 (780, 20) 屏幕坐标弹出二级菜单
# 但这是之前窗口位置时的坐标，现在需要根据实际窗口位置计算

# 方法：扫描 Trae 窗口顶部区域，找到用户图标
# 用户图标通常是圆形的头像，在积分数字左侧
# 窗口宽度约 1330，用户图标大约在 x = 窗口宽度 * 0.58 处

# 从上次运行结果看，Trae 窗口位置是 (1282, 628)，大小 64x64（这是错误的，可能找错了窗口）
# 需要找到正确的主窗口

# 尝试找到最大的 Trae 窗口
largest_window = None
largest_area = 0
for hwnd, win_title, win_rect in windows:
    w = win_rect[2] - win_rect[0]
    h = win_rect[3] - win_rect[1]
    area = w * h
    if area > largest_area:
        largest_area = area
        largest_window = (hwnd, win_title, win_rect)

if largest_window:
    hwnd, title, rect = largest_window
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    print(f"\n最大 Trae 窗口: {title}")
    print(f"位置: ({left}, {top}), 大小: {width}x{height}")

# 用户图标位置：在窗口顶部工具栏，积分数字左侧
# 积分数字通常在右上角，用户图标在其左侧约 100-150px
USER_ICON_RELATIVE_X = int(width * 0.55)  # 尝试在 55% 宽度处
USER_ICON_Y = 20

USER_ICON_SCREEN_X = left + USER_ICON_RELATIVE_X
USER_ICON_SCREEN_Y = top + USER_ICON_Y

print(f"\n用户图标位置:")
print(f"  窗口内: ({USER_ICON_RELATIVE_X}, {USER_ICON_Y})")
print(f"  屏幕坐标: ({USER_ICON_SCREEN_X}, {USER_ICON_SCREEN_Y})")
print(f"  关闭按钮: ({right-10}, {top+15})")

time.sleep(1)

# ========== 步骤2: 点击用户图标 ==========
print(f"\n移动鼠标到用户图标...")
pyautogui.moveTo(USER_ICON_SCREEN_X, USER_ICON_SCREEN_Y, duration=0.3)
time.sleep(0.3)

print(f"点击用户图标...")
pyautogui.click()
time.sleep(1.5)

# 截图查看菜单
menu_screenshot = f"C:\\test\\github\\trae_auto\\menu_after_click_{now_str}.png"
pyautogui.screenshot().save(menu_screenshot)
print(f"菜单截图: {menu_screenshot}")

# ========== 步骤3: 在菜单中查找并点击"签到"按钮 ==========
print(f"\n正在寻找签到按钮...")

# 签到按钮通常在菜单的第一个或第二个位置
# 尝试在用户图标正下方扫描菜单项
MENU_SCAN_RANGE = 150  # 向下扫描 150px
MENU_STEP = 30  # 每 30px 尝试一次

for i in range(MENU_SCAN_RANGE // MENU_STEP):
    item_y = USER_ICON_SCREEN_Y + 40 + i * MENU_STEP
    item_x = USER_ICON_SCREEN_X  # 对齐用户图标

    print(f"  尝试 ({item_x}, {item_y})")
    pyautogui.moveTo(item_x, item_y, duration=0.1)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(0.5)

    # 检查是否触发了签到
    check_screenshot = f"C:\\test\\github\\trae_auto\\scan_{i}_{now_str}.png"
    pyautogui.screenshot().save(check_screenshot)
    print(f"    截图: {check_screenshot}")

    # 如果点击后弹出了新的菜单，返回重新扫描
    time.sleep(0.5)

# 最终截图
final_screenshot = f"C:\\test\\github\\trae_auto\\after_checkin_{now_str}.png"
pyautogui.screenshot().save(final_screenshot)
print(f"\n最终截图: {final_screenshot}")
print(f"请检查截图确认签到是否成功")
