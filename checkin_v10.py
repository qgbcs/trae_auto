# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v10 - 窗口内截图 + 精确点击
"""
import pyautogui
import win32gui
import win32ui
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

def capture_window_area(hwnd, x, y, w, h):
    """截取窗口指定区域"""
    try:
        # 获取设备上下文
        hdc = win32gui.GetWindowDC(hwnd)
        if not hdc:
            return None

        # 创建兼容 DC
        mem_dc = win32gui.CreateCompatibleDC(hdc)
        if not mem_dc:
            win32gui.ReleaseDC(hwnd, hdc)
            return None

        # 创建位图
        bitmap = win32gui.CreateCompatibleBitmap(hdc, w, h)
        if not bitmap:
            win32gui.DeleteDC(mem_dc)
            win32gui.ReleaseDC(hwnd, hdc)
            return None

        # 选择位图并复制
        old_bitmap = win32gui.SelectObject(mem_dc, bitmap)
        win32gui.BitBlt(mem_dc, 0, 0, w, h, hdc, x, y, win32con.SRCCOPY)

        # 恢复并清理
        win32gui.SelectObject(mem_dc, old_bitmap)
        win32gui.DeleteDC(mem_dc)
        win32gui.ReleaseDC(hwnd, hdc)

        # 保存
        import io
        bmpinfo = win32gui.GetBitmapInfoStructure(bitmap)
        bmpbits = win32gui.GetBitmapBits(bitmap)

        from PIL import Image
        img = Image.frombuffer('RGB', (w, h), bmpbits, 'RGB', 0, 1, 0)
        win32gui.DeleteObject(bitmap)
        return img
    except Exception as e:
        print(f"  截图错误: {e}")
        return None

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v10 ===\n")

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

# 用户图标：窗口顶部栏，约 55% 宽度处，Y=20px
USER_REL_X = int(width * 0.55)
USER_REL_Y = 20

# 补偿窗口在屏幕外的部分
screen_offset_y = max(0, -top)
screen_x = left + USER_REL_X
screen_y = top + USER_REL_Y + screen_offset_y

print(f"\n用户图标: 窗口内({USER_REL_X}, {USER_REL_Y}), 屏幕({screen_x}, {screen_y})")

# 用 pyautogui 截图 Trae 窗口区域（需要先让 Trae 窗口在前）
print("\n激活 Trae 窗口并截图...")
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 直接保存截图
shot1 = f"C:\\test\\github\\trae_auto\\v10_before_{now_str}.png"
pyautogui.screenshot(shot1, region=(left, top, width, height))
print(f"截图1: {shot1}")

# 点击用户图标
print(f"\n点击用户图标 ({screen_x}, {screen_y})...")
pyautogui.click(screen_x, screen_y)
time.sleep(1.5)

# 截图菜单
shot2 = f"C:\\test\\github\\trae_auto\\v10_menu_{now_str}.png"
pyautogui.screenshot(shot2, region=(left, top, width, height))
print(f"截图2: {shot2}")

# 在菜单中找签到按钮
# 菜单通常在用户图标下方，从 Y=60 开始扫描
MENU_START_Y = USER_REL_Y + 40
FOUND = False

for i in range(6):
    item_y = MENU_START_Y + i * 28
    item_screen_y = top + item_y + screen_offset_y

    # 先检查是否有菜单栏/下拉菜单覆盖
    # 移动鼠标到菜单项位置
    pyautogui.moveTo(screen_x, item_screen_y, duration=0.1)
    time.sleep(0.15)

    # 点击
    pyautogui.click()
    time.sleep(0.5)

    # 截图检查
    shot = f"C:\\test\\github\\trae_auto\\v10_scan{i}_{now_str}.png"
    pyautogui.screenshot(shot, region=(left, top, width, height))
    print(f"  扫描{i}: ({screen_x}, {item_screen_y}), 截图: {shot}")

    # 如果签到成功，积分应该变化，检查截图
    # 暂时只截图，不自动判断
    time.sleep(0.3)

# 最终截图
shot3 = f"C:\\test\\github\\trae_auto\\v10_final_{now_str}.png"
pyautogui.screenshot(shot3, region=(left, top, width, height))
print(f"\n最终截图: {shot3}")

# 恢复窗口焦点
win32gui.SetForegroundWindow(hwnd)
print("\n完成！请检查截图确认签到结果")
