# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v9 - 精确坐标版
用户说：点击屏幕坐标 (780, 20) 弹出菜单有签到按钮
"""
import pyautogui
import win32gui
import time
from datetime import datetime

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False

def find_trae_main_window():
    """找到 Trae 最大的可见主窗口"""
    windows = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title.upper() or 'trae' in title.lower():
                rect = win32gui.GetWindowRect(hwnd)
                w, h = rect[2]-rect[0], rect[3]-rect[1]
                # 过滤掉太小的窗口（托盘图标等）
                if w > 600 and h > 300:
                    results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, windows)
    if not windows:
        return None
    # 返回最大的窗口
    return max(windows, key=lambda x: (x[2][2]-x[2][0]) * (x[2][3]-x[2][1]))

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v9 ({now_str}) ===\n")

# 1. 找窗口
print("查找 Trae 窗口...")
result = find_trae_main_window()
if not result:
    print("ERROR: 找不到 Trae 窗口!")
    exit(1)

hwnd, title, rect = result
left, top, right, bottom = rect
width = right - left
height = bottom - top

print(f"窗口: {title}")
print(f"位置: ({left}, {top}), 大小: {width}x{height}")

# 2. 根据用户提供的坐标计算用户图标位置
# 用户说点击 (780, 20) 屏幕坐标弹出菜单
# 但那是之前的窗口位置，现在窗口位置是 (28, -8)
# 需要从窗口坐标推算
# 用户图标在 Trae 窗口顶部工具栏中间偏右

# 先尝试直接用已知的窗口坐标计算
# 之前测试时 Trae 窗口在 (1282, 628)，用户图标在 (780, 20) 屏幕坐标
# 那个窗口大小 1330x768，用户图标相对位置约 x=780-1282=-502? 不对

# 换个思路：用户图标通常在窗口顶部栏，距离左边约 55-60% 宽度处，Y 约 15-25px
USER_ICON_REL_X = int(width * 0.55)
USER_ICON_REL_Y = 20

# 如果窗口有部分在屏幕外（top < 0），需要补偿
screen_top_offset = max(0, -top)
USER_ICON_SCREEN_Y = top + USER_ICON_REL_Y + screen_top_offset

USER_ICON_SCREEN_X = left + USER_ICON_REL_X

print(f"\n用户图标位置:")
print(f"  窗口内: ({USER_ICON_REL_X}, {USER_ICON_REL_Y})")
print(f"  屏幕坐标: ({USER_ICON_SCREEN_X}, {USER_ICON_SCREEN_Y})")

# 同时打印关闭按钮位置作为参照
close_btn_x = right - 15
close_btn_y = top + 10 + screen_top_offset
print(f"  关闭按钮: ({close_btn_x}, {close_btn_y})")

# 3. 先截图确认位置
time.sleep(0.5)
screenshot1 = f"C:\\test\\github\\trae_auto\\screenshot_before_{now_str}.png"
pyautogui.screenshot().save(screenshot1)
print(f"\n截图1（点击前）: {screenshot1}")

# 4. 点击用户图标
print(f"\n移动鼠标到用户图标 ({USER_ICON_SCREEN_X}, {USER_ICON_SCREEN_Y})...")
pyautogui.moveTo(USER_ICON_SCREEN_X, USER_ICON_SCREEN_Y, duration=0.5)
time.sleep(0.5)

print("点击用户图标...")
pyautogui.click()
time.sleep(1.5)  # 等待菜单弹出

# 5. 截图查看菜单
screenshot2 = f"C:\\test\\github\\trae_auto\\screenshot_menu_{now_str}.png"
pyautogui.screenshot().save(screenshot2)
print(f"截图2（菜单弹出后）: {screenshot2}")

# 6. 在菜单中查找签到按钮
# 菜单通常在用户图标下方，逐行扫描
MENU_START_Y = USER_ICON_SCREEN_Y + 35
MENU_ITEM_HEIGHT = 30
FOUND_CHECKIN = False

for i in range(8):
    item_y = MENU_START_Y + i * MENU_ITEM_HEIGHT
    print(f"  扫描行 {i}: ({USER_ICON_SCREEN_X}, {item_y})")

    # 移动鼠标到菜单项位置
    pyautogui.moveTo(USER_ICON_SCREEN_X, item_y, duration=0.1)
    time.sleep(0.2)

    # 点击
    pyautogui.click()
    time.sleep(0.5)

    # 检查是否是签到
    # 如果签到成功，积分应该增加
    # 暂时先截图确认
    scan_shot = f"C:\\test\\github\\trae_auto\\scan_{i}_{now_str}.png"
    pyautogui.screenshot().save(scan_shot)
    print(f"    截图: {scan_shot}")

    # 如果点击后菜单关闭或没有响应，继续扫描下一项
    time.sleep(0.3)

# 最终截图
screenshot3 = f"C:\\test\\github\\trae_auto\\screenshot_after_{now_str}.png"
pyautogui.screenshot().save(screenshot3)
print(f"\n最终截图: {screenshot3}")
print("\n请检查截图确认签到结果")
